#!/usr/bin/env python3
"""
Script de Comparação de Políticas de Cache - CDN P2P
Compara LRU vs LFU vs GREEN em diferentes padrões de acesso
"""

import requests
import time
import random
import statistics
from collections import defaultdict
import subprocess
import sys

# Configuração
PEERS = {
    'peer1': {'url': 'http://localhost:5001', 'policy': 'GREEN', 'region': 'Recife'},
    'peer2': {'url': 'http://localhost:5002', 'policy': 'LRU', 'region': 'Recife'},
    'peer3': {'url': 'http://localhost:5003', 'policy': 'LFU', 'region': 'Recife'},
}

FILES = [
    'video1.mp4',
    'video2.mp4',
]

# NOTA: Teste-SD.png removido por causar timeout


class PolicyComparator:
    def __init__(self):
        self.results = defaultdict(lambda: {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'latencies': [],
            'fast_requests': 0,  # < 50ms (cache hit)
            'slow_requests': 0,  # > 500ms (cache miss)
        })
    
    def clear_all_caches(self):
        """Limpa caches de todos os peers"""
        print("\n🧹 Limpando caches...")
        try:
            subprocess.run(['python3', 'clear_cache.py'], 
                          capture_output=True, check=True)
            time.sleep(1)  # Aguarda limpeza
            print("✓ Caches limpos!\n")
        except:
            print("⚠️  Não foi possível limpar automaticamente")
            print("Execute manualmente: python3 clear_cache.py\n")
            input("Pressione ENTER após limpar os caches...")
    
    def request_file(self, peer_name, file_name):
        """Faz requisição e mede latência"""
        peer = PEERS[peer_name]
        url = f"{peer['url']}/file/{file_name}"
        
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            latency = (time.time() - start) * 1000  # em ms
            
            if response.status_code == 200:
                # Classifica como hit ou miss baseado na latência
                is_cache_hit = latency < 50  # menos de 50ms = cache hit
                
                self.results[peer_name]['total_requests'] += 1
                self.results[peer_name]['latencies'].append(latency)
                
                if is_cache_hit:
                    self.results[peer_name]['cache_hits'] += 1
                    self.results[peer_name]['fast_requests'] += 1
                else:
                    self.results[peer_name]['cache_misses'] += 1
                    if latency > 500:
                        self.results[peer_name]['slow_requests'] += 1
                
                return True, latency, is_cache_hit
            else:
                return False, latency, False
        except Exception as e:
            return False, 0, False
    
    def print_comparison_table(self):
        """Imprime tabela comparativa"""
        print("\n" + "=" * 80)
        print("📊 COMPARAÇÃO DE POLÍTICAS")
        print("=" * 80)
        print(f"{'Política':<10} | {'Requisições':<12} | {'Hit Rate':<10} | "
              f"{'Lat. Média':<12} | {'Lat. Min':<10} | {'Lat. Max':<10}")
        print("-" * 80)
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            data = self.results[peer_name]
            policy = PEERS[peer_name]['policy']
            
            if data['total_requests'] > 0:
                hit_rate = (data['cache_hits'] / data['total_requests']) * 100
                avg_lat = statistics.mean(data['latencies'])
                min_lat = min(data['latencies'])
                max_lat = max(data['latencies'])
                
                print(f"{policy:<10} | {data['total_requests']:<12} | "
                      f"{hit_rate:>6.1f}%    | {avg_lat:>8.2f}ms   | "
                      f"{min_lat:>6.2f}ms  | {max_lat:>6.2f}ms")
        
        print("=" * 80)
        
        # Determina vencedor
        winner = self.get_winner()
        if winner:
            print(f"\n🏆 MELHOR POLÍTICA: {winner['policy']} "
                  f"(Hit Rate: {winner['hit_rate']:.1f}%, "
                  f"Latência: {winner['avg_latency']:.2f}ms)")
    
    def get_winner(self):
        """Determina política vencedora"""
        best = None
        best_score = -1
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            data = self.results[peer_name]
            if data['total_requests'] > 0:
                hit_rate = (data['cache_hits'] / data['total_requests']) * 100
                avg_lat = statistics.mean(data['latencies'])
                
                # Score: 70% hit rate + 30% latência inversa
                score = (hit_rate * 0.7) + ((1000 / avg_lat) * 0.3)
                
                if score > best_score:
                    best_score = score
                    best = {
                        'policy': PEERS[peer_name]['policy'],
                        'hit_rate': hit_rate,
                        'avg_latency': avg_lat
                    }
        
        return best


def test_sequential_access():
    """Teste 1: Acesso Sequencial
    
    Padrão: arquivo1 → arquivo2 → arquivo3 → arquivo4 → arquivo5
    
    Expectativa: LRU deve performar bem (remove o mais antigo)
    """
    print("\n" + "=" * 80)
    print("TESTE 1: PADRÃO DE ACESSO SEQUENCIAL")
    print("=" * 80)
    print("Descrição: Acessa arquivos em ordem sequencial")
    print("Cache Size: 2 arquivos")
    print("Padrão: video1 → video2 → video3 → video4 → video5")
    print("\nExpectativa: LRU deve ter melhor desempenho")
    print("-" * 80)
    
    comp = PolicyComparator()
    comp.clear_all_caches()
    
    # Sequência de acessos
    sequence = FILES * 2  # Repete 2x para ter mais dados
    
    print("\nExecutando requisições sequenciais...")
    for i, file_name in enumerate(sequence, 1):
        print(f"\nRodada {i}/{len(sequence)}: {file_name}")
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            success, latency, is_hit = comp.request_file(peer_name, file_name)
            policy = PEERS[peer_name]['policy']
            status = "HIT " if is_hit else "MISS"
            print(f"  {policy:5s}: {latency:7.2f}ms [{status}]")
        
        time.sleep(0.3)  # Pequeno delay entre requisições
    
    comp.print_comparison_table()
    return comp.results


def test_repeated_access():
    """Teste 2: Acesso com Reuso Frequente
    
    Padrão: arquivo1 usado 5x, outros arquivos usados 1x
    
    Expectativa: LFU deve performar melhor (mantém o mais frequente)
    """
    print("\n" + "=" * 80)
    print("TESTE 2: PADRÃO DE ACESSO COM REUSO FREQUENTE")
    print("=" * 80)
    print("Descrição: Um arquivo é muito popular, outros são raros")
    print("Cache Size: 2 arquivos")
    print("Padrão: video1 (5x) >> video2, video3, video4, video5 (1x cada)")
    print("\nExpectativa: LFU deve ter melhor desempenho")
    print("-" * 80)
    
    comp = PolicyComparator()
    comp.clear_all_caches()
    
    # Sequência: video1 é muito acessado
    sequence = []
    popular_file = 'video1.txt'
    
    for _ in range(3):  # 3 rodadas
        sequence.append(popular_file)  # Arquivo popular
        for other_file in [f for f in FILES if f != popular_file]:
            sequence.append(other_file)  # Outros arquivos
            sequence.append(popular_file)  # Volta pro popular
    
    random.shuffle(sequence)  # Embaralha mas mantém frequências
    
    print(f"\nArquivo popular: {popular_file}")
    print(f"Total de requisições: {len(sequence)}")
    print(f"Frequência de {popular_file}: {sequence.count(popular_file)}/{len(sequence)}")
    
    print("\nExecutando requisições com reuso...")
    for i, file_name in enumerate(sequence, 1):
        if i % 5 == 0:  # Mostra progresso a cada 5 requisições
            print(f"\nProgresso: {i}/{len(sequence)}")
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            comp.request_file(peer_name, file_name)
        
        time.sleep(0.2)
    
    comp.print_comparison_table()
    
    # Estatísticas extras
    print("\n📈 ANÁLISE DE FREQUÊNCIA:")
    print(f"Arquivo popular ({popular_file}): {sequence.count(popular_file)} acessos")
    for file in FILES:
        if file != popular_file:
            print(f"Arquivo raro ({file}): {sequence.count(file)} acessos")
    
    return comp.results


def test_regional_popularity():
    """Teste 3: Popularidade Regional
    
    Padrão: Alguns arquivos são "populares" na região
    
    Expectativa: GREEN deve performar melhor (prioriza por região)
    
    NOTA: Este teste é conceitual porque a implementação atual do GREEN
    não usa informação regional real, mas simula o conceito.
    """
    print("\n" + "=" * 80)
    print("TESTE 3: PADRÃO DE POPULARIDADE REGIONAL")
    print("=" * 80)
    print("Descrição: Arquivos têm popularidades diferentes por região")
    print("Cache Size: 2 arquivos")
    print("Padrão: 70% requisições em 2 arquivos 'regionais', 30% em outros")
    print("\nExpectativa: GREEN deveria ter melhor desempenho")
    print("(conceitual - implementação atual é simplificada)")
    print("-" * 80)
    
    comp = PolicyComparator()
    comp.clear_all_caches()
    
    # Arquivos "populares" na região
    regional_files = ['video1.txt', 'video2.txt']
    other_files = [f for f in FILES if f not in regional_files]
    
    # 70% requisições nos arquivos regionais, 30% nos outros
    sequence = []
    for _ in range(20):
        if random.random() < 0.7:
            sequence.append(random.choice(regional_files))
        else:
            sequence.append(random.choice(other_files))
    
    print(f"\nArquivos regionais populares: {regional_files}")
    print(f"Total de requisições: {len(sequence)}")
    
    print("\nExecutando requisições com viés regional...")
    for i, file_name in enumerate(sequence, 1):
        if i % 5 == 0:
            print(f"\nProgresso: {i}/{len(sequence)}")
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            comp.request_file(peer_name, file_name)
        
        time.sleep(0.2)
    
    comp.print_comparison_table()
    
    # Estatísticas de distribuição
    print("\n📈 DISTRIBUIÇÃO DE ACESSOS:")
    for file in regional_files:
        count = sequence.count(file)
        pct = (count / len(sequence)) * 100
        print(f"Regional ({file}): {count} acessos ({pct:.1f}%)")
    
    for file in other_files:
        count = sequence.count(file)
        pct = (count / len(sequence)) * 100
        print(f"Outros ({file}): {count} acessos ({pct:.1f}%)")
    
    return comp.results


def test_random_workload():
    """Teste 4: Workload Aleatório (Realista)
    
    Padrão: Mix de todos os padrões anteriores
    
    Expectativa: Descobre qual política é mais robusta
    """
    print("\n" + "=" * 80)
    print("TESTE 4: WORKLOAD ALEATÓRIO (REALISTA)")
    print("=" * 80)
    print("Descrição: Mix de padrões sequenciais, frequentes e regionais")
    print("Cache Size: 2 arquivos")
    print("Padrão: Aleatório com viés de Zipf (alguns arquivos mais populares)")
    print("\nExpectativa: Teste de robustez - qual política é mais versátil?")
    print("-" * 80)
    
    comp = PolicyComparator()
    comp.clear_all_caches()
    
    # Distribuição Zipf simplificada: alguns arquivos mais populares
    weights = [5, 3, 2, 1, 1]  # video1 é 5x mais popular que video5
    
    sequence = random.choices(FILES, weights=weights, k=30)
    
    print(f"\nTotal de requisições: {len(sequence)}")
    print("Distribuição esperada: Zipf (poucos arquivos muito populares)")
    
    print("\nExecutando workload aleatório...")
    for i, file_name in enumerate(sequence, 1):
        if i % 5 == 0:
            print(f"\nProgresso: {i}/{len(sequence)}")
            for peer_name in ['peer1', 'peer2', 'peer3']:
                policy = PEERS[peer_name]['policy']
                data = comp.results[peer_name]
                if data['total_requests'] > 0:
                    hit_rate = (data['cache_hits'] / data['total_requests']) * 100
                    print(f"  {policy}: Hit Rate = {hit_rate:.1f}%")
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            comp.request_file(peer_name, file_name)
        
        time.sleep(0.2)
    
    comp.print_comparison_table()
    
    # Distribuição real
    print("\n📈 DISTRIBUIÇÃO REAL DE ACESSOS:")
    for file in FILES:
        count = sequence.count(file)
        pct = (count / len(sequence)) * 100
        print(f"{file}: {count} acessos ({pct:.1f}%)")
    
    return comp.results


def test_cache_size_impact():
    """Teste BONUS: Impacto do Tamanho do Cache
    
    NOTA: Requer modificar CACHE_SIZE nos peers manualmente
    """
    print("\n" + "=" * 80)
    print("TESTE BONUS: IMPACTO DO TAMANHO DO CACHE")
    print("=" * 80)
    print("⚠️  Este teste requer modificação manual do CACHE_SIZE")
    print("Edite peer*/app.py e mude CACHE_SIZE para diferentes valores")
    print("Exemplo: CACHE_SIZE=1, CACHE_SIZE=3, CACHE_SIZE=5")
    print("\nNão implementado no script automático.")
    print("=" * 80)


def compare_all_policies():
    """Executa todos os testes e gera relatório final"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COMPARAÇÃO COMPLETA DE POLÍTICAS" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Verifica se peers estão online
    print("\n🔍 Verificando peers...")
    for peer_name, peer_info in PEERS.items():
        try:
            response = requests.get(f"{peer_info['url']}/file/video1.txt", timeout=2)
            print(f"  ✓ {peer_name} ({peer_info['policy']}): Online")
        except:
            print(f"  ✗ {peer_name} ({peer_info['policy']}): OFFLINE")
            print("\n❌ ERRO: Todos os peers precisam estar rodando!")
            return
    
    # Executa todos os testes
    all_results = {}
    
    tests = [
        ("Sequencial", test_sequential_access),
        ("Reuso Frequente", test_repeated_access),
        ("Regional", test_regional_popularity),
        ("Aleatório", test_random_workload),
    ]
    
    for test_name, test_func in tests:
        input(f"\n▶️  Pressione ENTER para executar: {test_name}")
        all_results[test_name] = test_func()
        time.sleep(2)
    
    # Relatório final
    print("\n\n" + "=" * 80)
    print("🏆 RELATÓRIO FINAL - RESUMO DE TODOS OS TESTES")
    print("=" * 80)
    
    # Conta vitórias
    victories = defaultdict(int)
    
    for test_name, results in all_results.items():
        print(f"\n{test_name}:")
        
        best_policy = None
        best_hit_rate = -1
        
        for peer_name in ['peer1', 'peer2', 'peer3']:
            data = results[peer_name]
            policy = PEERS[peer_name]['policy']
            
            if data['total_requests'] > 0:
                hit_rate = (data['cache_hits'] / data['total_requests']) * 100
                avg_lat = statistics.mean(data['latencies'])
                
                print(f"  {policy:5s}: Hit Rate = {hit_rate:5.1f}%, "
                      f"Latência = {avg_lat:6.2f}ms")
                
                if hit_rate > best_hit_rate:
                    best_hit_rate = hit_rate
                    best_policy = policy
        
        if best_policy:
            print(f"  → Vencedor: {best_policy}")
            victories[best_policy] += 1
    
    print("\n" + "=" * 80)
    print("📊 PLACAR FINAL:")
    print("=" * 80)
    for policy in ['LRU', 'LFU', 'GREEN']:
        wins = victories[policy]
        print(f"  {policy}: {wins} vitória(s)")
    
    overall_winner = max(victories.items(), key=lambda x: x[1])
    print(f"\n🥇 POLÍTICA MAIS ROBUSTA: {overall_winner[0]} "
          f"({overall_winner[1]} vitórias)")
    print("=" * 80)


def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    CDN P2P - Comparação de Políticas de Cache            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    while True:
        print("\n" + "=" * 60)
        print("MENU DE TESTES COMPARATIVOS")
        print("=" * 60)
        print("1. Teste Sequencial (LRU deveria vencer)")
        print("2. Teste de Reuso Frequente (LFU deveria vencer)")
        print("3. Teste Regional (GREEN deveria vencer)")
        print("4. Teste Aleatório (robustez)")
        print("5. 🔥 EXECUTAR TODOS + RELATÓRIO COMPLETO")
        print("0. Sair")
        print()
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '1':
            test_sequential_access()
        elif choice == '2':
            test_repeated_access()
        elif choice == '3':
            test_regional_popularity()
        elif choice == '4':
            test_random_workload()
        elif choice == '5':
            compare_all_policies()
        elif choice == '0':
            print("\nEncerrando...\n")
            break
        else:
            print("\n⚠️  Opção inválida!")
        
        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    main()
