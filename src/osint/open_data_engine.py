import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import logging
from io import StringIO
import datetime

class OpenDataEngine:
    def __init__(self):
        logging.info("OpenDataEngine inicializado.")
        
    def get_cochilco_production_data(self):
        """
        Simula la ingesta de un dataset de Datos Abiertos de COCHILCO
        sobre la producción de cobre por faena en Chile (Miles de Toneladas Métricas).
        """
        # Datos basados en estadísticas recientes de grandes faenas chilenas (Anualizado/Trimestral)
        csv_data = """Faena,Produccion_KMT,Promedio_Historico
Escondida,1100,1050
Collahuasi,570,580
El Teniente,350,360
Los Pelambres,330,310
Radomiro Tomic,315,320
Los Bronces,270,300"""
        
        df = pd.read_csv(StringIO(csv_data))
        # Calcular la variación vs el promedio histórico globalmente
        df['Variacion_Promedio'] = ((df['Produccion_KMT'] - df['Promedio_Historico']) / df['Promedio_Historico'] * 100).round(1)
        return df
        
    def generate_production_chart_base64(self, df):
        """Genera un gráfico de barras estilizado usando Matplotlib y lo devuelve como Base64."""
        # Estilo oscuro tipo Altus AI / Terminal
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('#111827')
        ax.set_facecolor('#111827')
        
        # Colores condicionales: verde si variacion > 0, rojo si < 0
        colors = ['#34d399' if var > 0 else '#f87171' for var in df['Variacion_Promedio']]
        
        bars = ax.barh(df['Faena'][::-1], df['Produccion_KMT'][::-1], color=colors[::-1], edgecolor='#1e293b')
        
        # Títulos y estilos
        ax.set_title('Producción de Cobre por Faena (Acumulado a Junio 2026)', fontsize=16, fontweight='bold', color='#f1f5f9', pad=20)
        ax.set_xlabel('Miles de Toneladas Métricas (KMT) | % Variación vs Promedio 5 Años', fontsize=12, color='#cbd5e1')
        ax.tick_params(axis='x', colors='#cbd5e1')
        ax.tick_params(axis='y', colors='#f1f5f9', labelsize=12)
        
        # Ocultar bordes innecesarios
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1e293b')
        ax.spines['bottom'].set_color('#1e293b')
        ax.grid(axis='x', color='#1e293b', linestyle='--', alpha=0.7)
        
        # Añadir etiquetas de datos en las barras
        for bar, var in zip(bars, df['Variacion_Promedio'][::-1]):
            width = bar.get_width()
            label_color = '#34d399' if var > 0 else '#f87171'
            sign = "+" if var > 0 else ""
            ax.text(width + 10, bar.get_y() + bar.get_height()/2, 
                    f"{int(width)} ({sign}{var}%)", 
                    ha='left', va='center', color=label_color, fontweight='bold', fontsize=11)
            
            
        plt.tight_layout()
        
        # Guardar a buffer de memoria en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
        
    def generate_llm_context(self, df):
        """Genera el texto de contexto estadístico para enviarlo a la Inteligencia Artificial."""
        total_prod = df['Produccion_KMT'].sum()
        top_faena = df.iloc[0]['Faena']
        top_prod = df.iloc[0]['Produccion_KMT']
        caida_mayor = df.loc[df['Variacion_Promedio'].idxmin()]
        alza_mayor = df.loc[df['Variacion_Promedio'].idxmax()]
        
        contexto = f"ESTADÍSTICAS OFICIALES DE PRODUCCIÓN DE COBRE EN CHILE (Acumulado 2026):\n"
        contexto += f"- Producción Total de las Top Faenas: {total_prod} KMT.\n"
        contexto += f"- Liderazgo: {top_faena} lidera con {top_prod} KMT.\n"
        contexto += f"- Mayor Crecimiento vs Promedio Histórico (5 Años): {alza_mayor['Faena']} con un alza de {alza_mayor['Variacion_Promedio']}%.\n"
        contexto += f"- Mayor Contracción vs Promedio Histórico (5 Años): {caida_mayor['Faena']} con una caída de {caida_mayor['Variacion_Promedio']}%.\n\n"
        contexto += "[INSTRUCCIÓN CRÍTICA PARA LA IA - MODO EXPERTO]: Toma estos datos duros de producción minera chilena y crúzalos con megatendencias globales (transición energética, demanda, etc.). IMPORTANTE: Mantén consistencia con nuestra línea editorial previa: destaca que, si bien hay faenas con números azules, la producción general en Chile lleva años estancada (en torno a 5 millones de toneladas anuales) debido a la asfixiante permisología y los altos royalties. Usa un tono crítico y realista para inversores patrimoniales. \n"
        contexto += "REQUISITOS OBLIGATORIOS PARA EL POST:\n"
        contexto += "1. Incluye una tabla (formato texto o markdown simple) con el Top 3 de faenas y su producción, para darle mucha seriedad y peso estadístico al análisis.\n"
        contexto += "2. Al final del post o de forma natural, debes incluir obligatoriamente las siguientes menciones (con el @ literal): @Cochilco, @Sociedad Nacional de Minería, @Ministerio de Minería de Chile.\n"
        
        return contexto

if __name__ == "__main__":
    engine = OpenDataEngine()
    df = engine.get_cochilco_production_data()
    b64 = engine.generate_production_chart_base64(df)
    print("Base64 Length:", len(b64))
    print("Context:\n", engine.generate_llm_context(df))
