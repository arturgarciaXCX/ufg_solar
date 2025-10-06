import pandas as pd
from uuid import uuid4
import numpy as np

def tratar_dados_weg(df: pd.DataFrame, parametros_weg: list):

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # --- Tratamento para tabela completa ---
    df_completo = df.copy()


    
    # if 'device_id' in df_completo.columns:
    #     df_completo = df_completo.drop(columns=['device_id'])
    
    df_completo = df_completo.astype(str)
    df_completo.columns = df_completo.columns.str.lower()
    df_completo = df_completo.dropna()

    condicao = (df_completo['time'].str.len() == 10)
    valor_se_verdadeiro = df_completo['time'] + ' 00:00:00'
    valor_se_falso = df_completo['time']
    df_completo['time'] = np.where(condicao, valor_se_verdadeiro, valor_se_falso)

    df_completo['id_leitura'] = df_completo['time'].astype(str) + '_' + df_completo['device_id'].astype(str)

    # --- Tratamento para tabela resumida (leitura) ---
    df_resumido = df_completo[['id_leitura', 'fonte', 'time', 'value', 'inversor_sn']]
    df_resumido.rename(columns={'time': 'data_hora', 'value': 'energia_kw_h'}, inplace=True)

    df_resumido['energia_kw_h'].replace('nan','0', inplace=True)
    df_resumido['energia_kw_h'] = pd.to_numeric(df_resumido['energia_kw_h'], errors='coerce') / 1000
    df_resumido['energia_kw_h'] = df_resumido['energia_kw_h'].astype(str)

    return df_completo, df_resumido