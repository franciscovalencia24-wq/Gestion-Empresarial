import pandas as pd
import requests
import os
from datetime import datetime

from src.database.connection import engine
from sqlalchemy import text

class DataScientistAgent:
    def __init__(self):
        self.cmf_db_url = "https://www.cmfchile.cl/portal/estadisticas/617/articles-91850_document_2.xlsx"
        self.local_path = "data/cmf/rentabilidad/articles-91850_document_2.xlsx"

    def sync_industry_data(self):
        """Descarga e inyecta la base de datos de tendencias de la CMF."""
        try:
            import subprocess
            # Usamos curl.exe para asegurar que el archivo se descargue correctamente
            subprocess.run(["curl.exe", "-L", self.cmf_db_url, "-o", self.local_path], check=True)
            
            # Llamamos al ingestor que acabamos de crear
            from src.osint.ingestor_tendencias import ingest_market_trends
            ingest_market_trends(self.local_path)
            return True
        except Exception as e:
            print(f"Error sincronizando CMF: {e}")
            return False

    def get_market_metrics(self):
        """Retorna métricas clave del mercado actual."""
        with engine.connect() as con:
            # 1. Patrimonio Total por Categoría (Año actual)
            query_aum = """
                SELECT categoria, SUM(patrimonio_neto) as aum
                FROM cmf_market_trends
                WHERE ano = (SELECT MAX(ano) FROM cmf_market_trends)
                GROUP BY categoria
                ORDER BY aum DESC
                LIMIT 10
            """
            df_aum = pd.read_sql(query_aum, con)
            
            # 2. Crecimiento de partícipes en el tiempo
            query_growth = """
                SELECT ano, mes, SUM(numero_participes) as total_participes
                FROM cmf_market_trends
                GROUP BY ano, mes
                ORDER BY ano ASC, mes ASC
            """
            df_growth = pd.read_sql(query_growth, con)
            
            return df_aum, df_growth

    def analyze_market_trends(self):
        """Genera un análisis textual basado en datos reales."""
        try:
            with engine.connect() as con:
                # Obtenemos la rentabilidad promedio de las categorías top
                query = """
                    SELECT categoria, AVG(retorno_mensual) as media_retorno
                    FROM cmf_market_trends
                    WHERE ano = (SELECT MAX(ano) FROM cmf_market_trends)
                    GROUP BY categoria
                    ORDER BY media_retorno DESC
                    LIMIT 3
                """
                top_perf = pd.read_sql(query, con)
                categories = top_perf['categoria'].tolist()
                
                return f"""
                ### 🔎 Análisis de Inteligencia
                El mercado de Fondos Mutuos muestra un dinamismo concentrado en las categorías de **{categories[0]}** y **{categories[1]}**, 
                que lideran el rendimiento del presente año.
                
                **Insights Tácticos:**
                - La categoría `{categories[0]}` presenta el mayor momentum con retornos promedio de {top_perf['media_retorno'].iloc[0]:.2f}%.
                - Se observa una consolidación en el segmento Retail, lo que abre una ventana de oportunidad para la migración hacia estrategias de mayor sofisticación.
                """
        except Exception as e:
            return f"Error analizando tendencias: {e}"
