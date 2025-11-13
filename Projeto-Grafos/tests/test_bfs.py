import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.graph import Graph, EdgeMeta
from graphs.algorithms import bfs, bfs_arvore


def test_bfs_simples():
    print("\n=== Teste 1: BFS Simples ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("A", "D", 1.0)
    g.add_edge("C", "E", 1.0)
    
    distancias = bfs(g, "A")
    
    assert distancias["A"] == 0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1, "Distância de A para B deve ser 1"
    assert distancias["C"] == 2, "Distância de A para C deve ser 2"
    assert distancias["D"] == 1, "Distância de A para D deve ser 1"
    assert distancias["E"] == 3, "Distância de A para E deve ser 3"
    
    print("✓ Distâncias corretas")
    print(f"  A: {distancias['A']}, B: {distancias['B']}, C: {distancias['C']}, D: {distancias['D']}, E: {distancias['E']}")


def test_bfs_desconectado():
    print("\n=== Teste 2: BFS Grafo Desconectado ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("C", "D", 1.0)
    
    distancias = bfs(g, "A")
    
    assert "A" in distancias, "A deve estar nas distâncias"
    assert "B" in distancias, "B deve estar nas distâncias"
    assert "C" not in distancias, "C não deve estar nas distâncias (desconectado)"
    assert "D" not in distancias, "D não deve estar nas distâncias (desconectado)"
    
    print("✓ Componente desconectada não alcançada")
    print(f"  Alcançados: {list(distancias.keys())}")


def test_bfs_arvore():
    print("\n=== Teste 3: BFS Árvore de Busca ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("A", "D", 1.0)
    g.add_edge("C", "E", 1.0)
    
    pais = bfs_arvore(g, "A")
    
    assert pais["A"] is None, "A não deve ter pai (é raiz)"
    assert pais["B"] == "A", "Pai de B deve ser A"
    assert pais["D"] == "A", "Pai de D deve ser A"
    assert pais["C"] == "B", "Pai de C deve ser B"
    assert pais["E"] == "C", "Pai de E deve ser C"
    
    print("✓ Árvore de busca correta")
    print(f"  Pais: {pais}")


def test_bfs_no_inexistente():
    print("\n=== Teste 4: BFS Nó Inexistente ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    
    distancias = bfs(g, "Z")
    
    assert len(distancias) == 0, "Não deve retornar distâncias para nó inexistente"
    
    print("✓ Nó inexistente tratado corretamente")


def test_bfs_ciclo():
    print("\n=== Teste 5: BFS com Ciclo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "A", 1.0)
    
    distancias = bfs(g, "A")
    
    assert distancias["A"] == 0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1, "Distância de A para B deve ser 1"
    assert distancias["C"] == 1, "Distância de A para C deve ser 1 (direto)"
    
    print("✓ Ciclo tratado corretamente")
    print(f"  Distâncias: {distancias}")


def test_bfs_grafo_completo():
    print("\n=== Teste 6: BFS Grafo Completo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("A", "D", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("B", "D", 1.0)
    g.add_edge("C", "D", 1.0)
    
    distancias = bfs(g, "A")
    
    assert distancias["A"] == 0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1, "Distância de A para B deve ser 1"
    assert distancias["C"] == 1, "Distância de A para C deve ser 1"
    assert distancias["D"] == 1, "Distância de A para D deve ser 1"
    
    print("✓ Grafo completo processado corretamente")
    print(f"  Distâncias: {distancias}")


def run_all_tests():
    print("=" * 70)
    print("EXECUTANDO TESTES: BFS (Busca em Largura)")
    print("=" * 70)
    
    try:
        test_bfs_simples()
        test_bfs_desconectado()
        test_bfs_arvore()
        test_bfs_no_inexistente()
        test_bfs_ciclo()
        test_bfs_grafo_completo()
        
        print("\n" + "=" * 70)
        print("✓ TODOS OS TESTES DE BFS PASSARAM!")
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
