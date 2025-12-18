import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from flask import Flask, send_file, abort
import os, requests
from cache.lru import LRUCache
from cache.lfu import LFUCache
from cache.green import GreenCache

PEER_NAME='peer3'
PORT=5003
REGION='Caruaru'
POLICY='LFU'
CACHE_SIZE=2
PEERS={'peer1': 'http://localhost:5001', 'peer2': 'http://localhost:5002'}

BASE=os.path.dirname(__file__)
CACHE=os.path.join(BASE,'cache')
ORIGIN=os.path.abspath(os.path.join(BASE,'..','origin','files'))
os.makedirs(CACHE,exist_ok=True)
cache = LRUCache(CACHE_SIZE) if POLICY=='LRU' else (LFUCache(CACHE_SIZE) if POLICY=='LFU' else GreenCache(CACHE_SIZE,REGION))
app=Flask(__name__)
def cp(f): return os.path.join(CACHE,f)
@app.route('/file/<f>')
def getf(f):
    if os.path.exists(cp(f)):
        cache.access(f); 
        print(f"[{PEER_NAME}] ACERTO LOCAL (cache) -> {f}"); 
        return send_file(cp(f))
    for p,u in PEERS.items():
        try:
            r=requests.get(u+'/file/'+f,timeout=10)
            if r.status_code==200:
                print(f"[{PEER_NAME}] ACERTO REMOTO (recebido de {p}) -> {f}")
                open(cp(f),'wb').write(r.content)
                ev=cache.insert(f)
                if ev and os.path.exists(cp(ev)): os.remove(cp(ev))
                return send_file(cp(f))
        except: pass
    of=os.path.join(ORIGIN,f)
    if os.path.exists(of):
        print(f"[{PEER_NAME}] FALHA NO CACHE (busca na origem) -> {f}")
        open(cp(f),'wb').write(open(of,'rb').read())
        ev=cache.insert(f)
        if ev and os.path.exists(cp(ev)): os.remove(cp(ev))
        return send_file(cp(f))
    abort(404)
if __name__=='__main__': app.run(port=PORT)
