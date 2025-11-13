import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.graph import Graph, EdgeMeta
from graphs.algorithms import dijkstra, reconstruir_caminho


def test_dijkstra_simples():
    print("\n=== Teste 1: Dijkstra Simples ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    
    distancias, predecessores = dijkstra(g, "A")
    
    assert distancias["A"] == 0.0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1.0, "Distância de A para B deve ser 1"
    assert distancias["C"] == 3.0, "Distância de A para C deve ser 3"
    
    print("✓ Distâncias corretas")
    print(f"  A: {distancias['A']}, B: {distancias['B']}, C: {distancias['C']}")


def test_dijkstra_caminho_mais_curto():
    print("\n=== Teste 2: Dijkstra Caminho Mais Curto ===")
    
    g = Graph()
    g.add_edge("A", "B", 5.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("C", "D", 1.0)
    g.add_edge("D", "B", 1.0)
    
    distancias, predecessores = dijkstra(g, "A")
    
    assert distancias["B"] == 3.0, "Caminho mais curto A→C→D→B deve ter peso 3"
    assert distancias["B"] < 5.0, "Deve escolher caminho de peso 3, não 5"
    
    caminho = reconstruir_caminho(predecessores, "B")
    assert caminho == ["A", "C", "D", "B"], "Caminho deve ser A→C→D→B"
    
    print("✓ Caminho mais curto encontrado")
    print(f"  Distância: {distancias['B']}")
    print(f"  Caminho: {' → '.join(caminho)}")


def test_dijkstra_no_isolado():
    print("\n=== Teste 3: Dijkstra Nó Isolado ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_node("C")
    
    distancias, predecessores = dijkstra(g, "A")
    
    assert distancias["A"] == 0.0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1.0, "Distância de A para B deve ser 1"
    assert distancias["C"] == float('inf'), "Distância para nó isolado deve ser infinita"
    
    print("✓ Nó isolado tratado corretamente")
    print(f"  C está isolado: distância = {distancias['C']}")


def test_dijkstra_pesos_diferentes():
    print("\n=== Teste 4: Dijkstra Pesos Diferentes ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 4.0)
    g.add_edge("B", "D", 2.0)
    g.add_edge("C", "D", 1.0)
    
    distancias, predecessores = dijkstra(g, "A")
    
    assert distancias["D"] == 3.0, "Caminho mais curto A→B→D deve ter peso 3"
    
    caminho = reconstruir_caminho(predecessores, "D")
    assert caminho == ["A", "B", "D"], "Caminho deve ser A→B→D"
    
    print("✓ Pesos diferentes processados corretamente")
    print(f"  Distância para D: {distancias['D']}")
    print(f"  Caminho: {' → '.join(caminho)}")


def test_dijkstra_grafo_completo():
    print("\n=== Teste 5: Dijkstra Grafo Completo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "C", 3.0)
    
    distancias, predecessores = dijkstra(g, "A")
    
    assert distancias["C"] == 3.0, "Distância para C deve ser 3"
    
    # Há dois caminhos: A→C (peso 3) e A→B→C (peso 3)
    # Ambos são válidos
    caminho = reconstruir_caminho(predecessores, "C")
    custo_caminho = sum([1.0 if i == 0 else 2.0 for i in range(len(caminho) - 1)])
    
    print("✓ Grafo completo processado")
    print(f"  Distância: {distancias['C']}")
    print(f"  Caminho: {' → '.join(caminho)}")


def test_dijkstra_reconstruir_caminho():
    print("\n=== Teste 6: Dijkstra Reconstruir Caminho ===")
    
    # Cria grafo linear: A -1- B -1- C -1- D
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "D", 1.0)
    
    distancias, predecessores = dijkstra(g, "A")
    
    caminho = reconstruir_caminho(predecessores, "D")
    
    assert caminho == ["A", "B", "C", "D"], "Caminho deve ser A→B→C→D"
    assert len(caminho) == 4, "Caminho deve ter 4 nós"
    
    print("✓ Caminho reconstruído corretamente")
    print(f"  Caminho: {' → '.join(caminho)}")


def test_dijkstra_no_inexistente():
    print("\n=== Teste 7: Dijkstra Nó Inexistente ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    
    distancias, predecessores = dijkstra(g, "Z")
    
    assert len(distancias) == 0, "Não deve retornar distâncias para nó inexistente"
    
    print("✓ Nó inexistente tratado corretamente")


def run_all_tests():
    print("=" * 70)
    print("EXECUTANDO TESTES: DIJKSTRA")
    print("=" * 70)
    
    try:
        test_dijkstra_simples()
        test_dijkstra_caminho_mais_curto()
        test_dijkstra_no_isolado()
        test_dijkstra_pesos_diferentes()
        test_dijkstra_grafo_completo()
        test_dijkstra_reconstruir_caminho()
        test_dijkstra_no_inexistente()
        
        print("\n" + "=" * 70)
        print("✓ TODOS OS TESTES DE DIJKSTRA PASSARAM!")
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
