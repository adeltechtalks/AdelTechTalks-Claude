import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
import numpy as np, wave
import engine.sfxlib as L
D=22.5; L.mix=np.zeros((int(L.SR*D),2),np.float32)
from engine.sfxlib import *
def add2(t,x,g=1.0,pan=0.0):
    i=int(t*L.SR); x=x[:max(0,len(L.mix)-i)]; l,r=np.sqrt(0.5*(1-pan)),np.sqrt(0.5*(1+pan))
    L.mix[i:i+len(x),0]+=x*g*l*1.41; L.mix[i:i+len(x),1]+=x*g*r*1.41
def bloop(f0=220):
    sec=0.22; n=int(SR*sec); t=np.arange(n)/SR; f=f0+500*(1-np.exp(-t*30))
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.004,0.06),0.6)
def ting(f=3200, sec=0.5):
    n=int(SR*sec); t=np.arange(n)/SR; x=np.zeros(n)
    for m,a in ((1,1),(2.76,0.4),(5.4,0.2)): x+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/(0.12/m))
    return norm(x,0.35)
B=1.875
for k,tb in enumerate((0.27,0.55,0.75)): add2(tb,thud(90,0.15),0.9-0.25*k)
for k in range(12): add2(B+0.1+k*0.1,tick(2200+k*30),0.35)
add2(2*B,bloop(260),0.8); add2(2*B+0.05,bloop(330),0.6,pan=0.4); add2(2*B+0.1,bloop(400),0.6,pan=-0.4)
for k in range(3): add2((3+k)*B,pop(),0.8,pan=0.4-0.4*k)
add2(6*B,whoosh(0.4,300,3000),0.8); add2(6*B+0.4,slap(big=True),0.9)
for k in range(6): add2(7*B+0.05+k*0.07,tick(2800),0.4)
add2(8*B+0.1,riser(1.5),0.7); add2(8*B+1.6,ting(2600),0.6)
add2(9*B,whoosh(0.35,600,5000),0.8); add2(9*B+0.2,land(),0.7)
add2(10*B,bloop(200),0.8)
add2(11*B,bloop(300),0.8); add2(11*B+0.8,tick(1500),1.2); add2(11*B+0.92,ting(2600),0.7); add2(11*B+1.0,ting(3500),0.5)
m=L.mix/np.abs(L.mix).max()*0.85
with wave.open(config.work('sfx_bl.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(L.SR); w.writeframes((m*32767).astype(np.int16).tobytes())
print('ok')
