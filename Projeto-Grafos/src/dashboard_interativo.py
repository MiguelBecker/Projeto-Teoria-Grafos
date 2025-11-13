#!/usr/bin/env python3
"""
Script para geração de dashboard interativo unificado.

Este módulo gera um único arquivo HTML contendo todas as visualizações do projeto
de análise de grafos urbanos do Recife. Inclui visualizações de grafo interativo,
métricas de conectividade, calculador de rotas, top 10 bairros, distribuições
estatísticas, árvores de busca (BFS) e rankings de densidade.
"""

import os
import sys
import json
import math
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = CURRENT_DIR
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.io import carregar_adjacencias
from graphs.algorithms import dijkstra, reconstruir_caminho, bfs_arvore, densidade_ego
from graphs.layout import spring_layout, circular_layout

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


def normalizar_texto(valor, fallback):
    """Normaliza valores vindos do CSV, lidando com NaN e strings vazias."""
    if valor is None:
        return fallback
    if isinstance(valor, float):
        if math.isnan(valor):
            return fallback
    texto = str(valor).strip()
    if not texto or texto.lower() in {'nan', 'none'}:
        return fallback
    return texto


def criar_html_unificado(grafo, df_bairros, out_dir):
    """
    Gera o arquivo HTML unificado contendo todas as visualizações.
    
    Args:
        grafo: Objeto Graph contendo a estrutura de dados do grafo
        df_bairros: DataFrame com informações dos bairros
        out_dir: Diretório de saída para o arquivo HTML
        
    Returns:
        Caminho completo do arquivo HTML gerado
    """
    
    print("\n" + "="*70)
    print("GERANDO DASHBOARD ÚNICO COM TODAS AS VISUALIZAÇÕES")
    print("="*70 + "\n")
    
    print("Preparando dados do grafo principal...")
    pos = spring_layout(grafo, k=1.5, iterations=50, seed=42)
    
    graus = {no: grafo.degree(no) for no in grafo.nodes()}
    densidades = {no: densidade_ego(grafo, no) for no in grafo.nodes()}
    
    micro_dict = {}
    for _, row in df_bairros.iterrows():
        micro_dict[row['bairro']] = row.get('microrregiao', 'N/A')
    
    nodes_data = []
    for no in grafo.nodes():
        x, y = pos[no]
        nodes_data.append({
            'id': no,
            'x': x,
            'y': y,
            'grau': graus[no],
            'densidade': densidades[no],
            'microregiao': micro_dict.get(no, 'N/A')
        })
    
    edges_data = []
    for u, v, peso, meta in grafo.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        logradouro = normalizar_texto(getattr(meta, 'logradouro', None), 'Sem informação')
        observacao = normalizar_texto(getattr(meta, 'observacao', None), 'Sem observação')
        edges_data.append({
            'source': u,
            'target': v,
            'x0': x0,
            'y0': y0,
            'x1': x1,
            'y1': y1,
            'peso': peso,
            'logradouro': logradouro,
            'observacao': observacao
        })
    
    bairros_list = sorted([no for no in grafo.nodes()])
    nodes_json = json.dumps(nodes_data)
    edges_json = json.dumps(edges_data)
    bairros_json = json.dumps(bairros_list)
    
    print("Criando grafo principal...")
    grafo_principal_dict = criar_grafo_principal(grafo, pos, graus, densidades, micro_dict)
    fig1 = go.Figure(data=grafo_principal_dict['data'], layout=grafo_principal_dict['layout'])
    grafo_principal_json = json.loads(fig1.to_json())
    
    print("Criando mapa de calor...")
    mapa_calor_dict = criar_mapa_calor_grau(grafo, pos, graus)
    fig2 = go.Figure(data=mapa_calor_dict['data'], layout=mapa_calor_dict['layout'])
    mapa_calor_json = json.loads(fig2.to_json())
    
    print("Criando subgrafo Top 10...")
    top10_dict = criar_top10_subgrafo(grafo, graus)
    fig3 = go.Figure(data=top10_dict['data'], layout=top10_dict['layout'])
    top10_json = json.loads(fig3.to_json())
    
    print("Criando distribuição de graus...")
    distribuicao_dict = criar_distribuicao_graus(graus)
    fig4 = go.Figure(data=distribuicao_dict['data'], layout=distribuicao_dict['layout'])
    distribuicao_json = json.loads(fig4.to_json())
    
    print("Criando árvore BFS...")
    arvore_bfs_dict = criar_arvore_bfs(grafo, "Boa Vista")
    fig5 = go.Figure(data=arvore_bfs_dict['data'], layout=arvore_bfs_dict['layout'])
    arvore_bfs_json = json.loads(fig5.to_json())
    
    print("Criando árvore de percurso...")
    arvore_percurso_dict = criar_arvore_percurso(grafo, "Nova Descoberta", "Boa Viagem", pos)
    fig6 = go.Figure(data=arvore_percurso_dict['data'], layout=arvore_percurso_dict['layout'])
    arvore_percurso_json = json.loads(fig6.to_json())
    
    print("Criando ranking de densidade...")
    ranking_dict = criar_ranking_densidade(densidades, micro_dict)
    fig7 = go.Figure(data=ranking_dict['data'], layout=ranking_dict['layout'])
    ranking_json = json.loads(fig7.to_json())
    
    print("\nGerando HTML unificado...")
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Completo - Rede Urbana do Recife</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: {PALETA['bg']};
            color: {PALETA['texto']};
            overflow: hidden;
        }}
        
        .container {{
            display: grid;
            grid-template-columns: 320px 1fr;
            grid-template-rows: 80px 1fr;
            height: 100vh;
            gap: 0;
        }}
        
        .header {{
            grid-column: 1 / -1;
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            padding: 15px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 28px;
            color: white;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 13px;
            color: rgba(255,255,255,0.9);
            font-weight: 400;
            margin-top: 2px;
            letter-spacing: 0.5px;
        }}
        
        .header-stats {{
            display: flex;
            gap: 30px;
            position: relative;
            z-index: 1;
        }}
        
        .stat-item {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .stat-label {{
            color: rgba(255,255,255,0.85);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-top: 2px;
        }}
        
        .sidebar {{
            background: {PALETA['paper']};
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid {PALETA['grid']};
        }}
        
        .sidebar::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .sidebar::-webkit-scrollbar-track {{
            background: {PALETA['bg']};
            border-radius: 4px;
        }}
        
        .sidebar::-webkit-scrollbar-thumb {{
            background: {PALETA['primario']};
            border-radius: 4px;
        }}
        
        .sidebar::-webkit-scrollbar-thumb:hover {{
            background: {PALETA['secundario']};
        }}
        
        .tabs {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .tab {{
            padding: 12px 16px;
            cursor: pointer;
            border: none;
            background: {PALETA['bg']};
            color: {PALETA['texto_sec']};
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s;
            border-radius: 8px;
            border-left: 3px solid transparent;
            text-align: left;
            white-space: nowrap;
        }}
        
        .tab:hover {{
            color: {PALETA['texto']};
            background: rgba(37, 99, 235, 0.1);
            transform: translateX(4px);
        }}
        
        .tab.active {{
            color: {PALETA['primario']};
            border-left-color: {PALETA['primario']};
            background: rgba(37, 99, 235, 0.15);
            font-weight: 700;
        }}
        
        .sidebar-section {{
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid {PALETA['grid']};
        }}
        
        .sidebar-section:last-child {{
            border-bottom: none;
        }}
        
        .sidebar-section h3 {{
            font-size: 11px;
            color: {PALETA['texto_sec']};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
            font-weight: 700;
        }}
        
        .info-card {{
            background: {PALETA['bg']};
            padding: 12px;
            border-radius: 6px;
            font-size: 12px;
            line-height: 1.6;
            color: {PALETA['texto_sec']};
            border-left: 3px solid {PALETA['destaque']};
        }}
        
        .info-card strong {{
            color: {PALETA['texto']};
            display: block;
            margin-bottom: 4px;
        }}
        
        .main-content {{
            background: {PALETA['bg']};
            padding: 20px;
            overflow-y: auto;
        }}
        
        .main-content::-webkit-scrollbar {{
            width: 10px;
        }}
        
        .main-content::-webkit-scrollbar-track {{
            background: {PALETA['bg']};
        }}
        
        .main-content::-webkit-scrollbar-thumb {{
            background: {PALETA['grid']};
            border-radius: 5px;
        }}
        
        .tab-content {{
            display: none;
            animation: fadeIn 0.4s ease-in-out;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ 
                opacity: 0; 
                transform: translateY(20px) scale(0.98);
            }}
            to {{ 
                opacity: 1; 
                transform: translateY(0) scale(1);
            }}
        }}
        
        .viz-container {{
            background: {PALETA['paper']};
            border-radius: 16px;
            padding: 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            overflow: hidden;
            border: 1px solid {PALETA['grid']};
        }}
        
        .viz-header {{
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
            padding: 20px 25px;
            border-bottom: 2px solid {PALETA['grid']};
        }}
        
        .viz-title {{
            font-size: 22px;
            color: {PALETA['texto']};
            margin-bottom: 8px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .viz-title::before {{
            content: '';
            width: 4px;
            height: 24px;
            background: {PALETA['primario']};
            border-radius: 2px;
        }}
        
        .viz-description {{
            font-size: 13px;
            color: {PALETA['texto_sec']};
            line-height: 1.6;
        }}
        
        .viz-body {{
            padding: 25px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, {PALETA['bg']} 0%, rgba(37, 99, 235, 0.05) 100%);
            padding: 18px;
            border-radius: 10px;
            border: 1px solid {PALETA['grid']};
            transition: all 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
            border-color: {PALETA['primario']};
        }}
        
        .stat-label {{
            font-size: 11px;
            color: {PALETA['texto_sec']};
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .stat-value {{
            font-size: 32px;
            color: {PALETA['texto']};
            font-weight: 800;
            background: linear-gradient(135deg, {PALETA['primario']} 0%, {PALETA['destaque']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .graph-container {{
            width: 100%;
            height: 700px;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        /* Estilos para Calculador de Rotas */
        .route-calculator {{
            background: {PALETA['paper']};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid {PALETA['grid']};
        }}
        
        .calculator-title {{
            font-size: 16px;
            color: {PALETA['texto']};
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .calculator-title::before {{
            content: '▶';
            font-size: 16px;
            color: {PALETA['primario']};
        }}
        
        .input-group {{
            margin-bottom: 15px;
        }}
        
        .input-label {{
            font-size: 11px;
            color: {PALETA['texto_sec']};
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 6px;
            display: block;
        }}
        
        select, input[type="text"] {{
            width: 100%;
            padding: 10px 12px;
            background: {PALETA['bg']};
            border: 1px solid {PALETA['grid']};
            border-radius: 6px;
            color: {PALETA['texto']};
            font-size: 13px;
            font-family: inherit;
            transition: all 0.3s;
        }}
        
        select:focus, input[type="text"]:focus {{
            outline: none;
            border-color: {PALETA['primario']};
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}
        
        select option {{
            background: {PALETA['bg']};
            color: {PALETA['texto']};
        }}
        
        .btn {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, {PALETA['primario']} 0%, {PALETA['secundario']} 100%);
            color: white;
            margin-bottom: 8px;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        }}
        
        .btn-secondary {{
            background: {PALETA['bg']};
            color: {PALETA['texto_sec']};
            border: 1px solid {PALETA['grid']};
        }}
        
        .btn-secondary:hover {{
            color: {PALETA['texto']};
            border-color: {PALETA['primario']};
        }}
        
        .result-box {{
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
            border: 1px solid {PALETA['grid']};
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }}
        
        .result-title {{
            font-size: 14px;
            color: {PALETA['primario']};
            font-weight: 700;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .result-box strong {{
            color: {PALETA['texto']};
        }}
        
        .result-box div {{
            color: {PALETA['texto_sec']};
            font-size: 13px;
            line-height: 1.8;
            margin-bottom: 5px;
        }}

        .edge-info {{
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(6, 182, 212, 0.04) 100%);
            border: 1px solid {PALETA['grid']};
            border-radius: 8px;
            padding: 18px;
            margin-top: 12px;
            color: {PALETA['texto']};
            font-size: 13px;
            line-height: 1.8;
        }}

        .edge-info strong {{
            color: {PALETA['primario']};
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .edge-info span {{
            display: block;
            margin-bottom: 6px;
            color: {PALETA['texto_sec']};
        }}

        .edge-info.edge-info-empty {{
            font-style: italic;
            color: {PALETA['texto_sec']};
            opacity: 0.8;
        }}
        
        .path-step {{
            background: {PALETA['bg']};
            padding: 10px;
            border-radius: 6px;
            margin-top: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.8;
            color: {PALETA['alerta']};
            max-height: 150px;
            overflow-y: auto;
        }}
        
        .info-badge {{
            display: inline-block;
            background: {PALETA['primario']};
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="header-content">
                <h1>REDE URBANA DO RECIFE</h1>
                <div class="subtitle">Sistema Integrado de Análise de Grafos e Conectividade</div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-value">98</div>
                    <div class="stat-label">Bairros</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">244</div>
                    <div class="stat-label">Conexões</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">7</div>
                    <div class="stat-label">Análises</div>
                </div>
            </div>
        </div>
        
        <!-- SIDEBAR -->
        <div class="sidebar">
            <div class="sidebar-section">
                <h3>Visualizações</h3>
                <div class="tabs">
                    <button class="tab active" onclick="openTab(event, 'tab1')">Grafo Principal</button>
                    <button class="tab" onclick="openTab(event, 'tab2')">Mapa de Calor</button>
                    <button class="tab" onclick="openTab(event, 'tab3')">Top 10 Bairros</button>
                    <button class="tab" onclick="openTab(event, 'tab4')">Distribuição</button>
                    <button class="tab" onclick="openTab(event, 'tab5')">Árvore BFS</button>
                    <button class="tab" onclick="openTab(event, 'tab6')">Percurso ND → BV</button>
                    <button class="tab" onclick="openTab(event, 'tab7')">Ranking</button>
                </div>
            </div>
            
            <div class="sidebar-section">
                <h3>Sobre o Dashboard</h3>
                <div class="info-card">
                    <strong>Tecnologias</strong>
                    Algoritmos customizados de grafos (BFS, DFS, Dijkstra, Bellman-Ford) sem uso de bibliotecas externas.
                </div>
                <div class="info-card" style="margin-top: 10px;">
                    <strong>Interatividade</strong>
                    Clique nas <strong>arestas</strong> para ver detalhes das conexões entre bairros (via, peso, observações).
                </div>
                <div class="info-card" style="margin-top: 10px;">
                    <strong>Navegação</strong>
                    Use zoom, pan e hover para explorar os dados. Tamanho dos nós = grau de conectividade.
                </div>
            </div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="main-content">
            <!-- TAB 1: Grafo Principal -->
            <div id="tab1" class="tab-content active">
                <div style="display: grid; grid-template-columns: 350px 1fr; gap: 20px;">
                    <!-- PAINEL LATERAL: Calculador de Rotas -->
                    <div>
                        <div class="route-calculator">
                            <div class="calculator-title">Calculador de Rotas</div>
                            
                            <div class="input-group">
                                <label class="input-label">Ponto de Origem</label>
                                <select id="origemSelect">
                                    <option value="">Selecione o bairro de origem...</option>
{chr(10).join(f'                                    <option value="{b}">{b}</option>' for b in bairros_list)}
                                </select>
                            </div>
                            
                            <div class="input-group">
                                <label class="input-label">Ponto de Destino</label>
                                <select id="destinoSelect">
                                    <option value="">Selecione o bairro de destino...</option>
{chr(10).join(f'                                    <option value="{b}">{b}</option>' for b in bairros_list)}
                                </select>
                            </div>
                            
                            <button class="btn btn-primary" onclick="calcularRota()">
                                CALCULAR PERCURSO
                            </button>
                            <button class="btn btn-secondary" onclick="limparRota()">
                                LIMPAR
                            </button>
                            
                            <div id="routeResult"></div>
                        </div>

                        <div class="route-calculator">
                            <div class="calculator-title">Detalhes da Conexão Selecionada</div>
                            <div id="edgeInfo" class="edge-info edge-info-empty">
                                Clique em qualquer aresta do grafo para ver via, peso e observações registradas nas adjacências.
                            </div>
                        </div>
                        
                        <div class="route-calculator">
                            <div class="calculator-title">Informações</div>
                            <div style="font-size: 12px; color: {PALETA['texto_sec']}; line-height: 1.8;">
                                <strong style="color: {PALETA['texto']};">Como usar:</strong><br>
                                1. Selecione o bairro de origem<br>
                                2. Selecione o bairro de destino<br>
                                3. Clique em "CALCULAR PERCURSO"<br>
                                <br>
                                O algoritmo de <strong style="color: {PALETA['primario']};">Dijkstra</strong> calculará o caminho de menor custo entre os bairros selecionados.
                                <br><br>
                                <strong style="color: {PALETA['texto']};">Pesos baseados em:</strong><br>
                                • Tipo de via (avenida, rua, ponte, viaduto)<br>
                                • Qualidade da pavimentação<br>
                                • Penalidades por complexidade viária
                            </div>
                        </div>
                    </div>
                    
                    <!-- ÁREA PRINCIPAL: Grafo -->
                    <div class="viz-container">
                        <div class="viz-header">
                            <h2 class="viz-title">Grafo Interativo Completo</h2>
                            <p class="viz-description">
                                Visualização completa da rede de bairros do Recife. 
                                <strong>Clique nas arestas</strong> para ver detalhes das conexões (via, peso, observações).
                                As rotas calculadas serão destacadas em <strong style="color: {PALETA['alerta']};">laranja</strong>.
                            </p>
                        </div>
                        <div class="viz-body">
                            <div class="graph-container" id="grafico1"></div>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- TAB 2: Mapa de Calor -->
            <div id="tab2" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Mapa de Calor por Grau de Conectividade</h2>
                        <p class="viz-description">
                            Visualização destacando os bairros mais conectados com gradiente de cor intenso.
                            Quanto mais quente a cor, maior o número de conexões diretas.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico2"></div>
                    </div>
                </div>
            </div>
            
            <!-- TAB 3: Top 10 -->
            <div id="tab3" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Top 10 Bairros Mais Conectados</h2>
                        <p class="viz-description">
                            Subgrafo exclusivo mostrando apenas os 10 bairros com maior número de conexões 
                            e todas as suas interligações diretas. <strong>Clique nas arestas</strong> para ver detalhes.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico3"></div>
                    </div>
                </div>
            </div>
            
            <!-- TAB 4: Distribuição -->
            <div id="tab4" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Distribuição de Graus</h2>
                        <p class="viz-description">
                            Histograma estatístico mostrando a distribuição do número de conexões entre os bairros.
                            Análise da topologia da rede urbana.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico4"></div>
                    </div>
                </div>
            </div>
            
            <!-- TAB 5: Árvore BFS -->
            <div id="tab5" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Árvore de Busca em Largura (BFS)</h2>
                        <p class="viz-description">
                            Árvore de exploração BFS a partir do bairro "Boa Vista", mostrando níveis de alcance
                            e ordem de visita dos nós no grafo.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico5"></div>
                    </div>
                </div>
            </div>
            
            <!-- TAB 6: Percurso -->
            <div id="tab6" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Percurso: Nova Descoberta → Boa Viagem</h2>
                        <p class="viz-description">
                            Caminho mínimo calculado com algoritmo de Dijkstra destacado no grafo. 
                            Verde = origem, Vermelho = destino, Laranja = caminho ótimo. <strong>Clique nas arestas do caminho</strong> para ver custos.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico6"></div>
                    </div>
                </div>
            </div>
            
            <!-- TAB 7: Ranking -->
            <div id="tab7" class="tab-content">
                <div class="viz-container">
                    <div class="viz-header">
                        <h2 class="viz-title">Ranking de Densidade de Ego-Network</h2>
                        <p class="viz-description">
                            Top 20 bairros com maior densidade na sua vizinhança imediata (ego-network).
                            Métrica de coesão local da rede.
                        </p>
                    </div>
                    <div class="viz-body">
                        <div class="graph-container" id="grafico7"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Paleta de cores
        const PALETA = {{
            bg: '#1a1d29',
            paper: '#242837',
            primario: '#2563eb',
            destaque: '#06b6d4',
            alerta: '#f59e0b',
            sucesso: '#10b981',
            erro: '#dc2626',
            texto: '#e2e8f0',
            texto_sec: '#94a3b8'
        }};
        
        // Dados dos nós e arestas para interatividade
        const nodesData = {nodes_json};
        const edgesData = {edges_json};
        
        // Dados dos gráficos
        const graficos = {json.dumps({
            'grafico1': grafo_principal_json,
            'grafico2': mapa_calor_json,
            'grafico3': top10_json,
            'grafico4': distribuicao_json,
            'grafico5': arvore_bfs_json,
            'grafico6': arvore_percurso_json,
            'grafico7': ranking_json
        })};

        function makeEdgeKey(a, b) {{
            return [a, b].sort((lhs, rhs) => lhs.localeCompare(rhs)).join('||');
        }}
        
        // Construir grafo de adjacência para Dijkstra
        function construirGrafoAdjacencia() {{
            const grafo = {{}};
            edgesData.forEach(e => {{
                if (!grafo[e.source]) grafo[e.source] = [];
                if (!grafo[e.target]) grafo[e.target] = [];
                grafo[e.source].push({{no: e.target, peso: e.peso}});
                grafo[e.target].push({{no: e.source, peso: e.peso}});
            }});
            return grafo;
        }}
        
        const grafoAdjacencia = construirGrafoAdjacencia();
        
        // Algoritmo de Dijkstra em JavaScript
        function dijkstra(grafo, origem, destino) {{
            const distancias = {{}};
            const predecessores = {{}};
            const visitados = new Set();
            const fila = [];
            
            Object.keys(grafo).forEach(no => {{
                distancias[no] = Infinity;
                predecessores[no] = null;
            }});
            distancias[origem] = 0;
            fila.push({{no: origem, dist: 0}});
            
            while (fila.length > 0) {{
                fila.sort((a, b) => a.dist - b.dist);
                const {{no: atual, dist: distAtual}} = fila.shift();
                
                if (visitados.has(atual)) continue;
                visitados.add(atual);
                
                if (atual === destino) break;
                
                grafo[atual].forEach(vizinho => {{
                    if (visitados.has(vizinho.no)) return;
                    
                    const novaDist = distAtual + vizinho.peso;
                    if (novaDist < distancias[vizinho.no]) {{
                        distancias[vizinho.no] = novaDist;
                        predecessores[vizinho.no] = atual;
                        fila.push({{no: vizinho.no, dist: novaDist}});
                    }}
                }});
            }}
            
            if (distancias[destino] === Infinity) {{
                return {{caminho: null, custo: null}};
            }}
            
            const caminho = [];
            let atual = destino;
            while (atual !== null) {{
                caminho.unshift(atual);
                atual = predecessores[atual];
            }}
            
            return {{caminho, custo: distancias[destino]}};
        }}
        
        // Variáveis globais para controlar destaque
        let highlightedNodes = new Set();
        let highlightedEdges = new Set();
        let selectedEdgeKey = null;
        let selectedNodes = new Set();
        let eventosRegistrados = false;
        
        // Função para redesenhar o grafo com destaques
        function redesenharGrafo() {{
            const graficoOriginal = graficos['grafico1'];
            const novasTraces = [];
            
            // Redesenhar arestas
            edgesData.forEach(edge => {{
                const edgeKey = makeEdgeKey(edge.source, edge.target);
                const isPath = highlightedEdges.has(edgeKey);
                const isSelected = selectedEdgeKey === edgeKey;
                const isHighlighted = isPath || isSelected;
                const obsText = edge.observacao && edge.observacao !== 'Sem observação' ? `<br>Obs: ${{edge.observacao}}` : '';
                const hoverDetails = `${{edge.source}} ↔ ${{edge.target}}<br>${{edge.logradouro}}<br>Peso: ${{edge.peso.toFixed(2)}}${{obsText}}`;
                const payload = {{
                    kind: 'edge',
                    source: edge.source,
                    target: edge.target,
                    peso: edge.peso,
                    logradouro: edge.logradouro,
                    observacao: edge.observacao
                }};
                
                novasTraces.push({{
                    type: 'scatter',
                    x: [edge.x0, edge.x1, null],
                    y: [edge.y0, edge.y1, null],
                    mode: 'lines',
                    line: {{
                        width: isSelected ? 6 : (isPath ? 5 : 0.8),
                        color: isSelected ? PALETA.destaque : (isPath ? PALETA.alerta : PALETA.texto_sec)
                    }},
                    opacity: isHighlighted ? 1.0 : 0.25,
                    hoverinfo: 'text',
                    hovertext: hoverDetails,
                    customdata: [payload, payload, payload],
                    showlegend: false
                }});
            }});
            
            // Redesenhar nós
            const nodeX = nodesData.map(n => n.x);
            const nodeY = nodesData.map(n => n.y);
            const nodeText = nodesData.map(n => n.id);
            const nodeColors = nodesData.map(n => {{
                if (selectedNodes.has(n.id)) return PALETA.destaque;
                if (highlightedNodes.has(n.id)) return PALETA.alerta;
                return n.grau > 9 ? PALETA.primario : PALETA.texto_sec;
            }});
            const nodeSizes = nodesData.map(n => {{
                if (selectedNodes.has(n.id)) return n.grau * 6 + 24;
                if (highlightedNodes.has(n.id)) return n.grau * 6 + 20;
                return n.grau * 4 + 12;
            }});
            const nodeHover = nodesData.map(n => `<b>${{n.id}}</b><br>Grau: ${{n.grau}}<br>Densidade: ${{n.densidade.toFixed(3)}}`);
            
            novasTraces.push({{
                type: 'scatter',
                x: nodeX,
                y: nodeY,
                mode: 'markers+text',
                text: nodeText,
                textposition: 'top center',
                textfont: {{
                    size: 9,
                    color: PALETA.texto,
                    family: 'Arial Black'
                }},
                marker: {{
                    size: nodeSizes,
                    color: nodeColors,
                    line: {{
                        width: 2,
                        color: PALETA.bg
                    }}
                }},
                hoverinfo: 'text',
                hovertext: nodeHover,
                showlegend: false
            }});
            
            Plotly.react('grafico1', novasTraces, graficoOriginal.layout);
        }}
        
        function mostrarInfoAresta(edge) {{
            selectedEdgeKey = makeEdgeKey(edge.source, edge.target);
            selectedNodes = new Set([edge.source, edge.target]);
            const container = document.getElementById('edgeInfo');
            if (container) {{
                container.classList.remove('edge-info-empty');
                const pesoFormatado = edge.peso.toFixed(2);
                const possuiObservacao = edge.observacao && edge.observacao !== 'Sem observação';
                const observacaoHtml = possuiObservacao
                    ? `Observação: <span style="color: ${{PALETA.texto}};">${{edge.observacao}}</span>`
                    : 'Observação: Sem observações registradas.';
                container.innerHTML = `
                    <strong>${{edge.source}} ↔ ${{edge.target}}</strong>
                    <span>Via principal: ${{edge.logradouro}}</span>
                    <span>Peso (custo): ${{pesoFormatado}}</span>
                    <span>${{observacaoHtml}}</span>
                    <span style="font-size:11px; opacity:0.75;">Fonte: adjacencias_bairros.csv</span>
                `;
            }}
            redesenharGrafo();
        }}

        function limparInfoAresta() {{
            selectedEdgeKey = null;
            selectedNodes = new Set();
            const container = document.getElementById('edgeInfo');
            if (container) {{
                container.classList.add('edge-info-empty');
                container.innerHTML = 'Clique em qualquer aresta do grafo para ver via, peso e observações registradas nas adjacências.';
            }}
        }}

    function registrarEventosGrafo() {{
            if (eventosRegistrados) return;
            const graphDiv = document.getElementById('grafico1');
            if (!graphDiv) return;

            graphDiv.on('plotly_click', (event) => {{
                if (!event.points || event.points.length === 0) return;
                const ponto = event.points[0];
                if (!ponto.data || ponto.data.mode !== 'lines') return;
                const customdata = ponto.data.customdata;
                if (!customdata) return;
                const payload = customdata[ponto.pointNumber] || customdata[0];
                if (!payload || payload.kind !== 'edge') return;
                mostrarInfoAresta(payload);
            }});

            graphDiv.on('plotly_doubleclick', () => {{
                limparInfoAresta();
                redesenharGrafo();
            }});

            eventosRegistrados = true;
        }}
        
        // Função para calcular rota
        function calcularRota() {{
            const origem = document.getElementById('origemSelect').value;
            const destino = document.getElementById('destinoSelect').value;
            
            if (!origem || !destino) {{
                alert('Selecione origem e destino!');
                return;
            }}
            
            if (origem === destino) {{
                alert('Origem e destino são iguais!');
                return;
            }}
            
            const resultado = dijkstra(grafoAdjacencia, origem, destino);
            
            if (resultado.caminho) {{
                highlightedNodes = new Set(resultado.caminho);
                highlightedEdges = new Set();
                
                // Marcar arestas do caminho
                for (let i = 0; i < resultado.caminho.length - 1; i++) {{
                    const a = resultado.caminho[i];
                    const b = resultado.caminho[i + 1];
                    highlightedEdges.add(makeEdgeKey(a, b));
                }}
                
                // Buscar logradouros
                const logradouros = [];
                for (let i = 0; i < resultado.caminho.length - 1; i++) {{
                    const edge = edgesData.find(e => 
                        (e.source === resultado.caminho[i] && e.target === resultado.caminho[i+1]) ||
                        (e.target === resultado.caminho[i] && e.source === resultado.caminho[i+1])
                    );
                    if (edge && edge.logradouro !== 'Sem informação') {{
                        logradouros.push(`${{i+1}}. ${{edge.logradouro}}`);
                    }}
                }}
                
                let logradourosHtml = '';
                if (logradouros.length > 0) {{
                    logradourosHtml = `<div style="margin-top: 12px;"><strong>Principais Vias:</strong><br><div style="font-size: 11px; line-height: 1.8;">${{logradouros.slice(0, 8).join('<br>')}}</div></div>`;
                }}
                
                document.getElementById('routeResult').innerHTML = `
                    <div class="result-box">
                        <div class="result-title">ROTA ENCONTRADA</div>
                        <div><strong>Custo Total:</strong> ${{resultado.custo.toFixed(2)}}</div>
                        <div><strong>Número de Saltos:</strong> ${{resultado.caminho.length - 1}}</div>
                        <div><strong>Bairros no Percurso:</strong> ${{resultado.caminho.length}}</div>
                        <div class="path-step">${{resultado.caminho.join(' → ')}}</div>
                        ${{logradourosHtml}}
                    </div>
                `;
                
                redesenharGrafo();
            }} else {{
                document.getElementById('routeResult').innerHTML = `
                    <div class="result-box">
                        <div class="result-title" style="color: ${{PALETA.erro}};">ROTA NÃO ENCONTRADA</div>
                        <div>Não existe caminho entre esses bairros no grafo atual.</div>
                    </div>
                `;
            }}
        }}
        
        // Função para limpar rota
        function limparRota() {{
            document.getElementById('origemSelect').value = '';
            document.getElementById('destinoSelect').value = '';
            document.getElementById('routeResult').innerHTML = '';
            highlightedNodes = new Set();
            highlightedEdges = new Set();
            limparInfoAresta();
            redesenharGrafo();
        }}
        
        // Função para trocar de aba
        function openTab(evt, tabName) {{
            const tabContents = document.getElementsByClassName("tab-content");
            for (let i = 0; i < tabContents.length; i++) {{
                tabContents[i].classList.remove("active");
            }}
            
            const tabs = document.getElementsByClassName("tab");
            for (let i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove("active");
            }}
            
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
            
            // Renderizar gráfico da aba se ainda não foi renderizado
            const graficoId = 'grafico' + tabName.replace('tab', '');
            const container = document.getElementById(graficoId);
            if (container && !container.hasAttribute('data-rendered')) {{
                Plotly.newPlot(graficoId, graficos[graficoId].data, graficos[graficoId].layout);
                container.setAttribute('data-rendered', 'true');
            }}
        }}
        
        // Renderizar o primeiro gráfico ao carregar
        window.onload = function() {{
            Plotly.newPlot('grafico1', graficos['grafico1'].data, graficos['grafico1'].layout);
            document.getElementById('grafico1').setAttribute('data-rendered', 'true');
            registrarEventosGrafo();
        }};
        
        console.log('%cDashboard Completo Carregado com Calculador de Rotas', 'font-size: 16px; color: #2563eb; font-weight: bold;');
        console.log('→ 7 visualizações disponíveis');
        console.log('→ Calculador de rotas com Dijkstra');
    console.log('→ Algoritmo implementado manualmente (sem NetworkX)');
    console.log('→ Clique nas arestas para detalhar pesos das adjacências');
    </script>
</body>
</html>"""
    
    # Salvar arquivo
    arquivo = os.path.join(out_dir, 'dashboard_interativo.html')
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n→ Dashboard único gerado: {arquivo}")
    return arquivo


def criar_grafo_principal(grafo, pos, graus, densidades, micro_dict):
    """
    Cria os dados do grafo principal interativo.
    
    Cada aresta é renderizada separadamente para permitir informações
    individuais ao passar o mouse (hover). Os nós são coloridos de acordo
    com seu grau de conectividade.
    """
    # Criar traces individuais para cada aresta (permite hover individual)
    edge_traces = []
    for u, v, peso, meta in grafo.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        # Informações da aresta
        logradouro = normalizar_texto(getattr(meta, 'logradouro', None), 'Sem informação')
        observacao = normalizar_texto(getattr(meta, 'observacao', None), 'Sem observação')
        tem_observacao = observacao != 'Sem observação'
        edge_payload = {
            'kind': 'edge',
            'source': u,
            'target': v,
            'peso': float(peso),
            'logradouro': logradouro,
            'observacao': observacao
        }
        
        hover_text = f"<b>{u} ⟷ {v}</b><br>"
        hover_text += f"Via: {logradouro}<br>"
        hover_text += f"Peso: {peso:.2f}<br>"
        if tem_observacao:
            hover_text += f"Obs: {observacao}"
        
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=1.2, color=PALETA['texto_sec']),
            hoverinfo='text',
            hovertext=hover_text,
            hoverlabel=dict(
                bgcolor=PALETA['paper'],
                font=dict(size=12, color=PALETA['texto']),
                bordercolor=PALETA['primario']
            ),
            showlegend=False,
            opacity=0.6
        )
        edge_trace.update(customdata=[edge_payload, edge_payload])
        edge_traces.append(edge_trace)
    
    # Nós
    node_x, node_y, node_text, node_color = [], [], [], []
    for no in grafo.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        grau = graus[no]
        node_text.append(f"<b>{no}</b><br>Grau: {grau}<br>Densidade ego: {densidades[no]:.3f}<br>RPA: {micro_dict.get(no, 'N/A')}")
        node_color.append(grau)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[no if graus[no] > 6 else '' for no in grafo.nodes()],  # Mostrar nomes dos mais conectados
        textposition='top center',
        textfont=dict(size=8, color=PALETA['texto'], family='Arial'),
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            size=[max(8, graus[no] * 2) for no in grafo.nodes()],  # Tamanho proporcional ao grau
            color=node_color,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Grau",
                thickness=15,
                len=0.7,
                bgcolor=PALETA['paper'],
                tickfont=dict(color=PALETA['texto'])
            ),
            line=dict(width=1.5, color=PALETA['bg'])
        ),
        hoverlabel=dict(
            bgcolor=PALETA['paper'],
            font=dict(size=13, color=PALETA['texto']),
            bordercolor=PALETA['primario']
        ),
        showlegend=False
    )
    
    layout = go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        height=700,
        title=dict(
            text="<b>Rede de Bairros do Recife</b><br><sub>Tamanho dos nós = conectividade | Hover para detalhes</sub>",
            font=dict(size=16, color=PALETA['texto']),
            x=0.5,
            xanchor='center'
        )
    )
    
    return {'data': edge_traces + [node_trace], 'layout': layout}


def criar_mapa_calor_grau(grafo, pos, graus):
    """Cria mapa de calor por grau"""
    edge_x, edge_y = [], []
    for u, v, peso, meta in grafo.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color=PALETA['texto_sec']),
        hoverinfo='none',
        opacity=0.3,
        showlegend=False
    )
    
    node_x, node_y, node_text, node_size = [], [], [], []
    for no in grafo.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        grau = graus[no]
        node_text.append(f"{no}<br>Conexões: {grau}")
        node_size.append(grau * 3 + 10)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[no for no in grafo.nodes()],
        textposition='top center',
        textfont=dict(size=8, color=PALETA['texto']),
        marker=dict(
            size=node_size,
            color=list(graus.values()),
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Grau")
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    layout = go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        height=600
    )
    
    return {'data': [edge_trace, node_trace], 'layout': layout}


def criar_top10_subgrafo(grafo, graus):
    """Cria subgrafo dos top 10 bairros"""
    from graphs.graph import Graph, EdgeMeta
    
    top_bairros = sorted(graus.items(), key=lambda x: x[1], reverse=True)[:10]
    top_nomes = {b for b, _ in top_bairros}
    
    g_sub = Graph()
    for bairro in top_nomes:
        g_sub.add_node(bairro)
    
    for u, v, peso, meta in grafo.edges():
        if u in top_nomes and v in top_nomes:
            g_sub.add_edge(u, v, peso, meta)
    
    pos = circular_layout(g_sub)
    
    edge_x, edge_y = [], []
    for u, v, peso, meta in g_sub.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=3, color=PALETA['primario']),
        hoverinfo='none',
        opacity=0.6,
        showlegend=False
    )
    
    node_x, node_y, node_text = [], [], []
    for no in g_sub.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"<b>{no}</b><br>Grau: {graus[no]}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[no for no in g_sub.nodes()],
        textposition='top center',
        textfont=dict(size=12, color=PALETA['texto']),
        marker=dict(
            size=[graus[no]*8 for no in g_sub.nodes()],
            color=[graus[no] for no in g_sub.nodes()],
            colorscale='Blues',
            showscale=True
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    layout = go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        height=600
    )
    
    return {'data': [edge_trace, node_trace], 'layout': layout}


def criar_distribuicao_graus(graus):
    """Cria histograma de distribuição de graus"""
    valores = list(graus.values())
    
    trace = go.Histogram(
        x=valores,
        nbinsx=15,
        marker=dict(color=PALETA['primario'], line=dict(color=PALETA['bg'], width=1)),
        name='Bairros'
    )
    
    layout = go.Layout(
        title=dict(text='Distribuição do Número de Conexões', font=dict(size=16, color=PALETA['texto'])),
        xaxis=dict(title='Número de Conexões (Grau)', color=PALETA['texto'], gridcolor=PALETA['grid']),
        yaxis=dict(title='Quantidade de Bairros', color=PALETA['texto'], gridcolor=PALETA['grid']),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        font=dict(color=PALETA['texto']),
        height=600,
        showlegend=False
    )
    
    return {'data': [trace], 'layout': layout}


def criar_arvore_bfs(grafo, origem):
    """Cria árvore BFS"""
    pais = bfs_arvore(grafo, origem)
    
    arestas_arvore = []
    niveis = {origem: 0}
    
    for filho, pai in pais.items():
        if pai is not None:
            arestas_arvore.append((pai, filho))
            niveis[filho] = niveis[pai] + 1
    
    # Layout hierárquico
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
    
    edge_x, edge_y = [], []
    for u, v in arestas_arvore:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color=PALETA['primario']),
        hoverinfo='none',
        showlegend=False
    )
    
    node_x, node_y, node_text, node_color = [], [], [], []
    for no in niveis.keys():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        nivel = niveis[no]
        node_text.append(f"<b>{no}</b><br>Nível: {nivel}")
        node_color.append(nivel)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[no for no in niveis.keys()],
        textposition='top center',
        textfont=dict(size=9, color=PALETA['texto']),
        marker=dict(
            size=18,
            color=node_color,
            colorscale='Teal',
            showscale=True,
            colorbar=dict(title="Nível")
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    layout = go.Layout(
        title=dict(text=f'Árvore BFS a partir de "{origem}"', font=dict(size=16, color=PALETA['texto'])),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        height=600
    )
    
    return {'data': [edge_trace, node_trace], 'layout': layout}


def criar_arvore_percurso(grafo, origem, destino, pos):
    """Cria visualização do percurso"""
    distancias, predecessores = dijkstra(grafo, origem)
    caminho = reconstruir_caminho(predecessores, destino)
    
    # Arestas (todas)
    edge_x, edge_y, edge_colors, edge_widths = [], [], [], []
    for u, v, peso, meta in grafo.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        
        eh_caminho = False
        for i in range(len(caminho) - 1):
            if (caminho[i] == u and caminho[i+1] == v) or (caminho[i] == v and caminho[i+1] == u):
                eh_caminho = True
                break
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(PALETA['alerta'] if eh_caminho else PALETA['texto_sec'])
        edge_widths.append(4 if eh_caminho else 0.5)
    
    # Criar múltiplos traces para diferentes larguras
    edge_traces = []
    idx = 0
    for i in range(0, len(edge_x), 3):
        edge_traces.append(go.Scatter(
            x=edge_x[i:i+3],
            y=edge_y[i:i+3],
            mode='lines',
            line=dict(width=edge_widths[idx], color=edge_colors[idx]),
            hoverinfo='none',
            showlegend=False,
            opacity=1.0 if edge_widths[idx] > 1 else 0.2
        ))
        idx += 1
    
    # Nós
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    for no in grafo.nodes():
        x, y = pos[no]
        node_x.append(x)
        node_y.append(y)
        
        if no == origem:
            node_color.append(PALETA['sucesso'])
            node_size.append(25)
            node_text.append(f"<b>ORIGEM</b><br>{no}")
        elif no == destino:
            node_color.append(PALETA['erro'])
            node_size.append(25)
            node_text.append(f"<b>DESTINO</b><br>{no}")
        elif no in caminho:
            node_color.append(PALETA['alerta'])
            node_size.append(18)
            node_text.append(f"<b>{no}</b><br>No caminho")
        else:
            node_color.append(PALETA['texto_sec'])
            node_size.append(8)
            node_text.append(no)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color=PALETA['bg'])
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    layout = go.Layout(
        title=dict(text=f'Percurso: {origem} → {destino} (Custo: {distancias[destino]:.1f})', 
                   font=dict(size=16, color=PALETA['texto'])),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        height=600
    )
    
    return {'data': edge_traces + [node_trace], 'layout': layout}


def criar_ranking_densidade(densidades, micro_dict):
    """Cria ranking de densidade de ego-network"""
    top_20 = sorted(densidades.items(), key=lambda x: x[1], reverse=True)[:20]
    bairros = [b for b, _ in top_20]
    valores = [d for _, d in top_20]
    cores = [PALETA['primario'] if micro_dict.get(b) in ['1', '2'] else PALETA['secundario'] for b in bairros]
    
    trace = go.Bar(
        y=bairros,
        x=valores,
        orientation='h',
        marker=dict(color=cores),
        text=[f'{v:.3f}' for v in valores],
        textposition='outside',
        hoverinfo='text',
        hovertext=[f"<b>{b}</b><br>Densidade: {v:.3f}<br>RPA: {micro_dict.get(b, 'N/A')}" 
                   for b, v in zip(bairros, valores)]
    )
    
    layout = go.Layout(
        title=dict(text='Top 20 - Densidade de Ego-Network', font=dict(size=16, color=PALETA['texto'])),
        xaxis=dict(title='Densidade', color=PALETA['texto'], gridcolor=PALETA['grid']),
        yaxis=dict(color=PALETA['texto'], autorange='reversed'),
        plot_bgcolor=PALETA['bg'],
        paper_bgcolor=PALETA['paper'],
        font=dict(color=PALETA['texto']),
        height=600,
        showlegend=False,
        margin=dict(l=150)
    )
    
    return {'data': [trace], 'layout': layout}


def main():
    """Função principal"""
    data_dir = os.path.join(ROOT_DIR, 'data')
    out_dir = os.path.join(ROOT_DIR, 'out')
    os.makedirs(out_dir, exist_ok=True)
    
    bairros_csv = os.path.join(data_dir, 'bairros_unique.csv')
    adj_csv = os.path.join(data_dir, 'adjacencias_bairros.csv')
    
    print("\nCARREGANDO DADOS...")
    df_bairros = pd.read_csv(bairros_csv)
    grafo = carregar_adjacencias(bairros_csv, adj_csv)
    print(f"→ Grafo carregado: {grafo.order()} nós, {grafo.size()} arestas")
    
    arquivo = criar_html_unificado(grafo, df_bairros, out_dir)
    
    print("\n" + "="*70)
    print("DASHBOARD ÚNICO GERADO COM SUCESSO")
    print("="*70)
    print(f"\nArquivo: {arquivo}")
    print("\nVisualizações incluídas:")
    print("  1. Grafo Principal Interativo")
    print("  2. Mapa de Calor por Grau")
    print("  3. Top 10 Bairros Mais Conectados")
    print("  4. Distribuição de Graus")
    print("  5. Árvore BFS (Boa Vista)")
    print("  6. Percurso Nova Descoberta → Boa Viagem")
    print("  7. Ranking de Densidade")
    print("\nTodas as visualizações em um único HTML com sistema de abas")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
