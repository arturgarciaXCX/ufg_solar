import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis import funcs_weg
from extratores.parametros import parametros_datas
from extratores.tratamento import tratamento_weg



def executar_extracao_weg(caminho_saida_completo: str, caminho_saida_resumido: str):
    parametros_completos = parametros_datas.gerar_parametros_de_data(plataformas_alvo=['WEG'])
    parametros_weg = parametros_completos.get('WEG', [])

    if parametros_weg:
        todos_os_dados = []
        print(f"\nIniciando extração para {len(parametros_weg)} inversor(es) da WEG...")

        for params_inversor in parametros_weg:
            df_inversor = funcs_weg.consultar_dados_historicos_weg(
                device_id=params_inversor['inversor'],
                device_sn=params_inversor['sn_original'],
                start_datetime_str=params_inversor['data_inicio'],
                end_datetime_str=params_inversor['data_fim']
            )
            if not df_inversor.empty:
                if 'device_id' not in df_inversor.columns:
                    df_inversor['device_id'] = params_inversor['inversor']
                todos_os_dados.append(df_inversor)

        if todos_os_dados:
            df_bruto = pd.concat(todos_os_dados, ignore_index=True)
            
            # ALTERAÇÃO AQUI: Passa a lista de parâmetros para a função de tratamento
            df_completo, df_resumido = tratamento_weg.tratar_dados_weg(df_bruto, parametros_weg)

            if not df_completo.empty:
                print("\n--- AMOSTRA DO RESULTADO COMPLETO (WEG) ---")
                print(df_completo.head())
                df_completo.to_csv(caminho_saida_completo, index=False)
                print(f" -> Resultado completo salvo em: {caminho_saida_completo}")

            if not df_resumido.empty:
                print("\n--- AMOSTRA DO RESULTADO RESUMIDO (WEG) ---")
                print(df_resumido.head())
                df_resumido.to_csv(caminho_saida_resumido, index=False)
                print(f" -> Resultado resumido salvo em: {caminho_saida_resumido}")
        else:
            print("\nExtração concluída, mas nenhum dado foi retornado para os inversores da WEG.")
    else:
        print("\nExtração WEG não executada: Nenhum parâmetro para 'WEG' foi encontrado.")

if __name__ == "__main__":
    executar_extracao_weg(
        caminho_saida_completo="extracao_weg_completo.csv",
        caminho_saida_resumido="extracao_weg_resumido.csv"
    )