import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
from engine import sfxlib
sfxlib.DUR = 32.0
import numpy as np
sfxlib.mix = np.zeros((int(sfxlib.SR*32.0),2),np.float32)
from engine.sfxlib import *
import engine.sfxlib as L, wave
def add2(t,x,g=1.0,pan=0.0):
    i=int(t*L.SR); x=x[:max(0,len(L.mix)-i)]; l,r=np.sqrt(0.5*(1-pan)),np.sqrt(0.5*(1+pan))
    L.mix[i:i+len(x),0]+=x*g*l*1.41; L.mix[i:i+len(x),1]+=x*g*r*1.41
def morph(sec=0.5):
    n=int(SR*sec); tt=np.linspace(0,1,n); src=noise(sec); out=np.zeros(n); blk=512
    for s0 in range(0,n,blk):
        c=250+1400*np.sin(np.pi*tt[s0]); seg=src[max(0,s0-2048):s0+blk]
        y=bp(seg,c*0.6,c*1.5); out[s0:s0+blk]=y[-len(out[s0:s0+blk]):]
    return norm(out*np.sin(np.pi*tt)**2,0.3)
def bloop():
    sec=0.22; n=int(SR*sec); t=np.arange(n)/SR; f=220+500*(1-np.exp(-t*30))
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.004,0.06),0.6)
for i in range(4): add2(0.15+i*0.12,tick(2000+i*150),0.6)
for i in range(4): add2(0.75+i*0.12,tick(2300+i*150),0.6)
add2(2.48,bloop(),0.9)
for t0 in (2.75,4.5,8.4,11.0,15.0,24.0): add2(t0-0.05,morph(0.55),1.0)
for i in range(7): add2(5.2+i*0.22,tick(2600),0.7,pan=0.2)
add2(7.2,tick(1500),1.3); add2(7.35,whoosh(0.3,800,4000),0.6)
for i in range(3): add2(9.0+i*0.28,pop(),0.7,pan=-0.4+i*0.4)
for i in range(4):
    for k in range(6): add2(11.4+i*0.55+k*0.07,tick(3000+k*60),0.35)
add2(13.6,riser(1.3),0.8); add2(14.85,sparkle(),0.6)
for i in range(3): add2(15.4+i*0.9,pop(),0.8,pan=0.3 if i!=1 else -0.3)
add2(18.4,riser(0.7),0.7); add2(19.0,whoosh(0.5,200,3000),1.0); add2(19.3,slap(big=True),0.8)
for i in range(3): add2(24.4+i*0.15,tick(1800+i*200),0.6)
add2(26.95,morph(0.55),1.0)
def ting(f=3200, sec=0.5):
    n=int(SR*sec); t=np.arange(n)/SR; x=np.zeros(n)
    for m,a in ((1,1),(2.76,0.4),(5.4,0.2)): x+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/(0.12/m))
    return norm(x,0.35)
def chime():
    x=np.zeros(int(SR*0.9))
    for i,f in enumerate((1318,1760,2637)):
        y=ting(f,0.7); s=int(i*0.08*SR); x[s:s+len(y)]+=y[:len(x)-s]
    return norm(x,0.45)
add2(27.3,bloop(),0.9); add2(28.0,tick(1500),1.3); add2(28.15,chime(),0.9); add2(28.7,whoosh(0.35,500,4000),0.7)
for k in range(5): add2(29.1+k*0.12,tick(2500+k*80),0.7)
for tt in (4.7,8.6,11.2,15.2,19.4): add2(tt+0.1,pop(),0.6,pan=0.5)
for k in range(6): add2(0.6+k*0.15,bloop(),0.25,pan=-0.6+0.24*k)
L.mix += np.stack([lp(noise(32.0),400)]*2,1)[:len(L.mix)].astype(np.float32)*0.003
m=L.mix/np.abs(L.mix).max()*0.85; pcm=(m*32767).astype(np.int16)
with wave.open(config.work('sfx_ui.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(L.SR); w.writeframes(pcm.tobytes())
print('ok')
