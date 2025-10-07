import pandas as pd
from uuid import uuid4
import numpy as np

def tratar_dados_solarman(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Tratamento para tabela completa
    df_completo = df.copy()
    df_completo = df_completo.astype(str)
    df_completo.columns = df_completo.columns.str.lower()

    condicao = (df_completo['collecttime'].str.len() == 10)
    valor_se_verdadeiro = df_completo['collecttime'] + ' 00:00:00'
    valor_se_falso = df_completo['collecttime']
    df_completo['collecttime'] = np.where(condicao, valor_se_verdadeiro, valor_se_falso)

    df_completo['id_leitura'] = df_completo['collecttime'].astype(str) + '_' + df_completo['sn'].astype(str)
    df_completo.drop_duplicates(subset='id_leitura',inplace=True)


    # Tratamento para tabela resumida (leitura)
    df_resumido = df_completo[['id_leitura', 'fonte', 'collecttime', 'total ac output power (active)', 'sn']].copy()
    df_resumido.rename(columns={
        'collecttime': 'data_hora',
        'sn': 'inversor_sn',
        'total ac output power (active)': 'energia_kw_h'
    }, inplace=True)
    
    df_resumido['energia_kw_h'].replace('nan', '0',inplace=True)
    df_resumido['energia_kw_h'] = df_resumido['energia_kw_h'].astype(str)

    return df_completo, df_resumido