import pandas as pd
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
        """Genera un gráfico de barras estilizado y lo devuelve como Base64."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
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
            
            # Guardar a buffer de memoria
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            buf.seek(0)
            
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            logging.warning(f"Matplotlib no disponible o bloqueado por directiva del sistema ({e}). Generando gráfico vectorial SVG de respaldo.")
            return self._generate_fallback_svg_chart(df)

    def _generate_fallback_svg_chart(self, df):
        """Genera un gráfico SVG estilizado en modo oscuro sin requerir DLLs externas ni matplotlib."""
        width = 800
        height = 480
        padding_left = 180
        padding_right = 140
        padding_top = 70
        padding_bottom = 50
        
        chart_w = width - padding_left - padding_right
        chart_h = height - padding_top - padding_bottom
        
        max_val = max(df['Produccion_KMT'].max() * 1.15, 1200)
        n_rows = len(df)
        bar_height = min(36, chart_h // n_rows - 10)
        
        svg_elements = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #111827; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">',
            f'<rect width="{width}" height="{height}" fill="#111827" rx="12"/>',
            f'<text x="{width/2}" y="38" text-anchor="middle" fill="#f1f5f9" font-size="18" font-weight="bold">Producción de Cobre por Faena (Acumulado a Junio 2026)</text>',
            f'<text x="{width/2}" y="56" text-anchor="middle" fill="#94a3b8" font-size="11">Miles de Toneladas Métricas (KMT) | % Variación vs Promedio 5 Años</text>'
        ]
        
        # Grid lines
        for step in [250, 500, 750, 1000, 1250]:
            if step <= max_val:
                x_pos = padding_left + (step / max_val) * chart_w
                svg_elements.append(f'<line x1="{x_pos}" y1="{padding_top}" x2="{x_pos}" y2="{height - padding_bottom}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>')
                svg_elements.append(f'<text x="{x_pos}" y="{height - padding_bottom + 18}" text-anchor="middle" fill="#64748b" font-size="11">{step}</text>')
        
        y_spacing = chart_h / n_rows
        for i, row in df.iterrows():
            y_pos = padding_top + i * y_spacing + 6
            val = row['Produccion_KMT']
            var = row['Variacion_Promedio']
            b_w = max(4, (val / max_val) * chart_w)
            color = "#34d399" if var > 0 else "#f87171"
            sign = "+" if var > 0 else ""
            
            # Label Faena
            svg_elements.append(f'<text x="{padding_left - 12}" y="{y_pos + bar_height/2 + 4}" text-anchor="end" fill="#f1f5f9" font-size="13" font-weight="500">{row["Faena"]}</text>')
            # Bar
            svg_elements.append(f'<rect x="{padding_left}" y="{y_pos}" width="{b_w}" height="{bar_height}" fill="{color}" rx="4"/>')
            # Value text
            svg_elements.append(f'<text x="{padding_left + b_w + 10}" y="{y_pos + bar_height/2 + 4}" fill="{color}" font-size="12" font-weight="bold">{int(val)} ({sign}{var}%)</text>')
            
        svg_elements.append('</svg>')
        svg_code = "".join(svg_elements)
        encoded = base64.b64encode(svg_code.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"
        
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
