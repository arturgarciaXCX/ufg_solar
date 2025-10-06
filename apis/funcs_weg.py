import sys
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from credenciais.gerenciador_credenciais import CREDENCIAIS_APIS

WEG_CRED = CREDENCIAIS_APIS.get('weg', {}) if CREDENCIAIS_APIS else {}
API_KEY = WEG_CRED.get('WEG_API_KEY')
API_SECRET = WEG_CRED.get('WEG_API_SECRET')
BASE_URL = WEG_CRED.get('BASE_URL')
DEFAULT_PLANT_ID = WEG_CRED.get('ID_DA_USINA')

def _consultar_medicoes_por_periodo(device_id: str, device_sn:str, date_from_iso: str, date_to_iso: str, plant_id: str) -> pd.DataFrame:
    """Função interna que faz a chamada de API para um período específico."""
    
    endpoint = f"{BASE_URL}/measurements"
    headers = {'x-api-key': API_KEY, 'x-api-secret': API_SECRET}
    params = {
        'dateFrom': date_from_iso,
        'dateTo': date_to_iso,
        'groupBy': "900000",
        'deviceId': device_id,
        'variables': "outputEnergy",
        'plantId': plant_id
    }

    try:
        print(f"Buscando dados para o dispositivo WEG: {device_id}...")
        response = requests.get(endpoint, headers=headers, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
        measurements = data.get('data', [])

        if not measurements:
            # Não imprime mais "nenhum dado", pois isso é esperado e será tratado
            return pd.DataFrame()

        df = pd.DataFrame(measurements)
        df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None) - pd.Timedelta(hours=3)
        df['fonte'] = "WEG"
        df['inversor_sn'] = device_sn
        return df

    except requests.exceptions.HTTPError as http_err:
        print(f" -> Erro HTTP: {http_err.response.status_code} - {http_err.response.text}")
    except requests.exceptions.RequestException as e:
        print(f" -> Erro de conexão: {e}")
    
    return pd.DataFrame()


def consultar_dados_historicos_weg(device_id: str, device_sn:str, start_datetime_str: str, end_datetime_str: str, plant_id: str = None) -> pd.DataFrame:
    start_dt = pd.to_datetime(start_datetime_str)
    end_dt = pd.to_datetime(end_datetime_str)
    plant_id_to_use = plant_id if plant_id else DEFAULT_PLANT_ID
    all_dfs = []

    print(f"\n--- Processando inversor WEG: {device_id} de {start_dt.date()} a {end_dt.date()} ---")
    dias_esperados = pd.date_range(start=start_dt.date(), end=end_dt.date(), freq='D')

    for dia in dias_esperados:
        start_of_day_local = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        start_of_day_utc = start_of_day_local + timedelta(hours=3)
        end_of_day_utc = start_of_day_utc + timedelta(days=1, seconds=-1)
        date_from_iso = start_of_day_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        date_to_iso = end_of_day_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        df_day = _consultar_medicoes_por_periodo(device_id, device_sn, date_from_iso, date_to_iso, plant_id_to_use)
        
        if not df_day.empty:
            all_dfs.append(df_day)
        else:
            # LÓGICA PARA ADICIONAR DIAS SEM DADOS
            print(f" -> Nenhum dado encontrado para {dia.date()}. Adicionando linha vazia.")
            linha_vazia = pd.DataFrame([{
                'time': pd.Timestamp(start_of_day_local),
                'value': None, # Deixa o valor vazio
                'fonte': 'WEG',
                'device_id': device_id,
                'inversor_sn':device_sn
            }])
            all_dfs.append(linha_vazia)

        time.sleep(0.2)
        
    if not all_dfs: return pd.DataFrame()
    
    df_final = pd.concat(all_dfs, ignore_index=True)
    return df_final.sort_values(by='time').reset_index(drop=True)