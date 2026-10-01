"""
Motor de PDF para Auditoría Patrimonial — FV Asesorías e Inversiones
Usa únicamente fpdf2 (primitivas nativas). Sin kaleido, sin matplotlib.
Cero dependencias externas que puedan bloquearse en Windows.
"""
import os
from fpdf import FPDF
from datetime import datetime


class AuditReport(FPDF):
    def header(self):
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "assets", "brand", "fv_logo_principal_light.png"
        )
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, 10, 8, 30)
            except Exception:
                pass
        self.set_font('Helvetica', 'B', 13)
        self.set_xy(45, 10)
        self.set_text_color(17, 24, 39)
        self.cell(0, 7, 'REPORTE DE AUDITORÍA PATRIMONIAL', 0, 1, 'L')
        self.set_font('Helvetica', '', 8)
        self.set_x(45)
        self.set_text_color(107, 114, 128)
        self.cell(0, 5, 'FV Asesorías e Inversiones SpA - Documento Confidencial', 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.line(10, 28, 200, 28)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6,
                  f'Página {self.page_no()} | Wealth 3.0 - Simulación Monte Carlo | '
                  f'Generado {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                  0, 0, 'C')

    def section_title(self, title):
        self.set_fill_color(0, 177, 64)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 7, f'  {title}', 0, 1, 'L', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)


def _draw_line_chart(pdf, stats_p, stats_c, path_infl, plazo_proj, x, y, w, h):
    """Dibuja un gráfico de líneas con primitivas fpdf2 natales."""
    n = plazo_proj + 1

    # Marco exterior
    pdf.set_draw_color(220, 220, 220)
    pdf.rect(x, y, w, h)

    # Calcular escala
    all_vals = list(stats_p['p5']) + list(stats_p['p95']) + list(stats_c['p50']) + list(path_infl)
    v_min = min(all_vals) * 0.95
    v_max = max(all_vals) * 1.05
    v_range = v_max - v_min if v_max != v_min else 1

    def sx(i): return x + (i / (n - 1)) * w  # x en papel
    def sy(v): return y + h - ((v - v_min) / v_range) * h  # y en papel

    # Grillas horizontales
    pdf.set_draw_color(240, 240, 240)
    for i in range(1, 4):
        gy = y + h * i / 4
        pdf.line(x, gy, x + w, gy)

    # Banda de confianza P5-P95 (relleno simulado con rectángulos finos)
    pdf.set_draw_color(0, 177, 64)
    for i in range(n - 1):
        y_top_l = sy(stats_p['p95'][i])
        y_bot_l = sy(stats_p['p5'][i])
        y_top_r = sy(stats_p['p95'][i + 1])
        y_bot_r = sy(stats_p['p5'][i + 1])
        x1, x2 = sx(i), sx(i + 1)
        # trapecio superior e inferior como líneas gruesas semitransparentes
        pdf.set_draw_color(180, 230, 180)
        pdf.set_line_width(abs(y_bot_l - y_top_l) * 0.05)
        # Dibujamos segmentos del área:
        steps = max(1, int(abs(y_bot_l - y_top_l) / 1.5))
        for s in range(steps):
            frac = s / steps
            _y = y_top_l + frac * (y_bot_l - y_top_l)
            _y2 = y_top_r + frac * (y_bot_r - y_top_r)
            pdf.set_draw_color(200, 240, 200)
            pdf.set_line_width(0.3)
            pdf.line(x1, _y, x2, _y2)

    pdf.set_line_width(0.2)

    # Competencia (rojo, discontinuo)
    pdf.set_draw_color(239, 68, 68)
    pdf.set_line_width(0.6)
    for i in range(n - 1):
        if i % 2 == 0:  # discontinuo
            pdf.line(sx(i), sy(stats_c['p50'][i]), sx(i + 1), sy(stats_c['p50'][i + 1]))

    # IPC (gris punteado)
    pdf.set_draw_color(148, 163, 184)
    pdf.set_line_width(0.4)
    for i in range(n - 1):
        if i % 3 != 1:
            pdf.line(sx(i), sy(path_infl[i]), sx(i + 1), sy(path_infl[i + 1]))

    # Propuesta (verde sólido, más grueso)
    pdf.set_draw_color(0, 177, 64)
    pdf.set_line_width(1.2)
    for i in range(n - 1):
        pdf.line(sx(i), sy(stats_p['p50'][i]), sx(i + 1), sy(stats_p['p50'][i + 1]))

    pdf.set_line_width(0.2)

    # Etiquetas eje X
    pdf.set_font('Helvetica', '', 6)
    pdf.set_text_color(100, 100, 100)
    for i in [0, plazo_proj // 2, plazo_proj]:
        pdf.set_xy(sx(i) - 3, y + h + 1)
        pdf.cell(6, 3, f'Año {i}', 0, 0, 'C')

    # Valor final propuesta (anotación)
    val_fin = stats_p['p50'][-1]
    label = f"$ {val_fin:,.0f}".replace(',', '.')
    pdf.set_font('Helvetica', 'B', 6)
    pdf.set_text_color(0, 140, 50)
    lx = sx(n - 1) - 28
    ly = sy(val_fin) - 4
    pdf.set_xy(lx, ly)
    pdf.cell(28, 3, label, 0, 0, 'R')

    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)


def generate_audit_pdf(client_name, metrics, summary_text=None,
                       rows_legal=None, stats_p=None, stats_c=None,
                       path_infl=None, plazo_proj=10,
                       # Parámetros legacy ignorados:
                       fig_roi=None):
    """
    Genera un PDF profesional con los resultados de la auditoría patrimonial.
    No requiere kaleido ni matplotlib — usa únicamente fpdf2.
    """
    pdf = AuditReport()
    pdf.add_page()

    # ── DATOS DEL CLIENTE ───────────────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, 7, f"Cliente: {client_name}", ln=False)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 7, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 5, "Metodología: Auditoría Patrimonial Wealth 3.0 - Monte Carlo 2.000 trayectorias", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # ── MÉTRICAS CLAVE ──────────────────────────────────────────────────────
    pdf.section_title("CONCLUSIONES CLAVE DE LA AUDITORÍA")

    col_w = 60
    mx = [15, 80, 145]

    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(107, 114, 128)
    for lbl, cx in zip(["PATRIMONIO PROYECTADO (MEDIANA)", "TAC - COSTO ANUAL PROPUESTA", "ALPHA TRIBUTARIO"], mx):
        pdf.set_xy(cx, pdf.get_y())
        pdf.cell(col_w, 5, lbl, ln=False)
    pdf.ln(6)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 177, 64)
    for key, cx in zip(["patrimonio", "tac", "alpha"], mx):
        pdf.set_xy(cx, pdf.get_y())
        pdf.cell(col_w, 8, metrics.get(key, 'N/A'), ln=False)
    pdf.ln(10)

    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(107, 114, 128)
    descs = [
        "Valor esperado al final del plazo (net. comisiones)",
        "Costo anual que descuenta el administrador",
        "Beneficio fiscal anual estimado por estructura legal"
    ]
    for desc, cx in zip(descs, mx):
        pdf.set_xy(cx, pdf.get_y())
        pdf.cell(col_w, 4, desc, ln=False)
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # ── GRÁFICO MONTE CARLO ─────────────────────────────────────────────────
    pdf.section_title("SIMULACIÓN ESTOCÁSTICA DEL PATRIMONIO (NETO DE COMISIONES)")

    if stats_p and stats_c and path_infl:
        chart_y = pdf.get_y() + 2
        _draw_line_chart(pdf, stats_p, stats_c, path_infl, plazo_proj,
                         x=10, y=chart_y, w=190, h=55)
        pdf.set_xy(10, chart_y + 58)

        # Leyenda
        items = [
            ((0, 177, 64), "── Propuesta Principal (Mediana)"),
            ((239, 68, 68), "- - Competencia (Mediana)"),
            ((148, 163, 184), "··· Poder Adquisitivo (IPC)"),
            ((200, 240, 200), "░░ Banda de Confianza 90%"),
        ]
        pdf.set_font('Helvetica', '', 6.5)
        for rgb, label in items:
            pdf.set_text_color(*rgb)
            pdf.cell(50, 4, label, ln=False)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)
    else:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, "[Estadísticas Monte Carlo no disponibles - ejecute la auditoría desde la plataforma]", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

    # ── TABLA COMPARATIVA ──────────────────────────────────────────────────
    if rows_legal:
        pdf.section_title("COMPARATIVA LEGAL Y DE COSTOS")
        col_ws = [55, 70, 65]
        headers = ["Atributo", "Portafolio Competencia", "Propuesta Principal"]

        pdf.set_fill_color(243, 244, 246)
        pdf.set_font('Helvetica', 'B', 8)
        for lbl, cw in zip(headers, col_ws):
            pdf.cell(cw, 6, f"  {lbl}", border=1, fill=True, ln=False)
        pdf.ln()

        pdf.set_font('Helvetica', '', 8)
        for i, row in enumerate(rows_legal):
            if len(row) != 3:
                continue
            icon, comp, princ = row
            fill = (i % 2 == 0)
            pdf.set_fill_color(249, 250, 251) if fill else pdf.set_fill_color(255, 255, 255)

            # Limpiamos emojis (fpdf no los soporta en Helvetica)
            # Limpiamos solo caracteres que no estén en Latin-1 (para evitar errores en fpdf2 standard fonts)
            def clean_pdf_text(s):
                if not s: return ""
                # fpdf2 con fuentes core (Helvetica) usa latin-1
                return str(s).encode('latin-1', 'replace').decode('latin-1')

            pdf.cell(col_ws[0], 6, f"  {clean_pdf_text(icon)[:30]}", border=1, fill=fill, ln=False)
            pdf.cell(col_ws[1], 6, f"  {clean_pdf_text(comp)[:40]}", border=1, fill=fill, ln=False)

            # Propuesta en verde si contiene '%' (es mejor)
            pdf.set_text_color(0, 140, 50) if 'Patrimonial' in str(princ) or 'Capital' in str(princ) else pdf.set_text_color(0, 0, 0)
            pdf.cell(col_ws[2], 6, f"  {clean_pdf_text(princ)[:40]}", border=1, fill=fill, ln=True)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

    # ── DISCLAIMER ─────────────────────────────────────────────────────────
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 4,
        "Nota Legal: Este reporte es una simulación basada en hipótesis de mercado y rentabilidades "
        "históricas oficiales reportadas a la CMF. Las rentabilidades pasadas no garantizan retornos "
        "futuros. Este documento es de carácter informativo y no constituye asesoría de inversión formal. "
        "TAC = Tasa Anual de Costo según reporte oficial CMF. Fuente UF/IPC: mindicador.cl")

    # ── GUARDAR ────────────────────────────────────────────────────────────
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    safe_name = client_name.replace(' ', '_')
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(output_dir, f"Auditoria_{safe_name}_{ts}.pdf")
    # fpdf 1.7.2 usa output(name, dest='F') para guardar en archivo
    try:
        pdf.output(filename, 'F')  # fpdf 1.x
    except TypeError:
        pdf.output(filename)        # fpdf 2.x
    return filename

class AltusAdoptionReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(15, 23, 42) # Slate 900
        self.cell(0, 8, "ALTUS AI SpA", ln=True, align='R')
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 116, 139) # Slate 500
        self.cell(0, 5, "División Institucional B2B", ln=True, align='R')
        self.line(10, self.get_y()+2, 200, self.get_y()+2)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} - Documento Confidencial', 0, 0, 'C')

def generate_adoption_certificate_pdf(empresa_nombre, empresa_rut, plan_contratado, total_contratado, total_cargados, saldo_licencias, activados, tasa_activacion, hash_cert):
    pdf = AltusAdoptionReport(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    def clean_pdf_text(s):
        if not s: return ""
        return str(s).encode('latin-1', 'replace').decode('latin-1')

    # Título Principal
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "CERTIFICADO OFICIAL DE ADOPCIÓN CORPORATIVA", ln=True, align='C')
    pdf.ln(8)
    
    # 1. Datos del Cliente
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(241, 245, 249) # Slate 100
    pdf.cell(0, 8, "  1. DATOS DEL CLIENTE INSTITUCIONAL", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(40, 6, "Razón Social:", ln=False)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, clean_pdf_text(empresa_nombre), ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(40, 6, "RUT:", ln=False)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, clean_pdf_text(empresa_rut), ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(40, 6, "Plan Contratado:", ln=False)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, clean_pdf_text(plan_contratado), ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(40, 6, "Fecha Emisión:", ln=False)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, datetime.now().strftime('%d-%m-%Y %H:%M:%S'), ln=True)
    pdf.ln(6)
    
    # 2. Métricas
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "  2. MÉTRICAS CONSOLIDADAS Y AGREGADAS", ln=True, fill=True)
    pdf.ln(2)
    
    metrics = [
        ("Cupos Originales Contratados", str(total_contratado)),
        ("Cupos Asignados a Ejecutivos", str(total_cargados)),
        ("Cupos Remanentes Disponibles", str(saldo_licencias)),
        ("Reportes 360 Emitidos", str(activados)),
        ("Tasa Global de Activación", f"{tasa_activacion:.1f}%")
    ]
    
    for k, v in metrics:
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(80, 7, clean_pdf_text(k), border=1, fill=False, ln=False)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(40, 7, clean_pdf_text(v), border=1, fill=False, ln=True, align='C')
    pdf.ln(8)
    
    # 3. Desglose Metodológico de Auditoría
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "  3. DESGLOSE METODOLÓGICO DE AUDITORÍA", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105)
    metodologia = (
        "Los análisis y simulaciones generadas para los ejecutivos de la nómina se construyen "
        "en base a los siguientes motores analíticos de ALTUS Core:\n"
        "• Auditoría de Reliquidación IGC (Motor: src/utils/simulators/reliquidacion_simulator.py): "
        "Simulación de impacto fiscal sobre indemnizaciones y rentas diferidas.\n"
        "• Optimización DPE (Motor: src/utils/simulators/dpe_simulator.py): "
        "Cálculo del Ahorro Fiscal mediante Depósito Pactado del Empleador."
    )
    pdf.multi_cell(0, 5, clean_pdf_text(metodologia))
    pdf.ln(6)
    
    # 4. Cumplimiento
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "  4. CLÁUSULA DE CUMPLIMIENTO Y CONFIDENCIALIDAD", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(71, 85, 105) # Slate 600
    
    clausula = (
        "Se certifica explícitamente que ALTUS AI SpA procesó los datos de la nómina gerencial "
        "bajo los más altos estándares de seguridad y confidencialidad. Toda la información patrimonial, "
        "simulaciones tributarias y reportes de los colaboradores fueron procesados mediante algoritmos "
        "con cifrado de grado militar (AES-256) en tránsito y reposo, y operan bajo un esquema arquitectónico "
        "Zero-Knowledge (Conocimiento Cero). La empresa contratante (empleador) NO posee, bajo ninguna "
        "circunstancia o autorización, acceso a datos patrimoniales ni fiscales individuales de sus ejecutivos.\n\n"
        "Este procesamiento es conforme a las disposiciones normadas por la Ley 21.096 (Protección de "
        "Datos Personales) y la Ley 21.521 (Ley Fintec) en la República de Chile."
    )
    pdf.multi_cell(0, 5, clean_pdf_text(clausula))
    pdf.ln(8)
    
    # Hash y QR
    import qrcode
    
    fecha_emision_str = datetime.now().strftime('%Y-%m-%d')
    qr_data = f"ALTUS-AUDIT:RUT={empresa_rut}|HASH={hash_cert}|DATE={fecha_emision_str}"
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_filename = f"qr_{hash_cert[:10]}.png"
    qr_img.save(qr_filename)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "Sello de Integridad y Verificación (SHA-256):", ln=True)
    
    # Guardar la Y actual antes de dibujar el QR y el hash
    current_y = pdf.get_y()
    
    pdf.set_font('Courier', '', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(10, current_y)
    pdf.multi_cell(140, 5, clean_pdf_text(hash_cert))
    
    # Renderizar código QR
    pdf.image(qr_filename, x=150, y=current_y - 5, w=35)
    
    pdf.set_xy(10, current_y + 25)
    
    # Limpiar archivo temporal de imagen QR
    try:
        os.remove(qr_filename)
    except:
        pass
    
    # Firmas
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(80, 5, "___________________________________", ln=True)
    pdf.cell(80, 5, "Sistema de Emisión Automatizada", ln=True)
    pdf.cell(80, 5, "ALTUS AI SpA", ln=True)
    
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(output_dir, f"Certificado_Adopcion_{str(empresa_rut).replace('.', '').replace('-', '')}_{ts}.pdf")
    
    try:
        pdf.output(filename, 'F')
    except TypeError:
        pdf.output(filename)
        
    return filename
