import os
import time

# Importa as funções de execução de cada extrator
from extrator_sideufg import executar_extracao_sideufg
from extrator_solis import executar_extracao_solis
from extrator_weg import executar_extracao_weg
from extrator_solarman import executar_extracao_solarman

def rodar_todas_as_extracoes():
    """
    Orquestra a execução de todos os extratores, que agora salvam
    resultados completos e resumidos.
    """
    print("="*60)
    print("|| INICIANDO PROCESSO COMPLETO DE EXTRAÇÃO E TRATAMENTO ||")
    print("="*60)
    
    # Define o caminho para a pasta de resultados
    pasta_resultados_completos = "resultados/completos"
    pasta_resultados_resumidos = "resultados/resumidos"
    
    # Cria a pasta de resultados se ela não existir
    os.makedirs(pasta_resultados_completos, exist_ok=True)
    print(f"\nOs resultados completos serão salvos na pasta: '{pasta_resultados_completos}/'")

    os.makedirs(pasta_resultados_resumidos, exist_ok=True)
    print(f"\nOs resultados completos serão salvos na pasta: '{pasta_resultados_resumidos}/'")


    
    # Dicionário mapeando cada função aos seus argumentos de caminho de saída
    extracoes_a_executar = {
        # O extrator do SideUFG continua salvando um único arquivo
        executar_extracao_sideufg: {
            "caminho_saida": os.path.join(pasta_resultados_completos, "resultado_sideufg.csv")
        },
        # Os extratores de API agora recebem dois caminhos de saída
        executar_extracao_solis: {
            "caminho_saida_completo": os.path.join(pasta_resultados_completos, "resultado_solis_completo.csv"),
            "caminho_saida_resumido": os.path.join(pasta_resultados_resumidos, "resultado_solis_resumido.csv"),
        },
        executar_extracao_weg: {
            "caminho_saida_completo": os.path.join(pasta_resultados_completos, "resultado_weg_completo.csv"),
            "caminho_saida_resumido": os.path.join(pasta_resultados_resumidos, "resultado_weg_resumido.csv"),
        },
        executar_extracao_solarman: {
            "caminho_saida_completo": os.path.join(pasta_resultados_completos, "resultado_solarman_completo.csv"),
            "caminho_saida_resumido": os.path.join(pasta_resultados_resumidos, "resultado_solarman_resumido.csv"),
        }
    }
    
    tempo_inicio_total = time.time()
    
    # Executa cada extração
    for funcao_extracao, kwargs in extracoes_a_executar.items():
        print("\n" + "-"*60)
        nome_extrator = funcao_extracao.__name__.replace('executar_', '').upper()
        print(f"EXECUTANDO EXTRATOR: {nome_extrator}")
        print("-"*60)
        
        tempo_inicio_extrator = time.time()
        try:
            # Chama a função de extração, passando os argumentos do dicionário
            funcao_extracao(**kwargs)
        except Exception as e:
            print(f"!!! ERRO INESPERADO AO EXECUTAR {nome_extrator}: {e} !!!")
        
        tempo_fim_extrator = time.time()
        print(f" -> Tempo de execução ({nome_extrator}): {tempo_fim_extrator - tempo_inicio_extrator:.2f} segundos.")

    tempo_fim_total = time.time()
    
    print("\n" + "="*60)
    print("|| PROCESSO DE EXTRAÇÃO E TRATAMENTO CONCLUÍDO ||")
    print(f"Tempo total de execução: {tempo_fim_total - tempo_inicio_total:.2f} segundos.")
    print("="*60)


if __name__ == "__main__":
    rodar_todas_as_extracoes()