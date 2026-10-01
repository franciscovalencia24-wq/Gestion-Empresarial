import os
import sys
import time
import tempfile
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 1. Reporte 360
from src.utils.pdf_generator import generate_reporte_360_from_markdown
# 2. Propuesta APV
from src.utils.pdf_generator_apv import generar_pdf_apv
# 3. Informe DPE
from src.utils.pdf_generator_dpe import generate_dpe_pdf
# 4. Informe Reliquidación
from src.utils.pdf_generator_reliquidacion import generate_reliquidacion_pdf
# 5. Propuesta Cuenta 2
from src.utils.pdf_generator_cuenta2 import generate_cuenta2_pdf
# 6. Reporte 360 Word DOCX
from src.utils.docx_generator_macro import generar_docx_reporte_360

def test_reporte_360():
    md_content = """# Reporte Patrimonial 360
    ## Resumen Ejecutivo
    Este es un reporte de prueba generado automáticamente.
    
    ### 🛡️ Auditoría Patrimonial de Seguros

    #### Desglose y Clasificación de Pólizas
    <table class="table-360">
    <thead><tr><th>Compañía</th><th>Contratante</th><th>Tipo de Cobertura</th><th>Destino del Beneficio</th></tr></thead>
    <tbody>
    <tr class="row-even"><td>Banco Estado</td><td>BANCO ESTADO CORREDORES</td><td>Desgravamen Bancario/Retail</td><td>Acreedor (Banco) / Mixto</td></tr>
    <tr class="row-odd"><td>Consorcio Nacional</td><td>JUAN PEREZ</td><td>Vida Individual</td><td>Familia / Herederos</td></tr>
    </tbody></table>

    #### Resumen Financiero y Brecha Sucesoria
    <table class="table-360">
    <thead><tr><th>Métrica Sucesoria</th><th>Monto (UF)</th></tr></thead>
    <tbody>
    <tr class="row-even"><td>Capital Vida Total (Bruto)</td><td>1,000 UF</td></tr>
    <tr class="row-odd"><td>Deuda Hipotecaria Total</td><td>3,500 UF</td></tr>
    <tr class="row-even"><td><b>Capital Líquido Familiar</b> (Real)</td><td class="highlight-val">0 UF</td></tr>
    <tr class="row-odd"><td>Brecha Sucesoria Proyectada (4%)</td><td class="highlight-val">2,000 UF</td></tr>
    <tr class="row-even"><td><b>Déficit Patrimonial / Descalce</b></td><td class="highlight-deficit">2,000 UF</td></tr>
    </tbody></table>

    <div class='alert-danger'><b>🚨 Riesgo de Liquidez Sucesoria:</b> La cobertura líquida para la familia es de $0 CLP. El patrimonio queda expuesto a remate o iliquidez.</div>

    <div class='tax-callout' style='border-left: 4px solid #ffc107;'><b>🔍 Duplicidad y Dispersión:</b> Se detectan múltiples pólizas dispersas (2) que no generan valor patrimonial eficiente.</div>

    <div class='callout-principal'><b>💼 Propuesta de Canje y Reestructuración con PRINCIPAL:</b> Proponer la desintermediación de seguros bancarios. Recomendar un Seguro de Vida con Ahorro Preferente en PRINCIPAL (Art. 17 N°8).</div>
    """
    start = time.time()
    pdf_bytes = generate_reporte_360_from_markdown(md_content, title="Reporte 360 de Prueba")
    end = time.time()
    
    assert pdf_bytes is not None and len(pdf_bytes) > 0, "PDF vacío"
    return len(pdf_bytes), end - start

def test_apv_proposal():
    df_proy = pd.DataFrame([
        {"Año": 5, "Ahorro Obligatorio (10%)": 0, "APV Régimen A": 1000000, "APV Régimen B": 0, "Depósito Convenido": 0},
        {"Año": 10, "Ahorro Obligatorio (10%)": 0, "APV Régimen A": 2000000, "APV Régimen B": 0, "Depósito Convenido": 0},
        {"Año": 25, "Ahorro Obligatorio (10%)": 0, "APV Régimen A": 5000000, "APV Régimen B": 0, "Depósito Convenido": 0}
    ])
    
    start = time.time()
    pdf_path = generar_pdf_apv(
        rut="12.345.678-9",
        nombre="Test APV Cliente",
        sueldo=3000000,
        aporte=100000,
        aporte_dc_anual=0,
        anos=25,
        rentabilidad=5.0,
        ahorro_anual=0,
        bono_estado=180000,
        df_proy=df_proy
    )
    end = time.time()
    
    assert os.path.exists(pdf_path), "No se generó el archivo de APV"
    size = os.path.getsize(pdf_path)
    os.remove(pdf_path)
    
    return size, end - start

def test_dpe_report():
    data = {
        "nombre": "Test DPE Cliente",
        "rut": "12.345.678-9",
        "total_historico_calculado": 5000000,
        "monto_exceso_estimado": 1500000,
        "estimacion_reajustabilidad": 200000,
        "total_proyectado_recuperar": 1700000,
        "registros": [
            {"empleador": "Empresa A", "rut_empleador": "76.123.456-7", "meses_exceso": 10, "monto_base": 1500000}
        ]
    }
    
    tmp_path = os.path.join(tempfile.gettempdir(), "test_dpe.pdf")
    start = time.time()
    generate_dpe_pdf(data, tmp_path)
    end = time.time()
    
    assert os.path.exists(tmp_path), "No se generó el archivo de DPE"
    size = os.path.getsize(tmp_path)
    os.remove(tmp_path)
    
    return size, end - start

def test_reliquidacion_report():
    data = {
        "nombre": "Test Reliquidación",
        "rut": "12.345.678-9",
        "renta_total": 45000000,
        "igc_original": 2000000,
        "igc_reliquidado": 1500000,
        "saldo_a_favor": 500000,
        "tabla_meses": [
            {"Mes": "Enero", "Renta": 3000000, "Retención": 300000},
            {"Mes": "Febrero", "Renta": 4000000, "Retención": 400000}
        ]
    }
    
    tmp_path = os.path.join(tempfile.gettempdir(), "test_reliq.pdf")
    start = time.time()
    generate_reliquidacion_pdf(data, tmp_path)
    end = time.time()
    
    assert os.path.exists(tmp_path), "No se generó el archivo de Reliquidación"
    size = os.path.getsize(tmp_path)
    os.remove(tmp_path)
    
    return size, end - start

def test_cuenta2_report():
    data = {
        "nombre": "Test Cuenta 2",
        "rut": "12.345.678-9",
        "horizonte_anios": 10,
        "monto_apertura": 10000000,
        "aporte_mensual": 200000,
        "tasa_anual": 6.5,
        "total_aportes": 34000000,
        "rentabilidad_total": 12000000,
        "saldo_final": 46000000,
        "rentabilidad_exenta": 12000000,
        "rentabilidad_afecta": 0,
        "limite_4000_uf_clp": 150000000
    }
    
    tmp_path = os.path.join(tempfile.gettempdir(), "test_cta2.pdf")
    start = time.time()
    generate_cuenta2_pdf(data, tmp_path)
    end = time.time()
    
    assert os.path.exists(tmp_path), "No se generó el archivo de Cuenta 2"
    size = os.path.getsize(tmp_path)
    os.remove(tmp_path)
    
    return size, end - start

def test_reporte_360_docx():
    data_360 = {
        'current_rut': '12.345.678-9',
        'propiedades': [
            {'nombre': 'Depto 1', 'destino': 'Habitacional', 'valor_uf': 5000, 'arriendo': 600000, 'dividendo': 400000, 'gastos_comunes': 50000, 'contribuciones': 150000, 'seguros': 10000, 'flujo_neto': 100000, 'cap_rate': 3.5}
        ],
        'inversiones': [
            {'nombre': 'Fondo A', 'tipo': 'Renta Variable', 'riesgo': 'Alto', 'moneda': 'CLP', 'monto': 10000000, 'tir': 8.5, 'rentabilidad': 12.0}
        ],
        'flujo_sucesorio': {
            'gastos_vida': 1500000,
            'sueldos': 500000,
            'compromisos': 200000,
            'seguros': 150000,
            'ingresos_pasivos': 2000000
        }
    }
    
    tmp_path = os.path.join(tempfile.gettempdir(), "test_reporte_360.docx")
    start = time.time()
    res_path = generar_docx_reporte_360(data_360, tmp_path)
    end = time.time()
    
    assert os.path.exists(res_path), "No se generó el archivo de DOCX 360"
    size = os.path.getsize(res_path)
    os.remove(res_path)
    
    return size, end - start

def run_suite():
    tests = [
        ("1. Reporte 360 (Markdown a PDF)", test_reporte_360),
        ("2. Propuesta APV", test_apv_proposal),
        ("3. Informe DPE (Excesos AFP)", test_dpe_report),
        ("4. Informe Reliquidación", test_reliquidacion_report),
        ("5. Propuesta Cuenta 2", test_cuenta2_report),
        ("6. Reporte 360 Word (.docx)", test_reporte_360_docx)
    ]
    
    print("-" * 65)
    print(f"{'SUITE DE PRUEBAS DE GENERADORES PDF - ALTUS CORE':^65}")
    print("-" * 65)
    print(f"{'Módulo':<40} | {'Estado':<6} | {'Tamaño':<8} | {'Tiempo'}")
    print("-" * 65)
    
    success_count = 0
    
    for name, test_func in tests:
        try:
            size_bytes, duration = test_func()
            size_kb = f"{size_bytes / 1024:.1f} KB"
            time_str = f"{duration:.2f}s"
            print(f"{name:<40} | [OK]   | {size_kb:<8} | {time_str}")
            success_count += 1
        except Exception as e:
            import traceback
            print(f"{name:<40} | [FAIL] | -------- | Error: {str(e)}")
            traceback.print_exc()
            
    print("-" * 65)
    print(f"Resultado: {success_count}/{len(tests)} pasaron correctamente.")
    print("-" * 65)
    
if __name__ == "__main__":
    run_suite()
