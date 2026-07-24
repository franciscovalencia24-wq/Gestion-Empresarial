"""
Motor de Enriquecimiento Unificado — BD SENIOR
Prioridad: Apollo.io (datos corporativos) → TransUnion (datos personales) → Sin enriquecimiento.
El dummy provider ya no se usa para producción. Solo existe para tests locales.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import text
from src.database.connection import engine

load_dotenv(override=True)

APOLLO_API_KEY   = os.getenv("APOLLO_API_KEY", "")
TRANSUNION_USER  = os.getenv("TRANSUNION_USER", "")
TRANSUNION_PASS  = os.getenv("TRANSUNION_PASS", "")


def get_active_provider() -> str:
    """Retorna el nombre del proveedor activo según las credenciales disponibles."""
    if APOLLO_API_KEY and len(APOLLO_API_KEY) > 10:
        return "apollo"
    if TRANSUNION_USER and TRANSUNION_PASS:
        return "transunion"
    return "none"


def enrich_prospect_apollo(rut: str, nombre: str = None, empresa: str = None) -> dict:
    """
    Enriquece un prospecto buscando en Apollo.io por nombre/empresa.
    Requiere APOLLO_API_KEY en .env
    """
    from src.enrichment.apollo_api import ApolloProvider
    apollo = ApolloProvider(api_key=APOLLO_API_KEY)

    results = []
    if empresa:
        results = apollo.search_people_by_company(empresa)
    elif nombre:
        # Búsqueda por nombre como fallback
        results, _ = apollo.search_prospects(job_titles=None, industries=None)

    if not results:
        return {"success": False, "source": "apollo", "message": "Sin resultados"}

    person = results[0]
    return {
        "success": True,
        "source":  "apollo",
        "nombre":  person.get("name", nombre),
        "email":   (person.get("email") or ""),
        "telefono": (person.get("phone_numbers") or [{}])[0].get("sanitized_number", ""),
        "linkedin": person.get("linkedin_url", ""),
        "cargo":    person.get("title", ""),
        "empresa":  person.get("organization", {}).get("name", empresa or ""),
    }


def enrich_prospect_transunion(rut: str) -> dict:
    """
    Enriquece un prospecto a través del scraper de TransUnion.
    Requiere TRANSUNION_USER y TRANSUNION_PASS en .env
    """
    try:
        from src.osint.transunion_scraper import TransUnionScraper
        scraper = TransUnionScraper()
        data = scraper.buscar_por_rut(rut)
        if data:
            return {"success": True, "source": "transunion", **data}
        return {"success": False, "source": "transunion", "message": "Sin resultados"}
    except Exception as e:
        return {"success": False, "source": "transunion", "message": str(e)}


def enrich_and_save(prospect_id: int, rut: str, nombre: str = None, empresa: str = None) -> dict:
    """
    Orquestador principal. Enriquece el prospecto con el mejor proveedor disponible
    y actualiza la base de datos si tiene éxito.
    """
    provider = get_active_provider()

    if provider == "none":
        return {
            "success": False,
            "message": (
                "No hay proveedores de enriquecimiento configurados. "
                "Agrega APOLLO_API_KEY o TRANSUNION_USER/TRANSUNION_PASS al archivo .env."
            ),
        }

    result = {}
    if provider == "apollo":
        result = enrich_prospect_apollo(rut, nombre, empresa)
    elif provider == "transunion":
        result = enrich_prospect_transunion(rut)

    # Persistir en la BD si hay datos nuevos
    if result.get("success"):
        updates = {}
        if result.get("telefono"):
            updates["telefono"] = result["telefono"]
        if result.get("email"):
            updates["email"] = result["email"]
        if result.get("nombre") and not nombre:
            updates["nombre"] = result["nombre"]

        if updates:
            set_clause = ", ".join([f"{k} = :{k}" for k in updates])
            updates["pid"] = prospect_id
            try:
                with engine.connect() as con:
                    con.execute(
                        text(f"UPDATE prospects SET {set_clause} WHERE id = :pid"),
                        updates,
                    )
                    con.commit()
                result["db_updated"] = True
            except Exception as e:
                result["db_error"] = str(e)

    return result


def run_batch_enrichment(limit: int = 50) -> dict:
    """
    Corre el enriquecimiento en lote sobre los prospectos que aún no tienen teléfono.
    Retorna un resumen de resultados.
    """
    provider = get_active_provider()
    if provider == "none":
        return {"error": "Sin proveedores configurados.", "procesados": 0, "exitosos": 0}

    with engine.connect() as con:
        rows = con.execute(text(
            "SELECT id, rut, nombre FROM prospects "
            "WHERE (telefono IS NULL OR telefono = 'No encontrado' OR telefono = 'None') "
            f"LIMIT {limit}"
        )).fetchall()

    total = len(rows)
    exitosos = 0
    for row in rows:
        res = enrich_and_save(row.id, row.rut, row.nombre)
        if res.get("success"):
            exitosos += 1

    return {
        "proveedor":  provider,
        "procesados": total,
        "exitosos":   exitosos,
        "tasa_exito": f"{(exitosos/total*100):.1f}%" if total > 0 else "N/A",
    }
