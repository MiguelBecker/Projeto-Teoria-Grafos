import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.graph import Graph, EdgeMeta
from graphs.algorithms import dfs


def test_dfs_simples():
    print("\n=== Teste 1: DFS Simples ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("A", "D", 1.0)
    g.add_edge("C", "E", 1.0)
    
    visitados = dfs(g, "A")
    
    assert "A" in visitados, "A deve ser visitado"
    assert "B" in visitados, "B deve ser visitado"
    assert "C" in visitados, "C deve ser visitado"
    assert "D" in visitados, "D deve ser visitado"
    assert "E" in visitados, "E deve ser visitado"
    assert len(visitados) == 5, "Deve visitar exatamente 5 nós"
    
    print("✓ Todos os nós visitados")
    print(f"  Ordem de visitação: {sorted(visitados.items(), key=lambda x: x[1])}")


def test_dfs_desconectado():
    print("\n=== Teste 2: DFS Grafo Desconectado ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("C", "D", 1.0)
    
    visitados = dfs(g, "A")
    
    assert "A" in visitados, "A deve ser visitado"
    assert "B" in visitados, "B deve ser visitado"
    assert "C" not in visitados, "C não deve ser visitado (desconectado)"
    assert "D" not in visitados, "D não deve ser visitado (desconectado)"
    
    print("✓ Componente desconectada não visitada")
    print(f"  Visitados: {list(visitados.keys())}")


def test_dfs_no_inexistente():
    print("\n=== Teste 3: DFS Nó Inexistente ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    
    visitados = dfs(g, "Z")
    
    assert len(visitados) == 0, "Não deve retornar visitados para nó inexistente"
    
    print("✓ Nó inexistente tratado corretamente")


def test_dfs_ciclo():
    print("\n=== Teste 4: DFS com Ciclo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "A", 1.0)
    
    visitados = dfs(g, "A")
    
    assert len(visitados) == 3, "Deve visitar cada nó exatamente uma vez"
    assert "A" in visitados, "A deve ser visitado"
    assert "B" in visitados, "B deve ser visitado"
    assert "C" in visitados, "C deve ser visitado"
    
    print("✓ Ciclo tratado corretamente (cada nó visitado uma vez)")
    print(f"  Ordem: {sorted(visitados.items(), key=lambda x: x[1])}")


def test_dfs_ordem_visitacao():
    print("\n=== Teste 5: DFS Ordem de Visitação ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "D", 1.0)
    
    visitados = dfs(g, "A")
    
    # Verifica que a ordem é crescente (0, 1, 2, 3)
    ordem = [visitados[n] for n in ["A", "B", "C", "D"]]
    assert ordem == sorted(ordem), "Ordem de visitação deve ser sequencial"
    
    print("✓ Ordem de visitação em profundidade correta")
    print(f"  A={visitados['A']}, B={visitados['B']}, C={visitados['C']}, D={visitados['D']}")


def test_dfs_grafo_estrela():
    print("\n=== Teste 6: DFS Grafo Estrela ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("A", "D", 1.0)
    
    visitados = dfs(g, "A")
    
    assert len(visitados) == 4, "Deve visitar todos os 4 nós"
    assert visitados["A"] == 0, "A deve ser visitado primeiro"
    
    print("✓ Grafo estrela processado corretamente")
    print(f"  Visitados: {visitados}")


def run_all_tests():
    print("=" * 70)
    print("EXECUTANDO TESTES: DFS (Busca em Profundidade)")
    print("=" * 70)
    
    try:
        test_dfs_simples()
        test_dfs_desconectado()
        test_dfs_no_inexistente()
        test_dfs_ciclo()
        test_dfs_ordem_visitacao()
        test_dfs_grafo_estrela()
        
        print("\n" + "=" * 70)
        print("✓ TODOS OS TESTES DE DFS PASSARAM!")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TESTE FALHOU: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
