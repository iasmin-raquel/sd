from collections import defaultdict
class LFUCache:
    def __init__(s,c): s.c=c; s.f=defaultdict(int)
    def access(s,k):
        if k in s.f: s.f[k]+=1; return True
        return False
    def insert(s,k):
        if k in s.f: s.f[k]+=1; return None
        ev=None
        if len(s.f)>=s.c: ev=min(s.f,key=s.f.get); del s.f[ev]
        s.f[k]=1; return ev
