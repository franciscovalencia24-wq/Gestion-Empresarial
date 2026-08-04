
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import engine
from sqlalchemy import text

# Lista de RUTs extraídos de la imagen del usuario
clientes_ruts = [
    "76107236-6", "8350143-k", "9697981-9", "8904562-2", "76352809-K",
    "6298500-3", "14283516-9", "10675057-2", "8757376-1", "7330058-4",
    "10123952-7", "8789145-3", "6560742-5", "13760515-5", "11400557-6",
    "6111512-9", "9448035-3", "76451622-2", "9632135-K", "10034620-6",
    "19837527-6", "20107864-4", "21515724-5", "15884242-4", "7012917-5"
]

def update_clients():
    try:
        with engine.connect() as con:
            ruts_clean = [r.upper() for r in clientes_ruts]
            
            # Formateamos manualmente los ruts para el query IN
            # O mejor, usamos bindparam dinámico si es posible, pero para 25 ruts podemos inyectar (con cuidado) o usar parámetros
            placeholders = ", ".join([f"'{r}'" for r in ruts_clean])
            query = text(f"UPDATE prospects SET es_cliente = 1 WHERE UPPER(rut) IN ({placeholders})")
            
            result = con.execute(query)
            con.commit()
            print(f"Update successful: {result.rowcount} records updated as Current Clients.")
            
    except Exception as e:
        print(f"Error updating clients: {e}")

if __name__ == "__main__":
    update_clients()
