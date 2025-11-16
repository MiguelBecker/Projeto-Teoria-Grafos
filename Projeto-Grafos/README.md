# Análise de Grafos Urbanos do Recife

Sistema de análise de conectividade entre bairros do Recife utilizando teoria de grafos.

## Início Rápido

```bash
# Instalar dependências
pip install -r requirements.txt

# Gerar dashboard completo
python src/dashboard_interativo.py
```

Abra `out/dashboard_interativo.html` no navegador.

---

## Estrutura do Projeto

```
Projeto-Grafos/
├── data/
│   ├── bairros_recife.csv          # Dataset original (microrregiões)
│   ├── bairros_unique.csv          # 94 bairros únicos normalizados
│   ├── adjacencias_bairros.csv     # 244 conexões com pesos
│   └── enderecos.csv               # 5 pares para cálculo de distância
├── src/
│   ├── graphs/
│   │   ├── graph.py                # Lista de adjacência + metadados
│   │   ├── io.py                   # Carregamento e normalização
│   │   ├── algorithms.py           # BFS, DFS, Dijkstra, Bellman-Ford
│   │   └── layout.py               # Spring layout e circular
│   ├── solve.py                    # Métricas (densidade, ego-networks)
│   ├── ranking.py                  # Rankings de grau e densidade
│   ├── calcular_distancias.py      # Dijkstra entre endereços
│   ├── dashboard_interativo.py     # Dashboard HTML unificado
│   └── cli.py                      # Interface de linha de comando
├── out/
│   ├── dashboard_interativo.html   # Visualização principal
│   ├── recife_global.json          # Ordem=94, Tamanho=244, Densidade=0.056
│   ├── microrregioes.json          # Métricas de 6 microrregiões
│   ├── ego_bairro.csv              # Ego-network de cada bairro
│   ├── graus.csv                   # Grau de conectividade
│   ├── distancias_enderecos.csv    # Rotas calculadas
│   └── percurso_nova_descoberta_setubal.json
└── tests/                          # 26 testes (100% passando)
```

---

## Pipeline de Processamento

### 1. Normalização dos Bairros (`io.py`)

**O que faz:**  
Converte o CSV original (formato wide com colunas "1.1", "1.2", etc.) em lista única de bairros.

**Processo:**
1. Lê `bairros_recife.csv`
2. Faz melt das colunas de microrregiões
3. Remove duplicatas e normaliza acentuação
4. Gera `bairros_unique.csv` (97 bairros únicos)

**Resultado:**
```csv
bairro,microrregiao
Boa Viagem,6
Casa Amarela,1
...
```

---

### 2. Construção do Grafo (`graph.py` + `io.py`)

**O que faz:**  
Carrega as conexões entre bairros e monta a estrutura de grafo não-direcionado.

**Processo:**
1. Lê `adjacencias_bairros.csv` (244 conexões)
2. Carrega apenas bairros que aparecem nas adjacências (94 conectados)
3. Monta lista de adjacência com pesos e metadados

**Estrutura do grafo:**
```python
Graph:
  - nodes: {bairro1, bairro2, ...}  # 94 nós
  - adj: {bairro1: [(vizinho, peso, meta), ...]}
```

**Metadados de cada aresta:**
- `logradouro`: Nome da via (ex: "Av. Boa Viagem")
- `observacao`: Informações adicionais
- `peso`: Custo de travessia (calculado)

---

### 3. Cálculo de Métricas (`solve.py`)

**O que faz:**  
Calcula métricas topológicas do grafo completo e subgrafos.

**Processo:**
1. **Métricas globais:**
   - Ordem: |V| = 94
   - Tamanho: |E| = 244
   - Densidade: 2×|E| / (|V|×(|V|-1)) = 0.05582

2. **Métricas por microrregião:**
   - Filtra bairros de cada microrregião
   - Cria subgrafo induzido
   - Calcula ordem, tamanho, densidade

3. **Ego-networks:**
   - Para cada bairro v: ego = {v} ∪ vizinhos(v)
   - Calcula densidade local
   - Grau = número de vizinhos

**Saídas:**
- `recife_global.json`
- `microrregioes.json` (6 regiões)
- `ego_bairro.csv` (94 linhas)

---

### 4. Sistema de Pesos (`calcular_pesos.py`)

**O que faz:**  
Calcula peso de cada aresta baseado em características reais das vias.

**Fórmula:**
```
peso_final = (peso_base × fator_pavimentacao) + penalidades
```

**Componentes:**

| Tipo de Via | Peso Base | Pavimentação | Fator | Penalidade | Valor |
|-------------|-----------|--------------|-------|------------|-------|
| Avenida | 1.0 | Asfalto | ×1.0 | Semáforo | +0.3 |
| Ponte | 1.5 | Concreto | ×1.0 | Travessia | +0.5 |
| Rua | 2.0 | Paralelepípedo | ×1.3 | - | - |
| Viaduto | 2.5 | Escadaria | ×1.5 | Acesso | +0.5 |
| Estrada | 3.0 | Sem pavimentação | ×2.0 | - | - |

**Exemplo:**
- Avenida asfaltada com semáforos: (1.0 × 1.0) + 0.3 = **1.3**
- Rua com paralelepípedo: (2.0 × 1.3) + 0 = **2.6**
- Estrada sem pavimentação: (3.0 × 2.0) + 0 = **6.0**

**Resultado:**  
Atualiza coluna `peso` em `adjacencias_bairros.csv`

---

### 5. Cálculo de Distâncias (`calcular_distancias.py`)

**O que faz:**  
Usa Dijkstra para calcular caminhos mínimos entre pares de endereços.

**Processo:**
1. Lê `enderecos.csv` (5 pares)
2. Para cada par (bairro_X, bairro_Y):
   - Executa Dijkstra com pesos calculados
   - Reconstrói caminho completo
   - Calcula custo total
3. Salva resultados em CSV e JSON

**Exemplo de resultado:**
```
Nova Descoberta → Boa Viagem
Custo: 10.3
Caminho: Nova Descoberta → Córrego Do Jenipapo → Dois Irmãos → 
         Caxangá → Várzea → Curado → Jardim São Paulo → 
         Areias → Ibura → Boa Viagem
```

**Saídas:**
- `distancias_enderecos.csv` (5 rotas)
- `percurso_nova_descoberta_setubal.json` (detalhado)

---

### 6. Rankings (`ranking.py`)

**O que faz:**  
Identifica bairros mais importantes por conectividade e densidade.

**Processo:**
1. Ordena bairros por grau (número de conexões)
2. Ordena por densidade_ego (densidade local)
3. Salva rankings

**Resultados:**
- **Maior grau:** Casa Amarela (11 conexões)
- **Maior densidade ego:** Brasília Teimosa

**Saídas:**
- `graus.csv` (94 bairros ordenados)
- `ranking.txt`

---

### 7. Dashboard Interativo (`dashboard_interativo.py`)

**O que faz:**  
Gera visualização HTML única com 7 análises diferentes em sistema de abas.

**Visualizações incluídas:**

1. **Grafo Principal:** Rede completa com 94 nós, cores por grau
2. **Mapa de Calor:** Intensidade de conectividade
3. **Top 10:** Subgrafo dos bairros mais conectados
4. **Distribuição de Graus:** Histograma de conectividade
5. **Árvore BFS:** Busca em largura a partir de Boa Vista
6. **Percurso ND→BV:** Caminho mínimo destacado
7. **Ranking:** Top 20 densidades ego

**Funcionalidades:**
- 🔍 Busca por bairro
- 🛣️ Calculadora de rotas (Dijkstra em tempo real)
- 📊 Tooltips com métricas detalhadas
- 🎨 Código de cores por conectividade
- ⚡ Totalmente interativo (zoom, pan, hover)

**Saída:**  
`dashboard_interativo.html` (arquivo único autocontido)

---

## Algoritmos Implementados

Todos implementados **do zero** (sem NetworkX/igraph):

### BFS (Busca em Largura)
- **Uso:** Exploração por níveis, árvore de busca
- **Complexidade:** O(V + E)
- **Implementação:** Fila + visitados

### DFS (Busca em Profundidade)
- **Uso:** Detecção de ciclos, componentes conexos
- **Complexidade:** O(V + E)
- **Implementação:** Pilha recursiva + visitados

### Dijkstra
- **Uso:** Caminho mínimo com pesos ≥ 0
- **Complexidade:** O((V + E) log V)
- **Implementação:** Heap + relaxamento de arestas
- **Aplicação:** Cálculo de rotas entre bairros

### Bellman-Ford
- **Uso:** Caminho mínimo com pesos negativos, detecção de ciclos negativos
- **Complexidade:** O(V × E)
- **Implementação:** |V|-1 iterações + relaxamento
- **Aplicação:** Dataset Parte 2 (testes com pesos negativos)

---

## Execução por Etapas

```bash
# 1. Gerar métricas globais e ego-networks
python src/solve.py

# 2. Gerar rankings
python src/ranking.py

# 3. Calcular distâncias entre endereços
python src/calcular_distancias.py

# 4. Gerar dashboard completo
python src/dashboard_interativo.py

# 5. CLI interativa
python -m src.cli --alg DIJKSTRA --source "Nova Descoberta" --target "Boa Viagem"
```

---

## Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Resultado: 26 testes, 100% passando
# - BFS: 6 testes
# - DFS: 6 testes  
# - Dijkstra: 7 testes
# - Bellman-Ford: 7 testes
```

---

## Dependências

```
pandas      # Manipulação de CSV
plotly      # Visualizações interativas
kaleido     # Exportação de imagens
matplotlib  # Gráficos estáticos (Parte 2)
```

---

## Dados do Grafo

- **Nós:** 94 bairros conectados
- **Arestas:** 244 conexões viárias
- **Densidade:** 0.05582 (grafo esparso)
- **Grau médio:** 5.19 conexões/bairro
- **Componentes:** 1 (grafo conexo)
- **Peso mínimo:** 1.0 (avenidas asfaltadas)
- **Peso máximo:** 6.0 (estradas sem pavimentação)
- **Peso médio:** 1.71

---

## Parte 2 - Dataset Maior

- **Dataset:** Rede de coautoria (17M arestas, 220k nós)
- **Algoritmos testados:** BFS, DFS, Dijkstra, Bellman-Ford
- **Casos especiais:** Pesos negativos, ciclos negativos
- **Métricas:** Tempo de execução documentado
- **Saída:** `parte2_report.json`, `parte2_distribuicao_graus.png`
