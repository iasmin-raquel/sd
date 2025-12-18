# CDN P2P - Cache Cooperativo

Projeto de Sistemas Distribuídos - UFAPE  
**Algoritmos de Política de Cache Cooperativo em CDN P2P**

## 📋 Descrição

Sistema CDN P2P com três políticas de cache cooperativo:
- **LRU** (Least Recently Used): Remove itens menos recentemente usados
- **LFU** (Least Frequently Used): Remove itens menos frequentemente acessados
- **GREEN**: Cache adaptativo baseado em demanda regional

## 🚀 Instalação

### 1. Clone ou extraia o projeto

```bash
cd cdn_p2p
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

**Opção 1: Instalação completa**
```bash
pip install -r requirements.txt
```

**Opção 2: Instalação mínima (apenas essencial)**
```bash
pip install -r requirements-minimal.txt
```

**Opção 3: Instalação manual**
```bash
pip install flask requests
```

## ▶️ Execução

### Inicie os 3 peers (em terminais separados)

**Terminal 1:**
```bash
python peer1/app.py
```
- Porta: 5001
- Região: Recife
- Política: GREEN
- Cache: 2 arquivos

**Terminal 2:**
```bash
python peer2/app.py
```
- Porta: 5002
- Região: São Paulo
- Política: LRU
- Cache: 2 arquivos

**Terminal 3:**
```bash
python peer3/app.py
```
- Porta: 5003
- Região: Rio de Janeiro
- Política: LFU
- Cache: 2 arquivos

## 🧪 Testando

### Via Browser
Acesse: `http://localhost:5001/file/Teste-SD.png`

### Via curl
```bash
# Requisição no peer1
curl http://localhost:5001/file/video1.txt

# Requisição no peer2
curl http://localhost:5002/file/img1.txt

# Requisição no peer3
curl http://localhost:5003/file/Teste-SD.png
```

## 📊 Como Funciona

1. **Requisição chega no peer**
2. **Busca no cache local** (acerto → retorna imediatamente)
3. **Busca em outros peers** (cooperação P2P)
4. **Busca na origem** (se ninguém tiver)
5. **Armazena no cache** seguindo a política configurada
6. **Eviction** se cache cheio (remove arquivo baseado na política)

## 🔧 Configuração dos Peers

Cada `app.py` possui configurações no topo:

```python
PEER_NAME = 'peer1'      # Nome do peer
PORT = 5001              # Porta HTTP
REGION = 'Recife'        # Região geográfica
POLICY = 'GREEN'         # Política: LRU, LFU ou GREEN
CACHE_SIZE = 2           # Número máximo de arquivos
```

## 📁 Estrutura do Projeto

```
cdn_p2p/
├── cache/
│   ├── __init__.py
│   ├── lru.py           # Implementação LRU
│   ├── lfu.py           # Implementação LFU
│   └── green.py         # Implementação GREEN
├── origin/
│   └── files/           # Arquivos originais (servidor origem)
│       ├── Teste-SD.png
│       ├── img1.txt
│       ├── video1.txt
│       ├── video2.txt
│       ├── video3.txt
│       └── video4.txt
├── peer1/
│   ├── app.py           # Aplicação peer1 (GREEN)
│   └── cache/           # Cache local (criado automaticamente)
├── peer2/
│   ├── app.py           # Aplicação peer2 (LRU)
│   └── cache/           # Cache local (criado automaticamente)
├── peer3/
│   ├── app.py           # Aplicação peer3 (LFU)
│   └── cache/           # Cache local (criado automaticamente)
├── requirements.txt
├── requirements-minimal.txt
└── README.md
```

## 📈 Métricas a Observar

Nos logs de cada peer, observe:
- **ACERTO LOCAL**: Arquivo encontrado no cache (hit)
- **ACERTO REMOTO**: Arquivo recebido de outro peer (cooperação)
- **FALHA NO CACHE**: Arquivo buscado na origem (miss total)

## 🎯 Próximos Passos (Sugestões)

- [ ] Implementar coleta automática de métricas
- [ ] Adicionar simulador de requisições (workload generator)
- [ ] Implementar topologia de rede com latências
- [ ] Criar visualizações comparativas das políticas
- [ ] Adicionar DHT (Distributed Hash Table) real
- [ ] Implementar replicação proativa

## 👥 Equipe

- Iasmin
- Maria Isabel  
- Nicoly

## 📚 Referências

- BitTorrent Protocol Specification
- IPFS (InterPlanetary File System)
- CDN Cooperative Caching Strategies
