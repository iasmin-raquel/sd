# Guia Rápido - Comandos Úteis

## Instalação e Setup

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

## Executar o Sistema

### Opção 1: Manualmente (3 terminais)
```bash
# Terminal 1
python peer1/app.py

# Terminal 2
python peer2/app.py

# Terminal 3
python peer3/app.py
```

### Opção 2: Todos juntos (Linux/Mac)
```bash
python peer1/app.py & python peer2/app.py & python peer3/app.py
```

### Opção 3: Com tmux (recomendado)
```bash
# Instalar tmux (se necessário)
sudo apt install tmux  # Ubuntu/Debian
brew install tmux      # Mac

# Criar sessão
tmux new -s cdn_p2p

# Dividir em 3 painéis
Ctrl+b "  # divide horizontal
Ctrl+b "  # divide novamente

# Navegar entre painéis: Ctrl+b + setas

# Em cada painel, execute um peer
python peer1/app.py
python peer2/app.py
python peer3/app.py

# Sair: Ctrl+b d (detach)
# Voltar: tmux attach -t cdn_p2p
```

## Testar o Sistema

### Testes Manuais
```bash
# Browser
http://localhost:5001/file/video1.txt
http://localhost:5002/file/img1.txt
http://localhost:5003/file/Teste-SD.png

# curl
curl http://localhost:5001/file/video1.txt
curl http://localhost:5002/file/video2.txt
curl http://localhost:5003/file/video3.txt

# wget
wget http://localhost:5001/file/Teste-SD.png
```

### Testes Automatizados
```bash
# Script interativo
python test_cdn.py

# Ou direto
python -c "
import requests
import time
for i in range(5):
    r = requests.get('http://localhost:5001/file/video1.txt')
    print(f'Requisição {i+1}: {r.status_code}')
    time.sleep(0.5)
"
```

## Gerenciar Cache

```bash
# Limpar todos os caches
python clear_cache.py

# Limpar manualmente
rm -rf peer1/cache/*
rm -rf peer2/cache/*
rm -rf peer3/cache/*

# Ver tamanho dos caches
du -sh peer*/cache
```

## Monitorar o Sistema

### Ver logs em tempo real
```bash
# Se rodando com &, ver logs
tail -f nohup.out

# Ou redirecionar saída
python peer1/app.py > peer1.log 2>&1 &
python peer2/app.py > peer2.log 2>&1 &
python peer3/app.py > peer3.log 2>&1 &

tail -f peer*.log
```

### Verificar processos
```bash
# Ver se peers estão rodando
ps aux | grep "python.*peer"

# Ver portas em uso
lsof -i :5001
lsof -i :5002
lsof -i :5003

# Ou no Linux
netstat -tulpn | grep 500
```

### Parar todos os peers
```bash
# Linux/Mac
pkill -f "python.*peer"

# Ou encontrar PIDs e matar
ps aux | grep "python.*peer" | awk '{print $2}' | xargs kill
```

## Debug

### Erro: Porta já em uso
```bash
# Encontrar processo usando a porta
lsof -i :5001
# Ou
netstat -tulpn | grep 5001

# Matar processo
kill -9 <PID>
```

### Erro: Módulo não encontrado
```bash
# Verificar ambiente virtual ativo
which python

# Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

### Erro: Permissão negada
```bash
# Dar permissão de execução aos scripts
chmod +x test_cdn.py
chmod +x clear_cache.py
```

## Análise de Resultados

### Comparar políticas
```bash
# Rodar workload aleatório múltiplas vezes
for i in {1..5}; do
    echo "Execução $i"
    python clear_cache.py
    python test_cdn.py # escolher opção 5
    sleep 5
done
```

### Exportar logs
```bash
# Capturar saída para análise
python peer1/app.py 2>&1 | tee peer1_output.txt
python peer2/app.py 2>&1 | tee peer2_output.txt
python peer3/app.py 2>&1 | tee peer3_output.txt

# Contar hits/misses
grep "ACERTO LOCAL" peer1_output.txt | wc -l
grep "ACERTO REMOTO" peer1_output.txt | wc -l
grep "FALHA NO CACHE" peer1_output.txt | wc -l
```

## Git

```bash
# Inicializar repositório
git init

# Adicionar arquivos
git add .

# Commit
git commit -m "Initial commit - CDN P2P com LRU, LFU e GREEN"

# Criar repositório no GitHub e push
git remote add origin <URL>
git push -u origin main
```

## Configurar Diferentes Cenários

### Cenário 1: Regiões diferentes
```python
# Editar peer1/app.py
REGION = 'Recife'

# Editar peer2/app.py
REGION = 'São Paulo'

# Editar peer3/app.py
REGION = 'Manaus'
```

### Cenário 2: Caches maiores
```python
# Editar todos os peers
CACHE_SIZE = 5
```

### Cenário 3: Testar apenas uma política
```python
# Todos os peers com mesma política
POLICY = 'LRU'  # ou 'LFU' ou 'GREEN'
```

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Peer não inicia | Verificar se porta está livre |
| Cache não funciona | Limpar cache e reiniciar |
| Requisição trava | Aumentar timeout nas requisições |
| Arquivo não encontrado | Verificar path em `origin/files/` |
| Import error | Ativar ambiente virtual |

## Atalhos Úteis

```bash
# Alias para facilitar
alias start_peers='python peer1/app.py & python peer2/app.py & python peer3/app.py'
alias stop_peers='pkill -f "python.*peer"'
alias clean_cache='python clear_cache.py'
alias test_cdn='python test_cdn.py'
```

Adicione ao `.bashrc` ou `.zshrc` para persistir entre sessões.
