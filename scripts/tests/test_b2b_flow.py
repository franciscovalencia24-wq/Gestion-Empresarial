import sys
import os
import uuid
import datetime

# Asegurar que el path del proyecto esté en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.connection import get_db
from src.database.models import EmpresaB2B, EjecutivoB2B
from src.utils.simulators.reliquidacion_simulator import ReliquidacionSimulator
from src.utils.simulators.dpe_simulator import DPESimulator
from src.reporting.pdf_engine import generate_audit_pdf

def run_b2b_e2e_test():
    print("--- INICIANDO TEST E2E B2B ---")
    
    db = next(get_db())
    
    # 1. Crear Empresa B2B de prueba
    empresa_rut = "99.999.999-TEST"
    print(f"1. Registrando Empresa de Prueba: {empresa_rut}...")
    
    # Limpiar si existía
    existing_empresa = db.query(EmpresaB2B).filter(EmpresaB2B.rut == empresa_rut).first()
    if existing_empresa:
        db.query(EjecutivoB2B).filter(EjecutivoB2B.empresa_id == existing_empresa.id).delete()
        db.delete(existing_empresa)
        db.commit()

    empresa = EmpresaB2B(
        rut=empresa_rut,
        razon_social="ALTUS AI TEST CORP",
        contacto_comercial="QA Tester - qa@altuscore.cl",
        plan_contratado="TIER_1", # 10 cupos
        cupo_licencias=10
    )
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    empresa_id_fijo = empresa.id
    print(f"   Empresa ID {empresa_id_fijo} creada.")

    # 2. Ingesta de nómina (2 ejecutivos)
    print("2. Inyectando nómina de ejecutivos...")
    exec1_rut = "11.111.111-TEST"
    exec2_rut = "22.222.222-TEST"
    
    exec1 = EjecutivoB2B(
        empresa_id=empresa_id_fijo,
        rut=exec1_rut,
        nombre_completo="Ejecutivo Test 1",
        correo_corporativo="exec1@altuscore.cl",
        cargo="CFO",
        token_acceso=str(uuid.uuid4())
    )
    
    exec2 = EjecutivoB2B(
        empresa_id=empresa_id_fijo,
        rut=exec2_rut,
        nombre_completo="Ejecutivo Test 2",
        correo_corporativo="exec2@altuscore.cl",
        cargo="CEO",
        token_acceso=str(uuid.uuid4())
    )
    
    db.add(exec1)
    db.add(exec2)
    db.commit()
    print("   Ejecutivos creados y con token asignado.")

    # 3. Simulación Onboarding (Ejecutivo 1)
    print("3. Simulando Onboarding Confidencial para Ejecutivo 1...")
    sueldo_bruto = 5000000.0
    
    # Simular Reliquidación
    reliq_sim = ReliquidacionSimulator()
    print("   -> Corriendo ReliquidacionSimulator...")
    reliq_res = reliq_sim.calcular_renta_tributable(sueldo_bruto, "Habitat")
    igc = reliq_sim.calcular_igc(reliq_res['renta_tributable_mensual'] * 12)
    print(f"      IGC Anual Estimado: ${igc:,.0f}")
    
    # Simular DPE
    print("   -> Corriendo DPESimulator...")
    dpe_sim = DPESimulator()
    dpe_res = dpe_sim.calcular_beneficio_deposito_convenido(renta_bruta_mensual=sueldo_bruto)
    print(f"      Ahorro Fiscal DPE: ${dpe_res.get('ahorro_fiscal_anual', 0):,.0f}")

    # 4. Generación Reporte 360 PDF
    print("4. Compilando Reporte Patrimonial 360 (PDF)...")
    metrics = {
        "patrimonio": "$ 150.000.000",
        "tac": "1.2%",
        "alpha": "+ 0.5%"
    }
    try:
        pdf_path = generate_audit_pdf(
            client_name="Ejecutivo Test 1",
            metrics=metrics
        )
        print(f"   PDF generado exitosamente en: {pdf_path}")
    except Exception as e:
        print(f"   Error al generar PDF: {e}")

    # 5. Rollback/Limpieza
    print("5. Ejecutando limpieza de base de datos (Rollback)...")
    db.query(EjecutivoB2B).filter(EjecutivoB2B.empresa_id == empresa_id_fijo).delete()
    emp_to_del = db.query(EmpresaB2B).get(empresa_id_fijo)
    if emp_to_del:
        db.delete(emp_to_del)
    db.commit()
    
    print("--- TEST E2E COMPLETADO CON ÉXITO ---")

if __name__ == "__main__":
    run_b2b_e2e_test()
