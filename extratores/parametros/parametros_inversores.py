import sys
import os
import pandas as pd
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bancos import funcs_supabase


def _formatar_identificador(inversor_row: pd.Series, formato: str) -> str:
    formato_limpo = formato.replace('"', '')
    placeholders = re.findall(r"'([^']*)'", formato)
    identificador_formatado = formato_limpo
    
    for placeholder in placeholders:
        if placeholder in inversor_row and pd.notna(inversor_row[placeholder]):
            valor = str(inversor_row[placeholder])
            identificador_formatado = identificador_formatado.replace(f"'{placeholder}'", valor)
        else:
            return None
    return identificador_formatado


def obter_lista_inversores(plataforma_alvo: str) -> list:
    print(f"\nBuscando parâmetros de inversores para a plataforma: '{plataforma_alvo}'...")
    
    df_inversores = funcs_supabase.consultar_supabase(tabela='inversor')
    df_plataformas = funcs_supabase.consultar_supabase(tabela='plataformas')

    if df_inversores.empty or df_plataformas.empty:
        print("ERRO: Não foi possível obter dados das tabelas 'inversor' ou 'plataformas'.")
        return []

    info_plataforma = df_plataformas[df_plataformas['nome_plataforma'] == plataforma_alvo]
    
    if info_plataforma.empty:
        print(f"ERRO: Plataforma '{plataforma_alvo}' não encontrada.")
        return []

    id_plataforma = info_plataforma.iloc[0]['id']
    formato_api = info_plataforma.iloc[0]['formato_inversor_api']

    print(f" -> ID da Plataforma: {id_plataforma}, Formato de API: {formato_api}")

    inversores_da_plataforma = df_inversores[df_inversores['plataforma'].astype(str) == str(id_plataforma)]

    if inversores_da_plataforma.empty:
        print(f" -> Nenhum inversor encontrado para a plataforma '{plataforma_alvo}'.")
        return []
    
    # --- MUDANÇA PRINCIPAL AQUI ---
    # Em vez de uma lista de strings, criamos uma lista de dicionários
    lista_final = []
    for _, inversor_row in inversores_da_plataforma.iterrows():
        identificador_formatado = _formatar_identificador(inversor_row, formato_api)
        # Garante que temos o SN original e o ID formatado antes de adicionar
        if identificador_formatado and 'inversor_sn' in inversor_row and pd.notna(inversor_row['inversor_sn']):
            inversor_info = {
                'sn_original': inversor_row['inversor_sn'],
                'id_formatado': identificador_formatado
            }
            # Evita adicionar dicionários duplicados à lista
            if inversor_info not in lista_final:
                lista_final.append(inversor_info)

    print(f" -> {len(lista_final)} inversores únicos encontrados e formatados.")
    return lista_final


# --- BLOCO DE TESTE ATUALIZADO ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("|| INICIANDO TESTE DO GERADOR DE PARÂMETROS DE INVERSORES ||")
    print("="*50)

    plataformas_para_testar = ['WEG']
    resultados_teste = {plat: obter_lista_inversores(plat) for plat in plataformas_para_testar}

    print("\n" + "="*50)
    print("|| RESULTADOS DO TESTE (ESTRUTURA DE DICIONÁRIO) ||")
    print("="*50)
    
    for plataforma, lista_inversores in resultados_teste.items():
        print(f"\n[ Lista para '{plataforma}' ]")
        if lista_inversores:
            for inv_dict in lista_inversores:
                print(f"  - SN Original: {inv_dict['sn_original']:<20} | ID Formatado: {inv_dict['id_formatado']}")
        else:
            print("  - Lista vazia.")
            
    print("\n" + "="*50)
    print("|| FIM DO TESTE ||")
    print("="*50)