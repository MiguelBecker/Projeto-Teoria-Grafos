"""
PARTE 7: VISUALIZAÇÃO DA ÁRVORE DE PERCURSO

Este script cria uma visualização interativa da árvore de percurso
entre Nova Descoberta e Boa Viagem (Setúbal), destacando o caminho
encontrado pelo algoritmo de Dijkstra.

SAÍDA:
- out/arvore_percurso.html: Visualização interativa com o caminho destacado
"""

import os
import sys
import json
import plotly.graph_objects as go
import networkx as nx
from graphs.io import carregar_adjacencias

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)


def criar_subgrafo_percurso(grafo, caminho):
    """
    Cria um subgrafo contendo apenas os nós e arestas do caminho.
    """
    # Cria grafo NetworkX para facilitar layout
    G = nx.Graph()
    
    # Adiciona todas as arestas do caminho
    for i in range(len(caminho) - 1):
        u = caminho[i]
        v = caminho[i + 1]
        
        # Busca peso da aresta
        peso = 1.0
        logradouro = ""
        for vizinho, w, meta in grafo.neighbors(u):
            if vizinho == v:
                peso = w
                logradouro = meta.logradouro if meta.logradouro else ""
                break
        
        G.add_edge(u, v, weight=peso, logradouro=logradouro)
    
    return G


def criar_visualizacao_interativa(caminho_json_path):
    """
    Cria visualização interativa HTML do percurso usando Plotly.
    """
    print("=" * 70)
    print("PARTE 7: GERANDO VISUALIZAÇÃO DA ÁRVORE DE PERCURSO")
    print("=" * 70)
    
    # Carrega dados do percurso
    with open(caminho_json_path, 'r', encoding='utf-8') as f:
        percurso = json.load(f)
    
    print(f"\n✓ Percurso carregado: {percurso['origem']} → {percurso['destino']}")
    print(f"  Custo total: {percurso['custo_total']}")
    print(f"  Bairros: {percurso['numero_bairros']}")
    
    # Carrega grafo
    grafo = carregar_adjacencias(
        "data/bairros_unique.csv",
        "data/adjacencias_bairros.csv"
    )
    
    # Cria subgrafo do caminho
    caminho = percurso['caminho']
    G = criar_subgrafo_percurso(grafo, caminho)
    
    # Calcula layout usando spring layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Prepara dados para Plotly
    edge_trace = []
    
    # Adiciona arestas
    for i, (u, v) in enumerate(G.edges()):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        peso = G[u][v]['weight']
        logradouro = G[u][v].get('logradouro', 'N/A')
        
        # Cor baseada na posição no caminho (gradiente)
        cor_idx = i / (len(G.edges()) - 1) if len(G.edges()) > 1 else 0
        cor = f'rgba({int(255 * (1 - cor_idx))}, {int(100 + 155 * cor_idx)}, {int(50 + 205 * cor_idx)}, 0.8)'
        
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=4, color=cor),
                hoverinfo='text',
                hovertext=f'{u} → {v}<br>Via: {logradouro}<br>Peso: {peso:.2f}',
                showlegend=False
            )
        )
        
        # Adiciona seta no meio da aresta
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        
        edge_trace.append(
            go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode='markers',
                marker=dict(
                    size=12,
                    color=cor,
                    symbol='arrow',
                    angle=0
                ),
                hoverinfo='skip',
                showlegend=False
            )
        )
    
    # Prepara nós
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for i, node in enumerate(caminho):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Informações do nó
        if i == 0:
            tipo = "ORIGEM"
            cor = '#00FF00'  # Verde
            tamanho = 30
        elif i == len(caminho) - 1:
            tipo = "DESTINO"
            cor = '#FF0000'  # Vermelho
            tamanho = 30
        else:
            tipo = f"Passo {i}"
            cor = '#4169E1'  # Azul
            tamanho = 20
        
        node_text.append(f'<b>{node}</b><br>{tipo}<br>Posição: {i + 1}/{len(caminho)}')
        node_color.append(cor)
        node_size.append(tamanho)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[node for node in caminho],
        textposition='top center',
        textfont=dict(size=10, color='black'),
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )
    
    # Cria figura
    fig = go.Figure(data=edge_trace + [node_trace])
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f'<b>Árvore de Percurso: {percurso["origem"]} → {percurso["destino"]}</b><br>' +
                 f'<sub>Custo Total: {percurso["custo_total"]} | {percurso["numero_bairros"]} bairros percorridos</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=100),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#F8F9FA',
        height=700,
        annotations=[
            dict(
                text='🟢 ORIGEM | 🔵 PERCURSO | 🔴 DESTINO',
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.05,
                xanchor='center',
                font=dict(size=12)
            )
        ]
    )
    
    # Salva HTML
    output_path = os.path.join(ROOT_DIR, "out", "arvore_percurso.html")
    fig.write_html(output_path)
    
    print(f"\n✓ Visualização salva em: {output_path}")
    print(f"\n{'=' * 70}")
    print("DETALHAMENTO DO PERCURSO")
    print("=" * 70)
    
    for detalhe in percurso['detalhes_percurso']:
        print(f"\nTrecho {detalhe['trecho']}: {detalhe['de']} → {detalhe['para']}")
        print(f"  Via: {detalhe['logradouro']}")
        print(f"  Custo: {detalhe['custo']}")
    
    print(f"\n{'=' * 70}")
    print("✓ PARTE 7 CONCLUÍDA COM SUCESSO!")
    print("=" * 70)


def main():
    """
    Função principal.
    """
    try:
        percurso_json = os.path.join(ROOT_DIR, "out", "percurso_nova_descoberta_setubal.json")
        
        if not os.path.exists(percurso_json):
            print("✗ Erro: Arquivo percurso_nova_descoberta_setubal.json não encontrado!")
            print("  Execute primeiro: python src/calcular_distancias.py")
            return 1
        
        criar_visualizacao_interativa(percurso_json)
        return 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
