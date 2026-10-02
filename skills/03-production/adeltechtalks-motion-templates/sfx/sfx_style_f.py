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
def ting(f=3200, sec=0.5):
    n=int(SR*sec); t=np.arange(n)/SR; x=np.zeros(n)
    for m,a in ((1,1),(2.76,0.4),(5.4,0.2)): x+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/(0.12/m))
    return norm(x,0.35)
HB=0.9375
styles=['big','small','strike','strike','big','hero','small','box','small','box','small','big','outline','box','big','count','small','big','strike','small','big','cta']
for i,s in enumerate(styles):
    t=i*HB
    if s in('big',): add2(t,whoosh(0.25,800,6000),0.6); add2(t+0.05,thud(110,0.12),0.6)
    elif s=='hero': add2(t-0.3,riser(0.3),0.6); add2(t,slap(big=True),1.0)
    elif s=='small': add2(t,tick(2400),0.5)
    elif s=='strike': add2(t,tick(2000),0.4); add2(t+0.35,peel(0.22),0.6)
    elif s=='box': add2(t,pop(),0.8)
    elif s=='outline': add2(t,whoosh(0.3,400,4000),0.8,pan=0.6)
    elif s=='count':
        for k in range(12): add2(t+k*0.065,tick(2200+k*60),0.35)
    elif s=='cta': add2(t,pop(),0.9); add2(t+0.8,tick(1500),1.2); add2(t+0.92,ting(2600),0.7); add2(t+1.0,ting(3500),0.5)
m=L.mix/np.abs(L.mix).max()*0.85
with wave.open(config.work('sfx_kt.wav'),'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(L.SR); w.writeframes((m*32767).astype(np.int16).tobytes())
print('ok')
