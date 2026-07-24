import time
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from src.database.connection import SessionLocal
from src.database.models import Prospect

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-CL,es;q=0.9",
}

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.upper()

def get_edition_id(date_str):
    """Obtiene el ID de edición desde la página de índice del día."""
    url = f"https://www.diariooficial.interior.gob.cl/edicionelectronica/index.php?date={date_str}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        m = re.search(r"edition=(\d+)", r.text)
        return m.group(1) if m else None
    except:
        return None

def fetch_section(date_str, edition_id, section):
    """Descarga el HTML crudo de una sección y lo parsea con BeautifulSoup."""
    url = f"https://www.diariooficial.interior.gob.cl/edicionelectronica/{section}.php?date={date_str}&edition={edition_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"Error descargando {section} de {date_str}: {e}")
        return None

def extract_entries(soup):
    """
    Extrae entradas del HTML del Diario Oficial.
    La estructura real es: tabla > tbody > tr
    Cada 'bloque' de empresa/acto tiene celdas con el TIPO, NOMBRE y detalles.
    """
    entries = []
    if not soup:
        return entries

    # El DO usa dos tipos de <tr>: los de título/encabezado y los de contenido
    rows = soup.find_all('tr')

    current_tipo = ""
    for row in rows:
        cells = row.find_all('td')
        row_text = row.get_text(" ", strip=True)

        if not row_text or len(row_text) < 5:
            continue

        # Guardamos el texto del tipo (CONSTITUCION, MODIFICACION, etc.)
        row_norm = normalize_text(row_text)
        for kw in ["CONSTITUCION", "MODIFICACION", "DISOLUCION", "FUSION"]:
            if kw in row_norm and len(row_text) < 80:
                current_tipo = row_text.strip()
                break

        # Buscar el link al PDF (CVE) en la fila
        link_tag = row.find('a', href=re.compile(r'\.pdf'))
        if link_tag:
            href = link_tag.get('href', '')
            # Construimos la entrada con el texto completo de esta fila + tipo
            entry = {
                "texto": f"[{current_tipo}] {row_text}".strip(),
                "link": href if href.startswith('http') else f"https://www.diariooficial.interior.gob.cl{href}",
                "cve": re.search(r'/(\d+)\.pdf', href).group(1) if re.search(r'/(\d+)\.pdf', href) else "",
            }
            entries.append(entry)

    return entries

def calculate_score(text):
    score = 30
    t = normalize_text(text)
    if "EXPROPIACION" in t: return 95
    if "POSESION" in t or "SUCESION" in t: return 90
    if "COMPRAVENTA" in t: return 85
    if "CONSTITUCION" in t: return 80
    if "FUSION" in t: return 80
    if "FINIQUITO" in t or "INDEMNIZACION" in t: return 75
    if "NEGOCIACION" in t or "CONVENIO" in t: return 70
    if "MODIFICACION" in t: return 40
    return score

def save_entry(texto, score, fecha, link, cve):
    db = SessionLocal()
    try:
        exists = db.query(Prospect).filter(Prospect.link_fuente == link).first()
        if not exists:
            new_p = Prospect(
                rut=f"DO-{cve}" if cve else f"DO-{int(time.time()*1000)}",
                nombre=texto[:190],
                score_liquidez=score,
                ultimo_evento=texto[:490],
                fecha_hallazgo=fecha,
                link_fuente=link,
                origen_web=1,
                status_contacto="Pendiente"
            )
            db.add(new_p)
            db.commit()
            return "NUEVO"
        return "IGNORADO"
    finally:
        db.close()

def run_scraper(region_target=None, days_back=30):
    """
    Motor OSINT V7 - usa requests + BeautifulSoup.
    Analiza el HTML real del Diario Oficial sin JavaScript ni buscadores.
    Si region_target=None, procesa TODO Chile.
    """
    stats = {"nuevos": 0, "actualizados": 0, "procesadas": 0}
    region_norm = normalize_text(region_target) if region_target else ""

    KEYWORDS = [
        "CONSTITUCION", "EXPROPIACION", "POSESION EFECTIVA", "SUCESION",
        "COMPRAVENTA", "CESION", "FUSION", "FINIQUITO", "INDEMNIZACION",
        "NEGOCIACION", "CONVENIO"
    ]

    SECTIONS = ["empresas_cooperativas", "publicaciones_judiciales", "normas_particulares", "avisos_destacados"]

    # Calculamos el rango de fechas
    start_date = datetime.now() - timedelta(days=days_back)

    current = datetime.now()
    while current >= start_date:
        if current.weekday() == 6:  # Domingo
            current -= timedelta(days=1)
            continue

        date_str = current.strftime("%d-%m-%Y")
        print(f"Procesando: {date_str}...")

        edition_id = get_edition_id(date_str)
        if not edition_id:
            print(f"  Sin edición para {date_str}, saltando.")
            current -= timedelta(days=1)
            continue

        for sec in SECTIONS:
            soup = fetch_section(date_str, edition_id, sec)
            entries = extract_entries(soup)
            stats["procesadas"] += len(entries)

            for entry in entries:
                t_norm = normalize_text(entry["texto"])

                # Filtro: debe tener alguna keyword de interés
                kw_match = any(kw in t_norm for kw in KEYWORDS)
                if not kw_match:
                    continue

                # Filtro de región (si se especifica)
                if region_norm and region_norm not in t_norm:
                    continue

                score = calculate_score(entry["texto"])
                res = save_entry(entry["texto"], score, date_str, entry["link"], entry["cve"])
                if res == "NUEVO":
                    stats["nuevos"] += 1
                    print(f"  + NUEVO LEAD: {entry['texto'][:80]}... (Score: {score})")

        current -= timedelta(days=1)
        time.sleep(0.5)  # Pausa educada para no sobrecargar el servidor

    print(f"\nResumen: {stats}")
    return stats
