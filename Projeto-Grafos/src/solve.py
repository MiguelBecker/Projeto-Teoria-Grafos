import os, sys, json
import pandas as pd
from graphs.io import carregar_adjacencias
from graphs.graph import Graph

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)

def densidade(g: Graph) -> float:
    v = g.order()
    e = g.size()
    return 0 if v < 2 else 2 * e / (v * (v - 1))

def subgrafo_por_bairros(G: Graph, bairros):
    sub = Graph()
    for u, v, w, meta in G.edges():
        if u in bairros and v in bairros:
            sub.add_edge(u, v, w, meta)
    return sub

def calcular_metricas():
    G = carregar_adjacencias("data/bairros_unique.csv", "data/adjacencias_bairros.csv")

    recife_global = {
        "ordem": int(G.order()),
        "tamanho": int(G.size()),
        "densidade": float(round(densidade(G), 4)),
    }
    with open("out/recife_global.json", "w", encoding="utf-8") as f:
        json.dump(recife_global, f, ensure_ascii=False, indent=2)

    df_bairros = pd.read_csv("data/bairros_unique.csv")
    resultados_micro = []
    for m in sorted(df_bairros["microrregiao"].unique()):
        bairros_m = df_bairros.loc[df_bairros["microrregiao"] == m, "bairro"].tolist()
        sub = subgrafo_por_bairros(G, bairros_m)
        resultados_micro.append({
            "microrregiao": str(m),
            "ordem": int(sub.order()),
            "tamanho": int(sub.size()),
            "densidade": float(round(densidade(sub), 4)),
        })
    with open("out/microrregioes.json", "w", encoding="utf-8") as f:
        json.dump(resultados_micro, f, ensure_ascii=False, indent=2)

    ego_data = []
    for bairro in G.nodes():
        vizinhos = [v for v, _, _ in G.neighbors(bairro)]
        ego_nodes = [bairro] + vizinhos
        ego = subgrafo_por_bairros(G, ego_nodes)
        ego_data.append({
            "bairro": bairro,
            "grau": int(G.degree(bairro)),
            "ordem_ego": int(ego.order()),
            "tamanho_ego": int(ego.size()),
            "densidade_ego": float(round(densidade(ego), 4)),
        })
    pd.DataFrame(ego_data).to_csv("out/ego_bairro.csv", index=False)

if __name__ == "__main__":
    calcular_metricas()
