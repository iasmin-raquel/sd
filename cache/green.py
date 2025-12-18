from collections import defaultdict
class GreenCache:
    def __init__(s,c,r): s.c=c; s.r=r; s.sc=defaultdict(int)
    def access(s,k):
        if k in s.sc: s.sc[k]+=2; return True
        return False
    def insert(s,k):
        if k in s.sc: s.sc[k]+=2; return None
        ev=None
        if len(s.sc)>=s.c: ev=min(s.sc,key=s.sc.get); del s.sc[ev]
        s.sc[k]=2; return ev
