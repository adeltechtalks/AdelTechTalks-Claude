import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
from engine.sfxlib import *
import numpy as np, wave
def ting(f=3200, sec=0.5):
    n=int(SR*sec); t=np.arange(n)/SR; x=np.zeros(n)
    for m,a in ((1,1),(2.76,0.4),(5.4,0.2)): x+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/(0.12/m))
    return norm(x,0.35)
def morph(sec=0.5):
    n=int(SR*sec); tt=np.linspace(0,1,n); src=noise(sec); out=np.zeros(n); blk=512
    for s0 in range(0,n,blk):
        c=250+1400*np.sin(np.pi*tt[s0]); seg=src[max(0,s0-2048):s0+blk]
        y=bp(seg,c*0.6,c*1.5); out[s0:s0+blk]=y[-len(out[s0:s0+blk]):]
    return norm(out*np.sin(np.pi*tt)**2,0.3)
def bloop():
    sec=0.22; n=int(SR*sec); t=np.arange(n)/SR; f=220+500*(1-np.exp(-t*30))
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.004,0.06),0.6)
def chime():
    x=np.zeros(int(SR*0.9))
    for i,f in enumerate((1318,1760,2637)):
        y=ting(f,0.7); s=int(i*0.08*SR); x[s:s+len(y)]+=y[:len(x)-s]
    return norm(x,0.45)
add(0.28,bloop(),0.9); add(0.6,morph(0.45),0.8); add(0.85,ting(2900),0.6)
for t0 in (2.6,4.6,7.0,9.4,11.4,13.6): add(t0-0.05,morph(0.55),0.9); add(t0+0.2,ting(3000+(t0*40)%600),0.5)
for t0 in (5.1,7.5):
    for i in range(6): add(t0+i*0.07,tick(2400+i*90),1.1,pan=-0.25+i*0.1)
add(9.7,bloop(),0.8,pan=0.3); add(9.82,bloop(),0.8,pan=-0.3)
add(11.8,pop(),0.9); add(11.84,sparkle(),0.7)
add(14.2,bloop(),0.7); add(15.3,tick(1500),1.2); add(15.42,chime(),0.9)
mix += np.stack([lp(noise(DUR),400)]*2,1)[:len(mix)].astype(np.float32)*0.003
mix=mix/np.abs(mix).max()*0.85; pcm=(mix*32767).astype(np.int16)
with wave.open(config.work('sfx_lg.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
