# debug_full.py
import requests
import os
import time

print("DEBUG: Testando conexões...")

# Testar com arquivo real
files = os.listdir('origin/files')
print(f"\nArquivos disponíveis: {files}")

for port in [5001, 5002, 5003]:
    try:
        url = f'http://localhost:{port}/file/imagem1.jpg'
        print(f"\nTestando porta {port}...")
        
        start = time.time()
        r = requests.get(url, timeout=10)
        lat = (time.time() - start) * 1000
        
        print(f"  ✓ Status: {r.status_code}")
        print(f"  ✓ Latência: {lat:.2f}ms")
        print(f"  ✓ Bytes: {len(r.content)}")
        
    except Exception as e:
        print(f"  ✗ Erro: {e}")

print("\n✓ Se todos retornaram 200, peers estão OK!")