import math
g=9.81
# ---- caudales por local (AF, ACS) l/s
STD=(0.60,0.33); ADP=(0.40,0.165); OFI=(0.50,0.20)
PB_AF=8.03; PB_ACS=4.10; SOT_AF=0.20
LEFT=dict(std=12,adp=2,ofi=0); RIGHT=dict(std=12,adp=0,ofi=1)
def qside(s,k): return s['std']*STD[k]+s['adp']*ADP[k]+s['ofi']*OFI[k]
QL=(qside(LEFT,0),qside(LEFT,1)); QR=(qside(RIGHT,0),qside(RIGHT,1))
def une(qt):
    if qt<=0: return 0
    qc=0.698*qt**0.5-0.12 if qt<=20 else qt**0.366
    return min(qt,qc)
# ---- tubos (Di mm) multicapa y PE100 SDR11
MC=[('MC 16x2',12),('MC 20x2',16),('MC 26x3',20),('MC 32x3',26),('MC 40x3.5',33),('MC 50x4',42),('MC 63x4.5',54),('MC 75x5',65),('MC 90x6',78)]
PE=[('PE 40x3.7',32.6),('PE 50x4.6',40.8),('PE 63x5.8',51.4),('PE 75x6.8',61.4),('PE 90x8.2',73.6),('PE 110x10',90.0),('PE 125x11.4',102.2)]
EPS=0.007e-3
def pick(Q,v,ser):
    dt=math.sqrt(4*Q/1000/(math.pi*v))*1000
    for n,d in ser:
        if d>=dt: return n,d
    return ser[-1]
def loss(Q,D,L,K,nu,fL=1.3):
    if Q<=0: return 0,0,0
    A=math.pi*(D/1000)**2/4; v=Q/1000/A; Re=v*D/1000/nu
    f=0.25/math.log10(EPS/(3.7*D/1000)+5.74/Re**0.9)**2
    hf=f*L*fL/(D/1000)*v*v/2/g; hm=K*v*v/2/g
    return v,hf,hm
print('QL',QL,'QR',QR)
