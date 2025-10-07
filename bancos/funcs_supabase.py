import pandas as pd
from supabase import create_client, Client
from postgrest import APIResponse # Importar para checagem de tipo
from credenciais.gerenciador_credenciais import CREDENCIAIS_BANCOS

SUPABASE_CRED = CREDENCIAIS_BANCOS.get('supabase') if CREDENCIAIS_BANCOS else None

def _criar_cliente_supabase_interno() -> Client:
    if not SUPABASE_CRED:
        print("Credenciais do Supabase não encontradas.")
        return None
    print("Criando cliente de conexão única com o Supabase...")
    return create_client(SUPABASE_CRED['url'], SUPABASE_CRED['key'])

supabase_client = _criar_cliente_supabase_interno()

def consultar_supabase(tabela: str, colunas: str = '*', filtros: dict = None) -> pd.DataFrame:
    if not supabase_client: return pd.DataFrame()
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
    if not supabase_client: return None
    try:
        query = supabase_client.table(tabela).select(coluna)
        if filtro:
            query = query.eq(filtro['col'], filtro['val'])
        response = query.order(coluna, desc=True).limit(1).execute()
        return response.data[0][coluna] if response.data else None
    except Exception as e:
        print(f"ERRO ao obter valor máximo da coluna '{coluna}': {e}")
        return None


def carregar_dados_supabase(df: pd.DataFrame, tabela: str) -> tuple[bool, str]:
    """
    Carrega (com upsert) os dados de um DataFrame para uma tabela no Supabase,
    dividindo em lotes se necessário para evitar timeouts.
    """
    if not supabase_client:
        return False, "Cliente Supabase não inicializado."
    
    if df.empty:
        return True, "DataFrame vazio, nenhuma ação de carregamento necessária."

    # Garante que colunas de data/hora sejam convertidas para string
    for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
        df[col] = df[col].astype(str)

    # --- LÓGICA DE CARREGAMENTO EM LOTES (CHUNKING) ---
    CHUNK_SIZE = 1500  # Um tamanho seguro para a maioria das APIs de banco de dados
    total_registros = len(df)
    total_processados_sucesso = 0

    try:
        # Itera sobre o DataFrame em pedaços de CHUNK_SIZE
        for i in range(0, total_registros, CHUNK_SIZE):
            lote_df = df.iloc[i:i + CHUNK_SIZE]
            registros = lote_df.to_dict(orient='records')
            
            num_lote = (i // CHUNK_SIZE) + 1
            num_total_lotes = (total_registros + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            print(f"Carregando (upsert) lote {num_lote}/{num_total_lotes} com {len(registros)} registros para a tabela '{tabela}'...")
            
            response: APIResponse = supabase_client.table(tabela).upsert(registros).execute()
            
            # Lógica de verificação de erro para cada lote
            if isinstance(response.data, list) and len(response.data) > 0:
                total_processados_sucesso += len(response.data)
            else:
                erro_msg = f"Falha no carregamento do lote {num_lote} para '{tabela}'."
                if isinstance(response.data, dict) and response.data.get('message'):
                    erro_msg += f" Detalhes: {response.data.get('message')} (Código: {response.data.get('code')})"
                elif hasattr(response, 'error') and response.error:
                    erro_msg += f" Detalhes: {response.error.message}"
                
                print(f" -> {erro_msg}")
                # Interrompe o processo no primeiro lote que falhar
                return False, erro_msg

        # Se todos os lotes foram processados com sucesso
        mensagem = f"Sucesso: {total_processados_sucesso} de {total_registros} registros processados em {num_total_lotes} lote(s) na tabela '{tabela}'."
        print(f" -> {mensagem}")
        return True, mensagem

    except Exception as e:
        erro_msg = f"Erro inesperado durante o carregamento para '{tabela}': {e}"
        print(f" -> {erro_msg}")
        return False, erro_msg