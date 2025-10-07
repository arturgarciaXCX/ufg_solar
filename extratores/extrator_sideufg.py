import sys, os, pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa as funções de ambos os bancos de dados
from bancos import funcs_sideufg, funcs_supabase
from extratores.parametros import parametros_datas


def executar_extracao_sideufg():
    params_completos = parametros_datas.gerar_parametros_de_data(plataformas_alvo=['SideUFG'])
    params_sideufg = params_completos.get('SideUFG', {})
    data_inicial = params_sideufg.get('data_inicio')
    data_final = params_sideufg.get('data_fim')

    if not (data_inicial and data_final):
        print("\nExtração SideUFG não executada: Parâmetros de data não gerados.")
        return None
        
    print(f"\nIniciando extração do SideUFG de {data_inicial} até {data_final}...")
    
    # --- MUDANÇA 1: Busca o mapeamento de medidores do Supabase ---
    print(" -> Buscando mapeamento de medidores do Supabase...")
    df_medidores_map = funcs_supabase.consultar_supabase(tabela='medidor', colunas='id,medidor')
    
    if df_medidores_map.empty:
        print(" -> ERRO: Não foi possível obter o mapeamento de medidores do Supabase. Abortando extração.")
        return None
        
    # Cria um dicionário para o mapeamento: {'valor_antigo': 'valor_novo'}
    mapeamento_medidor_para_id = pd.Series(df_medidores_map.id.values, index=df_medidores_map.medidor.astype(str)).to_dict()

    # Extrai os dados brutos do SideUFG
    query = "SELECT * FROM public.sideufg_medicao WHERE data_medicao BETWEEN %(start_date)s AND %(end_date)s;"
    params = {'start_date': data_inicial, 'end_date': data_final}
    df_resultado = funcs_sideufg.consultar_postgresql(query, params)
    
    if df_resultado.empty:
        print(" -> Nenhum dado encontrado para o período no SideUFG.")
        return None
    
    # --- Aplica o mapeamento na coluna 'medidor_id' ---
    print(f" -> {len(df_resultado)} registros brutos encontrados. Mapeando 'medidor_id'...")
    df_resultado['medidor_id'] = df_resultado['medidor_id'].astype(str).map(mapeamento_medidor_para_id)
    df_resultado['medidor_id'].replace(".0","",inplace=True)
    df_resultado['medidor_id'] = df_resultado['medidor_id'].astype(str)
    df_resultado = df_resultado[df_resultado['medidor_id'] != "nan"]
    # df_resultado = df_resultado.dropna(subset=['medidor_id'])
    print(" -> Mapeamento concluído.")


    return df_resultado

if __name__ == "__main__":
    df_final = executar_extracao_sideufg()
    if df_final is not None:
        print("\n--- AMOSTRA DO RESULTADO FINAL (SIDEUFG) ---")
        print(df_final.head())