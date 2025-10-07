import sys
import os
import time

# Garante que os módulos nas subpastas sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as funções de execução, carregamento e log
from extratores.extrator_sideufg import executar_extracao_sideufg
from extratores.extrator_solis import executar_extracao_solis
from extratores.extrator_weg import executar_extracao_weg
from extratores.extrator_solarman import executar_extracao_solarman
from bancos.funcs_supabase import carregar_dados_supabase
from extratores.logger import iniciar_log, logar

def main():

    iniciar_log()
    tempo_inicio_total = time.time()
    
    # Mapeamento de funções extratoras para suas tabelas de destino no Supabase
    pipelines = {
        "SideUFG": {
            "funcao": executar_extracao_sideufg,
            "tabelas": {'resumido': 'medicao'} 
        },
        "Solis": {
            "funcao": executar_extracao_solis,
            "tabelas": {'completo': 'leituras_completas_solis', 'resumido': 'leitura'}
        },
        "WEG": {
            "funcao": executar_extracao_weg,
            "tabelas": {'completo': 'leituras_completas_weg', 'resumido': 'leitura'}
        },
        "Solarman": {
            "funcao": executar_extracao_solarman,
            "tabelas": {'completo': 'leituras_completas_solarman', 'resumido': 'leitura'}
        }
    }

    for nome, pipe in pipelines.items():
        logar(f"--- Iniciando pipeline para {nome} ---")
        try:
            resultados = pipe["funcao"]()
            
            # Lida com extratores que retornam um ou dois DataFrames
            if not isinstance(resultados, tuple):
                resultados = (None, resultados) # Padroniza para (completo, resumido)
            
            df_completo, df_resumido = resultados

            # Carrega DataFrame completo, se existir
            if df_completo is not None:
                tabela_completa = pipe["tabelas"].get('completo')
                if tabela_completa:
                    sucesso, msg = carregar_dados_supabase(df_completo, tabela_completa)
                    logar(f"Resultado do carregamento {nome} (completo): {msg}")

            # Carrega DataFrame resumido, se existir
            if df_resumido is not None:
                tabela_resumida = pipe["tabelas"].get('resumido')
                if tabela_resumida:
                    sucesso, msg = carregar_dados_supabase(df_resumido, tabela_resumida)
                    logar(f"Resultado do carregamento {nome} (resumido): {msg}")

            if df_completo is None and df_resumido is None:
                logar(f"Nenhum dado retornado pela extração {nome}.")

        except Exception as e:
            logar(f"!!! ERRO CRÍTICO no pipeline de {nome}: {e} !!!")

    tempo_fim_total = time.time()
    logar(f"--- PROCESSO COMPLETO FINALIZADO. Tempo total: {tempo_fim_total - tempo_inicio_total:.2f} segundos. ---")

if __name__ == "__main__":
    main()