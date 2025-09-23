import os
import json
import pandas as pd
import networkx as nx
from .graph.algorithms import dijkstra_path_and_cost

def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _path_data(*names):
    return os.path.join(_project_root(), "data", *names)

def _path_out(*names):
    out_dir = os.path.join(_project_root(), "out")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, *names)

def _load_adjacencias():
    df = pd.read_csv(_path_data("adjacencias_bairros.csv"))
    df.columns = [c.strip() for c in df.columns]
    if "peso" not in df.columns:
        raise ValueError("Coluna 'peso' não encontrada em adjacencias_bairros.csv")
    df["peso"] = df["peso"].astype(float)
    return df

def _build_graph_from_adjacencias(df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for _, r in df.iterrows():
        u = str(r["bairro_origem"]).strip()
        v = str(r["bairro_destino"]).strip()
        G.add_edge(u, v, peso=float(r["peso"]), logradouro=str(r.get("logradouro", "")), observacao=str(r.get("observacao", "")))
    return G

def _normalize_microcols(df: pd.DataFrame):
    cols_map = {c.lower(): c for c in df.columns}
    if "bairros" not in cols_map:
        raise ValueError("Arquivo bairros_unique.csv precisa ter a coluna 'Bairros'.")
    mic_col = cols_map.get("microregiões") or cols_map.get("microregioes")
    if not mic_col:
        raise ValueError("Arquivo bairros_unique.csv precisa ter a coluna 'Microregiões' (ou 'Microregioes').")
    return "Bairros", mic_col

def _normalize_setubal(name: str) -> str:
    n = (name or "").strip()
    low = n.lower()
    if "setúbal" in low or "setubal" in low or "boa viagem (setúbal)" in low or "boa viagem (setubal)" in low:
        return "Boa Viagem"
    return n

def calc_global_metrics():
    adj = _load_adjacencias()
    G = _build_graph_from_adjacencias(adj)
    ordem = G.number_of_nodes()
    tamanho = G.number_of_edges()
    densidade = nx.density(G) if ordem >= 2 else 0.0
    with open(_path_out("recife_global.json"), "w", encoding="utf-8") as f:
        json.dump({"ordem": ordem, "tamanho": tamanho, "densidade": densidade}, f, indent=4, ensure_ascii=False)
    print("✅ out/recife_global.json gerado")

def calc_microrregioes():
    adj = _load_adjacencias()
    G = _build_graph_from_adjacencias(adj)
    bu = pd.read_csv(_path_data("bairros_unique.csv"))
    b_col, mic_col = _normalize_microcols(bu)
    mic_json = {}
    for mic in sorted(bu[mic_col].dropna().unique()):
        bairros = bu.loc[bu[mic_col] == mic, b_col].dropna().astype(str).str.strip().tolist()
        sub = G.subgraph(bairros)
        o = sub.number_of_nodes()
        e = sub.number_of_edges()
        d = nx.density(sub) if o >= 2 else 0.0
        mic_key = str(int(mic)) if isinstance(mic, (int, float)) and float(mic).is_integer() else str(mic)
        mic_json[mic_key] = {"ordem": o, "tamanho": e, "densidade": d}
    with open(_path_out("microrregioes.json"), "w", encoding="utf-8") as f:
        json.dump(mic_json, f, indent=4, ensure_ascii=False)
    print("✅ out/microrregioes.json gerado")

def calc_ego_network():
    adj = _load_adjacencias()
    G = _build_graph_from_adjacencias(adj)
    rows = []
    for v in sorted(G.nodes()):
        ego = nx.ego_graph(G, v)
        o = ego.number_of_nodes()
        e = ego.number_of_edges()
        d = nx.density(ego) if o >= 2 else 0.0
        rows.append({"bairro": v, "grau": G.degree(v), "ordem_ego": o, "tamanho_ego": e, "densidade_ego": d})
    pd.DataFrame(rows).to_csv(_path_out("ego_bairro.csv"), index=False, encoding="utf-8")
    print("✅ out/ego_bairro.csv gerado")

def calc_graus():
    ego_path = _path_out("ego_bairro.csv")
    if not os.path.exists(ego_path):
        raise FileNotFoundError("out/ego_bairro.csv não encontrado. Rode primeiro: calc_ego_network().")
    ego = pd.read_csv(ego_path)
    ego.columns = [c.strip() for c in ego.columns]
    ego[["bairro", "grau"]].to_csv(_path_out("graus.csv"), index=False, encoding="utf-8")
    print("✅ out/graus.csv gerado")
    top_grau = ego.loc[ego["grau"].idxmax(), ["bairro", "grau"]]
    top_dens = ego.loc[ego["densidade_ego"].idxmax(), ["bairro", "densidade_ego"]]
    print(f"🏆 Maior grau: {top_grau['bairro']} ({int(top_grau['grau'])})")
    print(f"🏆 Maior densidade_ego: {top_dens['bairro']} ({top_dens['densidade_ego']:.3f})")

def calc_distancias():
    adj = _load_adjacencias()
    G = _build_graph_from_adjacencias(adj)
    end = pd.read_csv(_path_data("enderecos.csv"))
    end.columns = [c.strip() for c in end.columns]
    if not {"bairro_origem", "bairro_destino"}.issubset(set(end.columns)):
        raise ValueError("enderecos.csv precisa conter as colunas 'bairro_origem' e 'bairro_destino'.")
    rows = []
    wrote_nd_setubal = False

    def _resolve_node(name: str):
        if name in G:
            return name
        if name == "Boa Viagem" and "Boa Viagem (Setúbal)" in G:
            return "Boa Viagem (Setúbal)"
        if name == "Boa Viagem (Setúbal)" and "Boa Viagem" in G:
            return "Boa Viagem"
        return name

    for _, r in end.iterrows():
        origem_raw = str(r["bairro_origem"]).strip()
        destino_raw = str(r["bairro_destino"]).strip()
        origem = _resolve_node(_normalize_setubal(origem_raw))
        destino = _resolve_node(_normalize_setubal(destino_raw))
        custo, caminho = dijkstra_path_and_cost(G, origem, destino, weight="peso")
        caminho_str = " -> ".join(caminho) if caminho else "sem caminho"
        rows.append({"X": origem_raw, "Y": destino_raw, "bairro_X": origem, "bairro_Y": destino, "custo": custo, "caminho": caminho_str})
        if (origem_raw.lower().startswith("nova descoberta") and ("setúbal" in destino_raw.lower() or "setubal" in destino_raw.lower() or "boa viagem" in destino_raw.lower())) and not wrote_nd_setubal:
            with open(_path_out("percurso_nova_descoberta_setubal.json"), "w", encoding="utf-8") as f:
                json.dump({"origem": origem_raw, "destino": destino_raw, "custo": custo, "caminho": caminho}, f, indent=4, ensure_ascii=False)
            wrote_nd_setubal = True

    pd.DataFrame(rows).to_csv(_path_out("distancias_enderecos.csv"), index=False, encoding="utf-8")
    print("✅ out/distancias_enderecos.csv gerado")
    if wrote_nd_setubal:
        print("✅ out/percurso_nova_descoberta_setubal.json gerado")

if __name__ == "__main__":
    calc_global_metrics()
    calc_microrregioes()
    calc_ego_network()
    calc_graus()
    calc_distancias()
