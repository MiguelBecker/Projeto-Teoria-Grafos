from collections import deque, defaultdict
from typing import Dict, List, Tuple, Set
import heapq
from graphs.graph import Graph


def bfs(grafo: Graph, origem: str) -> Dict[str, int]:
    """
    Busca em largura (BFS) a partir de um nó origem.
    Retorna um dicionário com as distâncias (em número de arestas) de cada nó até a origem.
    """
    if origem not in grafo.nodes():
        return {}
    
    distancias = {origem: 0}
    fila = deque([origem])
    
    while fila:
        atual = fila.popleft()
        dist_atual = distancias[atual]
        
        for vizinho, _, _ in grafo.neighbors(atual):
            if vizinho not in distancias:
                distancias[vizinho] = dist_atual + 1
                fila.append(vizinho)
    
    return distancias


def bfs_arvore(grafo: Graph, origem: str) -> Dict[str, str]:
    """
    Busca em largura (BFS) retornando a árvore de busca.
    Retorna um dicionário onde a chave é o nó e o valor é seu pai na árvore.
    """
    if origem not in grafo.nodes():
        return {}
    
    pais = {origem: None}
    fila = deque([origem])
    
    while fila:
        atual = fila.popleft()
        
        for vizinho, _, _ in grafo.neighbors(atual):
            if vizinho not in pais:
                pais[vizinho] = atual
                fila.append(vizinho)
    
    return pais


def dfs(grafo: Graph, origem: str) -> Dict[str, int]:
    """
    Busca em profundidade (DFS) a partir de um nó origem.
    Retorna um dicionário com a ordem de visitação.
    """
    if origem not in grafo.nodes():
        return {}
    
    visitados = {}
    ordem = [0]
    
    def dfs_recursivo(no: str):
        visitados[no] = ordem[0]
        ordem[0] += 1
        
        for vizinho, _, _ in grafo.neighbors(no):
            if vizinho not in visitados:
                dfs_recursivo(vizinho)
    
    dfs_recursivo(origem)
    return visitados


def dijkstra(grafo: Graph, origem: str) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Algoritmo de Dijkstra para caminho mínimo com pesos não-negativos.
    Retorna:
        - Dicionário de distâncias mínimas
        - Dicionário de predecessores para reconstruir o caminho
    """
    if origem not in grafo.nodes():
        return {}, {}
    
    distancias = {no: float('inf') for no in grafo.nodes()}
    distancias[origem] = 0.0
    predecessores = {origem: None}
    
    heap = [(0.0, origem)]
    visitados = set()
    
    while heap:
        dist_atual, atual = heapq.heappop(heap)
        
        if atual in visitados:
            continue
        
        visitados.add(atual)
        
        for vizinho, peso, _ in grafo.neighbors(atual):
            if vizinho not in visitados:
                nova_dist = dist_atual + peso
                
                if nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    predecessores[vizinho] = atual
                    heapq.heappush(heap, (nova_dist, vizinho))
    
    return distancias, predecessores


def bellman_ford(grafo: Graph, origem: str) -> Tuple[Dict[str, float], Dict[str, str], bool]:
    """
    Algoritmo de Bellman-Ford para caminho mínimo (aceita pesos negativos).
    Retorna:
        - Dicionário de distâncias mínimas
        - Dicionário de predecessores
        - Bool indicando se há ciclo negativo
    """
    if origem not in grafo.nodes():
        return {}, {}, False
    
    distancias = {no: float('inf') for no in grafo.nodes()}
    distancias[origem] = 0.0
    predecessores = {origem: None}
    
    nos = grafo.nodes()
    arestas = grafo.edges()
    
    # Relaxamento de arestas (V-1 iterações)
    for _ in range(len(nos) - 1):
        for u, v, peso, _ in arestas:
            if distancias[u] + peso < distancias[v]:
                distancias[v] = distancias[u] + peso
                predecessores[v] = u
            if distancias[v] + peso < distancias[u]:
                distancias[u] = distancias[v] + peso
                predecessores[u] = v
    
    # Verificação de ciclo negativo
    tem_ciclo_negativo = False
    for u, v, peso, _ in arestas:
        if distancias[u] + peso < distancias[v]:
            tem_ciclo_negativo = True
            break
        if distancias[v] + peso < distancias[u]:
            tem_ciclo_negativo = True
            break
    
    return distancias, predecessores, tem_ciclo_negativo


def reconstruir_caminho(predecessores: Dict[str, str], destino: str) -> List[str]:
    """
    Reconstrói o caminho do nó origem até o destino usando o dicionário de predecessores.
    """
    if destino not in predecessores:
        return []
    
    caminho = []
    atual = destino
    
    while atual is not None:
        caminho.append(atual)
        atual = predecessores.get(atual)
    
    return list(reversed(caminho))


def densidade_ego(grafo: Graph, no: str) -> float:
    """
    Calcula a densidade da ego-subrede de um nó.
    Densidade = arestas_reais / arestas_possíveis
    
    A ego-subrede inclui o nó central e todos os seus vizinhos,
    além das conexões entre eles.
    """
    if no not in grafo.nodes():
        return 0.0
    
    # Coletar vizinhos
    vizinhos = set()
    for v, _, _ in grafo.neighbors(no):
        vizinhos.add(v)
    
    # Ego-subrede inclui o nó central e seus vizinhos
    ego_nos = {no} | vizinhos
    
    if len(ego_nos) <= 1:
        return 0.0
    
    # Contar arestas dentro da ego-subrede
    arestas_ego = 0
    arestas_vistas = set()
    
    for u in ego_nos:
        for v, _, _ in grafo.neighbors(u):
            if v in ego_nos:
                aresta = tuple(sorted([u, v]))
                if aresta not in arestas_vistas:
                    arestas_vistas.add(aresta)
                    arestas_ego += 1
    
    # Número máximo de arestas possíveis em um grafo não-direcionado
    n = len(ego_nos)
    arestas_possiveis = n * (n - 1) / 2
    
    return arestas_ego / arestas_possiveis if arestas_possiveis > 0 else 0.0


def componentes_conexos(grafo: Graph) -> List[Set[str]]:
    """
    Encontra todos os componentes conexos do grafo usando DFS.
    Retorna uma lista de conjuntos, onde cada conjunto contém os nós de um componente.
    """
    visitados = set()
    componentes = []
    
    def dfs_componente(no: str, componente: Set[str]):
        componente.add(no)
        visitados.add(no)
        
        for vizinho, _, _ in grafo.neighbors(no):
            if vizinho not in visitados:
                dfs_componente(vizinho, componente)
    
    for no in grafo.nodes():
        if no not in visitados:
            componente = set()
            dfs_componente(no, componente)
            componentes.append(componente)
    
    return componentes


def grau_medio(grafo: Graph) -> float:
    """
    Calcula o grau médio do grafo.
    """
    if grafo.order() == 0:
        return 0.0
    
    soma_graus = sum(grafo.degree(no) for no in grafo.nodes())
    return soma_graus / grafo.order()


def calcular_metricas_basicas(grafo: Graph) -> Dict:
    """
    Calcula métricas básicas do grafo.
    """
    return {
        'num_nos': grafo.order(),
        'num_arestas': grafo.size(),
        'grau_medio': grau_medio(grafo),
        'num_componentes': len(componentes_conexos(grafo))
    }
