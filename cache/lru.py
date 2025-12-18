from collections import deque
class LRUCache:
    def __init__(s,c): s.c=c; s.q=deque(); s.s=set()
    def access(s,k):
        if k in s.s: s.q.remove(k); s.q.appendleft(k); return True
        return False
    def insert(s,k):
        if k in s.s: s.q.remove(k); s.q.appendleft(k); return None
        ev=None
        if len(s.s)>=s.c: ev=s.q.pop(); s.s.remove(ev)
        s.s.add(k); s.q.appendleft(k); return ev
