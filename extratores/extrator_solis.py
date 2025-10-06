import sys
import os
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis import funcs_solis
from extratores.parametros import parametros_datas
# Importa o novo módulo de tratamento específico da Solis
from extratores.tratamento import tratamento_solis

def executar_extracao_solis(caminho_saida_completo: str, caminho_saida_resumido: str):
    """
    Executa a lógica de extração da Solis, aplica os tratamentos
    e salva os resultados em arquivos CSV separados.
    """
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

            # Salva o resultado COMPLETO
            if not df_completo.empty:
                print("\n--- AMOSTRA DO RESULTADO COMPLETO (SOLIS) ---")
                print(df_completo.head())
                df_completo.to_csv(caminho_saida_completo, index=False)
                print(f" -> Resultado completo salvo em: {caminho_saida_completo}")
            
            # Salva o resultado RESUMIDO
            if not df_resumido.empty:
                print("\n--- AMOSTRA DO RESULTADO RESUMIDO (SOLIS) ---")
                print(df_resumido.head())
                df_resumido.to_csv(caminho_saida_resumido, index=False)
                print(f" -> Resultado resumido salvo em: {caminho_saida_resumido}")
        else:
            print("\nExtração concluída, mas nenhum dado foi retornado para os inversores da Solis.")
    else:
        print("\nExtração Solis não executada: Nenhum parâmetro para 'Solis' foi encontrado.")

if __name__ == "__main__":
    # O bloco de teste agora passa os dois caminhos de saída
    executar_extracao_solis(
        caminho_saida_completo="extracao_solis_completo.csv",
        caminho_saida_resumido="extracao_solis_resumido.csv"
    )