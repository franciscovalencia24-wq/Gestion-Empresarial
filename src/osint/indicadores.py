import requests
import pandas as pd
from datetime import datetime
import streamlit as st

import os
import json

CACHE_FILE = os.path.join(os.path.dirname(__file__), "indicadores_cache.json")

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

@st.cache_data(ttl=3600)
def get_uf_info():
    """Obtiene UF con metadata: valor, fecha y si es fallback."""
    urls = [
        'https://mindicador.cl/api/uf',
        'https://api.cmfchile.cl/api-sbifv3/recursos_api/uf?apikey=guest&formato=json'
    ]
    cache = _load_cache()
    for url in urls:
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                if 'serie' in data and len(data['serie']) > 0:
                    val = float(data['serie'][0]['valor'])
                    if val > 30000:
                        fecha = data['serie'][0]['fecha'][:10]
                        cache["uf"] = {"valor": val, "fecha": fecha}
                        _save_cache(cache)
                        return {"valor": val, "fecha": fecha, "is_fallback": False}
                elif 'UFs' in data and len(data['UFs']) > 0:
                    val_str = data['UFs'][0]['Valor'].replace('.', '').replace(',', '.')
                    val = float(val_str)
                    if val > 30000:
                        fecha = data['UFs'][0]['Fecha']
                        cache["uf"] = {"valor": val, "fecha": fecha}
                        _save_cache(cache)
                        return {"valor": val, "fecha": fecha, "is_fallback": False}
        except Exception:
            continue
            
    # Fallback to local cache if API fails
    if "uf" in cache:
        return {"valor": cache["uf"]["valor"], "fecha": cache["uf"]["fecha"], "is_fallback": True}
        
    # Hard fallback
    return {"valor": 39650.0, "fecha": "2026-09-07", "is_fallback": True}

@st.cache_data(ttl=3600)
def get_uf_today():
    return get_uf_info()["valor"]

@st.cache_data(ttl=86400)
def get_uf_historica(fecha_str: str) -> float:
    """
    Obtiene la UF histórica para una fecha dada (formato DD-MM-YYYY o YYYY-MM-DD).
    """
    try:
        dt = pd.to_datetime(fecha_str, dayfirst=True)
        # mindicador.cl usa formato dd-mm-yyyy
        fecha_api = dt.strftime('%d-%m-%Y')
        url = f'https://mindicador.cl/api/uf/{fecha_api}'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'serie' in data and len(data['serie']) > 0:
                return float(data['serie'][0]['valor'])
    except Exception as e:
        print(f"Error fetching UF histórica para {fecha_str}: {e}")
        
    return get_uf_today() # Fallback a UF de hoy si falla

@st.cache_data(ttl=86400)
def get_ipc_accumulated(start_date_str, end_date_str=None):
    """
    Calcula la inflación acumulada (IPC) desde start_date hasta end_date
    multiplicando las variaciones mensuales.
    """
    try:
        start_date = pd.to_datetime(start_date_str)
        if pd.isna(start_date):
            return 0.0
            
        if end_date_str is None:
            end_date = pd.Timestamp.now()
        else:
            end_date = pd.to_datetime(end_date_str)
            
        years = range(start_date.year, end_date.year + 1)
        accumulated = 1.0
        
        for y in years:
            resp = requests.get(f'https://mindicador.cl/api/ipc/{y}', timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('serie', []):
                    dt = pd.to_datetime(item['fecha']).tz_localize(None)
                    # Tomamos el IPC de los meses estrictamente posteriores al mes del contrato
                    # hasta la fecha actual.
                    if start_date.replace(day=1) < dt <= end_date:
                        accumulated *= (1 + (item['valor'] / 100.0))
                        
        return (accumulated - 1) * 100
    except Exception as e:
        print("Error calculando IPC:", e)
        return 0.0

@st.cache_data(ttl=3600)
def get_utm_info():
    """Obtiene UTM con metadata."""
    cache = _load_cache()
    try:
        resp = requests.get('https://mindicador.cl/api/utm', timeout=4, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            val = float(data['serie'][0]['valor'])
            fecha = data['serie'][0]['fecha'][:10]
            cache["utm"] = {"valor": val, "fecha": fecha}
            _save_cache(cache)
            return {"valor": val, "fecha": fecha, "is_fallback": False}
    except Exception as e:
        pass
        
    if "utm" in cache:
        return {"valor": cache["utm"]["valor"], "fecha": cache["utm"]["fecha"], "is_fallback": True}
        
    # Hard fallback
    return {"valor": 71721.0, "fecha": "2026-09-07", "is_fallback": True}

@st.cache_data(ttl=3600)
def get_utm_today():
    return get_utm_info()["valor"]

@st.cache_data(ttl=3600)
def get_tpm_today():
    """Obtiene la Tasa de Política Monetaria (TPM) oficial del Banco Central de Chile usando mindicador.cl"""
    try:
        resp = requests.get('https://mindicador.cl/api/tpm', timeout=5, verify=False)
        if resp.status_code == 200:
            return float(resp.json()['serie'][0]['valor'])
    except Exception as e:
        pass
    return 4.5 # Fallback oficial del Banco Central de Chile (bcentral.cl)


