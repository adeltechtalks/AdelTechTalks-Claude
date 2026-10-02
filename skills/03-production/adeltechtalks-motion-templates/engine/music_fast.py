import numpy as np, wave, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; BPM=128; BEAT=60/BPM; BAR=4*BEAT; DUR=float(sys.argv[1]); N=int(SR*DUR); DROP=float(sys.argv[2]); END=float(sys.argv[3])
rng=np.random.default_rng(3)
def lp(x,f): return sosfilt(butter(2,f,'lowpass',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'highpass',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'bandpass',fs=SR,output='sos'),x)
def m2f(n): return 440*2**((n-69)/12)
def place(buf,t,x,g=1.0):
    i=int(t*SR); x=x[:max(0,len(buf)-i)]; buf[i:i+len(x)]+=x*g
CH=[[60,64,67,71],[55,59,62,67],[57,60,64,67],[53,57,60,64]]; BASS=[36,43,45,41]
tr={k:np.zeros(N) for k in ('kick','clap','hat','ohat','stab','bass','pad','arp','roll')}
def kick():
    t=np.arange(int(SR*0.3))/SR; f=48+110*np.exp(-t*35); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.11)
def clap():
    n=int(SR*0.22); t=np.arange(n)/SR; x=bp(rng.standard_normal(n),1000,5000); e=np.exp(-t/0.06)
    for d in (0.008,0.016): e[int(d*SR):]+=0.6*np.exp(-(t[:n-int(d*SR)])/0.01)
    return x*e
def hat(o=False):
    n=int(SR*(0.25 if o else 0.06)); t=np.arange(n)/SR; return hp(rng.standard_normal(n),8000)*np.exp(-t/(0.07 if o else 0.012))
def stab(notes):
    n=int(SR*0.28); t=np.arange(n)/SR; x=np.zeros(n)
    for m in notes:
        f=m2f(m+12)
        for dt in (-0.004,0.004): x+=np.sign(np.sin(2*np.pi*f*(1+dt)*t))*0.5+np.sin(2*np.pi*f*t)
    return lp(x,3500)*np.exp(-t/0.09)*np.minimum(1,t/0.003)
def bassn(m):
    n=int(SR*0.22); t=np.arange(n)/SR; f=m2f(m); return lp(np.sin(2*np.pi*f*t)+0.5*np.sign(np.sin(2*np.pi*f*t)),600)*np.exp(-t/0.12)*np.minimum(1,t/0.004)
def padn(notes,sec):
    t=np.arange(int(SR*sec))/SR; x=np.zeros_like(t)
    for m in notes:
        for d in (-0.15,0.15): x+=np.sin(2*np.pi*m2f(m)*(1+d/100)*t)
    return x*np.minimum(1,t/0.2)*np.minimum(1,np.clip((sec-t)/0.4,0,1))
def arpn(m):
    t=np.arange(int(SR*0.2))/SR; return np.sin(2*np.pi*m2f(m+24)*t)*np.exp(-t/0.07)
nb=int(np.ceil(DUR/BAR))
for b in range(nb):
    t0=b*BAR; ch=CH[b%4]
    if t0>=END: 
        place(tr['pad'],t0,padn(CH[0],DUR-t0+0.1),0.5); break
    place(tr['pad'],t0,padn(ch,BAR+0.2),0.35)
    build = DROP-BAR<=t0<DROP
    for k in range(4):
        tb=t0+k*BEAT
        if not build or k<2: place(tr['kick'],tb,kick(),1.0)
        place(tr['ohat'],tb+BEAT/2,hat(True),0.35)
        if k in (1,3) and not build: place(tr['clap'],tb,clap(),0.5)
        place(tr['bass'],tb+BEAT/2,bassn(BASS[b%4]),0.7)
        if b>0: place(tr['stab'],tb+BEAT/2,stab(ch),0.25)
    for k in range(16):
        place(tr['hat'],t0+k*BEAT/4,hat(),0.18 if k%2 else 0.1)
        if t0>=DROP: place(tr['arp'],t0+k*BEAT/4,arpn(ch[k%4]),0.18)
    if build:
        for k in range(16):
            tt=t0+BAR/2+k*BAR/32; place(tr['roll'],tt,clap()*0.8,0.2+0.5*k/16)
env=lp(np.abs(tr['kick']),10); env/=env.max()+1e-9
pump=1-0.5*env
mix=(tr['kick']+tr['clap']+tr['hat']+tr['ohat']+tr['roll']+(tr['stab']+tr['pad']*0.6+tr['bass'])*pump+tr['arp'])
ir=rng.standard_normal(int(SR*0.6))*np.exp(-np.arange(int(SR*0.6))/(SR*0.15)); ir/=np.abs(ir).sum()/5
mix+=fftconvolve(tr['stab']+tr['clap']+tr['arp'],ir)[:N]*0.2
mix*=np.clip((DUR-np.arange(N)/SR)/1.0,0,1)
mix/=np.abs(mix).max()
st=np.stack([mix+0.05*np.roll(tr['hat']+tr['arp'],300),mix-0.05*np.roll(tr['hat']+tr['arp'],300)],1); st/=np.abs(st).max()
with wave.open(config.work('music_fast.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*0.85*32767).astype(np.int16).tobytes())
print('ok')
