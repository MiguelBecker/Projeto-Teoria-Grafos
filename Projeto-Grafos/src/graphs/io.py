import os, sys, re
import pandas as pd
from graphs.graph import Graph, EdgeMeta

CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
os.chdir(ROOT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)




def melt_bairros(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    cols = []
    for i in range(1, 7):
        for j in range(1, 4):
            col = f"{i}.{j}"
            if col in df.columns:
                cols.append(col)
    melted = df.melt(value_vars=cols, var_name="microrregiao", value_name="bairro").dropna()
    melted["bairro"] = melted["bairro"].astype(str).str.strip().str.title()
    melted = melted[melted["bairro"] != ""].drop_duplicates().reset_index(drop=True)
    melted["bairro"] = melted["bairro"].replace(
        {"Setúbal": "Boa Viagem (Setúbal)", "Setubal": "Boa Viagem (Setúbal)"}
    )

    def extrair_num_principal(valor):
        m = re.match(r"^(\d+)", str(valor))
        return m.group(1) if m else valor

    melted["microrregiao"] = melted["microrregiao"].apply(extrair_num_principal)
    melted.to_csv(output_csv, index=False)
    return melted






def carregar_adjacencias(bairros_unique_csv: str, adj_csv: str) -> Graph:
    df_adj = pd.read_csv(adj_csv)

    G = Graph()

    for _, r in df_adj.iterrows():
        u = str(r["bairro_origem"]).strip().title()
        v = str(r["bairro_destino"]).strip().title()
        w = float(r.get("peso", 1.0))

        meta = EdgeMeta(
            logradouro=r.get("logradouro"),
            observacao=r.get("observacao")
        )

        if u in ["Setúbal", "Boa Viagem (Setúbal)"]:
            u = "Boa Viagem"
        if v in ["Setúbal", "Boa Viagem (Setúbal)"]:
            v = "Boa Viagem"

        G.add_edge(u, v, w, meta)

    return G




def carregar_dataset_parte2(edges_path: str) -> Graph:
    """
    Carrega dataset maior (Parte 2) do formato .edges:
    % asym weighted
    u\tv\tpeso
    
    Args:
        edges_path: caminho para arquivo .edges
    
    Returns:
        Graph com nós e arestas carregadas (tratado como não-direcionado para comparação)
    """
    G = Graph()
    
    print(f"Carregando dataset Parte 2: {edges_path}")
    
    with open(edges_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            u = parts[0]
            v = parts[1]
            w = 1.0
            
            if len(parts) >= 3:
                try:
                    w = float(parts[2])
                except ValueError:
                    w = 1.0
            
            # Adiciona aresta (não-direcionado para experimentos)
            G.add_edge(u, v, w)
    
    print(f"✓ Dataset carregado: {G.order()} nós, {G.size()} arestas")
    return G


if __name__ == "__main__":
    input_path = os.path.join(ROOT_DIR, "data", "bairros_recife.csv")
    output_path = os.path.join(ROOT_DIR, "data", "bairros_unique.csv")
    melt_bairros(input_path, output_path)
