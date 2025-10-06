import sys
import os
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bancos import funcs_sideufg
from extratores.parametros import parametros_datas

def executar_extracao_sideufg(caminho_saida: str):
    """
    Executa a lógica de extração do SideUFG com datas dinâmicas.
    """
    # Lógica de produção: busca os parâmetros de data dinamicamente
    parametros_completos = parametros_datas.gerar_parametros_de_data(plataformas_alvo=['SideUFG'])
    parametros_sideufg = parametros_completos.get('SideUFG', {})
    
    data_inicial = parametros_sideufg.get('data_inicio')
    data_final = parametros_sideufg.get('data_fim')

    if data_inicial and data_final:
        print(f"\nIniciando extração do SideUFG de {data_inicial} até {data_final}...")
        
        query = "SELECT * FROM public.sideufg_medicao WHERE data_medicao BETWEEN %(start_date)s AND %(end_date)s;"
        params = {'start_date': data_inicial, 'end_date': data_final}
        df_resultado = funcs_sideufg.consultar_postgresql(query, params)
        
        if not df_resultado.empty:
            df_resultado.to_csv(caminho_saida, index=False)
            print(f" -> Resultado do SideUFG salvo em: {caminho_saida}")
        else:
            print(" -> Nenhum dado encontrado para o período no SideUFG.")
    else:
        print("\nExtração SideUFG não executada: Parâmetros de data não foram gerados.")

if __name__ == "__main__":
    executar_extracao_sideufg(caminho_saida="extracao_sideufg.csv")