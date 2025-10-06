import sys
import os
import pandas as pd
# CORREÇÃO: Adicionado 'timezone' ao import
from datetime import datetime, timedelta, timezone
import json
import time
import hmac
import base64
import requests
import hashlib

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from credenciais.gerenciador_credenciais import CREDENCIAIS_APIS

SOLIS_CRED = CREDENCIAIS_APIS.get('solis', {}) if CREDENCIAIS_APIS else {}
KEY_ID = SOLIS_CRED.get('KEY_ID')
KEY_SECRET = SOLIS_CRED.get('KEY_SECRET')
BASE_URL = SOLIS_CRED.get('BASE_URL')

def _build_solis_headers(body_str: str, api_resource: str) -> dict:
    # CORREÇÃO: Usar timezone.utc em vez de datetime.UTC para compatibilidade
    now_utc = datetime.now(timezone.utc)
    
    request_date = now_utc.strftime('%a, %d %b %Y %H:%M:%S GMT')
    md5_hash = hashlib.md5(body_str.encode('utf-8')).digest()
    content_md5 = base64.b64encode(md5_hash).decode('utf-8')
    content_type_for_signing = "application/json"
    canonical_string = (
        f"POST\n{content_md5}\n{content_type_for_signing}\n{request_date}\n{api_resource}"
    )
    signature = hmac.new(
        KEY_SECRET.encode('utf-8'), canonical_string.encode('utf-8'), hashlib.sha1
    ).digest()
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    return {
        'Content-MD5': content_md5,
        'Content-Type': 'application/json;charset=UTF-8',
        'Date': request_date,
        'Authorization': f"API {KEY_ID}:{encoded_signature}"
    }

def _fetch_data_for_day(inverter_identifier: dict, day_str: str) -> list:
    api_resource = "/v1/api/inverterDay"
    endpoint = f"{BASE_URL.rstrip('/')}{api_resource}"
    print(f"Buscando dados para o dia: {day_str}...")
    body = {"money": "BRL", "time": day_str, "timeZone": 8, **inverter_identifier}
    body_json_str = json.dumps(body, sort_keys=True, separators=(',', ':'))
    try:
        headers = _build_solis_headers(body_json_str, api_resource)
        response = requests.post(endpoint, data=body_json_str, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "0":
            return data.get('data') or []
        print(f"  -> API retornou um erro: {data.get('msg')}")
        return []
    except Exception as e:
        print(f"  -> Ocorreu um erro: {e}")
        return []

def consultar_dados_inversores_solis(inverter_identifiers: list, start_datetime_str: str, end_datetime_str: str) -> pd.DataFrame:
    start_dt = pd.to_datetime(start_datetime_str)
    end_dt = pd.to_datetime(end_datetime_str)
    all_inverter_data = []

    for identifier_str in inverter_identifiers:
        id_type, id_value = identifier_str.split(':', 1)
        inverter_id_dict = {id_type: id_value}
        print(f"\n--- Processando inversor: {identifier_str} de {start_dt.date()} a {end_dt.date()} ---")
        
        records_inverter = []
        dias_esperados = pd.date_range(start=start_dt.date(), end=end_dt.date(), freq='D')
        
        for dia in dias_esperados:
            day_str = dia.strftime('%Y-%m-%d')
            records_dia = _fetch_data_for_day(inverter_id_dict, day_str)
            
            if records_dia:
                for record in records_dia:
                    record['inverter_identifier'] = identifier_str
                records_inverter.extend(records_dia)
            else:
                print(f" -> Nenhum dado encontrado para {day_str}. Adicionando linha vazia.")
                timestamp_vazio = int(dia.timestamp() * 1000)
                linha_vazia = {
                    'dataTimestamp': timestamp_vazio,
                    'inverter_identifier': identifier_str,
                    'timeStr': day_str
                }
                records_inverter.append(linha_vazia)

            time.sleep(0.6)
        
        all_inverter_data.extend(records_inverter)

    if not all_inverter_data: return pd.DataFrame()

    df = pd.DataFrame(all_inverter_data)
    df['fonte'] = "Solis"
    df['datetime'] = pd.to_datetime(df['dataTimestamp'], unit='ms', errors='coerce')
    df = df.dropna(subset=['datetime'])
    
    df_filtrado = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)].copy()
    if df_filtrado.empty:
        return pd.DataFrame()

    df_filtrado['datetime'] = df_filtrado['datetime'] - pd.Timedelta(hours=3)
    df_filtrado['inverter_identifier'] = df_filtrado['inverter_identifier'].str.split(':').str[1]
    
    return df_filtrado.sort_values(by=['inverter_identifier', 'datetime']).reset_index(drop=True)