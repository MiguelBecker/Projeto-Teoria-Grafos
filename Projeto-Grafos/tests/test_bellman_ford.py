import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.graph import Graph, EdgeMeta
from graphs.algorithms import bellman_ford, reconstruir_caminho


def test_bellman_ford_simples():
    print("\n=== Teste 1: Bellman-Ford Simples ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Não deve ter ciclo negativo"
    assert distancias["A"] == 0.0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1.0, "Distância de A para B deve ser 1"
    assert distancias["C"] == 3.0, "Distância de A para C deve ser 3"
    
    print("✓ Distâncias corretas")
    print(f"  A: {distancias['A']}, B: {distancias['B']}, C: {distancias['C']}")
    print(f"  Ciclo negativo: {tem_ciclo_neg}")


def test_bellman_ford_pesos_positivos():
    print("\n=== Teste 2: Bellman-Ford Pesos Positivos ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 4.0)
    g.add_edge("B", "D", 2.0)
    g.add_edge("C", "D", 1.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Não deve ter ciclo negativo"
    assert distancias["D"] == 3.0, "Caminho mais curto A→B→D deve ter peso 3"
    
    caminho = reconstruir_caminho(predecessores, "D")
    assert caminho == ["A", "B", "D"], "Caminho deve ser A→B→D"
    
    print("✓ Caminho mais curto encontrado")
    print(f"  Distância para D: {distancias['D']}")
    print(f"  Caminho: {' → '.join(caminho)}")


def test_bellman_ford_no_isolado():
    print("\n=== Teste 3: Bellman-Ford Nó Isolado ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_node("C")
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Não deve ter ciclo negativo"
    assert distancias["C"] == float('inf'), "Distância para nó isolado deve ser infinita"
    
    print("✓ Nó isolado tratado corretamente")
    print(f"  C está isolado: distância = {distancias['C']}")


def test_bellman_ford_ciclo_positivo():
    print("\n=== Teste 4: Bellman-Ford Ciclo Positivo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "A", 1.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Ciclo positivo não deve ser detectado como negativo"
    assert distancias["A"] == 0.0, "Distância de A para A deve ser 0"
    assert distancias["B"] == 1.0, "Distância de A para B deve ser 1"
    assert distancias["C"] == 1.0, "Distância de A para C deve ser 1 (direto)"
    
    print("✓ Ciclo positivo tratado corretamente")
    print(f"  Distâncias: A={distancias['A']}, B={distancias['B']}, C={distancias['C']}")


def test_bellman_ford_grafo_completo():
    print("\n=== Teste 5: Bellman-Ford Grafo Completo ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "C", 3.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Não deve ter ciclo negativo"
    assert distancias["C"] == 3.0, "Distância para C deve ser 3"
    
    print("✓ Grafo completo processado")
    print(f"  Distância para C: {distancias['C']}")


def test_bellman_ford_no_inexistente():
    print("\n=== Teste 6: Bellman-Ford Nó Inexistente ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "Z")
    
    assert len(distancias) == 0, "Não deve retornar distâncias para nó inexistente"
    assert not tem_ciclo_neg, "Não deve detectar ciclo para nó inexistente"
    
    print("✓ Nó inexistente tratado corretamente")


def test_bellman_ford_caminho_linear():
    print("\n=== Teste 7: Bellman-Ford Caminho Linear ===")
    
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("C", "D", 3.0)
    
    distancias, predecessores, tem_ciclo_neg = bellman_ford(g, "A")
    
    assert not tem_ciclo_neg, "Não deve ter ciclo negativo"
    assert distancias["A"] == 0.0, "Distância A→A = 0"
    assert distancias["B"] == 1.0, "Distância A→B = 1"
    assert distancias["C"] == 3.0, "Distância A→C = 3"
    assert distancias["D"] == 6.0, "Distância A→D = 6"
    
    caminho = reconstruir_caminho(predecessores, "D")
    assert caminho == ["A", "B", "C", "D"], "Caminho deve ser A→B→C→D"
    
    print("✓ Caminho linear processado corretamente")
    print(f"  Distâncias: {distancias}")


def run_all_tests():
    print("=" * 70)
    print("EXECUTANDO TESTES: BELLMAN-FORD")
    print("=" * 70)
    
    try:
        test_bellman_ford_simples()
        test_bellman_ford_pesos_positivos()
        test_bellman_ford_no_isolado()
        test_bellman_ford_ciclo_positivo()
        test_bellman_ford_grafo_completo()
        test_bellman_ford_no_inexistente()
        test_bellman_ford_caminho_linear()
        
        print("\n" + "=" * 70)
        print("✓ TODOS OS TESTES DE BELLMAN-FORD PASSARAM!")
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
