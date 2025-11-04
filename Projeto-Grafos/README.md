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

Próximos Passos

Parte 5 — Distâncias entre Endereços (Dijkstra)

Criar data/enderecos.csv com colunas:
endereco_X, endereco_Y, bairro_X, bairro_Y

Implementar Dijkstra para calcular:

custo e caminho entre bairros (distancias_enderecos.csv)

percurso “Nova Descoberta → Boa Viagem (Setúbal)”

visualização da árvore do percurso (out/arvore_percurso.html)