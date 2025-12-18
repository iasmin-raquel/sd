#!/usr/bin/env python3
"""
Script de teste automatizado para o CDN P2P
Simula requisições e coleta métricas básicas
"""

import requests
import time
import random
from collections import defaultdict

# Configuração
PEERS = {
    'peer1': {'url': 'http://localhost:5001', 'policy': 'GREEN'},
    'peer2': {'url': 'http://localhost:5002', 'policy': 'LRU'},
    'peer3': {'url': 'http://localhost:5003', 'policy': 'LFU'},
}

FILES = [
    'Teste-SD.png',
    'img1.txt',
    'video1.txt',
    'video2.txt',
    'video3.txt',
    'video4.txt',
]

def test_single_request(peer_name, file_name):
    """Testa uma única requisição"""
    peer = PEERS[peer_name]
    url = f"{peer['url']}/file/{file_name}"
    
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000  # em ms
        
        if response.status_code == 200:
            return {
                'success': True,
                'latency': latency,
                'size': len(response.content)
            }
        else:
            return {'success': False, 'error': f'Status {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def run_basic_test():
    """Teste básico - cada peer requisita todos os arquivos"""
    print("=" * 60)
    print("TESTE BÁSICO - Cada peer requisita todos os arquivos")
    print("=" * 60)
    
    for peer_name in PEERS.keys():
        print(f"\n[{peer_name}] Testando...")
        for file_name in FILES:
            result = test_single_request(peer_name, file_name)
            if result['success']:
                print(f"  ✓ {file_name}: {result['latency']:.2f}ms")
            else:
                print(f"  ✗ {file_name}: {result['error']}")
            time.sleep(0.5)  # Delay entre requisições

def run_cache_test():
    """Teste de cache - requisita o mesmo arquivo várias vezes"""
    print("\n" + "=" * 60)
    print("TESTE DE CACHE - Requisita mesmo arquivo 3x")
    print("=" * 60)
    
    test_file = 'video1.txt'
    
    for peer_name in PEERS.keys():
        print(f"\n[{peer_name}] Testando cache com {test_file}...")
        latencies = []
        
        for i in range(3):
            result = test_single_request(peer_name, test_file)
            if result['success']:
                latencies.append(result['latency'])
                print(f"  Tentativa {i+1}: {result['latency']:.2f}ms")
            time.sleep(0.3)
        
        if len(latencies) >= 2:
            improvement = ((latencies[0] - latencies[-1]) / latencies[0]) * 100
            print(f"  Melhoria: {improvement:.1f}%")

def run_cooperative_test():
    """Teste cooperativo - peer1 busca, depois peer2 busca o mesmo"""
    print("\n" + "=" * 60)
    print("TESTE COOPERATIVO - Compartilhamento entre peers")
    print("=" * 60)
    
    test_file = 'video2.txt'
    
    print(f"\n1. Peer1 requisita {test_file} (deve buscar da origem)...")
    result1 = test_single_request('peer1', test_file)
    if result1['success']:
        print(f"   Latência: {result1['latency']:.2f}ms")
    
    time.sleep(1)
    
    print(f"\n2. Peer2 requisita {test_file} (deve buscar do peer1)...")
    result2 = test_single_request('peer2', test_file)
    if result2['success']:
        print(f"   Latência: {result2['latency']:.2f}ms")
    
    time.sleep(1)
    
    print(f"\n3. Peer3 requisita {test_file} (pode buscar de peer1 ou peer2)...")
    result3 = test_single_request('peer3', test_file)
    if result3['success']:
        print(f"   Latência: {result3['latency']:.2f}ms")

def run_eviction_test():
    """Teste de eviction - enche o cache e observa remoções"""
    print("\n" + "=" * 60)
    print("TESTE DE EVICTION - Cache cheio (capacidade: 2)")
    print("=" * 60)
    
    peer_name = 'peer1'
    test_files = ['video1.txt', 'video2.txt', 'video3.txt']
    
    print(f"\n[{peer_name}] Requisitando 3 arquivos em cache tamanho 2...")
    print("Ordem: video1 → video2 → video3")
    print("Esperado (GREEN): video1 ou video2 será removido")
    
    for i, file_name in enumerate(test_files, 1):
        print(f"\n{i}. Requisitando {file_name}...")
        result = test_single_request(peer_name, file_name)
        if result['success']:
            print(f"   ✓ Sucesso: {result['latency']:.2f}ms")
        time.sleep(0.5)
    
    # Requisita novamente o primeiro arquivo
    print(f"\n4. Requisitando novamente {test_files[0]}...")
    print("   (Se estiver no cache = acerto, se não = miss + cooperação)")
    result = test_single_request(peer_name, test_files[0])
    if result['success']:
        print(f"   Latência: {result['latency']:.2f}ms")

def run_random_workload(num_requests=20):
    """Workload aleatório - simula uso real"""
    print("\n" + "=" * 60)
    print(f"WORKLOAD ALEATÓRIO - {num_requests} requisições")
    print("=" * 60)
    
    metrics = defaultdict(lambda: {'requests': 0, 'total_latency': 0})
    
    for i in range(num_requests):
        peer_name = random.choice(list(PEERS.keys()))
        file_name = random.choice(FILES)
        
        result = test_single_request(peer_name, file_name)
        
        if result['success']:
            metrics[peer_name]['requests'] += 1
            metrics[peer_name]['total_latency'] += result['latency']
            status = "✓"
        else:
            status = "✗"
        
        print(f"{i+1:2d}. [{peer_name}] {file_name:15s} {status}")
        time.sleep(0.2)
    
    print("\n" + "-" * 60)
    print("MÉTRICAS POR PEER:")
    print("-" * 60)
    for peer_name, data in metrics.items():
        if data['requests'] > 0:
            avg_latency = data['total_latency'] / data['requests']
            policy = PEERS[peer_name]['policy']
            print(f"{peer_name} ({policy:5s}): {data['requests']:2d} reqs | "
                  f"Latência média: {avg_latency:.2f}ms")

def check_peers_online():
    """Verifica se todos os peers estão online"""
    print("Verificando status dos peers...")
    all_online = True
    
    for peer_name, peer_info in PEERS.items():
        try:
            response = requests.get(f"{peer_info['url']}/file/video1.txt", timeout=2)
            status = "✓ Online" if response.status_code in [200, 404] else "✗ Erro"
            print(f"  {peer_name}: {status}")
        except:
            print(f"  {peer_name}: ✗ Offline")
            all_online = False
    
    return all_online

def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       CDN P2P - Script de Testes Automatizados           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Verifica se peers estão rodando
    if not check_peers_online():
        print("\n⚠️  ERRO: Nem todos os peers estão online!")
        print("Execute os peers antes de rodar os testes:")
        print("  Terminal 1: python peer1/app.py")
        print("  Terminal 2: python peer2/app.py")
        print("  Terminal 3: python peer3/app.py")
        return
    
    print("\n✓ Todos os peers estão online!\n")
    
    # Menu de testes
    while True:
        print("\n" + "=" * 60)
        print("MENU DE TESTES")
        print("=" * 60)
        print("1. Teste Básico (todos peers, todos arquivos)")
        print("2. Teste de Cache (requisições repetidas)")
        print("3. Teste Cooperativo (compartilhamento P2P)")
        print("4. Teste de Eviction (remoção de cache)")
        print("5. Workload Aleatório")
        print("6. Executar TODOS os testes")
        print("0. Sair")
        print()
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '1':
            run_basic_test()
        elif choice == '2':
            run_cache_test()
        elif choice == '3':
            run_cooperative_test()
        elif choice == '4':
            run_eviction_test()
        elif choice == '5':
            run_random_workload()
        elif choice == '6':
            run_basic_test()
            run_cache_test()
            run_cooperative_test()
            run_eviction_test()
            run_random_workload()
        elif choice == '0':
            print("\nEncerrando...\n")
            break
        else:
            print("\n⚠️  Opção inválida!")
        
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main()
