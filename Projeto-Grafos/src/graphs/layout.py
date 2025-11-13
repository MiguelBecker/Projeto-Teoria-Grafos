"""
Implementação própria de algoritmo de layout para visualização de grafos.
Force-directed layout baseado no algoritmo de Fruchterman-Reingold.
Não usa NetworkX ou outras bibliotecas de grafos proibidas.
"""

import math
import random
from typing import Dict, Tuple
from graphs.graph import Graph


def spring_layout(grafo: Graph, k: float = 1.5, iterations: int = 50, seed: int = 42) -> Dict[str, Tuple[float, float]]:
    """
    Implementação própria de spring layout (force-directed layout).
    Baseado no algoritmo de Fruchterman-Reingold.
    
    Args:
        grafo: Grafo a ser visualizado
        k: Distância ideal entre nós (parâmetro de controle)
        iterations: Número de iterações do algoritmo
        seed: Semente para reprodutibilidade
    
    Returns:
        Dicionário {nó: (x, y)} com posições dos nós
    """
    random.seed(seed)
    
    nodes = grafo.nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    if n == 1:
        return {nodes[0]: (0.5, 0.5)}
    
    pos = {}
    for node in nodes:
        pos[node] = (random.random(), random.random())
    
    area = 1.0
    k_ideal = k * math.sqrt(area / n)
    
    temperature = 0.1
    dt = temperature / (iterations + 1)
    
    for iteration in range(iterations):
        displacement = {node: (0.0, 0.0) for node in nodes}
        
        for i, v in enumerate(nodes):
            for u in nodes[i+1:]:
                delta_x = pos[v][0] - pos[u][0]
                delta_y = pos[v][1] - pos[u][1]
                
                distance = math.sqrt(delta_x**2 + delta_y**2)
                if distance < 0.01:
                    distance = 0.01
                
                force = (k_ideal ** 2) / distance
                
                fx = (delta_x / distance) * force
                fy = (delta_y / distance) * force
                
                displacement[v] = (displacement[v][0] + fx, displacement[v][1] + fy)
                displacement[u] = (displacement[u][0] - fx, displacement[u][1] - fy)
        
        for u, v, peso, _ in grafo.edges():
            delta_x = pos[v][0] - pos[u][0]
            delta_y = pos[v][1] - pos[u][1]
            
            distance = math.sqrt(delta_x**2 + delta_y**2)
            if distance < 0.01:
                distance = 0.01
            
            force = (distance ** 2) / k_ideal
            
            fx = (delta_x / distance) * force
            fy = (delta_y / distance) * force
            
            displacement[v] = (displacement[v][0] - fx, displacement[v][1] - fy)
            displacement[u] = (displacement[u][0] + fx, displacement[u][1] + fy)
        
        for node in nodes:
            dx, dy = displacement[node]
            disp_length = math.sqrt(dx**2 + dy**2)
            
            if disp_length > 0:
                limited_length = min(disp_length, temperature)
                dx = (dx / disp_length) * limited_length
                dy = (dy / disp_length) * limited_length
                
                new_x = pos[node][0] + dx
                new_y = pos[node][1] + dy
                
                new_x = max(0.01, min(0.99, new_x))
                new_y = max(0.01, min(0.99, new_y))
                
                pos[node] = (new_x, new_y)
        
        temperature -= dt
    
    if nodes:
        xs = [pos[node][0] for node in nodes]
        ys = [pos[node][1] for node in nodes]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        range_x = max_x - min_x if max_x - min_x > 0.01 else 0.01
        range_y = max_y - min_y if max_y - min_y > 0.01 else 0.01
        
        for node in nodes:
            x = ((pos[node][0] - min_x) / range_x) * 2 - 1
            y = ((pos[node][1] - min_y) / range_y) * 2 - 1
            pos[node] = (x, y)
    
    return pos


def circular_layout(grafo: Graph, scale: float = 1.0) -> Dict[str, Tuple[float, float]]:
    """
    Layout circular simples - nós dispostos em círculo.
    Útil para grafos pequenos ou quando spring_layout não converge bem.
    
    Args:
        grafo: Grafo a ser visualizado
        scale: Escala do raio do círculo
    
    Returns:
        Dicionário {nó: (x, y)} com posições dos nós
    """
    nodes = grafo.nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    if n == 1:
        return {nodes[0]: (0.0, 0.0)}
    
    pos = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = scale * math.cos(angle)
        y = scale * math.sin(angle)
        pos[node] = (x, y)
    
    return pos


def grid_layout(grafo: Graph, cols: int = None) -> Dict[str, Tuple[float, float]]:
    """
    Layout em grade - nós dispostos em grid regular.
    
    Args:
        grafo: Grafo a ser visualizado
        cols: Número de colunas (se None, usa sqrt(n))
    
    Returns:
        Dicionário {nó: (x, y)} com posições dos nós
    """
    nodes = grafo.nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    if n == 1:
        return {nodes[0]: (0.0, 0.0)}
    
    if cols is None:
        cols = int(math.ceil(math.sqrt(n)))
    
    rows = int(math.ceil(n / cols))
    
    pos = {}
    for i, node in enumerate(nodes):
        row = i // cols
        col = i % cols
        
        x = (col - (cols - 1) / 2) / max(cols - 1, 1)
        y = (row - (rows - 1) / 2) / max(rows - 1, 1)
        
        pos[node] = (x, y)
    
    return pos
