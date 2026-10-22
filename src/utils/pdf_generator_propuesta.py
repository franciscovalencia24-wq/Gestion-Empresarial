"""
Generador de Documento PDF: Propuesta de Valor Patrimonial
FV Asesorías e Inversiones & Altus AI Core | Alianza Estratégica Principal Financial Group
Arquitectura basada en ReportLab (in-memory buffer, sin dependencias nativas complejas).
"""

import os
import sys
import io
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

from src.database.connection import SessionLocal
from src.database.models import Prospect, ClientProfile, ClientProperty, ClientPortfolio, ClientInsurance, ClientDebt
from src.osint.indicadores import get_uf_today, get_utm_today
from src.utils.simulators.apv_simulator import APVSimulator


def _safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        val_str = str(val).strip().lower()
        if val_str in ["", "none", "nan", "null"]:
            return default
        return float(val_str)
    except Exception:
        return default


def header_footer_propuesta(canvas, doc):
    """Membrete ejecutivo con logos institucionales de FV Asesorías y Altus AI"""
    canvas.saveState()
    margin = 16 * mm
    width, height = A4
    top_y = height - margin

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    candidates_fv = [
        os.path.join(project_root, 'assets', 'brand', 'fv_logo_principal_official.png'),
        os.path.join(project_root, 'assets', 'brand', 'fv_logo_principal.png'),
        os.path.join(project_root, 'assets', 'brand', 'fv_logo_principal_trimmed.png'),
        os.path.join(project_root, 'assets', 'brand', 'fv_logo_vector_pure_clean.png')
    ]
    logo_fv = next((p for p in candidates_fv if os.path.exists(p)), None)

    candidates_altus = [
        os.path.join(project_root, 'assets', 'brand', 'altus_logo_light_bg.png'),
        os.path.join(project_root, 'assets', 'brand', 'altus_ai_logo_dark.png'),
        os.path.join(project_root, 'assets', 'brand', 'altus_clean_transparent.png'),
        os.path.join(project_root, 'assets', 'brand', 'altus_logo_official.png')
    ]
    logo_altus = next((p for p in candidates_altus if os.path.exists(p)), None)

    # 1. Logo FV Asesorías (Izquierda) - proporción simétrica y nítida
    if logo_fv:
        try:
            canvas.drawImage(logo_fv, margin, top_y - 12.8 * mm, width=35 * mm, height=12.5 * mm,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # 2. Logo Altus AI Dark Badge (Derecha) - proporción simétrica
    if logo_altus:
        try:
            canvas.drawImage(logo_altus, width - margin - 13.2 * mm, top_y - 12.8 * mm, width=13.2 * mm, height=12.5 * mm,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # 3. Título Central del Membrete
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColor(colors.HexColor('#0F172A'))
    canvas.drawCentredString(width / 2.0, top_y - 5 * mm, "FV ASESORÍAS E INVERSIONES  &  ALTUS AI")

    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(colors.HexColor('#0284C7'))
    canvas.drawCentredString(width / 2.0, top_y - 9.5 * mm, "Alianza Estratégica Principal Financial Group — Wealth Management 360°")

    # 4. Línea divisoria elegante
    canvas.setStrokeColor(colors.HexColor('#0F172A'))
    canvas.setLineWidth(1)
    canvas.line(margin, top_y - 15 * mm, width - margin, top_y - 15 * mm)

    canvas.setStrokeColor(colors.HexColor('#D4AF37'))
    canvas.setLineWidth(0.5)
    canvas.line(margin, top_y - 16 * mm, width - margin, top_y - 16 * mm)

    # 5. Pie de página
    canvas.setStrokeColor(colors.HexColor('#CBD5E1'))
    canvas.setLineWidth(0.5)
    canvas.line(margin, 14 * mm, width - margin, 14 * mm)

    canvas.setFont('Helvetica-Oblique', 7.5)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(margin, 9.5 * mm, "Documento Estrictamente Confidencial — Propuesta de Valor Patrimonial Privada")
    canvas.drawRightString(width - margin, 9.5 * mm, f"Página {doc.page}  |  {datetime.now().strftime('%d/%m/%Y')}")

    canvas.restoreState()


def generate_propuesta_valor_pdf(
    prospect_id=None, 
    rut=None, 
    db_session=None, 
    custom_data=None,
    tasa_retorno_banca: float = 0.068,
    costo_banca: float = 0.028,
    tasa_retorno_fv: float = 0.0865,
    costo_fv: float = 0.0115
) -> bytes:
    """
    Genera un documento PDF formal y ejecutivo con la Propuesta de Valor Patrimonial.
    Retorna los bytes del archivo PDF listo para su descarga.
    """
    close_db = False
    if db_session is None:
        db_session = SessionLocal()
        close_db = True

    try:
        # 1. Obtener Prospecto
        prospect = None
        if prospect_id:
            prospect = db_session.query(Prospect).filter(Prospect.id == prospect_id).first()
        elif rut:
            clean_rut = rut.replace(".", "").replace("-", "").strip()
            fmt_rut = clean_rut[:-1] + "-" + clean_rut[-1].upper() if len(clean_rut) > 1 else clean_rut
            prospect = db_session.query(Prospect).filter(
                (Prospect.rut == fmt_rut) | (Prospect.rut == clean_rut) | (Prospect.rut == rut)
            ).first()

        # Variables base
        nombre_cliente = str(prospect.nombre) if prospect and prospect.nombre else (rut or "Cliente Preferencial")
        rut_cliente = str(prospect.rut) if prospect and prospect.rut else (rut or "S/I")

        # 2. Variables Macroeconómicas
        uf_val = get_uf_today() or 38000.0
        utm_val = get_utm_today() or 66000.0

        # 3. Perfil del Cliente
        perfil_inversion = "Moderado (50% RV / 50% RF)"
        regimen_patrimonial = "No Informado"
        edad_cliente = 52
        edad_actuarial = 52
        fecha_nac_str = ""
        sueldo_mensual = 6500000.0

        if prospect and prospect.profile:
            if getattr(prospect.profile, 'nivel_riesgo', None):
                perfil_inversion = prospect.profile.nivel_riesgo
            if getattr(prospect.profile, 'regimen_patrimonial', None):
                regimen_patrimonial = prospect.profile.regimen_patrimonial
            if getattr(prospect.profile, 'fecha_nacimiento', None):
                try:
                    fecha_nac_str = prospect.profile.fecha_nacimiento.strftime("%d/%m/%Y")
                except Exception:
                    pass
            if getattr(prospect.profile, 'edad', None):
                edad_cliente = int(prospect.profile.edad)
            elif getattr(prospect.profile, 'edad_actuarial', None):
                edad_cliente = int(prospect.profile.edad_actuarial)
            if getattr(prospect.profile, 'edad_actuarial', None):
                edad_actuarial = int(prospect.profile.edad_actuarial)
            else:
                edad_actuarial = edad_cliente
            if getattr(prospect.profile, 'sueldo_liquido_mensual', None) and prospect.profile.sueldo_liquido_mensual > 0:
                sueldo_mensual = float(prospect.profile.sueldo_liquido_mensual)
            elif getattr(prospect.profile, 'renta_anual_declarada', None) and prospect.profile.renta_anual_declarada > 0:
                sueldo_mensual = float(prospect.profile.renta_anual_declarada) / 12.0

        if custom_data:
            if "nombre_cliente" in custom_data and custom_data["nombre_cliente"]:
                nombre_cliente = str(custom_data["nombre_cliente"])
            if "perfil_inversion" in custom_data:
                perfil_inversion = custom_data["perfil_inversion"]
            if "regimen_patrimonial" in custom_data:
                regimen_patrimonial = custom_data["regimen_patrimonial"]
            if "edad_cliente" in custom_data and custom_data["edad_cliente"]:
                try:
                    edad_cliente = int(custom_data["edad_cliente"])
                except Exception:
                    pass
            if "fecha_nacimiento" in custom_data and custom_data["fecha_nacimiento"]:
                fecha_nac_str = str(custom_data["fecha_nacimiento"])
            if "edad_actuarial" in custom_data and custom_data["edad_actuarial"]:
                try:
                    edad_actuarial = int(custom_data["edad_actuarial"])
                except Exception:
                    edad_actuarial = edad_cliente
            if "sueldo_mensual" in custom_data:
                sueldo_mensual = float(custom_data["sueldo_mensual"])
            if "tasa_retorno_banca" in custom_data:
                tasa_retorno_banca = float(custom_data["tasa_retorno_banca"])
            if "costo_banca" in custom_data:
                costo_banca = float(custom_data["costo_banca"])
            if "tasa_retorno_fv" in custom_data:
                tasa_retorno_fv = float(custom_data["tasa_retorno_fv"])
            if "costo_fv" in custom_data:
                costo_fv = float(custom_data["costo_fv"])

        # Tasas Netas de Inversión y Porcentajes Formateados (Fuente Única de Verdad)
        tasa_neta_banca = tasa_retorno_banca - costo_banca
        tasa_neta_fv = tasa_retorno_fv - costo_fv

        pct_ret_banca = tasa_retorno_banca * 100.0
        pct_costo_banca = costo_banca * 100.0
        pct_neta_banca = tasa_neta_banca * 100.0

        pct_ret_fv = tasa_retorno_fv * 100.0
        pct_costo_fv = costo_fv * 100.0
        pct_neta_fv = tasa_neta_fv * 100.0

        # Capital Líquido
        capital_liquido = 0.0
        if custom_data and "capital_liquido" in custom_data and custom_data["capital_liquido"] > 0:
            capital_liquido = float(custom_data["capital_liquido"])
        elif prospect and prospect.portfolios:
            capital_liquido = sum([_safe_float(p.monto_clp or p.monto_original) for p in prospect.portfolios])
        if capital_liquido <= 0 and prospect and prospect.saldo_administrado:
            capital_liquido = _safe_float(prospect.saldo_administrado)
        if capital_liquido <= 0:
            capital_liquido = 120000000.0

        # Activos Inmobiliarios y Masa Total
        total_inmuebles_clp = 0.0
        total_avaluo_fiscal_clp = 0.0
        if prospect and prospect.properties:
            total_inmuebles_clp = sum([_safe_float(p.valor_comercial_estimado or (_safe_float(p.avaluo_fiscal) / uf_val)) * uf_val for p in prospect.properties])
            total_avaluo_fiscal_clp = sum([_safe_float(p.avaluo_fiscal) for p in prospect.properties])

        patrimonio_total_clp = capital_liquido + total_inmuebles_clp
        if custom_data and "patrimonio_total_clp" in custom_data and custom_data["patrimonio_total_clp"] > 0:
            patrimonio_total_clp = float(custom_data["patrimonio_total_clp"])
        elif patrimonio_total_clp < 150000000.0:
            patrimonio_total_clp = max(capital_liquido * 2.5, 380000000.0)

        patrimonio_total_uf = patrimonio_total_clp / uf_val

        # 4. Cálculos Pilar 1 (APV Régimen B)
        sim_apv = APVSimulator(uf_val, utm_val)
        sueldo_bruto = sueldo_mensual * 1.25
        tope_apv_mensual = 50.0 * uf_val
        res_apv = sim_apv.calcular_beneficio_regimen_b(sueldo_bruto, tope_apv_mensual)

        ahorro_tributario_mensual = res_apv.get("ahorro_tributario_mensual_clp", 0.0)
        ahorro_tributario_anual = res_apv.get("ahorro_tributario_anual_clp", 0.0)
        tasa_beneficio = res_apv.get("tasa_beneficio_efectivo", 35.0)

        if ahorro_tributario_anual <= 0:
            ahorro_tributario_anual = 50.0 * uf_val * 12.0 * 0.35
            ahorro_tributario_mensual = ahorro_tributario_anual / 12.0
            tasa_beneficio = 35.0

        ahorro_acum_5 = ahorro_tributario_anual * 5
        ahorro_acum_10 = ahorro_tributario_anual * 10

        # 5. Cálculos Pilar 2 (Proyección a 10 Años con Tasas Netas Dinámicas)
        anios = [0, 1, 3, 5, 7, 10]
        tasa_trad = tasa_neta_banca
        tasa_fv_val = tasa_neta_fv

        rows_proyeccion = []
        for t in anios:
            v_trad = capital_liquido * ((1.0 + tasa_trad) ** t)
            v_fv_base = capital_liquido * ((1.0 + tasa_fv_val) ** t)
            v_tax = sum([ahorro_tributario_anual * ((1.0 + tasa_fv_val) ** (t - i)) for i in range(1, t + 1)])
            v_fv_total = v_fv_base + v_tax
            alfa = v_fv_total - v_trad
            rows_proyeccion.append((t, v_trad, v_fv_total, alfa))

        # 6. Cálculos Pilar 3 (Blindaje Sucesorio)
        es_sociedad_conyugal = ("sociedad conyugal" in regimen_patrimonial.lower())
        if es_sociedad_conyugal:
            gananciales_uf = patrimonio_total_uf * 0.50
            masa_hered_uf = patrimonio_total_uf * 0.50
        else:
            gananciales_uf = 0.0
            masa_hered_uf = patrimonio_total_uf

        mitad_legit_uf = masa_hered_uf * 0.50
        cuarta_mej_uf = masa_hered_uf * 0.25
        cuarta_libre_uf = masa_hered_uf * 0.25

        ahorro_herencia_clp = patrimonio_total_clp * 0.075

        # 7. CONSTRUCCIÓN DEL DOCUMENTO REPORTLAB
        buffer = io.BytesIO()
        margin = 16 * mm
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=34 * mm,
            bottomMargin=18 * mm
        )

        styles = getSampleStyleSheet()

        # Estilos Tipográficos Ejecutivos
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0F172A'),
            alignment=1,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#0284C7'),
            alignment=1,
            spaceAfter=14
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=colors.white,
            backColor=colors.HexColor('#0F172A'),
            spaceBefore=10,
            spaceAfter=8,
            borderPadding=4
        )
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        )
        callout_style = ParagraphStyle(
            'CalloutStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11.5,
            textColor=colors.HexColor('#1E3A8A'),
            backColor=colors.HexColor('#EFF6FF'),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8
        )
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#1E293B'),
            alignment=1
        )
        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#0F172A'),
            alignment=1
        )

        elements = []

        # --- ENCABEZADO Y TÍTULO ---
        elements.append(Paragraph("PROPUESTA DE VALOR PATRIMONIAL", title_style))
        elements.append(Paragraph("ESTRUCTURACIÓN FINANCIERA, EFICIENCIA TRIBUTARIA Y BLINDAJE FAMILIAR 360°", subtitle_style))

        # --- FICHA RESUMEN DEL CLIENTE ---
        edad_desc = f"{edad_cliente} años"
        if fecha_nac_str and fecha_nac_str != "S/I":
            edad_desc = f"{edad_cliente} años (F. Nac: {fecha_nac_str})"

        data_cliente = [
            [
                Paragraph(f"<b>Cliente / Prospecto:</b> {nombre_cliente}", body_style),
                Paragraph(f"<b>RUT:</b> {rut_cliente}", body_style)
            ],
            [
                Paragraph(f"<b>Perfil Asignado:</b> {perfil_inversion.split('(')[0].strip()} &nbsp;|&nbsp; <b>Edad:</b> {edad_desc}", body_style),
                Paragraph(f"<b>Régimen Patrimonial:</b> {regimen_patrimonial}", body_style)
            ],
            [
                Paragraph(f"<b>Capital a Trasladar:</b> ${capital_liquido:,.0f} CLP (~{capital_liquido/uf_val:,.0f} UF)", body_style),
                Paragraph(f"<b>Plataforma:</b> ALTUS CORE AI / Principal Financial", body_style)
            ]
        ]
        t_cliente = Table(data_cliente, colWidths=[89 * mm, 89 * mm])
        t_cliente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_cliente)
        elements.append(Spacer(1, 8))

        # --- PILAR 1: OPTIMIZACIÓN TRIBUTARIA ---
        elements.append(Paragraph("1. EFICIENCIA TRIBUTARIA ACTIVA (APV RÉGIMEN B & IGC)", section_style))
        elements.append(Paragraph(
            "El Ahorro Previsional Voluntario bajo Régimen B (Art. 20 L D.L. 3.500) permite rebajar hasta <b>50 UF mensuales (600 UF anuales)</b> "
            "de la base imponible del Impuesto Único de Segunda Categoría / Impuesto Global Complementario. El beneficio tributario se traduce en una "
            "devolución o rebaja directa de impuestos en su Declaración de Renta anual (Formulario 22).",
            body_style
        ))

        data_pilar1 = [
            [
                Paragraph("Concepto Tributario", table_header_style),
                Paragraph("Monto Mensual", table_header_style),
                Paragraph("Monto Anual (F22)", table_header_style),
                Paragraph("Impacto en 10 Años", table_header_style)
            ],
            [
                Paragraph("Aporte Previsional Sugerido (Tope)", table_cell_style),
                Paragraph(f"${tope_apv_mensual:,.0f} CLP (50 UF)", table_cell_bold),
                Paragraph(f"${tope_apv_mensual * 12:,.0f} CLP (600 UF)", table_cell_bold),
                Paragraph("Inversión acumulada deducible", table_cell_style)
            ],
            [
                Paragraph("Ahorro Tributario Recuperado (SII)", table_cell_style),
                Paragraph(f"${ahorro_tributario_mensual:,.0f} CLP", table_cell_bold),
                Paragraph(f"<b>${ahorro_tributario_anual:,.0f} CLP</b>", table_cell_bold),
                Paragraph(f"<b>${ahorro_acum_10:,.0f} CLP</b>", table_cell_bold)
            ],
            [
                Paragraph("Subsidio Fiscal Efectivo Inmediato", table_cell_style),
                Paragraph(f"+{tasa_beneficio:.1f}%", table_cell_bold),
                Paragraph(f"+{tasa_beneficio:.1f}% s/aporte", table_cell_bold),
                Paragraph("Retorno garantizado por Ley", table_cell_style)
            ]
        ]
        t_pilar1 = Table(data_pilar1, colWidths=[55 * mm, 39 * mm, 43 * mm, 41 * mm])
        t_pilar1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_pilar1)
        elements.append(Paragraph(
            "<b>Impacto en la Decisión:</b> Al trasladar sus fondos a Principal APV, los impuestos recuperados se reinvierten automáticamente "
            "en portafolios internacionales de arquitectura abierta, generando un efecto bola de nieve imposible de replicar en la banca tradicional.",
            callout_style
        ))
        elements.append(Spacer(1, 6))

        # --- PILAR 2: PROYECCIÓN DE CAPITAL Y TRASLADO ---
        elements.append(Paragraph("2. PROYECCIÓN DE CAPITAL Y CREACIÓN DE RIQUEZA (TRASLADO A PRINCIPAL)", section_style))
        elements.append(Paragraph(
            f"Comparativa cuantitativa entre mantener el capital en la banca comercial tradicional (afectada por fondos cautivos con retorno bruto "
            f"estimado del <b>{pct_ret_banca:.1f}%</b> y costos de administración bancaria del <b>{pct_costo_banca:.2f}% anual</b>, arrojando un retorno neto del <b>{pct_neta_banca:.1f}% anual</b>) "
            f"versus la migración a la arquitectura abierta institucional de <b>Principal Financial Group & FV Asesorías (retorno bruto estimado del {pct_ret_fv:.2f}%, "
            f"costo optimizado del {pct_costo_fv:.2f}% anual y retorno proyectado neto del <b>{pct_neta_fv:.1f}% anual</b>)</b>, integrando además la reinversión anual del ahorro tributario recuperado.",
            body_style
        ))

        data_pilar2 = [
            [
                Paragraph("Horizonte", table_header_style),
                Paragraph(f"Banca Tradicional ({pct_neta_banca:.1f}%)", table_header_style),
                Paragraph(f"FV Asesorías & Principal ({pct_neta_fv:.1f}%)", table_header_style),
                Paragraph("Sobre-Retorno (Alfa Neto)", table_header_style)
            ]
        ]
        for t, v_t, v_fv, alfa in rows_proyeccion:
            label_ano = "Año 0 (Hoy)" if t == 0 else f"Año {t}"
            data_pilar2.append([
                Paragraph(label_ano, table_cell_bold),
                Paragraph(f"${v_t:,.0f}".replace(",", "."), table_cell_style),
                Paragraph(f"<b>${v_fv:,.0f}</b>".replace(",", "."), table_cell_bold),
                Paragraph(f"<font color='#059669'><b>+${alfa:,.0f}</b></font>".replace(",", "."), table_cell_bold)
            ])

        t_pilar2 = Table(data_pilar2, colWidths=[34 * mm, 46 * mm, 52 * mm, 46 * mm])
        t_pilar2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(t_pilar2)
        elements.append(Paragraph(
            f"<b>Ventaja Exclusiva de Traslado:</b> A 10 años, el diferencial acumulado a su favor es de <b>+${rows_proyeccion[-1][3]:,.0f} CLP</b> "
            f"(generando un sobre-retorno fiduciario neto superior en +{pct_neta_fv - pct_neta_banca:.1f}% anual sobre la banca tradicional). "
            "El traspaso de fondos entre administradoras es <b>100% neutro tributariamente</b>: no genera rescate de capital ni liquidación forzosa ante el SII.",
            callout_style
        ))
        
        # Salto de página limpio: Pilar 1 y 2 en Página 1; Pilar 3, Hoja de Ruta y Formalización en Página 2
        elements.append(PageBreak())

        # --- PILAR 3: BLINDAJE SUCESORIO ---
        elements.append(Paragraph("3. BLINDAJE SUCESORIO Y PROTECCIÓN FAMILIAR (LEY N° 16.271)", section_style))
        desc_matrimonio = "Al estar bajo <b>Sociedad Conyugal</b>, el 50% del acervo patrimonial califica como Gananciales del Cónyuge y se retira libre de impuestos de herencia." if es_sociedad_conyugal else "Estructuración testamentaria sobre la masa patrimonial para maximizar asignaciones preferentes."
        elements.append(Paragraph(
            f"{desc_matrimonio} Diseñamos la distribución legal para garantizar liquidez inmediata a sus herederos forzosos y evitar la venta "
            "apresurada de activos inmobiliarios para pagar el tributo sucesorio.",
            body_style
        ))

        data_pilar3 = [
            [
                Paragraph("Porción Legal (Código Civil)", table_header_style),
                Paragraph("% Asignado", table_header_style),
                Paragraph("Monto en UF", table_header_style),
                Paragraph("Monto Estimado (CLP)", table_header_style)
            ]
        ]
        if es_sociedad_conyugal:
            data_pilar3.append([
                Paragraph("Gananciales Cónyuge (Exento)", table_cell_bold),
                Paragraph("50.0%", table_cell_style),
                Paragraph(f"{gananciales_uf:,.1f} UF", table_cell_bold),
                Paragraph(f"${gananciales_uf * uf_val:,.0f}".replace(",", "."), table_cell_bold)
            ])
        data_pilar3.extend([
            [
                Paragraph("Mitad Legitimaria (Herederos Forzosos)", table_cell_style),
                Paragraph("25.0%" if es_sociedad_conyugal else "50.0%", table_cell_style),
                Paragraph(f"{mitad_legit_uf:,.1f} UF", table_cell_bold),
                Paragraph(f"${mitad_legit_uf * uf_val:,.0f}".replace(",", "."), table_cell_style)
            ],
            [
                Paragraph("Cuarta de Mejoras (Asignación Preferente)", table_cell_style),
                Paragraph("12.5%" if es_sociedad_conyugal else "25.0%", table_cell_style),
                Paragraph(f"{cuarta_mej_uf:,.1f} UF", table_cell_bold),
                Paragraph(f"${cuarta_mej_uf * uf_val:,.0f}".replace(",", "."), table_cell_style)
            ],
            [
                Paragraph("Cuarta de Libre Disposición (Libertad Total)", table_cell_style),
                Paragraph("12.5%" if es_sociedad_conyugal else "25.0%", table_cell_style),
                Paragraph(f"{cuarta_libre_uf:,.1f} UF", table_cell_bold),
                Paragraph(f"${cuarta_libre_uf * uf_val:,.0f}".replace(",", "."), table_cell_style)
            ]
        ])

        t_pilar3 = Table(data_pilar3, colWidths=[68 * mm, 26 * mm, 40 * mm, 44 * mm])
        t_pilar3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B45309')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        elements.append(t_pilar3)
        elements.append(Paragraph(
            f"<b>Blindaje con Pólizas Principal:</b> Se estima un ahorro fiscal de herencia de aprox. <b>${ahorro_herencia_clp:,.0f} CLP</b>. "
            "Las pólizas de Vida con Ahorro en Principal son <b>inembargables y quedan fuera de la masa hereditaria (Art. 17 N°3 LIR)</b>, "
            "entregando liquidez en 72 horas sin congelamiento ni esperas de posesión efectiva judicial.",
            callout_style
        ))
        elements.append(Spacer(1, 6))

        # --- HOJA DE RUTA / PRÓXIMOS PASOS ---
        elements.append(Paragraph("4. HOJA DE RUTA PARA MATERIALIZAR EL TRASLADO", section_style))
        data_steps = [
            [
                Paragraph("<b>Paso 1: Mandato Asesor</b><br/>Firma de mandato de asesoría patrimonial y apertura de cuenta de custodia en Principal (sin costo de apertura ni mantención).", body_style),
                Paragraph("<b>Paso 2: Traspaso Directo</b><br/>Instrucción formal de traslado entre administradoras. Los activos se transfieren sin rescates ni impacto tributario ante el SII.", body_style),
                Paragraph("<b>Paso 3: Monitoreo 360°</b><br/>Activación de cartolas consolidadas en Altus Core, rebalanceos tácticos periódicos y asesoría sucesoria continua.", body_style)
            ]
        ]
        t_steps = Table(data_steps, colWidths=[59.3 * mm, 59.3 * mm, 59.4 * mm])
        t_steps.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_steps)

        # --- SECCIÓN 5: FORMALIZACIÓN Y ACUERDO DE TRASLADO ---
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("5. FORMALIZACIÓN Y MANDATO DE ASESORÍA PATRIMONIAL", section_style))
        elements.append(Paragraph(
            "La presente propuesta de estructuración patrimonial constituye una simulación fiduciaria confidencial y establece la base de "
            "acuerdos para la apertura de cuentas de custodia institucional en Principal Financial Group bajo mandato de FV Asesorías e Inversiones. "
            "Condiciones vigentes por 30 días corridos.",
            body_style
        ))

        data_firmas = [
            [
                Paragraph("<b>POR FV ASESORÍAS E INVERSIONES</b><br/><br/><br/>________________________________________<br/><b>Asesor Patrimonial Senior</b><br/>Registro Asesores Acreditados CMF / Principal", body_style),
                Paragraph(f"<b>ACEPTACIÓN CLIENTE / MANDANTE</b><br/><br/><br/>________________________________________<br/><b>{nombre_cliente}</b><br/>RUT: {rut_cliente}<br/>Fecha: ____ / ____ / ________", body_style)
            ]
        ]
        t_firmas = Table(data_firmas, colWidths=[89 * mm, 89 * mm])
        t_firmas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_firmas)

        # Construir Documento
        doc.build(elements, onFirstPage=header_footer_propuesta, onLaterPages=header_footer_propuesta)
        buffer.seek(0)
        return buffer.getvalue()

    finally:
        if close_db:
            db_session.close()


try:
    import streamlit as st

    @st.cache_data(ttl=300, show_spinner=False)
    def get_cached_propuesta_pdf(
        rut: str, 
        custom_key: str = "",
        tasa_retorno_banca: float = 0.068,
        costo_banca: float = 0.028,
        tasa_retorno_fv: float = 0.0865,
        costo_fv: float = 0.0115
    ) -> bytes:
        """
        Versión cacheada en memoria (Streamlit) para descarga instantánea en la interfaz web.
        """
        return generate_propuesta_valor_pdf(
            rut=rut,
            tasa_retorno_banca=tasa_retorno_banca,
            costo_banca=costo_banca,
            tasa_retorno_fv=tasa_retorno_fv,
            costo_fv=costo_fv
        )
except Exception:
    def get_cached_propuesta_pdf(
        rut: str, 
        custom_key: str = "",
        tasa_retorno_banca: float = 0.068,
        costo_banca: float = 0.028,
        tasa_retorno_fv: float = 0.0865,
        costo_fv: float = 0.0115
    ) -> bytes:
        return generate_propuesta_valor_pdf(
            rut=rut,
            tasa_retorno_banca=tasa_retorno_banca,
            costo_banca=costo_banca,
            tasa_retorno_fv=tasa_retorno_fv,
            costo_fv=costo_fv
        )


if __name__ == "__main__":
    # Prueba rápida CLI
    pdf_bytes = generate_propuesta_valor_pdf(rut="12345678-9")
    with open("Propuesta_Valor_Demo.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"Propuesta generada con éxito ({len(pdf_bytes)} bytes)")
