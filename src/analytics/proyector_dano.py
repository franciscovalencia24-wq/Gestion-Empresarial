import sys
import os
from sqlalchemy import text

# CONFIGURACION DE RUTAS
base_path = os.path.abspath(os.curdir)
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from src.database.connection import engine

def buscar_fondo(criterio):
    """Busca un fondo en la base de datos local usando una palabra clave (Ej: BICE ACCIONES)"""
    with engine.connect() as con:
        # Busca por similitud de nombre
        res = con.execute(text("""
            SELECT nemotecnico, administradora, nombre_fondo, serie, tac_anual 
            FROM fondos_mutuos 
            WHERE UPPER(nombre_fondo) LIKE :c OR UPPER(administradora) LIKE :c
            ORDER BY tac_anual DESC LIMIT 10
        """), {"c": f"%{criterio.upper()}%"})
        return res.fetchall()

def analizar_dano_patrimonial(nem_competencia, nem_principal, monto_inversion, horizonte_anios, retorno_mercado_esperado=0.08):
    """
    Motor matemático para calcular la pérdida de dinero por comisiones ocultas.
    Asume que ambos fondos apuntan al mismo mercado (Ej: 8% bruto), pero descuenta la TAC capitalizada.
    """
    with engine.connect() as con:
        fondo_c = con.execute(text("SELECT * FROM fondos_mutuos WHERE nemotecnico = :n"), {"n": nem_competencia}).fetchone()
        fondo_p = con.execute(text("SELECT * FROM fondos_mutuos WHERE nemotecnico = :n"), {"n": nem_principal}).fetchone()

    if not fondo_c:
        print(f"Error: Fondo de competencia '{nem_competencia}' no encontrado.")
        return
    if not fondo_p:
        print(f"Error: Fondo tuyo '{nem_principal}' no encontrado.")
        return

    tac_c = (fondo_c.tac_anual or 0) / 100
    tac_p = (fondo_p.tac_anual or 0) / 100

    # Rentabilidad real del cliente (Retorno bruto - Comisiones)
    retorno_neto_competencia = retorno_mercado_esperado - tac_c
    retorno_neto_principal = retorno_mercado_esperado - tac_p

    # Formula de Interés Compuesto: VF = VI * (1 + r)^n
    vf_competencia = monto_inversion * ((1 + retorno_neto_competencia) ** horizonte_anios)
    vf_principal = monto_inversion * ((1 + retorno_neto_principal) ** horizonte_anios)

    diferencia_perdida = vf_principal - vf_competencia

    print("="*60)
    print(" PROYECTOR DE DANO PATRIMONIAL (FEE DRAG ANALYSIS)")
    print("="*60)
    print(f"Inversión inicial: ${monto_inversion:,.0f} CLP")
    print(f"Horizonte proyectado: {horizonte_anios} años")
    print(f"Retorno de Mercado Ilustrativo: {retorno_mercado_esperado*100:.1f}% Nominal anual (Antes de Inflación)\n")
    
    print("BANCO ACTUAL DEL CLIENTE:")
    print(f"  Fondo: {fondo_c.nombre_fondo} (Serie {fondo_c.serie}) - {fondo_c.administradora}")
    print(f"  Comisión Anual (TAC): {fondo_c.tac_anual}%")
    print(f"  Monto al final de {horizonte_anios} años: ${vf_competencia:,.0f} CLP\n")

    print("PROPUESTA PRINCIPAL:")
    print(f"  Fondo: {fondo_p.nombre_fondo} (Serie {fondo_p.serie}) - {fondo_p.administradora}")
    print(f"  Comisión Anual (TAC): {fondo_p.tac_anual}%")
    print(f"  Monto al final de {horizonte_anios} años: ${vf_principal:,.0f} CLP\n")

    print(f"CONCLUSION PARA EL CLIENTE:")
    print(f"  Si no se cambia a Principal hoy, perderá ${diferencia_perdida:,.0f} CLP")
    print(f"  durante este periodo, dinero que se irá exclusivamente al bolsillo del banco.")
    print("\n  *Nota Técnica: Proyección ilustrativa matemática aislada. Asume el mismo ")
    print(f"   retorno bruto nominal ({retorno_mercado_esperado*100:.1f}%) para ambos fondos. Retornos pasados no ")
    print("   garantizan retornos futuros. Cifras no incluyen descuento por inflación.")
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Proyector Patrimonial WealthTech")
    parser.add_argument("--buscar", type=str, help="Busca el Nemotecnico de un fondo")
    parser.add_argument("--comparar", nargs=4, metavar=('NEM_MALO', 'NEM_TUYO', 'MONTO', 'AÑOS'), 
                        help="Compara dos NEMs (Ej: FOO_A BAR_B 50000000 10)")
    parser.add_argument("--retorno", type=float, default=0.08, help="Tasa nominal a proyectar (Ej: 0.08 para 8%)")
    
    args = parser.parse_args()

    if args.buscar:
        resultados = buscar_fondo(args.buscar)
        print(f"\n RESULTADOS PARA '{args.buscar}':")
        for r in resultados:
            print(f"  NEM: {r.nemotecnico} | {r.administradora[:15]} | {r.nombre_fondo[:30]} Serie {r.serie} | TAC: {r.tac_anual}%")
    
    elif args.comparar:
        nem_c, nem_p, monto, anios = args.comparar
        analizar_dano_patrimonial(nem_c, nem_p, float(monto), int(anios), args.retorno)
    else:
        # Modo Interactivo simple de demostración
        print(" Modo demo iniciado. (Usa --help para comandos)")
        print("Buscaremos 'SANTANDER GLOBAL' vs algún fondo para la demostración...")
        
        # Encontramos cualquier NEM del Santander y uno para Principal como ejemplo
        with engine.connect() as con:
            fondo_malo = con.execute(text("SELECT nemotecnico FROM fondos_mutuos WHERE UPPER(administradora) LIKE '%SANTANDER%' ORDER BY tac_anual DESC LIMIT 1")).fetchone()
            fondo_bueno = con.execute(text("SELECT nemotecnico FROM fondos_mutuos WHERE UPPER(administradora) LIKE '%PRINCIPAL%' AND tac_anual < 1.5 LIMIT 1")).fetchone()
            
            if fondo_malo and fondo_bueno:
                analizar_dano_patrimonial(fondo_malo[0], fondo_bueno[0], 50000000, 15, args.retorno)
            else:
                print("No se encontraron fondos suficientes en la base de datos para la demo.")
