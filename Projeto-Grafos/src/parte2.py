#!/usr/bin/env python3
"""
Parte 2: Dataset Maior e Comparação de Algoritmos

Este módulo implementa todos os experimentos da Parte 2:
- Descrição do dataset (|V|, |E|, distribuição de graus)
- BFS/DFS a partir de ≥3 fontes
- Dijkstra com ≥5 pares origem-destino
- Bellman-Ford com casos de pesos negativos (com e sem ciclo negativo)
- Métricas de desempenho (tempo)
- Visualização de distribuição de graus
"""

import os
import sys
import time
import json
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sem GUI

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from graphs.io import carregar_dataset_parte2
from graphs.algorithms import bfs, dfs, dijkstra, bellman_ford, reconstruir_caminho
from graphs.graph import Graph


def descrever_dataset(grafo: Graph) -> dict:
    """
    Calcula métricas descritivas do dataset:
    - Número de nós (|V|)
    - Número de arestas (|E|)
    - Distribuição de graus (min, max, médio, histograma)
    """
    print("\n" + "="*70)
    print("DESCRIÇÃO DO DATASET")
    print("="*70)
    
    num_nos = grafo.order()
    num_arestas = grafo.size()
    
    graus = [grafo.degree(no) for no in grafo.nodes()]
    
    if graus:
        grau_min = min(graus)
        grau_max = max(graus)
        grau_medio = sum(graus) / len(graus)
        
        # Distribuição de graus
        dist_graus = Counter(graus)
        dist_graus_top = dict(sorted(dist_graus.items(), key=lambda x: x[1], reverse=True)[:20])
    else:
        grau_min = grau_max = grau_medio = 0.0
        dist_graus_top = {}
    
    descricao = {
        "tipo": "não-direcionado (tratado)",
        "ponderado": True,
        "num_nos": num_nos,
        "num_arestas": num_arestas,
        "grau_min": int(grau_min),
        "grau_max": int(grau_max),
        "grau_medio": round(grau_medio, 2),
        "distribuicao_graus_top20": dist_graus_top,
    }
    
    print(f"Tipo: não-direcionado, ponderado")
    print(f"|V| (nós): {num_nos}")
    print(f"|E| (arestas): {num_arestas}")
    print(f"Grau mínimo: {grau_min}")
    print(f"Grau máximo: {grau_max}")
    print(f"Grau médio: {grau_medio:.2f}")
    
    return descricao, graus


def rodar_bfs_dfs(grafo: Graph, fontes: list[str]) -> list[dict]:
    """
    Executa BFS e DFS a partir de ≥3 fontes distintas.
    Relata ordem/camadas/nós alcançados para cada execução.
    """
    print("\n" + "="*70)
    print("EXPERIMENTOS BFS/DFS (≥3 fontes)")
    print("="*70)
    
    resultados = []
    
    for i, origem in enumerate(fontes, 1):
        if origem not in grafo.nodes():
            print(f"\n⚠ Fonte {origem} não encontrada no grafo")
            continue
        
        print(f"\n[{i}/{len(fontes)}] Fonte: {origem}")
        
        # BFS
        print("  → Executando BFS...")
        t0 = time.perf_counter()
        distancias = bfs(grafo, origem)
        t1 = time.perf_counter()
        tempo_bfs = t1 - t0
        
        nos_alcancados = len(distancias)
        niveis = set(distancias.values())
        num_camadas = len(niveis)
        
        print(f"     ✓ Nós alcançados: {nos_alcancados}")
        print(f"     ✓ Número de camadas: {num_camadas}")
        print(f"     ✓ Tempo: {tempo_bfs:.6f}s")
        
        resultados.append({
            "algoritmo": "bfs",
            "origem": origem,
            "nos_alcancados": nos_alcancados,
            "num_camadas": num_camadas,
            "tempo_seg": tempo_bfs,
        })
        
        # DFS
        print("  → Executando DFS...")
        t0 = time.perf_counter()
        ordem_visitacao = dfs(grafo, origem)
        t1 = time.perf_counter()
        tempo_dfs = t1 - t0
        
        nos_visitados = len(ordem_visitacao)
        
        print(f"     ✓ Nós visitados: {nos_visitados}")
        print(f"     ✓ Tempo: {tempo_dfs:.6f}s")
        
        resultados.append({
            "algoritmo": "dfs",
            "origem": origem,
            "nos_visitados": nos_visitados,
            "tempo_seg": tempo_dfs,
        })
    
    return resultados


def rodar_dijkstra_pairs(grafo: Graph, pares: list[tuple[str, str]]) -> list[dict]:
    """
    Executa Dijkstra com ≥5 pares origem-destino.
    Verifica pesos não-negativos e calcula caminhos mínimos.
    """
    print("\n" + "="*70)
    print("EXPERIMENTOS DIJKSTRA (≥5 pares)")
    print("="*70)
    
    # Verificação: todos pesos devem ser ≥0
    print("\nVerificando pesos do grafo...")
    pesos_negativos = []
    for u, v, w, _ in grafo.edges():
        if w < 0:
            pesos_negativos.append((u, v, w))
    
    if pesos_negativos:
        print(f"✗ ERRO: {len(pesos_negativos)} arestas com peso negativo detectadas!")
        print(f"  Exemplo: {pesos_negativos[0]}")
        raise ValueError("Dijkstra não pode ser usado: dataset contém pesos negativos.")
    
    print("✓ Todos os pesos são não-negativos (válido para Dijkstra)")
    
    resultados = []
    
    for i, (origem, destino) in enumerate(pares, 1):
        if origem not in grafo.nodes() or destino not in grafo.nodes():
            print(f"\n⚠ Par {i}: {origem} → {destino} - nós não encontrados")
            continue
        
        print(f"\n[{i}/{len(pares)}] Par: {origem} → {destino}")
        
        t0 = time.perf_counter()
        distancias, predecessores = dijkstra(grafo, origem)
        t1 = time.perf_counter()
        tempo_dijkstra = t1 - t0
        
        custo = distancias.get(destino, float("inf"))
        
        if custo == float("inf"):
            print(f"  ✗ Sem caminho")
            caminho = []
            tam_caminho = 0
        else:
            caminho = reconstruir_caminho(predecessores, destino)
            tam_caminho = len(caminho)
            print(f"  ✓ Custo: {custo:.2f}")
            print(f"  ✓ Caminho ({tam_caminho} nós): {' → '.join(caminho[:5])}{'...' if tam_caminho > 5 else ''}")
        
        print(f"  ✓ Tempo: {tempo_dijkstra:.6f}s")
        
        resultados.append({
            "algoritmo": "dijkstra",
            "origem": origem,
            "destino": destino,
            "custo": None if custo == float("inf") else custo,
            "tam_caminho": tam_caminho,
            "tempo_seg": tempo_dijkstra,
        })
    
    return resultados


def rodar_bellman_ford_experimentos() -> list[dict]:
    """
    Executa Bellman-Ford em dois casos:
    1. Grafo com pesos negativos sem ciclo negativo
    2. Grafo com ciclo negativo (detectado)
    """
    print("\n" + "="*70)
    print("EXPERIMENTOS BELLMAN-FORD (casos com pesos negativos)")
    print("="*70)
    
    resultados = []
    
    # Caso 1: Pesos negativos SEM ciclo negativo
    print("\n[1/2] Caso: Pesos negativos SEM ciclo negativo")
    G1 = Graph()
    G1.add_edge("A", "B", 4.0)
    G1.add_edge("B", "C", -2.0)  # peso negativo
    G1.add_edge("A", "C", 5.0)
    G1.add_edge("C", "D", 1.0)
    
    origem1 = "A"
    print(f"  Grafo: A --(4)--> B --(-2)--> C --(1)--> D")
    print(f"         A --(5)---------> C")
    print(f"  Origem: {origem1}")
    
    t0 = time.perf_counter()
    distancias1, predecessores1, tem_ciclo1 = bellman_ford(G1, origem1)
    t1 = time.perf_counter()
    tempo_bf1 = t1 - t0
    
    print(f"  ✓ Ciclo negativo detectado: {tem_ciclo1}")
    print(f"  ✓ Distâncias: {distancias1}")
    print(f"  ✓ Tempo: {tempo_bf1:.6f}s")
    
    resultados.append({
        "algoritmo": "bellman-ford",
        "dataset": "G1_negativo_sem_ciclo",
        "origem": origem1,
        "tem_ciclo_negativo": tem_ciclo1,
        "distancias": distancias1,
        "tempo_seg": tempo_bf1,
    })
    
    # Caso 2: COM ciclo negativo
    print("\n[2/2] Caso: COM ciclo negativo")
    G2 = Graph()
    G2.add_edge("X", "Y", 2.0)
    G2.add_edge("Y", "Z", -3.0)
    G2.add_edge("Z", "X", -2.0)  # Ciclo X→Y→Z→X com peso total = 2 + (-3) + (-2) = -3 < 0
    
    origem2 = "X"
    print(f"  Grafo: X --(2)--> Y --(-3)--> Z --(-2)--> X  (ciclo negativo)")
    print(f"  Origem: {origem2}")
    
    t0 = time.perf_counter()
    distancias2, predecessores2, tem_ciclo2 = bellman_ford(G2, origem2)
    t1 = time.perf_counter()
    tempo_bf2 = t1 - t0
    
    print(f"  ✓ Ciclo negativo detectado: {tem_ciclo2}")
    print(f"  ✓ Tempo: {tempo_bf2:.6f}s")
    
    resultados.append({
        "algoritmo": "bellman-ford",
        "dataset": "G2_ciclo_negativo",
        "origem": origem2,
        "tem_ciclo_negativo": tem_ciclo2,
        "distancias": distancias2 if not tem_ciclo2 else None,
        "tempo_seg": tempo_bf2,
    })
    
    return resultados


def gerar_visualizacao_distribuicao_graus(graus: list[int], out_dir: str):
    """
    Gera histograma da distribuição de graus do dataset.
    Salva como out/parte2_distribuicao_graus.png
    """
    print("\n" + "="*70)
    print("GERANDO VISUALIZAÇÃO: Distribuição de Graus")
    print("="*70)
    
    plt.figure(figsize=(12, 6))
    
    # Histograma
    plt.hist(graus, bins=50, color='#2563eb', edgecolor='white', alpha=0.8)
    plt.xlabel('Grau (número de conexões)', fontsize=12, fontweight='bold')
    plt.ylabel('Número de nós', fontsize=12, fontweight='bold')
    plt.title('Distribuição de Graus - Dataset Parte 2', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Estatísticas no gráfico
    grau_min = min(graus)
    grau_max = max(graus)
    grau_medio = sum(graus) / len(graus)
    
    textstr = f'Min: {grau_min}\nMax: {grau_max}\nMédio: {grau_medio:.1f}'
    plt.text(0.98, 0.97, textstr, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    out_path = os.path.join(out_dir, "parte2_distribuicao_graus.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Visualização salva: {out_path}")


def escolher_fontes_e_pares(grafo: Graph):
    """
    Escolhe 3 fontes e 5 pares de forma estratégica:
    - Fontes: nós com grau alto, médio e baixo
    - Pares: combinações variadas para testar diferentes cenários
    """
    nos = list(grafo.nodes())
    
    # Calcular graus
    nos_com_grau = [(no, grafo.degree(no)) for no in nos]
    nos_ordenados = sorted(nos_com_grau, key=lambda x: x[1], reverse=True)
    
    # Fontes: maior grau, mediano, menor grau
    if len(nos_ordenados) >= 3:
        fontes = [
            nos_ordenados[0][0],  # maior grau
            nos_ordenados[len(nos_ordenados) // 2][0],  # mediano
            nos_ordenados[-1][0],  # menor grau
        ]
    else:
        fontes = [no for no, _ in nos_ordenados]
    
    # Pares: variações para testar distâncias diferentes
    pares = []
    if len(nos_ordenados) >= 10:
        pares = [
            (nos_ordenados[0][0], nos_ordenados[5][0]),  # alto → médio-alto
            (nos_ordenados[1][0], nos_ordenados[9][0]),  # alto → médio-baixo
            (nos_ordenados[2][0], nos_ordenados[7][0]),  # alto → médio
            (nos_ordenados[-1][0], nos_ordenados[0][0]),  # baixo → alto
            (nos_ordenados[len(nos_ordenados) // 2][0], nos_ordenados[-5][0]),  # médio → baixo
        ]
    else:
        # Dataset pequeno: pares simples
        for i in range(min(5, len(nos) - 1)):
            pares.append((nos[i], nos[i + 1]))
    
    return fontes, pares


def rodar_experimentos_parte2(edges_path: str, out_dir: str = "out"):
    """
    Função principal: executa todos os experimentos da Parte 2.
    """
    print("\n" + "="*70)
    print("PARTE 2: DATASET MAIOR E COMPARAÇÃO DE ALGORITMOS")
    print("="*70)
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Carregar dataset
    grafo = carregar_dataset_parte2(edges_path)
    
    # 1. Descrever dataset
    descricao, graus = descrever_dataset(grafo)
    
    # 2. Escolher fontes e pares estrategicamente
    fontes, pares = escolher_fontes_e_pares(grafo)
    
    print(f"\nFontes selecionadas (graus): {[(f, grafo.degree(f)) for f in fontes]}")
    print(f"Pares selecionados: {len(pares)} pares")
    
    # 3. Executar experimentos
    resultados = []
    
    # BFS/DFS (≥3 fontes)
    resultados.extend(rodar_bfs_dfs(grafo, fontes))
    
    # Dijkstra (≥5 pares)
    resultados.extend(rodar_dijkstra_pairs(grafo, pares))
    
    # Bellman-Ford (casos negativos)
    resultados.extend(rodar_bellman_ford_experimentos())
    
    # 4. Gerar visualização
    gerar_visualizacao_distribuicao_graus(graus, out_dir)
    
    # 5. Gerar relatório JSON
    parte2_report = {
        "dataset_path": edges_path,
        "descricao_dataset": descricao,
        "fontes_selecionadas": fontes,
        "pares_selecionados": [{"origem": o, "destino": d} for o, d in pares],
        "experimentos": resultados,
        "observacoes": {
            "algoritmos_implementados": ["bfs", "dfs", "dijkstra", "bellman-ford"],
            "sem_libs_externas": True,
            "dataset_tratado_como": "não-direcionado para comparação",
            "metricas_coletadas": ["tempo_execucao", "nos_alcancados", "custo_caminho"],
        }
    }
    
    out_path = os.path.join(out_dir, "parte2_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(parte2_report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*70)
    print("✓ PARTE 2 CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f"\nArquivos gerados:")
    print(f"  • {out_path}")
    print(f"  • {os.path.join(out_dir, 'parte2_distribuicao_graus.png')}")
    print(f"\nTotal de experimentos: {len(resultados)}")
    print(f"  • BFS/DFS: {len([r for r in resultados if r['algoritmo'] in ['bfs', 'dfs']])} execuções")
    print(f"  • Dijkstra: {len([r for r in resultados if r['algoritmo'] == 'dijkstra'])} pares")
    print(f"  • Bellman-Ford: {len([r for r in resultados if r['algoritmo'] == 'bellman-ford'])} casos")
    print("="*70 + "\n")


def main():
    """Ponto de entrada do módulo Parte 2"""
    edges_path = os.path.join(ROOT_DIR, "data", "dataset_parte2.edges")
    
    if not os.path.exists(edges_path):
        print(f"✗ ERRO: Dataset não encontrado em {edges_path}")
        print("\nPor favor, copie o arquivo .edges para data/dataset_parte2.edges")
        return 1
    
    try:
        rodar_experimentos_parte2(edges_path)
        return 0
    except Exception as e:
        print(f"\n✗ ERRO durante execução: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
