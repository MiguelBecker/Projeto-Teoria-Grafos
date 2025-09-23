import argparse
import sys

from .solve import (
    calc_global_metrics,
    calc_microrregioes,
    calc_ego_network,
    calc_graus,
    calc_distancias,
)
from .viz import gerar_arvore_percurso


def main():
    parser = argparse.ArgumentParser(
        description="Projeto Teoria dos Grafos — CLI"
    )
    parser.add_argument(
        "acao",
        choices=["global", "microrregioes", "ego", "graus", "distancias", "percurso"],
        help="Qual etapa deseja executar?"
    )
    args = parser.parse_args()

    if args.acao == "global":
        calc_global_metrics()
    elif args.acao == "microrregioes":
        calc_microrregioes()
    elif args.acao == "ego":
        calc_ego_network()
    elif args.acao == "graus":
        calc_graus()
    elif args.acao == "distancias":
        calc_distancias()
    elif args.acao == "percurso":
        gerar_arvore_percurso()
    else:
        print("⚠️ Ação inválida!", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
