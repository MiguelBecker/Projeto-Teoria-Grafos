
import os
import sys
import json
import pandas as pd
from graphs.io import carregar_adjacencias
from graphs.algorithms import dijkstra, reconstruir_caminho

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)


def normalizar_bairro(nome):
    """Normaliza nome do bairro para busca."""
    if pd.isna(nome):
        return None
    nome = str(nome).strip().title()
    # Trata caso especial de Setúbal
    if nome.lower() in ['setúbal', 'setubal', 'boa viagem (setúbal)']:
        return 'Boa Viagem'
    return nome


def criar_enderecos_exemplo():
    """
    Cria o arquivo enderecos.csv com formato correto e exemplos.
    Conforme especificação: X, Y, bairro_X, bairro_Y
    """
    enderecos_data = [
        {
            'endereco_X': 'Rua do Futuro, 1000',
            'endereco_Y': 'Av. Boa Viagem, 500',
            'bairro_X': 'Aflitos',
            'bairro_Y': 'Boa Viagem'
        },
        {
            'endereco_X': 'Av. Caxangá, 3000',
            'endereco_Y': 'Rua da Aurora, 100',
            'bairro_X': 'Iputinga',
            'bairro_Y': 'Santo Antônio'
        },
        {
            'endereco_X': 'Estrada do Arraial, 2000',
            'endereco_Y': 'Av. Recife, 1500',
            'bairro_X': 'Casa Amarela',
            'bairro_Y': 'Recife'
        },
        {
            'endereco_X': 'Rua da Hora, 500',
            'endereco_Y': 'Av. Agamenon Magalhães, 2000',
            'bairro_X': 'Espinheiro',
            'bairro_Y': 'Campo Grande'
        },
        {
            'endereco_X': 'Av. Norte, 1000',
            'endereco_Y': 'Av. Boa Viagem (Setúbal)',
            'bairro_X': 'Nova Descoberta',
            'bairro_Y': 'Boa Viagem'
        }
    ]
    
    df = pd.DataFrame(enderecos_data)
    csv_path = os.path.join(ROOT_DIR, "data", "enderecos.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"✓ Arquivo enderecos.csv criado com {len(enderecos_data)} pares")
    return df


def calcular_distancias():
    """
    Calcula distâncias entre todos os pares de endereços usando Dijkstra.
    """
    print("=" * 70)
    print("PARTE 6: CALCULANDO DISTÂNCIAS ENTRE ENDEREÇOS")
    print("=" * 70)
    
    # Carrega o grafo com pesos calculados
    grafo = carregar_adjacencias(
        "data/bairros_unique.csv",
        "data/adjacencias_bairros.csv"
    )
    
    print(f"\n✓ Grafo carregado: {grafo.order()} bairros, {grafo.size()} conexões")
    
    # Cria/carrega endereços
    enderecos_path = os.path.join(ROOT_DIR, "data", "enderecos.csv")
    
    if not os.path.exists(enderecos_path):
        print("\n! Arquivo enderecos.csv não encontrado, criando exemplo...")
        df_enderecos = criar_enderecos_exemplo()
    else:
        df_enderecos = pd.read_csv(enderecos_path)
        print(f"\n✓ Arquivo enderecos.csv carregado: {len(df_enderecos)} pares")
        
        # Verifica se tem as colunas corretas
        colunas_esperadas = ['endereco_X', 'endereco_Y', 'bairro_X', 'bairro_Y']
        if not all(col in df_enderecos.columns for col in colunas_esperadas):
            print("! Formato incorreto, recriando arquivo...")
            df_enderecos = criar_enderecos_exemplo()
    
    # Calcula distâncias para cada par
    resultados = []
    
    for idx, row in df_enderecos.iterrows():
        bairro_origem = normalizar_bairro(row['bairro_X'])
        bairro_destino = normalizar_bairro(row['bairro_Y'])
        
        print(f"\n{idx + 1}. Calculando: {bairro_origem} → {bairro_destino}")
        
        # Verifica se os bairros existem no grafo
        if bairro_origem not in grafo.nodes():
            print(f"   ✗ Bairro de origem '{bairro_origem}' não encontrado no grafo")
            custo = None
            caminho = []
        elif bairro_destino not in grafo.nodes():
            print(f"   ✗ Bairro de destino '{bairro_destino}' não encontrado no grafo")
            custo = None
            caminho = []
        else:
            # Executa Dijkstra
            distancias, predecessores = dijkstra(grafo, bairro_origem)
            
            if bairro_destino in distancias and distancias[bairro_destino] != float('inf'):
                custo = distancias[bairro_destino]
                caminho = reconstruir_caminho(predecessores, bairro_destino)
                print(f"   ✓ Custo: {custo:.2f}")
                print(f"   ✓ Caminho ({len(caminho)} bairros): {' → '.join(caminho)}")
            else:
                print(f"   ✗ Não há caminho entre os bairros")
                custo = None
                caminho = []
        
        resultados.append({
            'endereco_X': row['endereco_X'],
            'endereco_Y': row['endereco_Y'],
            'bairro_X': bairro_origem,
            'bairro_Y': bairro_destino,
            'custo': custo,
            'caminho': ' → '.join(caminho) if caminho else 'Sem caminho'
        })
    
    # Salva resultados
    df_resultados = pd.DataFrame(resultados)
    output_csv = os.path.join(ROOT_DIR, "out", "distancias_enderecos.csv")
    df_resultados.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"\n{'=' * 70}")
    print(f"✓ Resultados salvos em: {output_csv}")
    
    return resultados, grafo


def calcular_percurso_especial(grafo):
    """
    Calcula e salva o percurso específico: Nova Descoberta → Boa Viagem (Setúbal)
    """
    print(f"\n{'=' * 70}")
    print("CALCULANDO PERCURSO ESPECIAL: Nova Descoberta → Boa Viagem (Setúbal)")
    print("=" * 70)
    
    origem = "Nova Descoberta"
    destino = "Boa Viagem"  # Setúbal é tratado como Boa Viagem
    
    # Verifica se os bairros existem
    if origem not in grafo.nodes():
        print(f"✗ Bairro '{origem}' não encontrado no grafo")
        return None
    
    if destino not in grafo.nodes():
        print(f"✗ Bairro '{destino}' não encontrado no grafo")
        return None
    
    # Executa Dijkstra
    distancias, predecessores = dijkstra(grafo, origem)
    
    if destino not in distancias or distancias[destino] == float('inf'):
        print(f"✗ Não há caminho entre {origem} e {destino}")
        return None
    
    # Reconstrói o caminho
    caminho = reconstruir_caminho(predecessores, destino)
    custo = distancias[destino]
    
    # Cria estrutura de saída
    percurso = {
        "origem": origem,
        "destino": f"{destino} (Setúbal)",
        "custo_total": round(custo, 2),
        "numero_bairros": len(caminho),
        "caminho": caminho,
        "detalhes_percurso": []
    }
    
    # Adiciona detalhes de cada trecho
    for i in range(len(caminho) - 1):
        atual = caminho[i]
        proximo = caminho[i + 1]
        
        # Busca peso da aresta
        peso_aresta = None
        for viz, peso, meta in grafo.neighbors(atual):
            if viz == proximo:
                peso_aresta = peso
                logradouro = meta.logradouro if meta.logradouro else "N/A"
                break
        
        percurso["detalhes_percurso"].append({
            "trecho": i + 1,
            "de": atual,
            "para": proximo,
            "logradouro": logradouro,
            "custo": round(peso_aresta, 2) if peso_aresta else None
        })
    
    # Salva JSON
    output_json = os.path.join(ROOT_DIR, "out", "percurso_nova_descoberta_setubal.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(percurso, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Percurso encontrado!")
    print(f"  Origem: {origem}")
    print(f"  Destino: {destino} (Setúbal)")
    print(f"  Custo total: {custo:.2f}")
    print(f"  Número de bairros: {len(caminho)}")
    print(f"  Caminho: {' → '.join(caminho)}")
    print(f"\n✓ Detalhes salvos em: {output_json}")
    
    return percurso


def main():
    """
    Função principal.
    """
    try:
        # Calcula todas as distâncias
        resultados, grafo = calcular_distancias()
        
        # Calcula percurso especial
        percurso = calcular_percurso_especial(grafo)
        
        # Resumo final
        print(f"\n{'=' * 70}")
        print("RESUMO DA OPERAÇÃO")
        print("=" * 70)
        print(f"Total de pares calculados: {len(resultados)}")
        
        com_caminho = sum(1 for r in resultados if r['custo'] is not None)
        print(f"Pares com caminho: {com_caminho}")
        print(f"Pares sem caminho: {len(resultados) - com_caminho}")
        
        if percurso:
            print(f"\nPercurso especial (Nova Descoberta → Setúbal):")
            print(f"  Custo: {percurso['custo_total']}")
            print(f"  Bairros percorridos: {percurso['numero_bairros']}")
        
        print("\n✓ PARTE 6 CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
