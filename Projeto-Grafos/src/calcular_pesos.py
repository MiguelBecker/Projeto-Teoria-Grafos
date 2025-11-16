
import os
import sys
import pandas as pd
import json
from collections import Counter

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
os.chdir(ROOT_DIR)


PESO_TIPO_VIA = {
    'avenida': 1.0,
    'ponte': 1.5,
    'rua': 2.0,
    'viaduto': 2.5,
    'estrada': 3.0,
}

FATOR_PAVIMENTACAO = {
    'asfalto': 1.0,
    'concreto': 1.0,
    'paralelo': 1.3,      
    'paralelepípedo': 1.3,
    'escadaria': 1.5,
    'sem_pavimentacao': 2.0,
    'terra': 2.0,
}

PENALIDADE_PONTE = 0.5
PENALIDADE_VIADUTO = 0.5
PENALIDADE_SEMAFORO = 0.3


def extrair_tipo_via(logradouro):
    """
    Extrai o tipo de via do logradouro.
    Ex: "Avenida Boa Viagem" -> "avenida"
    """
    if pd.isna(logradouro):
        return 'rua'  
    
    logradouro_lower = str(logradouro).lower()
    
    for tipo in PESO_TIPO_VIA.keys():
        if tipo in logradouro_lower:
            return tipo
    
    return 'rua'  


def extrair_fator_pavimentacao(pavimentacao):
    
    if pd.isna(pavimentacao):
        return 1.0  
    
    pav_str = str(pavimentacao).lower().strip()
    
    codigo_para_nome = {
        '0': 'sem_pavimentacao',
        '1': 'asfalto',
        '2': 'concreto',
        '3': 'paralelo',
        '4': 'escadaria',
    }
    
    if pav_str in codigo_para_nome:
        pav_str = codigo_para_nome[pav_str]
    
    if pav_str in FATOR_PAVIMENTACAO:
        return FATOR_PAVIMENTACAO[pav_str]
    
    for key, fator in FATOR_PAVIMENTACAO.items():
        if key in pav_str:
            return fator
    
    return 1.0 


def calcular_penalidades(logradouro, tipo_via):
    penalidade = 0.0
    
    if pd.isna(logradouro):
        return penalidade
    
    logradouro_lower = str(logradouro).lower()
    
    if tipo_via == 'ponte' or 'ponte' in logradouro_lower:
        penalidade += PENALIDADE_PONTE
    
    if tipo_via == 'viaduto' or 'viaduto' in logradouro_lower:
        penalidade += PENALIDADE_VIADUTO
    
    grandes_avenidas = [
        'boa viagem', 'caxangá', 'recife', 'dantas barreto',
        'agamenon magalhães', 'norte', 'sul', 'visconde de suassuna'
    ]
    
    if tipo_via == 'avenida':
        for av in grandes_avenidas:
            if av in logradouro_lower:
                penalidade += PENALIDADE_SEMAFORO
                break
    
    return penalidade


def calcular_peso(logradouro, pavimentacao):
    tipo_via = extrair_tipo_via(logradouro)
    peso_base = PESO_TIPO_VIA[tipo_via]
    fator_pav = extrair_fator_pavimentacao(pavimentacao)
    penalidades = calcular_penalidades(logradouro, tipo_via)
    
    peso_final = (peso_base * fator_pav) + penalidades

    return round(peso_final, 2), tipo_via


def processar_adjacencias():
    
    csv_path = os.path.join(ROOT_DIR, "data", "adjacencias_bairros.csv")
    csv_output = os.path.join(ROOT_DIR, "out", "adjacencias_bairros_com_pesos.csv")
    
    print("=" * 70)
    print("PARTE 5: CALCULANDO PESOS DAS ARESTAS")
    print("=" * 70)
    
    df = pd.read_csv(csv_path)
    print(f"\n✓ Lido CSV com {len(df)} arestas")
    print(f"  Colunas: {df.columns.tolist()}")
    
    if 'observacao' not in df.columns:
        df['observacao'] = ''
    
    if 'peso' in df.columns and df['peso'].notna().all():
        print("\nOs pesos já foram calculados anteriormente!")
        print("   Extraindo apenas tipo de via para estatísticas...")
        
        tipos_via = [extrair_tipo_via(log) for log in df['logradouro']]
        df['tipo_via'] = tipos_via
        
        colunas_finais = ['bairro_origem', 'bairro_destino', 'logradouro', 
                         'observacao', 'tipo_via', 'peso']
        colunas_finais = [col for col in colunas_finais if col in df.columns]
        df = df[colunas_finais]
        
        return df
    
    novos_pesos = []
    tipos_via = []
    detalhes_calculo = []
    
    pavimentacao_default = '1'
    
    for idx, row in df.iterrows():
        pav = row.get('pavimentacao', pavimentacao_default)
        peso, tipo = calcular_peso(row['logradouro'], pav)
        novos_pesos.append(peso)
        tipos_via.append(tipo)
        
        if idx < 5:
            detalhes_calculo.append({
                'origem': row['bairro_origem'],
                'destino': row['bairro_destino'],
                'logradouro': row['logradouro'],
                'tipo_via': tipo,
                'pavimentacao': row.get('pavimentacao', 'asfalto'),
                'peso_calculado': peso
            })
    
    df['peso'] = novos_pesos
    df['tipo_via'] = tipos_via  
    
    if 'pavimentacao' in df.columns:
        colunas_ordenadas = ['bairro_origem', 'bairro_destino', 'logradouro', 
                             'pavimentacao', 'tipo_via', 'observacao', 'peso']
    else:
        colunas_ordenadas = ['bairro_origem', 'bairro_destino', 'logradouro', 
                             'tipo_via', 'observacao', 'peso']
    
    colunas_finais = [col for col in colunas_ordenadas if col in df.columns]
    df = df[colunas_finais]
    
    try:
        import csv as csv_module
        with open(csv_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv_module.writer(f)
            writer.writerow(df.columns.tolist())
            for _, row in df.iterrows():
                writer.writerow(row.tolist())
        print(f"\n✓ CSV com pesos calculados salvo em: {csv_output}")
    except Exception as e:
        print(f"\n✗ Erro ao salvar CSV: {e}")
        print("Tentando método alternativo...")
        df.to_csv(csv_output, index=False)
        print(f"✓ CSV salvo com método alternativo")
    print(f"\nExemplos de cálculo:")
    for det in detalhes_calculo[:3]:
        print(f"  {det['origem']} → {det['destino']}")
        print(f"    Via: {det['logradouro']} (tipo: {det['tipo_via']})")
        print(f"    Peso calculado: {det['peso_calculado']}")
    
    return df


def gerar_estatisticas(df):
    
    stats = {
        "total_arestas": int(len(df)),
        "peso_minimo": float(df['peso'].min()),
        "peso_maximo": float(df['peso'].max()),
        "peso_medio": float(round(df['peso'].mean(), 2)),
        "peso_mediano": float(round(df['peso'].median(), 2)),
        "distribuicao_tipos_via": dict(Counter(df['tipo_via'])),
        "distribuicao_pesos": {
            "0.0-1.0": int(len(df[df['peso'] <= 1.0])),
            "1.0-2.0": int(len(df[(df['peso'] > 1.0) & (df['peso'] <= 2.0)])),
            "2.0-3.0": int(len(df[(df['peso'] > 2.0) & (df['peso'] <= 3.0)])),
            "3.0-4.0": int(len(df[(df['peso'] > 3.0) & (df['peso'] <= 4.0)])),
            "4.0+": int(len(df[df['peso'] > 4.0])),
        },
        "exemplos": []
    }
    
    for tipo in df['tipo_via'].unique():
        exemplo = df[df['tipo_via'] == tipo].iloc[0]
        stats['exemplos'].append({
            "tipo_via": tipo,
            "origem": exemplo['bairro_origem'],
            "destino": exemplo['bairro_destino'],
            "logradouro": exemplo['logradouro'],
            "peso": float(exemplo['peso'])
        })
    stats_path = os.path.join(ROOT_DIR, "out", "analise_pesos.json")
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Estatísticas salvas em: {stats_path}")
    
    return stats


def main():
    try:
        df = processar_adjacencias()
        
        stats = gerar_estatisticas(df)
        
        print("\n" + "=" * 70)
        print("RESUMO DA OPERAÇÃO")
        print("=" * 70)
        print(f"Total de arestas processadas: {stats['total_arestas']}")
        print(f"Peso mínimo: {stats['peso_minimo']}")
        print(f"Peso máximo: {stats['peso_maximo']}")
        print(f"Peso médio: {stats['peso_medio']}")
        print(f"\nDistribuição por tipo de via:")
        for tipo, count in stats['distribuicao_tipos_via'].items():
            print(f"  {tipo.capitalize()}: {count}")
        print("\n SUCESSO!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
