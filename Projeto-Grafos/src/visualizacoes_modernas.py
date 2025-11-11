import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = CURRENT_DIR
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.io import carregar_adjacencias
from graphs.algorithms import dijkstra, reconstruir_caminho, bfs_arvore, densidade_ego


PALETA = {
    'bg': '#1a1d29',
    'paper': '#242837',
    'primario': '#2563eb',
    'secundario': '#3b82f6',
    'terciario': '#60a5fa',
    'destaque': '#06b6d4',
    'sucesso': '#10b981',
    'alerta': '#f59e0b',
    'erro': '#dc2626',
    'texto': '#e2e8f0',
    'texto_sec': '#94a3b8',
    'grid': '#334155'
}


def criar_grafo_nx(grafo):
    G = nx.Graph()
    for no in grafo.nodes():
        G.add_node(no)
    for u, v, peso, meta in grafo.edges():
        G.add_edge(u, v, weight=peso, 
                   logradouro=meta.logradouro if meta.logradouro else "",
                   observacao=meta.observacao if meta.observacao else "")
    return G


def etapa7_arvore_percurso(grafo, df_bairros, out_dir):
    origem = "Nova Descoberta"
    destino = "Boa Viagem"
    
    print(f"\n{'='*60}")
    print(f"ETAPA 7: Árvore do Percurso {origem} → {destino}")
    print(f"{'='*60}\n")
    
    distancias, predecessores = dijkstra(grafo, origem)
    caminho = reconstruir_caminho(predecessores, destino)
    
    if not caminho:
        print(f"Erro: Caminho não encontrado entre {origem} e {destino}")
        return
    
    custo_total = distancias[destino]
    print(f"Caminho encontrado: {' → '.join(caminho)}")
    print(f"Custo total: {custo_total}")
    
    percurso_json = {
        "origem": origem,
        "destino": destino,
        "custo": custo_total,
        "caminho": caminho,
        "num_saltos": len(caminho) - 1
    }
    
    with open(os.path.join(out_dir, 'percurso_nova_descoberta_setubal.json'), 'w', encoding='utf-8') as f:
        json.dump(percurso_json, f, indent=2, ensure_ascii=False)
    
    G = criar_grafo_nx(grafo)
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    edge_x = []
    edge_y = []
    edge_colors = []
    edge_widths = []
    
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        eh_caminho = False
        for i in range(len(caminho) - 1):
            if (caminho[i] == u and caminho[i+1] == v) or (caminho[i] == v and caminho[i+1] == u):
                eh_caminho = True
                break
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(PALETA['alerta'] if eh_caminho else PALETA['secundario'])
        edge_widths.append(6 if eh_caminho else 1)
    
    edge_trace = []
    idx = 0
    for i in range(0, len(edge_x), 3):
        edge_trace.append(go.Scatter(
            x=edge_x[i:i+3],
            y=edge_y[i:i+3],
            mode='lines',
            line=dict(width=edge_widths[idx], color=edge_colors[idx]),
            hoverinfo='none',
            showlegend=False
        ))
        idx += 1
    
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    for no in G.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        node_text.append(no)
        
        if no == origem:
            node_colors.append(PALETA['sucesso'])
            node_sizes.append(30)
        elif no == destino:
            node_colors.append(PALETA['erro'])
            node_sizes.append(30)
        elif no in caminho:
            node_colors.append(PALETA['alerta'])
            node_sizes.append(25)
        else:
            node_colors.append(PALETA['terciario'])
            node_sizes.append(15)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        textfont=dict(size=10, color=PALETA['texto'], family='Arial Black'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    fig = go.Figure(data=edge_trace + [node_trace])
    
    fig.update_layout(
        title=dict(
            text=f'Percurso: {origem} → {destino}<br><sub>Custo: {custo_total} | Saltos: {len(caminho)-1}</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1400,
        height=900
    )
    
    arquivo = os.path.join(out_dir, 'arvore_percurso.html')
    fig.write_html(arquivo)
    print(f"✓ Visualização salva: {arquivo}\n")


def etapa8_visualizacoes_analiticas(grafo, df_bairros, out_dir):
    print(f"\n{'='*60}")
    print("ETAPA 8: Visualizações Analíticas")
    print(f"{'='*60}\n")
    
    graus = {no: grafo.degree(no) for no in grafo.nodes()}
    densidades = {no: densidade_ego(grafo, no) for no in grafo.nodes()}
    
    df_metricas = pd.DataFrame([
        {
            'bairro': bairro,
            'grau': graus[bairro],
            'densidade_ego': densidades[bairro]
        }
        for bairro in grafo.nodes()
    ])
    
    df_metricas = df_metricas.merge(df_bairros[['bairro', 'microrregiao']], 
                                     on='bairro', how='left')
    
    viz1_mapa_calor_grau(grafo, df_metricas, out_dir)
    viz2_ranking_densidade(df_metricas, out_dir)
    viz3_subgrafo_top10(grafo, graus, out_dir)
    viz4_distribuicao_graus(df_metricas, out_dir)
    viz5_arvore_bfs(grafo, "Boa Vista", out_dir)


def viz1_mapa_calor_grau(grafo, df_metricas, out_dir):
    print("Gerando: Mapa de Calor por Grau...")
    
    G = criar_grafo_nx(grafo)
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    edge_x = []
    edge_y = []
    
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=0.8, color=PALETA['texto_sec']),
        hoverinfo='none',
        opacity=0.3,
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_graus = []
    
    for no in G.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        grau = grafo.degree(no)
        node_text.append(f"{no}<br>Conexões: {grau}")
        node_graus.append(grau)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[no for no in G.nodes()],
        textposition='top center',
        textfont=dict(size=8, color=PALETA['texto']),
        marker=dict(
            size=[g*3 + 10 for g in node_graus],
            color=node_graus,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(
                title=dict(text="Grau", side='right', font=dict(size=14, color=PALETA['texto'])),
                thickness=15,
                len=0.7,
                bgcolor=PALETA['paper'],
                tickfont=dict(color=PALETA['texto'])
            ),
            line=dict(width=2, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title=dict(
            text='Mapa de Conectividade dos Bairros<br><sub>Intensidade = Número de Conexões</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1400,
        height=900
    )
    
    arquivo = os.path.join(out_dir, 'viz1_mapa_calor_grau.html')
    fig.write_html(arquivo)
    print(f"  ✓ {arquivo}\n")


def viz2_ranking_densidade(df_metricas, out_dir):
    print("Gerando: Ranking de Densidade Ego...")
    
    df_top = df_metricas.nlargest(15, 'densidade_ego')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_top['bairro'],
        x=df_top['densidade_ego'],
        orientation='h',
        marker=dict(
            color=df_top['densidade_ego'],
            colorscale='Teal',
            showscale=True,
            colorbar=dict(
                title=dict(text="Densidade", font=dict(size=12, color=PALETA['texto'])),
                thickness=15,
                bgcolor=PALETA['paper'],
                tickfont=dict(color=PALETA['texto'])
            ),
            line=dict(width=2, color=PALETA['bg'])
        ),
        text=[f"{d:.3f}" for d in df_top['densidade_ego']],
        textposition='outside',
        textfont=dict(size=11, color=PALETA['texto']),
        hovertemplate='<b>%{y}</b><br>Densidade: %{x:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 15: Densidade de Ego-Subrede<br><sub>Coesão da Vizinhança Local</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text='Densidade Ego', font=dict(size=14, color=PALETA['texto'])),
            gridcolor=PALETA['grid'],
            gridwidth=0.5,
            tickfont=dict(color=PALETA['texto'])
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=PALETA['texto'], family='Arial')
        ),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1200,
        height=700,
        margin=dict(l=200, r=50, t=100, b=80),
        showlegend=False
    )
    
    arquivo = os.path.join(out_dir, 'viz2_ranking_densidade.html')
    fig.write_html(arquivo)
    print(f"  ✓ {arquivo}\n")


def viz3_subgrafo_top10(grafo, graus, out_dir):
    print("Gerando: Subgrafo Top 10...")
    
    top_bairros = sorted(graus.items(), key=lambda x: x[1], reverse=True)[:10]
    top_nomes = {b for b, _ in top_bairros}
    
    G_sub = nx.Graph()
    for bairro in top_nomes:
        G_sub.add_node(bairro, grau=graus[bairro])
    
    for u, v, peso, _ in grafo.edges():
        if u in top_nomes and v in top_nomes:
            G_sub.add_edge(u, v, weight=peso)
    
    pos = nx.circular_layout(G_sub)
    
    edge_x = []
    edge_y = []
    
    for u, v in G_sub.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=3, color=PALETA['primario']),
        hoverinfo='none',
        opacity=0.6,
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_graus = []
    
    for no in G_sub.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        g = graus[no]
        node_text.append(f"<b>{no}</b><br>Grau: {g}")
        node_graus.append(g)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[no for no in G_sub.nodes()],
        textposition='top center',
        textfont=dict(size=12, color=PALETA['texto'], family='Arial Black'),
        marker=dict(
            size=[g*8 for g in node_graus],
            color=node_graus,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(
                title=dict(text="Grau", font=dict(size=12, color=PALETA['texto'])),
                thickness=15,
                bgcolor=PALETA['paper'],
                tickfont=dict(color=PALETA['texto'])
            ),
            line=dict(width=3, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title=dict(
            text='Top 10 Bairros Mais Conectados<br><sub>Principais Hubs da Rede</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1200,
        height=900
    )
    
    arquivo = os.path.join(out_dir, 'viz3_subgrafo_top10.html')
    fig.write_html(arquivo)
    print(f"  ✓ {arquivo}\n")


def viz4_distribuicao_graus(df_metricas, out_dir):
    print("Gerando: Distribuição de Graus...")
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df_metricas['grau'],
        nbinsx=20,
        marker=dict(
            color=df_metricas['grau'],
            colorscale='Blues',
            showscale=False,
            line=dict(width=2, color=PALETA['bg'])
        ),
        hovertemplate='Grau: %{x}<br>Frequência: %{y}<extra></extra>'
    ))
    
    media = df_metricas['grau'].mean()
    mediana = df_metricas['grau'].median()
    
    fig.add_vline(
        x=media,
        line=dict(color=PALETA['alerta'], width=3, dash='dash'),
        annotation_text=f"Média: {media:.2f}",
        annotation_position="top",
        annotation_font=dict(size=12, color=PALETA['alerta'])
    )
    
    fig.add_vline(
        x=mediana,
        line=dict(color=PALETA['destaque'], width=3, dash='dot'),
        annotation_text=f"Mediana: {mediana:.0f}",
        annotation_position="bottom",
        annotation_font=dict(size=12, color=PALETA['destaque'])
    )
    
    fig.update_layout(
        title=dict(
            text='Distribuição do Grau dos Bairros<br><sub>Padrão de Conectividade</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        xaxis=dict(
            title=dict(text='Número de Conexões (Grau)', font=dict(size=14, color=PALETA['texto'])),
            gridcolor=PALETA['grid'],
            gridwidth=0.5,
            tickfont=dict(color=PALETA['texto'])
        ),
        yaxis=dict(
            title=dict(text='Frequência (Número de Bairros)', font=dict(size=14, color=PALETA['texto'])),
            gridcolor=PALETA['grid'],
            gridwidth=0.5,
            tickfont=dict(color=PALETA['texto'])
        ),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1200,
        height=700,
        showlegend=False
    )
    
    arquivo = os.path.join(out_dir, 'viz4_distribuicao_graus.html')
    fig.write_html(arquivo)
    print(f"  ✓ {arquivo}\n")


def viz5_arvore_bfs(grafo, origem, out_dir):
    print(f"Gerando: Árvore BFS de '{origem}'...")
    
    pais = bfs_arvore(grafo, origem)
    
    if not pais:
        print(f"  Erro: Bairro '{origem}' não encontrado")
        return
    
    G_arvore = nx.DiGraph()
    niveis = {origem: 0}
    
    for filho, pai in pais.items():
        if pai is not None:
            G_arvore.add_edge(pai, filho)
            niveis[filho] = niveis[pai] + 1
        else:
            G_arvore.add_node(filho)
    
    pos = {}
    nivel_nos = {}
    for no, nivel in niveis.items():
        if nivel not in nivel_nos:
            nivel_nos[nivel] = []
        nivel_nos[nivel].append(no)
    
    for nivel, nos in nivel_nos.items():
        largura = len(nos)
        for i, no in enumerate(nos):
            x = (i - largura/2) * 2
            y = -nivel * 2
            pos[no] = (x, y)
    
    edge_x = []
    edge_y = []
    
    for u, v in G_arvore.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=2, color=PALETA['secundario']),
        hoverinfo='none',
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    
    for no in G_arvore.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        nivel = niveis[no]
        node_text.append(f"<b>{no}</b><br>Nível: {nivel}")
        node_colors.append(nivel)
        node_sizes.append(25 if no == origem else 18)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[no for no in G_arvore.nodes()],
        textposition='top center',
        textfont=dict(size=9, color=PALETA['texto']),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale='Teal',
            showscale=True,
            colorbar=dict(
                title=dict(text="Nível", font=dict(size=12, color=PALETA['texto'])),
                thickness=15,
                bgcolor=PALETA['paper'],
                tickfont=dict(color=PALETA['texto'])
            ),
            line=dict(width=2, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title=dict(
            text=f'Árvore BFS: {origem}<br><sub>Camadas de Alcançabilidade</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=24, color=PALETA['texto'], family='Arial Black')
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1400,
        height=1000
    )
    
    arquivo = os.path.join(out_dir, f'viz5_arvore_bfs_{origem.replace(" ", "_")}.html')
    fig.write_html(arquivo)
    print(f"  ✓ {arquivo}\n")


def etapa9_grafo_interativo_completo(grafo, df_bairros, out_dir):
    print(f"\n{'='*60}")
    print("ETAPA 9: Grafo Interativo Completo")
    print(f"{'='*60}\n")
    
    G = criar_grafo_nx(grafo)
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
    
    graus = {no: grafo.degree(no) for no in grafo.nodes()}
    densidades = {no: densidade_ego(grafo, no) for no in grafo.nodes()}
    
    micro_dict = {}
    for _, row in df_bairros.iterrows():
        micro_dict[row['bairro']] = row.get('microrregiao', 'N/A')
    
    origem_especial = "Nova Descoberta"
    destino_especial = "Boa Viagem"
    distancias, predecessores = dijkstra(grafo, origem_especial)
    caminho_especial = reconstruir_caminho(predecessores, destino_especial)
    
    edge_x = []
    edge_y = []
    edge_hover = []
    
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        logradouro = data.get('logradouro', 'Sem informação')
        peso = data.get('weight', 1.0)
        edge_hover.append(f"{u} ↔ {v}<br>{logradouro}<br>Peso: {peso}")
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1, color=PALETA['texto_sec']),
        hoverinfo='text',
        hovertext=edge_hover * len(G.edges()),
        opacity=0.4,
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_hover = []
    node_colors = []
    node_sizes = []
    
    for no in G.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        node_text.append(no)
        
        grau = graus[no]
        densidade = densidades[no]
        microregiao = micro_dict.get(no, 'N/A')
        
        hover_info = f"<b>{no}</b><br>"
        hover_info += f"Grau: {grau}<br>"
        hover_info += f"Microrregião: RPA {microregiao}<br>"
        hover_info += f"Densidade Ego: {densidade:.3f}"
        node_hover.append(hover_info)
        
        if grau <= 3:
            cor = PALETA['texto_sec']
        elif grau <= 6:
            cor = PALETA['terciario']
        elif grau <= 9:
            cor = PALETA['secundario']
        else:
            cor = PALETA['primario']
        
        node_colors.append(cor)
        node_sizes.append(grau * 4 + 15)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        textfont=dict(size=8, color=PALETA['texto']),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_hover,
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title=dict(
            text='Grafo Interativo: Bairros do Recife<br><sub>Explore as conexões | Busque bairros | Visualize métricas</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=26, color=PALETA['texto'], family='Arial Black')
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=100),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        width=1600,
        height=1000
    )
    
    fig.add_annotation(
        text=f"Caminho: {origem_especial} → {destino_especial}<br>" + 
             " → ".join(caminho_especial) if caminho_especial else "Caminho não encontrado",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        xanchor='left', yanchor='top',
        showarrow=False,
        font=dict(size=10, color=PALETA['alerta'], family='Courier New'),
        bgcolor=PALETA['paper'],
        bordercolor=PALETA['alerta'],
        borderwidth=2,
        borderpad=8
    )
    
    arquivo = os.path.join(out_dir, 'grafo_interativo.html')
    fig.write_html(arquivo)
    print(f"✓ Grafo interativo salvo: {arquivo}\n")


def main():
    data_dir = os.path.join(ROOT_DIR, 'data')
    out_dir = os.path.join(ROOT_DIR, 'out')
    os.makedirs(out_dir, exist_ok=True)
    
    bairros_csv = os.path.join(data_dir, 'bairros_unique.csv')
    adj_csv = os.path.join(data_dir, 'adjacencias_bairros.csv')
    
    print("\n" + "="*60)
    print("GERANDO VISUALIZAÇÕES MODERNAS")
    print("="*60)
    
    print("\nCarregando dados...")
    df_bairros = pd.read_csv(bairros_csv)
    grafo = carregar_adjacencias(bairros_csv, adj_csv)
    print(f"Grafo: {grafo.order()} nós, {grafo.size()} arestas")
    
    etapa7_arvore_percurso(grafo, df_bairros, out_dir)
    etapa8_visualizacoes_analiticas(grafo, df_bairros, out_dir)
    etapa9_grafo_interativo_completo(grafo, df_bairros, out_dir)
    
    print("="*60)
    print("CONCLUÍDO! Todas as visualizações foram geradas.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
