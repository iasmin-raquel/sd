#!/usr/bin/env python3
"""
Teste SIMPLES - Passo a passo
"""

import requests
import time
import os
import glob

print("\n" + "="*60)
print("TESTE SIMPLES - CDN P2P")
print("="*60)

# Configuração
PEERS = {
    'peer1': 'http://localhost:5001',
    'peer2': 'http://localhost:5002',
    'peer3': 'http://localhost:5003',
}

FILES = ['video1.txt', 'video2.txt']

# ==============================================================
# PASSO 1: Verificar se peers estão online
# ==============================================================
print("\n📍 PASSO 1: Verificando se peers estão online...")
all_online = True

for name, url in PEERS.items():
    try:
        r = requests.get(f'{url}/file/{FILES[0]}', timeout=5)
        if r.status_code in [200, 404]:
            print(f"  ✓ {name}: Online")
        else:
            print(f"  ✗ {name}: Status estranho ({r.status_code})")
            all_online = False
    except Exception as e:
        print(f"  ✗ {name}: Offline ou erro - {e}")
        all_online = False

if not all_online:
    print("\n❌ Nem todos os peers estão online!")
    print("Execute em terminais separados:")
    print("  python3 peer1/app.py")
    print("  python3 peer2/app.py")
    print("  python3 peer3/app.py")
    exit(1)

print("✓ Todos os peers estão online!")

# ==============================================================
# PASSO 2: Limpar caches
# ==============================================================
print("\n📍 PASSO 2: Limpando caches...")
cleared = 0

for peer in ['peer1', 'peer2', 'peer3']:
    cache_dir = f'{peer}/cache'
    if os.path.exists(cache_dir):
        for f in glob.glob(f'{cache_dir}/*'):
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    cleared += 1
                except:
                    pass

print(f"✓ {cleared} arquivo(s) removido(s)")

# ==============================================================
# PASSO 3: Teste com UMA requisição
# ==============================================================
print("\n📍 PASSO 3: Fazendo UMA requisição em cada peer...")
print(f"Arquivo: {FILES[0]}\n")

for name, url in PEERS.items():
    try:
        start = time.time()
        r = requests.get(f'{url}/file/{FILES[0]}', timeout=30)
        latency = (time.time() - start) * 1000
        
        if r.status_code == 200:
            print(f"  ✓ {name}: {latency:.2f}ms - {len(r.content)} bytes recebidos")
        else:
            print(f"  ✗ {name}: Erro {r.status_code}")
    except Exception as e:
        print(f"  ✗ {name}: Erro - {e}")

# ==============================================================
# PASSO 4: Teste de CACHE (requisição repetida)
# ==============================================================
print("\n📍 PASSO 4: Testando CACHE (requisição repetida)...")
print(f"Peer: peer1, Arquivo: {FILES[0]}\n")

# Primeira requisição
start = time.time()
r1 = requests.get(f'{PEERS["peer1"]}/file/{FILES[0]}', timeout=30)
lat1 = (time.time() - start) * 1000

print(f"  1ª requisição: {lat1:.2f}ms")

time.sleep(0.5)

# Segunda requisição (deveria ser do cache)
start = time.time()
r2 = requests.get(f'{PEERS["peer1"]}/file/{FILES[0]}', timeout=30)
lat2 = (time.time() - start) * 1000

print(f"  2ª requisição: {lat2:.2f}ms")

if lat2 < lat1 / 2:
    print(f"  ✓ CACHE FUNCIONANDO! ({((lat1-lat2)/lat1*100):.0f}% mais rápido)")
else:
    print(f"  ⚠️  Cache pode não estar funcionando (diferença pequena)")

# ==============================================================
# PASSO 5: Teste de COOPERAÇÃO P2P
# ==============================================================
print("\n📍 PASSO 5: Testando COOPERAÇÃO P2P...")
print("Limpar cache de peer2, depois pedir arquivo que peer1 tem\n")

# Limpar cache do peer2
cache_dir = 'peer2/cache'
if os.path.exists(cache_dir):
    for f in glob.glob(f'{cache_dir}/*'):
        if os.path.isfile(f):
            os.remove(f)

print(f"  Cache de peer2 limpo")

# Peer1 deve ter o arquivo no cache (do teste anterior)
# Peer2 vai buscar de peer1

start = time.time()
r = requests.get(f'{PEERS["peer2"]}/file/{FILES[0]}', timeout=30)
latency = (time.time() - start) * 1000

print(f"  peer2 requisitou: {latency:.2f}ms")

if 10 < latency < 100:
    print(f"  ✓ COOPERAÇÃO P2P FUNCIONANDO! (pegou de peer1)")
    print(f"    Latência típica de cooperação: 10-100ms")
elif latency < 10:
    print(f"  ⚠️  Muito rápido - pode ter sido cache local")
else:
    print(f"  ⚠️  Muito lento - pode ter ido na origem")

# ==============================================================
# PASSO 6: Teste de EVICTION (remoção de cache)
# ==============================================================
print("\n📍 PASSO 6: Testando EVICTION (cache cheio)...")
print("Cache size = 2, vamos requisitar 3 arquivos diferentes\n")

# Limpar cache de peer1
cache_dir = 'peer1/cache'
if os.path.exists(cache_dir):
    for f in glob.glob(f'{cache_dir}/*'):
        if os.path.isfile(f):
            os.remove(f)

print(f"  Cache de peer1 limpo")

# Criar arquivo extra se não existir
extra_file = 'teste_extra.txt'
extra_path = f'origin/files/{extra_file}'
if not os.path.exists(extra_path):
    with open(extra_path, 'w') as f:
        f.write("Arquivo extra para teste de eviction")
    print(f"  Criado arquivo extra: {extra_file}")

test_files = [FILES[0], FILES[1], extra_file]

print(f"\n  Requisitando 3 arquivos em cache tamanho 2:")
for i, file in enumerate(test_files, 1):
    r = requests.get(f'{PEERS["peer1"]}/file/{file}', timeout=30)
    print(f"    {i}. {file}: {r.status_code}")
    time.sleep(0.5)

print(f"\n  Verificando cache de peer1:")
cache_files = glob.glob('peer1/cache/*')
print(f"    Arquivos no cache: {len(cache_files)}")
for f in cache_files:
    print(f"      - {os.path.basename(f)}")

if len(cache_files) == 2:
    print(f"  ✓ EVICTION FUNCIONANDO! (manteve apenas 2 arquivos)")
else:
    print(f"  ⚠️  Esperava 2 arquivos, encontrou {len(cache_files)}")

# ==============================================================
# RESUMO
# ==============================================================
print("\n" + "="*60)
print("✅ RESUMO DOS TESTES")
print("="*60)
print("Se todos os passos passaram, o sistema está funcionando!")
print("\nPróximo passo:")
print("  python3 compare_policies.py")
print("="*60 + "\n")