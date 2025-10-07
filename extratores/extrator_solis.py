import sys
import os
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis import funcs_solis
from extratores.parametros import parametros_datas
# Importa o novo módulo de tratamento específico da Solis
from extratores.tratamento import tratamento_solis

def executar_extracao_solis():
    parametros_completos = parametros_datas.gerar_parametros_de_data(plataformas_alvo=['Solis'])
    parametros_solis = parametros_completos.get('Solis', [])
    
    if parametros_solis:
        todos_os_dados = []
        print(f"\nIniciando extração para {len(parametros_solis)} inversor(es) da Solis...")

        for params_inversor in parametros_solis:
            df_resultado = funcs_solis.consultar_dados_inversores_solis(
                inverter_identifiers=[params_inversor['inversor']],
                start_datetime_str=params_inversor['data_inicio'],
                end_datetime_str=params_inversor['data_fim']
            )
            if not df_resultado.empty:
                todos_os_dados.append(df_resultado)

        if todos_os_dados:
            df_bruto = pd.concat(todos_os_dados, ignore_index=True)
            
            # --- INTEGRAÇÃO DO TRATAMENTO ---
            # Chama a função de tratamento que retorna os dois DataFrames
            df_completo, df_resumido = tratamento_solis.tratar_dados_solis(df_bruto)

            if not df_completo.empty:
                print("\n--- RESULTADO COMPLETO PRONTO (SOLIS) ---")

            if not df_resumido.empty:
                print("\n--- RESULTADO RESUMIDO PRONTO (SOLARMAN) ---")

            return df_completo, df_resumido

        else:
            print("\nExtração concluída, mas nenhum dado foi retornado para os inversores da Solis.")
    else:
        print("\nExtração Solis não executada: Nenhum parâmetro para 'Solis' foi encontrado.")

if __name__ == "__main__":
    # O bloco de teste agora passa os dois caminhos de saída
    executar_extracao_solis()