import sys
import os
import pandas as pd
import requests
import time

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from credenciais.gerenciador_credenciais import CREDENCIAIS_APIS

SOLARMAN_CRED = CREDENCIAIS_APIS.get('solarman', {}) if CREDENCIAIS_APIS else {}

class SolarmanAPI:
    def __init__(self):
        self._config = SOLARMAN_CRED
        self._token_type = "bearer"
        self._base_url = self._config.get('BASE_URL')

    def _get_new_token(self):
        print("Token expirado ou ausente. Solicitando um novo...")
        endpoint = f"{self._base_url}/account/v1.0/token"
        headers = {'Content-Type': 'application/json'}
        params = {'appId': self._config['SOLARMAN_APP_ID']}
        body = {
            "appSecret": self._config['SOLARMAN_APP_SECRET'],
            "password": self._config['SOLARMAN_PASSWORD_HASH'],
        }
        body[self._config['SOLARMAN_LOGIN_TYPE']] = self._config['SOLARMAN_LOGIN_VALUE']

        try:
            response = requests.post(endpoint, headers=headers, params=params, json=body, timeout=20)
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                self._config['ACCESS_TOKEN'] = data.get('access_token')
                self._config['EXPIRES_IN_SECONDS'] = data.get('expires_in')
                self._config['TOKEN_OBTAINED_AT_TIMESTAMP'] = int(time.time())
                print(" -> Novo token obtido com sucesso.")
                return True
            print(f" -> FALHA AO OBTER TOKEN: {data.get('msg')}")
            return False
        except requests.exceptions.RequestException as e:
            print(f" -> ERRO DE CONEXÃO AO OBTER TOKEN: {e}")
            return False

    def _ensure_token(self):
        expires_at = int(self._config.get('TOKEN_OBTAINED_AT_TIMESTAMP', 0)) + int(self._config.get('EXPIRES_IN_SECONDS', 0))
        if time.time() > expires_at - 300:
            return self._get_new_token()
        print("Token existente é válido.")
        return True

    def get_device_historical_data(self, device_sn, start_date, end_date):
        if not self._ensure_token():
            return pd.DataFrame()

        endpoint = f"{self._base_url}/device/v1.0/historical"
        headers = {'Authorization': f"{self._token_type} {self._config['ACCESS_TOKEN']}"}
        body = {"deviceSn": device_sn, "startTime": start_date, "endTime": end_date, "timeType": 1}

        try:
            print(f" -> Buscando dados para o SN {device_sn} em {start_date}...")
            response = requests.post(endpoint, headers=headers, json=body, timeout=120)
            response.raise_for_status()
            data = response.json()

            if not data.get('success'):
                print(f"  -> A API retornou um erro: {data.get('msg')}")
                return pd.DataFrame()

            param_data_list = data.get('paramDataList', [])
            if not param_data_list:
                return pd.DataFrame()

            processed_rows = [
                {
                    'collectTime': pd.to_datetime(tp.get('collectTime'), unit='s') - pd.Timedelta(hours=3),
                    **{item.get('name'): item.get('value') for item in tp.get('dataList', [])}
                }
                for tp in param_data_list
            ]
            df = pd.DataFrame(processed_rows)
            df['fonte'] = "Solarman"
            return df
        except Exception as e:
            print(f"  -> Erro ao buscar dados históricos: {e}")
            return pd.DataFrame()
    
    def get_historical_data_for_range(self, device_sn: str, start_datetime_str: str, end_datetime_str: str) -> pd.DataFrame:
        start_dt = pd.to_datetime(start_datetime_str)
        end_dt = pd.to_datetime(end_datetime_str)
        all_dfs = []
        
        print(f"\n--- Processando inversor Solarman: {device_sn} de {start_dt.date()} a {end_dt.date()} ---")
        dias_esperados = pd.date_range(start=start_dt.date(), end=end_dt.date(), freq='D')

        for dia in dias_esperados:
            day_str = dia.strftime('%Y-%m-%d')
            df_day = self.get_device_historical_data(device_sn, day_str, day_str)
            
            if not df_day.empty:
                all_dfs.append(df_day)
            else:
                # LÓGICA PARA ADICIONAR DIAS SEM DADOS
                print(f" -> Nenhum dado encontrado para {day_str}. Adicionando linha vazia.")
                linha_vazia = pd.DataFrame([{
                    'collectTime': pd.Timestamp(dia),
                    'SN': device_sn,
                    'fonte': 'Solarman'
                }])
                all_dfs.append(linha_vazia)

            time.sleep(0.2)
            
        if not all_dfs: return pd.DataFrame()

        df_final = pd.concat(all_dfs, ignore_index=True)
        return df_final.sort_values(by='collectTime').reset_index(drop=True)