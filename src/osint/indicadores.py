import requests
import pandas as pd
from datetime import datetime
import streamlit as st

@st.cache_data(ttl=3600)
def get_uf_today():
    """Obtiene el valor de la UF al día de hoy usando mindicador.cl"""
    try:
        resp = requests.get('https://mindicador.cl/api/uf', timeout=5)
        if resp.status_code == 200:
            return resp.json()['serie'][0]['valor']
    except Exception as e:
        pass
    return 38000.0 # Fallback aprox

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
def get_utm_today():
    """Obtiene el valor de la UTM al día de hoy usando mindicador.cl"""
    try:
        resp = requests.get('https://mindicador.cl/api/utm', timeout=5)
        if resp.status_code == 200:
            return resp.json()['serie'][0]['valor']
    except Exception as e:
        pass
    return 66000.0 # Fallback aprox

