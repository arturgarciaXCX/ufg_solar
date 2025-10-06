import pandas as pd
from uuid import uuid4

def tratar_dados_solis(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Tratamento para tabela completa
    df_completo = df.copy()
    df_completo = df_completo.astype(str)
    df_completo.columns = df_completo.columns.str.lower()


    df_completo['datatimestamp'] = pd.to_datetime(df_completo['datatimestamp'], unit='ms') \
                                .dt.tz_localize('UTC') \
                                .dt.tz_convert('America/Sao_Paulo') \
                                .dt.strftime('%Y-%m-%d %H:%M:%S').astype(str)
    
    df_completo['id_leitura'] = df_completo['datatimestamp'].astype(str) + '_' + df_completo['inverter_identifier'].astype(str)


    
    df_resumido = df_completo[['id_leitura', 'fonte', 'datatimestamp', 'pac', 'inverter_identifier']].copy()
    df_resumido.rename(columns={
        'datatimestamp': 'data_hora',
        'inverter_identifier': 'inversor_sn',
        'pac':'energia_kw_h'
    }, inplace=True)

    df_resumido['energia_kw_h'].replace('nan', '0', inplace=True)
    df_resumido['energia_kw_h'] = df_resumido['energia_kw_h'].astype(str)
    
    return df_completo, df_resumido