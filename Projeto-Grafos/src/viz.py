import os
import json

import networkx as nx
import matplotlib.pyplot as plt

try:
    from pyvis.network import Network
    _HAS_PYVIS = True
except Exception:
    _HAS_PYVIS = False


def gerar_arvore_percurso():
    """
    Lê out/percurso_nova_descoberta_setubal.json (gerado no Passo 6)
    e exporta:
      - out/arvore_percurso.png (matplotlib)
      - out/arvore_percurso.html (pyvis, se disponível)
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(base, "out")
    os.makedirs(out_path, exist_ok=True)

    percurso_file = os.path.join(out_path, "percurso_nova_descoberta_setubal.json")
    if not os.path.exists(percurso_file):
        print("⚠️ Arquivo 'out/percurso_nova_descoberta_setubal.json' não encontrado.")
        return

    with open(percurso_file, "r", encoding="utf-8") as f:
        percurso = json.load(f)

    caminho = percurso.get("caminho", [])
    if not caminho:
        print("⚠️ Caminho vazio no JSON, nada a desenhar.")
        return

    sub_edges = list(zip(caminho[:-1], caminho[1:]))
    subG = nx.Graph()
    subG.add_edges_from(sub_edges)

    pos = nx.spring_layout(subG, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(
        subG, pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=2000,
        font_size=10,
        font_weight="bold",
    )
    nx.draw_networkx_edges(subG, pos, edgelist=sub_edges, edge_color="red", width=3)
    plt.title("Árvore do percurso: Nova Descoberta → Boa Viagem (Setúbal)")
    plt.savefig(os.path.join(out_path, "arvore_percurso.png"), dpi=300)
    plt.close()

    if _HAS_PYVIS:
        net = Network(height="600px", width="100%", notebook=False, directed=False)
        for node in caminho:
            net.add_node(node, label=node, color="lightblue", size=25)
        for u, v in sub_edges:
            net.add_edge(u, v, color="red", width=3)
        net.show(os.path.join(out_path, "arvore_percurso.html"))
    else:
        print("ℹ️ pyvis não encontrado — gerado apenas o PNG. (instale com: pip install pyvis)")

    print("✅ Gerado: out/arvore_percurso.png" + (" e out/arvore_percurso.html" if _HAS_PYVIS else ""))
