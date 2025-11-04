import os, sys, pandas as pd
from graphs.io import carregar_adjacencias

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)

def calcular_ranking():
    G = carregar_adjacencias("data/bairros_unique.csv", "data/adjacencias_bairros.csv")

    graus = []
    for bairro in G.nodes():
        graus.append({"bairro": bairro, "grau": G.degree(bairro)})

    df_graus = pd.DataFrame(graus).sort_values("grau", ascending=False)
    df_graus.to_csv("out/graus.csv", index=False)

    df_ego = pd.read_csv("out/ego_bairro.csv")
    bairro_maior_grau = df_graus.iloc[0]["bairro"]
    bairro_maior_densidade = df_ego.sort_values("densidade_ego", ascending=False).iloc[0]["bairro"]

    with open("out/ranking.txt", "w", encoding="utf-8") as f:
        f.write(f"Bairro com maior grau: {bairro_maior_grau}\n")
        f.write(f"Bairro com maior densidade_ego: {bairro_maior_densidade}\n")

if __name__ == "__main__":
    calcular_ranking()
