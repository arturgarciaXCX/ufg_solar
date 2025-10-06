import sys
import os
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.funcs_solarman import SolarmanAPI
from extratores.parametros import parametros_datas
# Importa o novo módulo de tratamento específico da Solarman
from extratores.tratamento import tratamento_solarman

def executar_extracao_solarman(caminho_saida_completo: str, caminho_saida_resumido: str):
    """
    Executa a lógica de extração da Solarman, aplica os tratamentos
    e salva os resultados em arquivos CSV separados.
    """
    parametros_completos = parametros_datas.gerar_parametros_de_data(plataformas_alvo=['Solarman'])
    parametros_solarman = parametros_completos.get('Solarman', [])

    if parametros_solarman:
        api = SolarmanAPI()
        all_records = []
        print(f"\nIniciando extração para {len(parametros_solarman)} inversor(es) da Solarman...")

        for params_inversor in parametros_solarman:
            df_inversor = api.get_historical_data_for_range(
                device_sn=params_inversor['inversor'],
                start_datetime_str=params_inversor['data_inicio'],
                end_datetime_str=params_inversor['data_fim']
            )
            if not df_inversor.empty:
                all_records.append(df_inversor)
        
        if all_records:
            df_bruto = pd.concat(all_records, ignore_index=True)
            
            # --- INTEGRAÇÃO DO TRATAMENTO ---
            df_completo, df_resumido = tratamento_solarman.tratar_dados_solarman(df_bruto)

            # Salva o resultado COMPLETO
            if not df_completo.empty:
                print("\n--- AMOSTRA DO RESULTADO COMPLETO (SOLARMAN) ---")
                print(df_completo.head())
                df_completo.to_csv(caminho_saida_completo, index=False)
                print(f" -> Resultado completo salvo em: {caminho_saida_completo}")
            
            # Salva o resultado RESUMIDO
            if not df_resumido.empty:
                print("\n--- AMOSTRA DO RESULTADO RESUMIDO (SOLARMAN) ---")
                print(df_resumido.head())
                df_resumido.to_csv(caminho_saida_resumido, index=False)
                print(f" -> Resultado resumido salvo em: {caminho_saida_resumido}")
        else:
            print("\nNenhum dado foi coletado para os inversores da Solarman.")
    else:
        print("\nExtração Solarman não executada: Nenhum parâmetro para 'Solarman' foi encontrado.")

if __name__ == "__main__":
    executar_extracao_solarman(
        caminho_saida_completo="extracao_solarman_completo.csv",
        caminho_saida_resumido="extracao_solarman_resumido.csv"
    )