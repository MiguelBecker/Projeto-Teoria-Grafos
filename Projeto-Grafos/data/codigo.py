import pandas as pd
import os

# ===== 1) Definir pasta base =====
base_path = os.path.dirname(os.path.abspath(__file__))

# Caminho correto da pasta out
out_path = r"C:\Users\migue\OneDrive\Desktop\Projeto-Teoria-Grafos-1\Projeto-Grafos\out"

# ===== 2) Carregar ego_bairro.csv =====
ego_bairro = pd.read_csv(os.path.join(out_path, "ego_bairro.csv"))

# ===== 3) Gerar graus.csv =====
graus = ego_bairro[["bairro", "grau"]].copy()
graus_path = os.path.join(out_path, "graus.csv")
graus.to_csv(graus_path, index=False, encoding="utf-8")

# ===== 4) Mostrar os campeões no terminal =====
bairro_maior_grau = ego_bairro.loc[ego_bairro["grau"].idxmax()]
bairro_maior_densidade = ego_bairro.loc[ego_bairro["densidade_ego"].idxmax()]

print(f"✅ Arquivo gerado: {graus_path}")
print("\n🏆 Bairro com maior grau:")
print(bairro_maior_grau[["bairro", "grau"]])

print("\n🏆 Bairro com maior densidade de ego:")
print(bairro_maior_densidade[["bairro", "densidade_ego"]])
