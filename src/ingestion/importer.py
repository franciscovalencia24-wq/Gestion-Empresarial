import os
import glob
import pandas as pd
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal, engine
from src.database.models import Prospect, Base
from src.ingestion.cleaner import clean_rut_chileno, clean_phone_number, clean_amount

def ingest_excel(file_path: str, db: Session):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return

    inserted = 0
    updated = 0
    
    col_upper = {str(c).upper().strip(): c for c in df.columns}
    
    def get_real_col(possible_names):
        for p in possible_names:
            p_upper = p.upper()
            for col_clean, real_col in col_upper.items():
                if p_upper in col_clean:
                    return real_col
        return None

    rut_col = get_real_col(['RUT CLIENTE', 'RUT'])
    if not rut_col:
        print(f"No se encontró columna 'RUT CLIENTE' en {file_path}. Abortando.")
        return
        
    nombre_col = get_real_col(['NOMBRE CLIENTE', 'NOMBRE'])
    tel_col = get_real_col(['TELEFONO'])
    email_col = get_real_col(['MAIL', 'EMAIL'])
    ciudad_col = get_real_col(['SUCURSAL', 'CIUDAD'])
    nombre_asesor_col = get_real_col(['NOMBRE ASESOR'])
    supervisor_col = get_real_col(['SUPEVISOR', 'SUPERVISOR']) 
    tipo_negocio_col = get_real_col(['TIPO DE NEGOCIO'])
    monto_suscrito_col = get_real_col(['AUM SUSCRITO', 'AUM'])
    saldo_admin_col = get_real_col(['SALDO ADMINISTRADO', 'SALDO'])
    origen_info_col = get_real_col(['ORIGEN INFORMACIÓN', 'ORIGEN'])
    tit_prof_col = get_real_col(['TITULO PROFESIONAL', 'TITULO'])
    obs_col = get_real_col(['OBSERVACIONES'])
    es_cliente_col = get_real_col(['ES CLIENTE', 'ES_CLIENTE', 'CLIENTE VIGENTE'])
    rrll_nombre_col = get_real_col(['NOMBRE RRLL', 'REPRESENTANTE', 'RRLL'])
    rrll_rut_col = get_real_col(['RUT RRLL'])

    # Diccionario de memoria RAM para hacer una caché de RUTs (100% resistente a duplicados intra-documento e híbridos)
    seen_prospects = {}

    for index, row in df.iterrows():
        raw_rut = row.get(rut_col)
        rut_clean = clean_rut_chileno(raw_rut)
        if not rut_clean:
            continue
            
        def clean_str(val):
            return str(val).strip() if pd.notna(val) else None

        # 1. Buscamos primero en el caché veloz de memoria (por si lo acabamos de registrar en la fila anterior)
        prospect = seen_prospects.get(rut_clean)
        
        # 2. Si no estaba en memoria reciente, miramos la base de datos por si estaba del Excel pasado
        if not prospect:
            prospect = db.query(Prospect).filter(Prospect.rut == rut_clean).first()
            if prospect:
                seen_prospects[rut_clean] = prospect # Lo cacheamos para futuras repeticiones
        
        nombre = clean_str(row.get(nombre_col)) if nombre_col else None
        telefono = clean_phone_number(row.get(tel_col)) if tel_col else None
        email = clean_str(row.get(email_col)) if email_col else None
        ciudad = clean_str(row.get(ciudad_col)) if ciudad_col else None
        
        nombre_asesor = clean_str(row.get(nombre_asesor_col)) if nombre_asesor_col else None
        supervisor = clean_str(row.get(supervisor_col)) if supervisor_col else None
        tipo_negocio = clean_str(row.get(tipo_negocio_col)) if tipo_negocio_col else None
        origen_info = clean_str(row.get(origen_info_col)) if origen_info_col else None
        tit_prof = clean_str(row.get(tit_prof_col)) if tit_prof_col else None
        obs = clean_str(row.get(obs_col)) if obs_col else None
        
        monto_suscrito = clean_amount(row.get(monto_suscrito_col)) if monto_suscrito_col else None
        saldo_admin = clean_amount(row.get(saldo_admin_col)) if saldo_admin_col else None
        
        nombre_rrll = clean_str(row.get(rrll_nombre_col)) if rrll_nombre_col else None
        rut_rrll = clean_str(row.get(rrll_rut_col)) if rrll_rut_col else None
        
        es_cliente_val = clean_str(row.get(es_cliente_col)) if es_cliente_col else "NO"
        es_cliente_bool = 1 if str(es_cliente_val).strip().upper() in ["SI", "SÍ", "1", "TRUE", "YES", "CLIENTE"] else 0
        
        if prospect:
            if nombre and not prospect.nombre: prospect.nombre = nombre
            if telefono and not prospect.telefono: prospect.telefono = telefono
            if email and not prospect.email: prospect.email = email
            if ciudad and not prospect.ciudad: prospect.ciudad = ciudad
            
            if nombre_asesor and not prospect.nombre_asesor: prospect.nombre_asesor = nombre_asesor
            if supervisor and not prospect.supervisor: prospect.supervisor = supervisor
            if tipo_negocio and not prospect.tipo_negocio: prospect.tipo_negocio = tipo_negocio
            if origen_info and not prospect.origen_info: prospect.origen_info = origen_info
            if tit_prof and not prospect.titulo_profesional: prospect.titulo_profesional = tit_prof
            
            if monto_suscrito and (not prospect.monto_suscrito or monto_suscrito > prospect.monto_suscrito): 
                prospect.monto_suscrito = monto_suscrito
            if saldo_admin and (not prospect.saldo_administrado or saldo_admin > prospect.saldo_administrado): 
                prospect.saldo_administrado = saldo_admin
                
            if obs and obs != prospect.observaciones:
                prospect.observaciones = f"{prospect.observaciones} | {obs}" if prospect.observaciones else obs
            if es_cliente_col:
                prospect.es_cliente = es_cliente_bool
            if nombre_rrll and not prospect.nombre_rrll: prospect.nombre_rrll = nombre_rrll
            if rut_rrll and not prospect.rut_rrll: prospect.rut_rrll = rut_rrll
            updated += 1
        else:
            prospect = Prospect(
                rut=rut_clean, nombre=nombre, telefono=telefono,
                email=email, ciudad=ciudad,
                nombre_asesor=nombre_asesor, supervisor=supervisor,
                tipo_negocio=tipo_negocio, origen_info=origen_info,
                titulo_profesional=tit_prof, observaciones=obs,
                monto_suscrito=monto_suscrito, saldo_administrado=saldo_admin,
                es_cliente=es_cliente_bool,
                nombre_rrll=nombre_rrll, rut_rrll=rut_rrll
            )
            # Guardamos el prospecto por primera vez en base de datos
            db.add(prospect)
            # Lo ponemos en nuestro caché de memoria instantáneo!
            seen_prospects[rut_clean] = prospect
            inserted += 1
            
    db.commit()
    print(f"Archivo procesado: {inserted} nuevos, {updated} actualizados.")

def run_import_all(raw_folder: str = "data/raw"):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not os.path.exists(raw_folder):
            os.makedirs(raw_folder, exist_ok=True)
            print(f"Directorio creado en {raw_folder}.")
            return

        excel_files = glob.glob(os.path.join(raw_folder, "*.xlsx"))
        if not excel_files:
            print(f"No se encontraron archivos .xlsx en {raw_folder}.")
            return
            
        for file in excel_files:
            print(f"Ingestando {file}...")
            ingest_excel(file, db)
            
    except Exception as e:
        print(f"Error crítico: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_import_all()
