#!/usr/bin/env python3
"""
CLI (Command-Line Interface) para o Projeto de Grafos do Recife.
Permite executar diferentes análises e visualizações via linha de comando.
"""

import argparse
import sys
import os

# Adicionar src ao path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

def main():
    parser = argparse.ArgumentParser(
        description='Projeto Grafos do Recife - Análise de Rede Urbana',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python cli.py --all                    # Executa análise completa
  python cli.py --metricas               # Calcula métricas globais
  python cli.py --distancias             # Calcula distâncias entre endereços
  python cli.py --visualizar             # Gera visualizações
  python cli.py --dashboard              # Gera dashboard interativo
        """
    )
    
    # Argumentos principais
    parser.add_argument(
        '--all',
        action='store_true',
        help='Executa análise completa (métricas, distâncias, visualizações)'
    )
    
    parser.add_argument(
        '--metricas',
        action='store_true',
        help='Calcula métricas globais e por microrregião'
    )
    
    parser.add_argument(
        '--distancias',
        action='store_true',
        help='Calcula distâncias entre endereços usando Dijkstra'
    )
    
    parser.add_argument(
        '--visualizar',
        action='store_true',
        help='Gera visualizações analíticas (mapas, rankings, etc.)'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Gera dashboard interativo completo'
    )
    
    parser.add_argument(
        '--origem',
        type=str,
        help='Bairro de origem para cálculo de distâncias'
    )
    
    parser.add_argument(
        '--destino',
        type=str,
        help='Bairro de destino para cálculo de distâncias'
    )
    
    parser.add_argument(
        '--algoritmo',
        type=str,
        choices=['dijkstra', 'bellman-ford', 'bfs', 'dfs'],
        default='dijkstra',
        help='Algoritmo a ser usado para busca/caminho mínimo (padrão: dijkstra)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verboso (mostra mais detalhes durante execução)'
    )
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi passado, mostrar help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Executar análises baseadas nos argumentos
    try:
        if args.all:
            print("="*70)
            print("EXECUTANDO ANÁLISE COMPLETA DO PROJETO")
            print("="*70 + "\n")
            
            # Executar todas as análises
            from solve import calcular_metricas
            from calcular_distancias import main as calc_dist_main
            from visualizacoes_modernas import main as viz_main
            from dashboard_interativo import main as dash_main
            
            print("\n[1/4] Calculando métricas...")
            calcular_metricas()
            
            print("\n[2/4] Calculando distâncias...")
            calc_dist_main()
            
            print("\n[3/4] Gerando visualizações...")
            viz_main()
            
            print("\n[4/4] Gerando dashboard...")
            dash_main()
            
        else:
            if args.metricas:
                print("\n[Calculando métricas...]")
                from solve import calcular_metricas
                calcular_metricas()
                
            if args.distancias:
                print("\n[Calculando distâncias...]")
                from calcular_distancias import main as calc_dist_main
                calc_dist_main()
                
            if args.visualizar:
                print("\n[Gerando visualizações...]")
                from visualizacoes_modernas import main as viz_main
                viz_main()
                
            if args.dashboard:
                print("\n[Gerando dashboard...]")
                from dashboard_interativo import main as dash_main
                dash_main()
        
        # Cálculo de rota específica
        if args.origem and args.destino:
            print(f"\n[Calculando rota específica: {args.origem} → {args.destino}]")
            from graphs.io import carregar_adjacencias
            from graphs.algorithms import dijkstra, bellman_ford, reconstruir_caminho
            
            grafo = carregar_adjacencias("data/bairros_unique.csv", "data/adjacencias_bairros.csv")
            
            if args.algoritmo == 'dijkstra':
                distancias, predecessores = dijkstra(grafo, args.origem)
            elif args.algoritmo == 'bellman-ford':
                distancias, predecessores, _ = bellman_ford(grafo, args.origem)
            else:
                print(f"Algoritmo {args.algoritmo} não suporta cálculo de caminho mínimo com pesos.")
                return
            
            caminho = reconstruir_caminho(predecessores, args.destino)
            if caminho:
                print(f"Caminho: {' → '.join(caminho)}")
                print(f"Custo total: {distancias[args.destino]}")
            else:
                print(f"Não há caminho entre {args.origem} e {args.destino}")
        
        print("\n" + "="*70)
        print("✓ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print("\nArquivos gerados em: out/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
