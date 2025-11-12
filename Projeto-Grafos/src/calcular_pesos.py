
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
    
    novos_pesos = []
    tipos_via = []
    detalhes_calculo = []
    
    for idx, row in df.iterrows():
        peso, tipo = calcular_peso(row['logradouro'], row['pavimentacao'])
        novos_pesos.append(peso)
        tipos_via.append(tipo)
        
        if idx < 5:
            detalhes_calculo.append({
                'origem': row['bairro_origem'],
                'destino': row['bairro_destino'],
                'logradouro': row['logradouro'],
                'tipo_via': tipo,
                'pavimentacao': row['pavimentacao'],
                'peso_calculado': peso
            })
    
    df['peso'] = novos_pesos
    df['tipo_via'] = tipos_via  
    
    colunas_ordenadas = ['bairro_origem', 'bairro_destino', 'logradouro', 
                         'pavimentacao', 'tipo_via', 'observacao', 'peso']
    

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
    """
    Gera estatísticas sobre os pesos calculados.
    """
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


def gerar_documentacao():
    """
    Gera documentação detalhada sobre o sistema de pesos.
    """
    doc = """
═══════════════════════════════════════════════════════════════════════════
                    DOCUMENTAÇÃO DO SISTEMA DE PESOS
                          Parte 5 - Projeto Grafos
═══════════════════════════════════════════════════════════════════════════

1. OBJETIVO
───────────
Definir pesos para as arestas do grafo de bairros do Recife, permitindo
calcular distâncias realistas usando o algoritmo de Dijkstra.

2. FÓRMULA GERAL
────────────────
    peso_final = (peso_base_via × fator_pavimentacao) + penalidades

3. COMPONENTES DO PESO
──────────────────────

3.1. PESO BASE POR TIPO DE VIA
Quanto menor, melhor o acesso:

    Tipo          | Peso Base | Justificativa
    ──────────────┼───────────┼─────────────────────────────────────
    Avenida       |    1.0    | Via principal, maior fluxo
    Ponte         |    1.5    | Travessia especial, fluxo moderado
    Rua           |    2.0    | Via local, menor fluxo
    Viaduto       |    2.5    | Elevado, acesso restrito
    Estrada       |    3.0    | Via de menor categoria urbana

3.2. FATOR DE PAVIMENTAÇÃO (Multiplicador)
Afeta a velocidade/conforto de deslocamento:

    Pavimentação      | Fator | Código CSV | Justificativa
    ──────────────────┼───────┼────────────┼──────────────────────
    Asfalto/Concreto  |  1.0  |    1, 2    | Melhor condição
    Paralelepípedo    |  1.3  |     3      | Condição intermediária
    Escadaria         |  1.5  |     4      | Acesso difícil
    Sem pavimentação  |  2.0  |     0      | Pior condição

3.3. PENALIDADES ADICIONAIS
Somadas ao peso final:

    Condição                | Penalidade | Justificativa
    ────────────────────────┼────────────┼────────────────────────
    Travessia de ponte      |   +0.5     | Tempo extra de travessia
    Travessia de viaduto    |   +0.5     | Acesso complexo
    Semáforos (grandes av.) |   +0.3     | Tempo de espera

4. EXEMPLOS DE CÁLCULO
──────────────────────

4.1. AVENIDA BOA VIAGEM (asfalto)
    peso = (1.0 × 1.0) + 0.3 = 1.3
    (avenida principal com semáforos)

4.2. PONTE ENTRE BAIRROS (concreto)
    peso = (1.5 × 1.0) + 0.5 = 2.0
    (ponte com penalidade de travessia)

4.3. RUA LOCAL (paralelepípedo)
    peso = (2.0 × 1.3) + 0.0 = 2.6
    (rua com pavimentação intermediária)

4.4. ESTRADA SEM PAVIMENTAÇÃO
    peso = (3.0 × 2.0) + 0.0 = 6.0
    (pior caso: estrada sem asfalto)

5. INTERPRETAÇÃO DOS PESOS
───────────────────────────
- Pesos menores (1.0-2.0): Conexões rápidas e eficientes
- Pesos médios (2.0-4.0): Conexões normais
- Pesos altos (4.0+): Conexões difíceis/lentas

6. VALIDAÇÃO
────────────
✓ Todos os pesos são positivos (requisito do Dijkstra)
✓ Pesos refletem características reais das vias
✓ Sistema é extensível para futuras melhorias

7. LIMITAÇÕES E MELHORIAS FUTURAS
──────────────────────────────────
Limitações:
- Não considera distância física real (apenas topológica)
- Não considera horário de pico dinamicamente
- Semáforos inferidos heuristicamente

Melhorias possíveis:
- Integrar dados de GPS/distâncias reais
- Adicionar variação temporal (hora do dia)
- Considerar dados de trânsito em tempo real
- Adicionar preferências (carro vs. ônibus vs. caminhada)

8. REFERÊNCIAS NO CÓDIGO
─────────────────────────
Arquivo: src/calcular_pesos.py
Funções principais:
- calcular_peso(): Calcula peso de uma aresta
- extrair_tipo_via(): Identifica tipo de via
- extrair_fator_pavimentacao(): Obtém fator de pavimentação
- calcular_penalidades(): Calcula penalidades adicionais

═══════════════════════════════════════════════════════════════════════════
Gerado automaticamente pelo script src/calcular_pesos.py
═══════════════════════════════════════════════════════════════════════════
"""
    
    doc_path = os.path.join(ROOT_DIR, "out", "documentacao_pesos.txt")
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"\n✓ Documentação salva em: {doc_path}")


def main():
    try:
        df = processar_adjacencias()
        
        stats = gerar_estatisticas(df)
        
        gerar_documentacao()
        
        # Exibe resumo
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
