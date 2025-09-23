import networkx as nx

def dijkstra_path_and_cost(G, origem, destino, weight="peso"):
    try:
        cost = nx.dijkstra_path_length(G, origem, destino, weight=weight)
        path = nx.dijkstra_path(G, origem, destino, weight=weight)
        return cost, path
    except nx.NetworkXNoPath:
        return None, []
