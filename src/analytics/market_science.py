"""
Motor de Análisis de Mercado (CMF) — BD SENIOR
Lee datos de la tabla `cmf_market_trends` (ingesta CMF). Si la tabla no existe,
retorna datos de ejemplo para que la UI no colapse en producción.
"""
import pandas as pd
from sqlalchemy import text, inspect
from src.database.connection import engine


# ─── Datos de muestra offline (por si aún no se corre el ingestor CMF) ───────
_SAMPLE_AUM = 85_500_000_000_000  # 85.5 Billones CLP (aprox industria real 2024)

_SAMPLE_TOP_AGFS = pd.DataFrame({
    "administradora": ["Banchile", "Santander", "Principal", "LarrainVial", "Scotia"],
    "aum":            [18_200_000_000_000, 14_700_000_000_000, 9_800_000_000_000,
                       8_100_000_000_000, 6_400_000_000_000],
})

_SAMPLE_GROWTH = pd.DataFrame({
    "ano":              [2020, 2020, 2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024],
    "mes":              [6, 12, 6, 12, 6, 12, 6, 12, 6, 12],
    "total_participes": [2_100_000, 2_300_000, 2_450_000, 2_600_000,
                         2_700_000, 2_850_000, 2_950_000, 3_100_000,
                         3_200_000, 3_350_000],
})

_SAMPLE_PERFORMANCE = pd.DataFrame({
    "tipo_fondo":  ["Acciones Chile", "Balanceado", "Internacional", "Deuda C/P", "Estructurado", "Deuda L/P"],
    "avg_retorno": [1.85, 1.12, 0.95, 0.38, 0.61, 0.52],
})


def _table_exists(table_name: str) -> bool:
    """Verifica si una tabla existe en la base de datos."""
    try:
        insp = inspect(engine)
        return table_name in insp.get_table_names()
    except Exception:
        return False


def get_market_summary() -> dict:
    """
    Resumen ejecutivo del mercado de FFMM.
    Si la tabla CMF no existe, retorna datos de ejemplo con aviso.
    """
    if not _table_exists("cmf_market_trends"):
        return {
            "total_aum":  _SAMPLE_AUM,
            "top_agfs":   _SAMPLE_TOP_AGFS,
            "growth":     _SAMPLE_GROWTH,
            "data_source": "offline_sample",
        }

    try:
        with engine.connect() as con:
            max_ano = con.execute(text("SELECT MAX(ano) FROM cmf_market_trends")).scalar()
            
            total_aum = con.execute(text(
                "SELECT SUM(patrimonio_neto) FROM cmf_market_trends "
                "WHERE ano = (SELECT MAX(ano) FROM cmf_market_trends)"
            )).scalar() or _SAMPLE_AUM

            top_agfs = pd.read_sql("""
                SELECT administradora, SUM(patrimonio_neto) as aum
                FROM cmf_market_trends
                WHERE ano = (SELECT MAX(ano) FROM cmf_market_trends)
                GROUP BY administradora
                ORDER BY aum DESC
                LIMIT 20
            """, con)

            growth = pd.read_sql("""
                SELECT ano, mes, SUM(numero_participes) as total_participes
                FROM cmf_market_trends
                GROUP BY ano, mes
                ORDER BY ano ASC, mes ASC
            """, con)

        return {
            "total_aum":  total_aum,
            "top_agfs":   top_agfs,
            "growth":     growth,
            "last_update": f"{max_ano}" if max_ano else "N/D",
            "data_source": "live_db",
        }
    except Exception as e:
        return {
            "total_aum":  _SAMPLE_AUM,
            "top_agfs":   _SAMPLE_TOP_AGFS,
            "growth":     _SAMPLE_GROWTH,
            "data_source": f"offline_fallback (error: {e})",
        }


def analyze_sector_performance() -> pd.DataFrame:
    """
    Retorno promedio por tipo de fondo.
    Si la tabla CMF no existe, retorna datos de ejemplo.
    """
    if not _table_exists("cmf_market_trends"):
        return _SAMPLE_PERFORMANCE

    try:
        with engine.connect() as con:
            df = pd.read_sql("""
                SELECT tipo_fondo, AVG(retorno_mensual) as avg_retorno
                FROM cmf_market_trends
                WHERE ano = (SELECT MAX(ano) FROM cmf_market_trends)
                GROUP BY tipo_fondo
                ORDER BY avg_retorno DESC
            """, con)
        return df if not df.empty else _SAMPLE_PERFORMANCE
    except Exception:
        return _SAMPLE_PERFORMANCE
