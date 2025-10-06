import pandas as pd
from supabase import create_client, Client
from credenciais.gerenciador_credenciais import CREDENCIAIS_BANCOS

SUPABASE_CRED = CREDENCIAIS_BANCOS.get('supabase') if CREDENCIAIS_BANCOS else None

def _criar_cliente_supabase_interno() -> Client:
    """Função interna para inicializar o cliente."""
    if not SUPABASE_CRED:
        print("Credenciais do Supabase não encontradas.")
        return None
    print("Criando cliente de conexão única com o Supabase...")
    return create_client(SUPABASE_CRED['url'], SUPABASE_CRED['key'])

# --- OTIMIZAÇÃO: Cliente Supabase é criado uma vez e reutilizado ---
supabase_client = _criar_cliente_supabase_interno()

def consultar_supabase(tabela: str, colunas: str = '*', filtros: dict = None) -> pd.DataFrame:
    """Executa uma consulta de leitura genérica no Supabase."""
    if not supabase_client:
        return pd.DataFrame()
    
    print(f"Executando consulta na tabela '{tabela}' do Supabase...")
    try:
        query = supabase_client.table(tabela).select(colunas)
        if filtros:
            if 'in_' in filtros:
                col, val = filtros['in_']
                query = query.in_(col, val)
        
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
            
    except Exception as exception:
        print(f"ERRO ao consultar o Supabase: {exception}")
        return pd.DataFrame()

def obter_valor_maximo_coluna(tabela: str, coluna: str, filtro: dict = None) -> str:
    """Busca o valor máximo de uma coluna específica em uma tabela do Supabase."""
    if not supabase_client:
        return None
    try:
        query = supabase_client.table(tabela).select(coluna)
        if filtro:
            query = query.eq(filtro['col'], filtro['val'])
        response = query.order(coluna, desc=True).limit(1).execute()
        return response.data[0][coluna] if response.data else None
            
    except Exception as e:
        print(f"ERRO ao obter valor máximo da coluna '{coluna}': {e}")
        return None