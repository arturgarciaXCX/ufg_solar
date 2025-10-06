import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bancos import funcs_supabase
from extratores.parametros import parametros_inversores

def _formatar_data(dt_obj: datetime, formato_api: str) -> str:
    mapeamento_formatos = {'YYYY': '%Y', 'MM': '%m', 'DD': '%d', 'HH': '%H', 'mm': '%M', 'SS': '%S'}
    formato_python = formato_api
    for codigo_api, codigo_py in mapeamento_formatos.items():
        formato_python = formato_python.replace(codigo_api, codigo_py)
    return dt_obj.strftime(formato_python)

def gerar_parametros_de_data(plataformas_alvo: list) -> dict:
    """
    Gera parâmetros de data_inicio e data_fim de forma direcionada,
    preservando o sn_original e o id_formatado (inversor).
    """
    parametros_finais = {}
    agora = datetime.now()
    data_padrao = datetime(2023, 1, 1, 0, 0, 0)
    
    df_plataformas = funcs_supabase.consultar_supabase(tabela='plataformas')
    if df_plataformas.empty: return {}

    for plataforma in plataformas_alvo:
        if plataforma == 'SideUFG':
            print("\nProcessando datas para a plataforma: 'SideUFG'...")
            ultima_medicao = funcs_supabase.obter_valor_maximo_coluna(tabela='medicao', coluna='data_medicao')
            data_inicio_obj = pd.to_datetime(ultima_medicao) if ultima_medicao else data_padrao
            formato_padrao = "%Y-%m-%d %H:%M:%S"
            parametros_finais['SideUFG'] = {
                'data_inicio': data_inicio_obj.strftime(formato_padrao),
                'data_fim': agora.strftime(formato_padrao)
            }
        else:
            print(f"\nProcessando datas para a plataforma: '{plataforma}'...")
            lista_info_inversores = parametros_inversores.obter_lista_inversores(plataforma)
            
            info_plataforma = df_plataformas[df_plataformas['nome_plataforma'] == plataforma]
            if info_plataforma.empty: continue
            
            formato_data = info_plataforma.iloc[0]['formato_data_hora_api']
            parametros_plataforma = []
            
            for inv_info in lista_info_inversores:
                ultima_leitura = funcs_supabase.obter_valor_maximo_coluna(
                    tabela='leitura', coluna='data_hora', filtro={'col': 'inversor_sn', 'val': inv_info['sn_original']}
                )
                data_inicio_obj = pd.to_datetime(ultima_leitura) if ultima_leitura else data_padrao
                data_fim_obj = agora

                if plataforma == 'Solis':
                    print(" -> Aplicando ajuste de fuso horário de +3h para a Solis.")
                    data_inicio_obj += timedelta(hours=3)
                    data_fim_obj += timedelta(hours=3)

                # ALTERAÇÃO CRÍTICA AQUI: Adicionamos 'sn_original' ao dicionário final
                parametros_plataforma.append({
                    'inversor': inv_info['id_formatado'],
                    'sn_original': inv_info['sn_original'],
                    'data_inicio': _formatar_data(data_inicio_obj, formato_data),
                    'data_fim': _formatar_data(data_fim_obj, formato_data)
                })
            parametros_finais[plataforma] = parametros_plataforma
            
    return parametros_finais


# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    print("\n" + "="*60)
    print("|| INICIANDO TESTE COMBINADO DE PARÂMETROS ||")
    print("="*60)

    # Pode testar uma ou mais plataformas
    plataformas_api = ['Solis', 'WEG', 'Solarman']
    
    parametros_completos = gerar_parametros_de_data(plataformas_api)

    print("\n" + "="*60)
    print("|| RESULTADO FINAL - PARÂMETROS COMPLETOS ||")
    print("="*60)

    for plataforma, parametros in parametros_completos.items():
        print(f"\n[ Plataforma: {plataforma} ]")
        if isinstance(parametros, list):
            if not parametros:
                print("  - Nenhum parâmetro de inversor encontrado.")
            for p in parametros:
                print(f"  - Inversor (Número de Série): {p['sn_original']}")
                print(f"  - Inversor (Formatado): {p['inversor']}")
                print(f"    - Data Início:        {p['data_inicio']}")
                print(f"    - Data Fim:           {p['data_fim']}")
        elif isinstance(parametros, dict):
            print(f"  - Data Início: {parametros['data_inicio']}")
            print(f"  - Data Fim:    {parametros['data_fim']}")

    print("\n" + "="*60)
    print("|| FIM DO TESTE ||")
    print("="*60)