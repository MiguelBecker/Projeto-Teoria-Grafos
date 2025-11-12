# Projeto-Teoria-Grafos

Estrutura de Pastas

Projeto-Grafos/
├── README.md
├── data/
│ ├── bairros_recife.csv
│ ├── bairros_unique.csv
│ ├── adjacencias_bairros.csv
│ └── enderecos.csv (Parte 5)
├── out/
│ ├── recife_global.json
│ ├── microrregioes.json
│ ├── ego_bairro.csv
│ ├── graus.csv
│ └── ranking.txt
├── src/
│ ├── graphs/
│ │ ├── io.py
│ │ └── graph.py
│ ├── solve.py
│ └── ranking.py
└── tests/

Etapas Concluídas
Parte 1 — Processamento de Bairros (io.py)

O arquivo original data/bairros_recife.csv continha colunas “1.1”, “1.2”, etc., representando microrregiões.
O script melt_bairros() foi responsável por derreter o CSV, normalizar acentuação e gerar uma lista única de bairros e suas microrregiões.

Saída: data/bairros_unique.csv
Formato:
bairro,microrregiao
Boa Viagem,6
Imbiribeira,6
Pina,6

Parte 2 — Construção do Grafo (graph.py + io.py)

Foi criada a estrutura de grafo não-direcionado utilizando listas de adjacência, com suporte a pesos e metadados (logradouro, tipo de via, etc.).

Arquivo: src/graphs/graph.py
Implementa:

Graph: estrutura principal de nós e arestas

EdgeMeta: metadados da aresta (logradouro, observação)

Arquivo: src/graphs/io.py
Contém:

melt_bairros(): normaliza o CSV de bairros

carregar_adjacencias(): lê adjacencias_bairros.csv e monta o grafo

Saída esperada:
data/bairros_unique.csv
data/adjacencias_bairros.csv

Formato de adjacências:
bairro_origem,bairro_destino,logradouro,observacao,peso
Boa Viagem,Ipsep,Av. Boa Viagem,Asfalto,1.0
Boa Viagem,Imbiribeira,Av. Domingos Ferreira,Asfalto,1.0

Legenda de pavimentação:
0 - Sem pavimentação
1 - Asfalto
2 - Concreto
3 - Paralelo
4 - Escadaria

Legenda de tipo de via:
Estrada - 1
Ponte - 2
Rua - 3
Viaduto - 4
Avenida - 5

Peso final = PesoBase × FatorPavimentação × Tamanho

Parte 3 — Métricas Globais e por Microrregião (solve.py)

O arquivo src/solve.py calcula métricas de conectividade e densidade do grafo completo e de subgrafos por microrregião, além de gerar as ego-networks.

Execução:
python src/solve.py

Saídas:

out/recife_global.json → ordem, tamanho e densidade do grafo total

out/microrregioes.json → métricas por microrregião

out/ego_bairro.csv → ego-network de cada bairro com grau, ordem_ego, tamanho_ego e densidade_ego

Fórmulas:
Ordem (|V|) = número de nós
Tamanho (|E|) = número de arestas
Densidade = 2 * |E| / (|V| * (|V| - 1))

Parte 4 — Graus e Rankings (ranking.py)

O script src/ranking.py gera os rankings dos bairros com maior conectividade e maior densidade de ego-network.

Execução:
python src/ranking.py

Saídas:

out/graus.csv → lista de bairros e seus graus

out/ranking.txt →
Bairro com maior grau: <nome>
Bairro com maior densidade_ego: <nome>

Como Executar Cada Etapa

Gerar bairros normalizados
python src/graphs/io.py

Calcular métricas globais, microrregiões e ego
python src/solve.py

Gerar ranking de graus e densidades
python src/ranking.py

Parte 5 — Pesos das Arestas (calcular_pesos.py)

O script src/calcular_pesos.py implementa um sistema completo de cálculo de pesos para as arestas, baseado em múltiplos fatores.

Fórmula:
peso_final = (peso_base_via × fator_pavimentacao) + penalidades

Componentes:
1. Peso base por tipo de via:
   - Avenida: 1.0 (via principal)
   - Ponte: 1.5 (travessia especial)
   - Rua: 2.0 (via local)
   - Viaduto: 2.5 (elevado)
   - Estrada: 3.0 (menor categoria)

2. Fator de pavimentação (multiplicador):
   - Asfalto/Concreto: 1.0
   - Paralelepípedo: 1.3
   - Escadaria: 1.5
   - Sem pavimentação: 2.0

3. Penalidades:
   - Ponte: +0.5
   - Viaduto: +0.5
   - Semáforos (grandes avenidas): +0.3

Execução:
python src/calcular_pesos.py

Resultado:
- Atualiza data/adjacencias_bairros.csv com pesos calculados
- Formato: bairro_origem, bairro_destino, logradouro, observacao, peso

Parte 6 — Distâncias entre Endereços (calcular_distancias.py)

O script src/calcular_distancias.py utiliza o algoritmo de Dijkstra para calcular distâncias entre pares de endereços, usando os pesos calculados na Parte 5.

Execução:
python src/calcular_distancias.py

Entrada:
data/enderecos.csv com colunas:
- endereco_X, endereco_Y, bairro_X, bairro_Y

Saídas:
- out/distancias_enderecos.csv → custo e caminho para cada par
- out/percurso_nova_descoberta_setubal.json → percurso detalhado "Nova Descoberta → Boa Viagem (Setúbal)"

Exemplo de resultado:
Nova Descoberta → Boa Viagem (Setúbal)
Custo: 10.3
Caminho: 10 bairros percorridos

Parte 7 — Árvore do Percurso (visualizar_arvore_percurso.py)

O script src/visualizar_arvore_percurso.py cria uma visualização interativa do percurso Nova Descoberta → Boa Viagem (Setúbal), destacando o caminho encontrado pelo Dijkstra.

Execução:
python src/visualizar_arvore_percurso.py

Saída:
- out/arvore_percurso.html → visualização interativa com:
  • Nós coloridos: verde (origem), azul (percurso), vermelho (destino)
  • Arestas em gradiente de cor mostrando a sequência
  • Tooltip com informações de cada trecho (via, peso)
  • Detalhamento completo de todos os 9 trechos do percurso

Características:
- Layout otimizado com NetworkX spring layout
- Visualização clara da sequência do percurso
- Informações detalhadas de cada logradouro
- Custo total e número de bairros percorridos

Testes (Obrigatórios)

Os testes cobrem todos os algoritmos implementados:

test/test_bfs.py — Testes de BFS (Busca em Largura)
- 6 casos de teste: grafo simples, desconectado, árvore, nó inexistente, ciclo, grafo completo
- Execução: python test/test_bfs.py
- Status: ✓ TODOS OS TESTES PASSARAM

test/test_dfs.py — Testes de DFS (Busca em Profundidade)
- 6 casos de teste: grafo simples, desconectado, nó inexistente, ciclo, ordem de visitação, grafo estrela
- Execução: python test/test_dfs.py
- Status: ✓ TODOS OS TESTES PASSARAM

test/test_dijkstra.py — Testes de Dijkstra
- 7 casos de teste: simples, caminho mais curto, nó isolado, pesos diferentes, grafo completo, reconstruir caminho, nó inexistente
- Execução: python test/test_dijkstra.py
- Status: ✓ TODOS OS TESTES PASSARAM

test/test_bellman_ford.py — Testes de Bellman-Ford
- 7 casos de teste: simples, pesos positivos, nó isolado, ciclo positivo, grafo completo, nó inexistente, caminho linear
- Execução: python test/test_bellman_ford.py
- Status: ✓ TODOS OS TESTES PASSARAM

Executar todos os testes:
python test/test_bfs.py; python test/test_dfs.py; python test/test_dijkstra.py; python test/test_bellman_ford.py

Total: 26 casos de teste, todos passando ✓