import pandas as pd
import psycopg2
from psycopg2 import OperationalError

# --- CREDENCIAIS ---
from credenciais.gerenciador_credenciais import CREDENCIAIS_BANCOS
DB_CONFIG = CREDENCIAIS_BANCOS['sideufg'] if CREDENCIAIS_BANCOS else None

# --- FUNÇÕES ---
def criar_conexao_psql():
    if not DB_CONFIG:
        print("Configuração do banco SideUFG não encontrada. Verifique as credenciais.")
        return None
        
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Conexão com o banco de dados PostgreSQL bem-sucedida.")
    except OperationalError as e:
        print(f"O erro '{e}' ocorreu ao tentar conectar ao PostgreSQL.")
    return conn

def consultar_postgresql(query: str, params: dict = None) -> pd.DataFrame:
    print("\nExecutando consulta no PostgreSQL...")
    conn = criar_conexao_psql()
    if conn is None:
        return pd.DataFrame()

    try:
        df = pd.read_sql_query(query, conn, params=params)
        print(f" -> {len(df)} registros encontrados.")
        return df
    except (Exception, psycopg2.Error) as error:
        print(f"Ocorreu um erro ao executar a consulta: {error}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            print("Conexão com o PostgreSQL foi fechada.")


