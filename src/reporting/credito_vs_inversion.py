import os
import io
import base64
import math
import locale
import datetime
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from html2image import Html2Image

class CreditoVsInversionReport:
    def __init__(self, templates_dir, assets_dir, output_dir):
        self.templates_dir = templates_dir
        self.assets_dir = assets_dir
        self.output_dir = output_dir
        self.hti = Html2Image()
        self.hti.output_path = output_dir
        self.hti.browser.args = [
            '--no-sandbox', '--disable-setuid-sandbox',
            '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1'
        ]
        
    def _format_clp(self, value):
        try:
            return f"${int(value):,} CLP".replace(',', '.')
        except:
            return str(value)

    def _format_clp_short(self, value):
        if value >= 1000000:
            return f"${value/1000000:.1f}M"
        return f"${int(value):,}".replace(',', '.')

    def get_image_base64(self, filepath):
        try:
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = filepath.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{encoded}"
        except Exception as e:
            print(f"Error cargando imagen {filepath}: {e}")
            return ""

    def generate_chart(self, monto_inicial, plazo_meses, cuota_mensual, tasas_anuales_inv):
        """Genera el gráfico comparativo de crecimiento patrimonial vs pago crédito"""
        
        meses = list(range(0, plazo_meses + 1))
        
        # Costo total del credito (Intereses acumulados como valor negativo)
        interes_total = (cuota_mensual * plazo_meses) - monto_inicial
        interes_mensual_aprox = interes_total / plazo_meses
        linea_costo_credito = [- (interes_mensual_aprox * m) for m in meses]
        
        # Inversiones (Conservador, Moderado, Optimista) - Solo Ganancia
        tasa_mensual_cons = (1 + tasas_anuales_inv[0]/100)**(1/12) - 1
        tasa_mensual_mod = (1 + tasas_anuales_inv[1]/100)**(1/12) - 1
        tasa_mensual_opt = (1 + tasas_anuales_inv[2]/100)**(1/12) - 1
        
        data_cons = [(monto_inicial * ((1 + tasa_mensual_cons)**m)) - monto_inicial for m in meses]
        data_mod = [(monto_inicial * ((1 + tasa_mensual_mod)**m)) - monto_inicial for m in meses]
        data_opt = [(monto_inicial * ((1 + tasa_mensual_opt)**m)) - monto_inicial for m in meses]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(16, 9), facecolor='#0f172a')
        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#1e293b')
        
        # Estilos de líneas más gruesos
        ax.plot(meses, data_opt, color='#22c55e', label='Ganancia (Optimista)', linewidth=6)
        ax.plot(meses, data_mod, color='#38bdf8', label='Ganancia (Moderado)', linewidth=6)
        ax.plot(meses, data_cons, color='#94a3b8', label='Ganancia (Conservador)', linestyle='--', linewidth=4)
        
        # Linea de costo total (Intereses)
        ax.plot(meses, linea_costo_credito, color='#ef4444', label='Intereses del Crédito', linewidth=5)

        ax.fill_between(meses, data_mod, 0, color='#38bdf8', alpha=0.1)
        ax.fill_between(meses, linea_costo_credito, 0, color='#ef4444', alpha=0.1)

        # Linea cero
        ax.axhline(0, color='white', linewidth=2, alpha=0.5)

        ax.set_title('PROYECCIÓN A ' + str(plazo_meses) + ' MESES', color='white', fontsize=40, fontweight='bold', pad=30)
        
        # Estilo de ejes y grilla
        ax.grid(True, color='#334155', alpha=0.8, linestyle='--', linewidth=2)
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=24, length=10, width=2)
        
        # Formato de y a millones
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x/1000000:,.1f}M"))
        
        # Leyenda en otra posicion y eje X con label
        ax.set_xlabel('Meses de Plazo', color='white', fontsize=26, fontweight='bold', labelpad=20)
        legend = ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, -0.15), 
            fontsize=26, frameon=False, ncol=2, columnspacing=1.5
        )
        for text in legend.get_texts():
            text.set_color('#f8fafc')
            
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)
        plt.savefig(buf := io.BytesIO(), format='png', bbox_extra_artists=(legend,), bbox_inches='tight', transparent=False, dpi=120)
        buf.seek(0)
        plt.close(fig)
        
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

    def generate_report(self, client_name, es_empresa, monto, valor_cuota, plazo_meses, tasas_inv):
        """
        tasas_inv = [pesimista, base, optimista]
        """
        # Cálculos Crédito
        cuota = valor_cuota
        costo_total = cuota * plazo_meses
        intereses_totales = costo_total - monto
        tasa_interes_total = (intereses_totales / monto) * 100 if monto > 0 else 0
        
        # Cálculos Inversión
        t_cons = (1 + tasas_inv[0]/100)**(1/12) - 1
        t_mod = (1 + tasas_inv[1]/100)**(1/12) - 1
        t_opt = (1 + tasas_inv[2]/100)**(1/12) - 1
        
        vf_cons = monto * ((1 + t_cons)**plazo_meses)
        vf_mod = monto * ((1 + t_mod)**plazo_meses)
        vf_opt = monto * ((1 + t_opt)**plazo_meses)
        
        # Texto Seguro Desgravamen
        if es_empresa:
            texto_seguro = "El <strong>Seguro de Desgravamen para Empresas</strong> es una cobertura que los bancos suelen exigir (o recomendar fuertemente) al otorgar créditos comerciales. En caso de fallecimiento o invalidez total y permanente (ITP 2/3) del socio principal o avalista, la compañía de seguros paga el saldo insoluto de la deuda. Esto garantiza la continuidad operativa del negocio y evita que la empresa o los herederos asuman esta pesada carga financiera."
        else:
            texto_seguro = "El <strong>Seguro de Desgravamen</strong> es un respaldo fundamental en créditos de consumo. En caso de fallecimiento o invalidez, el seguro liquida la deuda pendiente con el banco. Esto asegura que la carga financiera no se herede a su familia y protege íntegramente su patrimonio."

        # Conclusión Lógica
        ganancia_inv = vf_mod - monto
        sobrecosto_credito = costo_total - monto
        if ganancia_inv > sobrecosto_credito:
            diferencia = ganancia_inv - sobrecosto_credito
            conclusion = f"Bajo un escenario moderado, su inversión generaría <span style='color: var(--accent-green)'>{self._format_clp(ganancia_inv)}</span> en retornos, mientras que el crédito cuesta <span style='color: var(--accent-red)'>{self._format_clp(sobrecosto_credito)}</span> en intereses. Por lo tanto, <strong>matemáticamente es más eficiente tomar el crédito</strong> y dejar el capital invertido trabajando a su favor."
        else:
            conclusion = f"El costo en intereses del crédito (<span style='color: var(--accent-red)'>{self._format_clp(sobrecosto_credito)}</span>) supera la rentabilidad esperada de la inversión moderada (<span style='color: var(--accent-green)'>{self._format_clp(ganancia_inv)}</span>). Matemáticamente, en este escenario resultaría menos costoso <strong>descapitalizarse</strong>."

        # Usar la carpeta assets en la raiz del proyecto para los logos nuevos
        root_assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(self.assets_dir))), "assets")
        
        # Preparar Diccionario Data con logos desde assets/brand
        logo_fv_p = os.path.join(root_assets_dir, "brand", "fv_logo_vector_pure.svg")
        if not os.path.exists(logo_fv_p):
            logo_fv_p = os.path.join(root_assets_dir, "brand", "fv_logo_principal_light.png")

        logo_altus_p = os.path.join(root_assets_dir, "brand", "altus_ai_logo_dark.svg")
        if not os.path.exists(logo_altus_p):
            logo_altus_p = os.path.join(root_assets_dir, "brand", "altus_ai_logo_dark.png")

        data = {
            "logo_fv_base64": self.get_image_base64(logo_fv_p),
            "logo_altus_base64": self.get_image_base64(logo_altus_p),
            "cliente_nombre": client_name,
            "fecha_reporte": datetime.datetime.now().strftime("%d de %B de %Y"),
            "cr_monto": self._format_clp(monto),
            "cr_plazo_meses": plazo_meses,
            "cr_plazo_anios": round(plazo_meses / 12, 1),
            "cr_tasa_total": round(tasa_interes_total, 2),
            "cr_intereses": self._format_clp(intereses_totales),
            "cr_cuota": self._format_clp(cuota),
            "cr_costo_total": self._format_clp(costo_total),
            "texto_seguro": texto_seguro,
            
            "inv_tasa_cons": tasas_inv[0],
            "inv_final_cons": self._format_clp(vf_cons),
            "inv_ganancia_cons": self._format_clp(vf_cons - monto),
            
            "inv_tasa_mod": tasas_inv[1],
            "inv_final_mod": self._format_clp(vf_mod),
            "inv_ganancia_mod": self._format_clp(vf_mod - monto),
            
            "inv_tasa_opt": tasas_inv[2],
            "inv_final_opt": self._format_clp(vf_opt),
            "inv_ganancia_opt": self._format_clp(vf_opt - monto),
            
            "chart_b64": self.generate_chart(monto, plazo_meses, cuota, tasas_inv),
            "conclusion_html": conclusion
        }
        
        # Render HTML
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template('credito_vs_inversion.html')
        html_content = template.render(data=data)
        
        temp_html_path = os.path.join(self.output_dir, "temp_credito.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Convert to PDF pages
        pdf_path = os.path.join(self.output_dir, f"Simulador_Credito_vs_Inversion_{client_name.replace(' ','_')}.pdf")
        
        # Como son diapositivas de 2160x2160 y están en divs .slide, podríamos intentar capturar el html entero como un PDF largo
        # o capturar screenshots por clase .slide y unir. Para simplificar y mantener la lógica del Html2Image, 
        # renderizaremos a PDF asumiendo que el navegador dividirá las páginas.
        # Imprimimos usando hti.print_to_pdf
        try:
            # Html2Image soporta print_to_pdf en navegadores Chrome
            # Usaremos una página de tamaño personalizado o dejaremos que Chrome corte
            self.hti.size = (2160, 10800)
            self.hti.screenshot(html_str=html_content, save_as=f"Simulador_Credito_vs_Inversion_{client_name.replace(' ','_')}.jpg")
            
            # Para hacer PDF de multiples fotos
            import PIL.Image
            
            # Asumimos que toma un pantallazo de 2160 * (5 slides)
            # Para asegurar que salga en multipagina de PDF, es más robusto dividir la imagen generada
            img = PIL.Image.open(os.path.join(self.output_dir, f"Simulador_Credito_vs_Inversion_{client_name.replace(' ','_')}.jpg"))
            
            width, height = img.size
            slide_height = 2160
            num_slides = 5
            
            pdf_pages = []
            for i in range(num_slides):
                box = (0, i * slide_height, width, (i + 1) * slide_height)
                cropped_img = img.crop(box).convert('RGB')
                pdf_pages.append(cropped_img)
                
            pdf_pages[0].save(
                pdf_path,
                save_all=True,
                append_images=pdf_pages[1:],
                resolution=100.0
            )
            return pdf_path
            
        except Exception as e:
            print("Error generando el PDF:", e)
            raise e
