import sys
import os
from sqlalchemy import text

# Path setup
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path: sys.path.insert(0, base_path)

from src.database.connection import engine

def generar_reporte_inteligencia():
    with engine.connect() as con:
        # 1. Totales Generales
        total = con.execute(text("SELECT count(id) FROM prospects")).scalar()
        con_fono = con.execute(text("SELECT count(id) FROM prospects WHERE telefono IS NOT NULL AND telefono != '' AND telefono NOT IN ('SIN INFO', 'RUT INVALIDO', 'RUT ERROR')")).scalar()
        
        # 2. Datos de Inteligencia (Enriquecimiento)
        con_nacimiento = con.execute(text("SELECT count(id) FROM prospects WHERE fecha_nacimiento IS NOT NULL")).scalar()
        con_direccion = con.execute(text("SELECT count(id) FROM prospects WHERE ultima_direccion IS NOT NULL AND ultima_direccion != ''")).scalar()
        fallecidos = con.execute(text("SELECT count(id) FROM prospects WHERE fallecido = 'SI'")).scalar()
        
        # 3. Top 5 Comunas detectadas
        res_direcciones = con.execute(text("SELECT ultima_direccion FROM prospects WHERE ultima_direccion IS NOT NULL AND ultima_direccion != ''")).fetchall()
        comunas = {}
        for row in res_direcciones:
            parts = row[0].split(',')
            if len(parts) > 1:
                comuna = parts[-1].strip().upper()
                comunas[comuna] = comunas.get(comuna, 0) + 1
            elif ' ' in row[0]: # Intento de capturar ultima palabra como comuna
                comuna = row[0].split(' ')[-1].strip().upper()
                comunas[comuna] = comunas.get(comuna, 0) + 1
        
        top_comunas = sorted(comunas.items(), key=lambda x: x[1], reverse=True)[:5]

        print('\n' + '='*50)
        print('      AUDITORIA DE INTELIGENCIA PATRIMONIAL')
        print('='*50)
        print(f'Total de registros en Base:  {total:,}')
        print(f'Prospectos con Teléfono:      {con_fono:,} ({round(con_fono/total*100, 1)}%)')
        print('-'*50)
        print('DATOS DE CUALIFICACION (Wealth Insight):')
        print(f'Con Fecha de Nacimiento:     {con_nacimiento:,} (Edad segmentable)')
        print(f'Con Domicilio Detectado:    {con_direccion:,} (Geolocalización)')
        print(f'Alertas de Defunción (SI):   {fallecidos:,} (Oportunidad Sucesoria)')
        print('-'*50)
        print('TOP 5 COMUNAS / CIUDADES DETECTADAS:')
        for c, count in top_comunas:
            if c:
                print(f' - {c}: {count} prospectos')
        print('='*50 + '\n')

if __name__ == '__main__':
    generar_reporte_inteligencia()
