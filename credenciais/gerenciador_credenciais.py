import pandas as pd
import os

# --- CAMINHOS DAS PLANILHAS ---
CAMINHO_BASE = os.path.dirname(__file__)
CAMINHO_CREDENCIAIS_BANCOS = os.path.join(CAMINHO_BASE, 'credenciais_bancos.xlsx')
CAMINHO_CREDENCIAIS_APIS = os.path.join(CAMINHO_BASE, 'credenciais_apis.xlsx')

# --- FUNÇÃO DE CARREGAMENTO DAS PLANILHAS ---
def carregar_credenciais(caminho_arquivo: str, abas_esperadas: list) -> dict:
    credenciais = {}
    try:
        xls = pd.ExcelFile(caminho_arquivo)
        for aba in abas_esperadas:
            if aba in xls.sheet_names:
                df = pd.read_excel(xls, aba, dtype=str)
                # Pega a primeira linha de dados e converte para dicionário
                credenciais[aba] = df.to_dict(orient='records')[0]
            else:
                print(f"AVISO: A aba '{aba}' não foi encontrada em '{os.path.basename(caminho_arquivo)}'.")
        
        print(f"Credenciais carregadas de '{os.path.basename(caminho_arquivo)}'.")
        return credenciais
        
    except FileNotFoundError:
        print(f"ERRO: Arquivo de credenciais não encontrado em '{caminho_arquivo}'")
        return None
    except Exception as e:
        print(f"ERRO ao ler o arquivo de credenciais '{os.path.basename(caminho_arquivo)}': {e}")
        return None



# --- CREDENCIAIS CARREGADAS ---
CREDENCIAIS_BANCOS = carregar_credenciais(CAMINHO_CREDENCIAIS_BANCOS, abas_esperadas=['sideufg', 'supabase'])
CREDENCIAIS_APIS = carregar_credenciais(CAMINHO_CREDENCIAIS_APIS, abas_esperadas=['solis', 'weg', 'solarman'])
