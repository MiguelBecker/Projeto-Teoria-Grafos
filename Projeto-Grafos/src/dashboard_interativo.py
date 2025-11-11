import os
import sys
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx

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


def gerar_dashboard_completo(grafo, df_bairros, out_dir):
    print("\n" + "="*60)
    print("GERANDO DASHBOARD INTERATIVO COMPLETO")
    print("="*60 + "\n")
    
    G = criar_grafo_nx(grafo)
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
    
    graus = {no: grafo.degree(no) for no in grafo.nodes()}
    densidades = {no: densidade_ego(grafo, no) for no in grafo.nodes()}
    
    micro_dict = {}
    for _, row in df_bairros.iterrows():
        micro_dict[row['bairro']] = row.get('microrregiao', 'N/A')
    
    nodes_data = []
    for no in G.nodes():
        x, y = pos[no]
        grau = graus[no]
        densidade = densidades[no]
        microregiao = micro_dict.get(no, 'N/A')
        
        nodes_data.append({
            'id': no,
            'x': x,
            'y': y,
            'grau': grau,
            'densidade': densidade,
            'microregiao': microregiao
        })
    
    edges_data = []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        peso = data.get('weight', 1.0)
        logradouro = data.get('logradouro', 'Sem informação')
        
        edges_data.append({
            'source': u,
            'target': v,
            'x0': x0,
            'y0': y0,
            'x1': x1,
            'y1': y1,
            'peso': peso,
            'logradouro': logradouro
        })
    
    bairros_list = sorted([no for no in G.nodes()])
    microrregioes_list = sorted(list(set(micro_dict.values())))
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Interativo - Bairros do Recife</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {PALETA['bg']};
            color: {PALETA['texto']};
            overflow: hidden;
        }}
        
        .container {{
            display: grid;
            grid-template-columns: 320px 1fr;
            grid-template-rows: 70px 1fr;
            height: 100vh;
            gap: 0;
        }}
        
        .header {{
            grid-column: 1 / -1;
            background: linear-gradient(135deg, {PALETA['paper']} 0%, {PALETA['bg']} 100%);
            padding: 20px 30px;
            border-bottom: 3px solid {PALETA['primario']};
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 26px;
            color: {PALETA['texto']};
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        
        .header h1 .subtitle {{
            font-size: 13px;
            color: {PALETA['texto_sec']};
            font-weight: 400;
            display: block;
            margin-top: 2px;
            letter-spacing: 0.5px;
        }}
        
        .header .stats {{
            display: flex;
            gap: 30px;
            font-size: 14px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: {PALETA['destaque']};
        }}
        
        .stat-label {{
            color: {PALETA['texto_sec']};
            font-size: 11px;
            text-transform: uppercase;
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
        }}
        
        .sidebar::-webkit-scrollbar-thumb {{
            background: {PALETA['primario']};
            border-radius: 4px;
        }}
        
        .control-section {{
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid {PALETA['grid']};
        }}
        
        .control-section:last-child {{
            border-bottom: none;
        }}
        
        .control-section h3 {{
            font-size: 13px;
            color: {PALETA['destaque']};
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            padding-bottom: 8px;
            border-bottom: 2px solid {PALETA['grid']};
        }}
        
        label {{
            display: block;
            font-size: 12px;
            color: {PALETA['texto_sec']};
            margin-bottom: 6px;
            font-weight: 500;
        }}
        
        input, select {{
            width: 100%;
            padding: 10px;
            background: {PALETA['bg']};
            border: 1px solid {PALETA['grid']};
            border-radius: 6px;
            color: {PALETA['texto']};
            font-size: 13px;
            margin-bottom: 12px;
            transition: all 0.2s;
        }}
        
        input:focus, select:focus {{
            outline: none;
            border-color: {PALETA['primario']};
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}
        
        button {{
            width: 100%;
            padding: 11px;
            background: {PALETA['primario']};
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }}
        
        button:hover {{
            background: {PALETA['secundario']};
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        }}
        
        button:active {{
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }}
        
        .btn-secondary {{
            background: transparent;
            border: 1px solid {PALETA['grid']};
            color: {PALETA['texto_sec']};
            margin-top: 8px;
        }}
        
        .btn-secondary:hover {{
            background: {PALETA['grid']};
            color: {PALETA['texto']};
            border-color: {PALETA['texto_sec']};
        }}
        
        .result-box {{
            background: {PALETA['bg']};
            border-left: 3px solid {PALETA['destaque']};
            border-radius: 4px;
            padding: 14px;
            margin-top: 12px;
            font-size: 12px;
            line-height: 1.7;
            max-height: 200px;
            overflow-y: auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        .result-box::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .result-box::-webkit-scrollbar-thumb {{
            background: {PALETA['destaque']};
            border-radius: 3px;
        }}
        
        .result-title {{
            color: {PALETA['destaque']};
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        
        .path-step {{
            color: {PALETA['alerta']};
            font-weight: 500;
        }}
        
        .main-content {{
            background: {PALETA['bg']};
            padding: 20px;
            overflow: hidden;
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .filter-badge {{
            display: inline-block;
            padding: 4px 10px;
            background: {PALETA['primario']};
            color: white;
            border-radius: 12px;
            font-size: 11px;
            margin: 4px 4px 4px 0;
        }}
        
        .info-badge {{
            background: {PALETA['primario']};
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 10px;
            display: inline-block;
            margin-right: 6px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>ANÁLISE DE REDE URBANA
                    <span class="subtitle">Sistema de Bairros do Recife</span>
                </h1>
            </div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{len(G.nodes())}</div>
                    <div class="stat-label">BAIRROS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(G.edges())}</div>
                    <div class="stat-label">CONEXÕES</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="visibleNodes">{len(G.nodes())}</div>
                    <div class="stat-label">ATIVOS</div>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="control-section">
                <h3>BUSCA DE BAIRROS</h3>
                <label>Nome do bairro:</label>
                <input type="text" id="searchInput" list="bairrosList" placeholder="Digite o nome..." 
                       oninput="buscarAoDigitar()" onkeypress="if(event.key==='Enter')buscarBairro()">
                <datalist id="bairrosList">
                    {"".join([f'<option value="{b}">' for b in bairros_list])}
                </datalist>
                <div id="sugestoes" style="margin-top: -8px; margin-bottom: 8px; font-size: 11px; color: {PALETA['destaque']};"></div>
                <button onclick="buscarBairro()">BUSCAR</button>
                <button class="btn-secondary" onclick="limparBusca()">LIMPAR</button>
                <div id="searchResult"></div>
            </div>
            
            <div class="control-section">
                <h3>CÁLCULO DE ROTA</h3>
                <label>Ponto de origem:</label>
                <select id="origemSelect">
                    <option value="">Selecione a origem...</option>
                    {"".join([f'<option value="{b}">{b}</option>' for b in bairros_list])}
                </select>
                <label>Ponto de destino:</label>
                <select id="destinoSelect">
                    <option value="">Selecione o destino...</option>
                    {"".join([f'<option value="{b}">{b}</option>' for b in bairros_list])}
                </select>
                <button onclick="calcularRota()">CALCULAR PERCURSO</button>
                <button class="btn-secondary" onclick="limparRota()">LIMPAR ROTA</button>
                <div id="routeResult"></div>
            </div>
            
            <div class="control-section">
                <h3>FILTROS AVANÇADOS</h3>
                <label>Microrregião (RPA):</label>
                <select id="microFilter" onchange="aplicarFiltros()">
                    <option value="">Todas as regiões</option>
                    {"".join([f'<option value="{m}">RPA {m}</option>' for m in microrregioes_list if m != 'N/A'])}
                </select>
                <label>Conectividade mínima:</label>
                <input type="number" id="grauMin" min="0" max="20" value="0" onchange="aplicarFiltros()">
                <label>Densidade mínima:</label>
                <input type="number" id="densidadeMin" min="0" max="1" step="0.1" value="0" onchange="aplicarFiltros()">
                <button onclick="resetarFiltros()">RESETAR</button>
                <div id="filterInfo"></div>
            </div>
            
            <div class="control-section">
                <h3>ANÁLISE DE DADOS</h3>
                <button onclick="mostrarTop10()">TOP 10 CONECTADOS</button>
                <button onclick="mostrarEstatisticas()">MÉTRICAS GERAIS</button>
                <div id="analysisResult"></div>
            </div>
        </div>
        
        <div class="main-content">
            <div id="graph"></div>
        </div>
    </div>
    
    <script>
        const nodesData = {json.dumps(nodes_data)};
        const edgesData = {json.dumps(edges_data)};
        const PALETA = {json.dumps(PALETA)};
        
        let filteredNodes = [...nodesData];
        let highlightedNodes = new Set();
        let highlightedEdges = new Set();
        
        function construirGrafoAdjacencia() {{
            const grafo = {{}};
            nodesData.forEach(n => grafo[n.id] = []);
            edgesData.forEach(e => {{
                if (!grafo[e.source]) grafo[e.source] = [];
                if (!grafo[e.target]) grafo[e.target] = [];
                grafo[e.source].push({{no: e.target, peso: e.peso}});
                grafo[e.target].push({{no: e.source, peso: e.peso}});
            }});
            return grafo;
        }}
        
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
        
        const grafoAdjacencia = construirGrafoAdjacencia();
        
        function criarGrafico() {{
            const edgeTraces = edgesData.map(edge => {{
                const isHighlighted = highlightedEdges.has(`${{edge.source}}-${{edge.target}}`);
                return {{
                    type: 'scatter',
                    x: [edge.x0, edge.x1, null],
                    y: [edge.y0, edge.y1, null],
                    mode: 'lines',
                    line: {{
                        width: isHighlighted ? 4 : 0.8,
                        color: isHighlighted ? PALETA.alerta : PALETA.texto_sec
                    }},
                    opacity: isHighlighted ? 0.9 : 0.3,
                    hoverinfo: 'text',
                    hovertext: `${{edge.source}} ↔ ${{edge.target}}<br>${{edge.logradouro}}<br>Peso: ${{edge.peso}}`,
                    showlegend: false
                }};
            }});
            
            const nodeX = filteredNodes.map(n => n.x);
            const nodeY = filteredNodes.map(n => n.y);
            const nodeText = filteredNodes.map(n => n.id);
            const nodeColors = filteredNodes.map(n => {{
                if (highlightedNodes.has(n.id)) return PALETA.alerta;
                if (n.grau <= 3) return PALETA.texto_sec;
                if (n.grau <= 6) return PALETA.terciario;
                if (n.grau <= 9) return PALETA.secundario;
                return PALETA.primario;
            }});
            const nodeSizes = filteredNodes.map(n => 
                highlightedNodes.has(n.id) ? n.grau * 6 + 20 : n.grau * 4 + 12
            );
            const nodeHover = filteredNodes.map(n => 
                `<b>${{n.id}}</b><br>Grau: ${{n.grau}}<br>Microrregião: RPA ${{n.microregiao}}<br>Densidade: ${{n.densidade.toFixed(3)}}`
            );
            
            const nodeTrace = {{
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
            }};
            
            const layout = {{
                title: {{
                    text: 'REDE DE CONECTIVIDADE URBANA<br><sub style="font-size: 11px; color: {PALETA["texto_sec"]};">Clique nos nós para detalhes | Arraste para navegar | Scroll para zoom</sub>',
                    x: 0.5,
                    xanchor: 'center',
                    font: {{
                        size: 18,
                        color: PALETA.texto,
                        family: 'Segoe UI, sans-serif',
                        weight: 600
                    }}
                }},
                showlegend: false,
                hovermode: 'closest',
                margin: {{b: 20, l: 5, r: 5, t: 80}},
                xaxis: {{
                    showgrid: false,
                    zeroline: false,
                    showticklabels: false
                }},
                yaxis: {{
                    showgrid: false,
                    zeroline: false,
                    showticklabels: false
                }},
                plot_bgcolor: PALETA.bg,
                paper_bgcolor: PALETA.paper,
                dragmode: 'pan'
            }};
            
            const config = {{
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                displaylogo: false
            }};
            
            Plotly.newPlot('graph', [...edgeTraces, nodeTrace], layout, config);
            
            const graphDiv = document.getElementById('graph');
            graphDiv.on('plotly_click', function(data) {{
                const point = data.points[0];
                if (point && point.text) {{
                    document.getElementById('searchInput').value = point.text;
                    buscarBairro();
                }}
            }});
            
            document.getElementById('visibleNodes').textContent = filteredNodes.length;
        }}
        
        function buscarAoDigitar() {{
            const texto = document.getElementById('searchInput').value.trim().toLowerCase();
            const sugestoesDiv = document.getElementById('sugestoes');
            
            if (texto.length < 2) {{
                sugestoesDiv.innerHTML = '';
                return;
            }}
            
            const matches = nodesData
                .filter(n => n.id.toLowerCase().includes(texto))
                .slice(0, 5)
                .map(n => n.id);
            
            if (matches.length > 0) {{
                sugestoesDiv.innerHTML = `Sugestões: ${{matches.join(', ')}}`;
            }} else {{
                sugestoesDiv.innerHTML = 'Nenhum resultado encontrado';
            }}
        }}
        
        function buscarBairro() {{
            const bairro = document.getElementById('searchInput').value.trim();
            const node = nodesData.find(n => n.id.toLowerCase() === bairro.toLowerCase());
            
            if (!node) {{
                const parcial = nodesData.find(n => n.id.toLowerCase().includes(bairro.toLowerCase()));
                if (parcial) {{
                    document.getElementById('searchInput').value = parcial.id;
                    buscarBairro();
                    return;
                }}
                alert('Bairro não encontrado! Use as sugestões.');
                return;
            }}
            
            highlightedNodes = new Set([node.id]);
            highlightedEdges.clear();
            
            const vizinhos = edgesData
                .filter(e => e.source === node.id || e.target === node.id)
                .map(e => e.source === node.id ? e.target : e.source)
                .sort();
            
            vizinhos.forEach(v => {{
                highlightedNodes.add(v);
                highlightedEdges.add(`${{node.id}}-${{v}}`);
                highlightedEdges.add(`${{v}}-${{node.id}}`);
            }});
            
            const distancias = dijkstra(grafoAdjacencia, node.id, nodesData[0].id);
            
            document.getElementById('searchResult').innerHTML = `
                <div class="result-box">
                    <div class="result-title">BAIRRO: ${{node.id.toUpperCase()}}</div>
                    <div style="margin: 8px 0;">
                        <span class="info-badge">Grau: ${{node.grau}}</span>
                        <span class="info-badge">RPA ${{node.microregiao}}</span>
                    </div>
                    <div><strong>Densidade Ego:</strong> ${{node.densidade.toFixed(3)}}</div>
                    <div style="margin-top: 8px;"><strong>Conexões Diretas (${{vizinhos.length}}):</strong></div>
                    <div style="font-size: 11px; line-height: 1.6; max-height: 100px; overflow-y: auto;">
                        ${{vizinhos.join(' • ')}}
                    </div>
                </div>
            `;
            
            document.getElementById('sugestoes').innerHTML = '';
            criarGrafico();
        }}
        
        function limparBusca() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('searchResult').innerHTML = '';
            highlightedNodes.clear();
            criarGrafico();
        }}
        
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
                
                for (let i = 0; i < resultado.caminho.length - 1; i++) {{
                    const a = resultado.caminho[i];
                    const b = resultado.caminho[i + 1];
                    highlightedEdges.add(`${{a}}-${{b}}`);
                    highlightedEdges.add(`${{b}}-${{a}}`);
                }}
                
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
                    logradourosHtml = `<div style="margin-top: 8px; font-size: 11px;"><strong>Vias:</strong><br>${{logradouros.slice(0, 5).join('<br>')}}</div>`;
                }}
                
                document.getElementById('routeResult').innerHTML = `
                    <div class="result-box">
                        <div class="result-title">ROTA CALCULADA</div>
                        <div><strong>Custo Total:</strong> ${{resultado.custo.toFixed(1)}}</div>
                        <div><strong>Número de Saltos:</strong> ${{resultado.caminho.length - 1}}</div>
                        <div><strong>Percurso:</strong></div>
                        <div class="path-step" style="font-size: 11px; line-height: 1.8;">${{resultado.caminho.join(' → ')}}</div>
                        ${{logradourosHtml}}
                    </div>
                `;
                
                criarGrafico();
            }} else {{
                document.getElementById('routeResult').innerHTML = `
                    <div class="result-box">
                        <div class="result-title" style="color: ${{PALETA.erro}};">ROTA NÃO ENCONTRADA</div>
                        <div>Não existe caminho entre esses bairros no grafo.</div>
                    </div>
                `;
            }}
        }}
        
        function limparRota() {{
            document.getElementById('origemSelect').value = '';
            document.getElementById('destinoSelect').value = '';
            document.getElementById('routeResult').innerHTML = '';
            highlightedNodes.clear();
            highlightedEdges.clear();
            criarGrafico();
        }}
        
        function aplicarFiltros() {{
            const microregiao = document.getElementById('microFilter').value;
            const grauMin = parseInt(document.getElementById('grauMin').value) || 0;
            const densidadeMin = parseFloat(document.getElementById('densidadeMin').value) || 0;
            
            filteredNodes = nodesData.filter(n => {{
                if (microregiao && n.microregiao !== microregiao) return false;
                if (n.grau < grauMin) return false;
                if (n.densidade < densidadeMin) return false;
                return true;
            }});
            
            let info = '<div style="margin-top: 10px;">';
            if (microregiao) info += `<span class="filter-badge">RPA ${{microregiao}}</span>`;
            if (grauMin > 0) info += `<span class="filter-badge">Grau ≥ ${{grauMin}}</span>`;
            if (densidadeMin > 0) info += `<span class="filter-badge">Densidade ≥ ${{densidadeMin}}</span>`;
            info += '</div>';
            
            document.getElementById('filterInfo').innerHTML = info;
            criarGrafico();
        }}
        
        function resetarFiltros() {{
            document.getElementById('microFilter').value = '';
            document.getElementById('grauMin').value = '0';
            document.getElementById('densidadeMin').value = '0';
            document.getElementById('filterInfo').innerHTML = '';
            filteredNodes = [...nodesData];
            criarGrafico();
        }}
        
        function mostrarTop10() {{
            const top = [...nodesData]
                .sort((a, b) => b.grau - a.grau)
                .slice(0, 10);
            
            highlightedNodes = new Set(top.map(n => n.id));
            
            let html = '<div class="result-box"><div class="result-title">TOP 10 MAIS CONECTADOS</div>';
            top.forEach((n, i) => {{
                html += `<div>${{i+1}}. <strong>${{n.id}}</strong> - ${{n.grau}} conexões</div>`;
            }});
            html += '</div>';
            
            document.getElementById('analysisResult').innerHTML = html;
            criarGrafico();
        }}
        
        function mostrarEstatisticas() {{
            const graus = nodesData.map(n => n.grau);
            const densidades = nodesData.map(n => n.densidade);
            
            const media = graus.reduce((a, b) => a + b) / graus.length;
            const mediana = graus.sort((a, b) => a - b)[Math.floor(graus.length / 2)];
            const maxGrau = Math.max(...graus);
            const mediaDens = densidades.reduce((a, b) => a + b) / densidades.length;
            
            document.getElementById('analysisResult').innerHTML = `
                <div class="result-box">
                    <div class="result-title">MÉTRICAS GERAIS</div>
                    <div><span class="info-badge">Média de Grau:</span> ${{media.toFixed(2)}}</div>
                    <div><span class="info-badge">Mediana:</span> ${{mediana}}</div>
                    <div><span class="info-badge">Grau Máximo:</span> ${{maxGrau}}</div>
                    <div><span class="info-badge">Densidade Média:</span> ${{mediaDens.toFixed(3)}}</div>
                </div>
            `;
        }}
        
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                limparBusca();
                limparRota();
            }}
            if (e.ctrlKey && e.key === 'f') {{
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }}
        }});
        
        document.getElementById('origemSelect').addEventListener('change', function() {{
            if (this.value && document.getElementById('destinoSelect').value) {{
                calcularRota();
            }}
        }});
        
        document.getElementById('destinoSelect').addEventListener('change', function() {{
            if (this.value && document.getElementById('origemSelect').value) {{
                calcularRota();
            }}
        }});
        
        console.log('%cSISTEMA DE ANÁLISE DE REDE URBANA', 'font-size: 16px; color: {PALETA["primario"]}; font-weight: bold;');
        console.log('%cAtalhos: Ctrl+F (buscar) | ESC (limpar) | Clique nos nós (detalhes)', 'color: {PALETA["destaque"]}');
        console.log(`Dados carregados: ${{nodesData.length}} bairros, ${{edgesData.length}} conexões`);
        
        criarGrafico();
    </script>
</body>
</html>"""
    
    arquivo = os.path.join(out_dir, 'dashboard_interativo.html')
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Dashboard interativo salvo: {arquivo}\n")
    return arquivo


def main():
    data_dir = os.path.join(ROOT_DIR, 'data')
    out_dir = os.path.join(ROOT_DIR, 'out')
    os.makedirs(out_dir, exist_ok=True)
    
    bairros_csv = os.path.join(data_dir, 'bairros_unique.csv')
    adj_csv = os.path.join(data_dir, 'adjacencias_bairros.csv')
    
    print("\nCarregando dados...")
    df_bairros = pd.read_csv(bairros_csv)
    grafo = carregar_adjacencias(bairros_csv, adj_csv)
    print(f"Grafo: {grafo.order()} nós, {grafo.size()} arestas\n")
    
    arquivo = gerar_dashboard_completo(grafo, df_bairros, out_dir)
    
    print("="*60)
    print("DASHBOARD PRONTO!")
    print("="*60)
    print(f"\nAbra o arquivo: {arquivo}")
    print("\nFuncionalidades:")
    print("  🔍 Buscar bairros e ver vizinhos")
    print("  🛣️  Calcular rotas entre bairros")
    print("  🎯 Filtrar por microrregião, grau, densidade")
    print("  📊 Análises: Top 10, estatísticas")
    print("  🖱️  Zoom, pan, hover interativo")


if __name__ == "__main__":
    main()
