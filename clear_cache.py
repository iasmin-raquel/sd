#!/usr/bin/env python3
"""
Script para limpar os caches de todos os peers
Útil para resetar o ambiente de testes
"""

import os
import shutil

def clear_cache(peer_name):
    """Remove todos os arquivos do cache de um peer"""
    cache_path = os.path.join(os.path.dirname(__file__), peer_name, 'cache')
    
    if os.path.exists(cache_path):
        files = os.listdir(cache_path)
        if files:
            for file in files:
                file_path = os.path.join(cache_path, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"  ✓ Removido: {peer_name}/cache/{file}")
                except Exception as e:
                    print(f"  ✗ Erro ao remover {file}: {e}")
            return len(files)
        else:
            print(f"  Cache já está vazio")
            return 0
    else:
        print(f"  Diretório de cache não existe")
        return 0

def main():
    print("\n" + "=" * 60)
    print("LIMPEZA DE CACHES - CDN P2P")
    print("=" * 60)
    
    peers = ['peer1', 'peer2', 'peer3']
    total_removed = 0
    
    for peer in peers:
        print(f"\n[{peer}]")
        removed = clear_cache(peer)
        total_removed += removed
    
    print("\n" + "=" * 60)
    print(f"Total de arquivos removidos: {total_removed}")
    print("=" * 60)
    print("\n✓ Caches limpos! Pronto para novos testes.\n")

if __name__ == "__main__":
    main()
