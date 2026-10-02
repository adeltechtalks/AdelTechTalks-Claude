import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
import numpy as np, wave
import engine.sfxlib as L
D=24.1; L.mix=np.zeros((int(L.SR*D),2),np.float32)
from engine.sfxlib import *
def add2(t,x,g=1.0,pan=0.0):
    i=int(t*L.SR); x=x[:max(0,len(L.mix)-i)]; l,r=np.sqrt(0.5*(1-pan)),np.sqrt(0.5*(1+pan))
    L.mix[i:i+len(x),0]+=x*g*l*1.41; L.mix[i:i+len(x),1]+=x*g*r*1.41
def ting(f=3200, sec=0.5):
    n=int(SR*sec); t=np.arange(n)/SR; x=np.zeros(n)
    for m,a in ((1,1),(2.76,0.4),(5.4,0.2)): x+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/(0.12/m))
    return norm(x,0.35)
BAR=1.875
for k in range(12):
    t0=k*BAR; add2(t0,whoosh(0.35,500,5000),0.7,pan=-0.5 if k%2 else 0.5); add2(t0+0.3,land(),0.7)
for i in range(3): add2(5*BAR+0.1+i*0.12,tick(2400+i*200),0.6)
for k in range(20): add2(9*BAR+0.05+k*0.065,tick(2000+k*40),0.4)
add2(10*BAR+0.05,slap(big=True),0.8)
add2(22.5,pop(),0.9); add2(23.25,tick(1500),1.2); add2(23.35,ting(2600),0.7); add2(23.45,ting(3500),0.5)
m=L.mix/np.abs(L.mix).max()*0.85
with wave.open(config.work('sfx_iso.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(L.SR); w.writeframes((m*32767).astype(np.int16).tobytes())
print('ok')
