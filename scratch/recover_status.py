import sqlite3
import glob
import os

db_files = glob.glob('**/*.db', recursive=True) + glob.glob('**/*.sqlite', recursive=True) + glob.glob('**/*.bak', recursive=True)
recovered_status = {}

for f in db_files:
    if not os.path.isfile(f) or 'crm_database.db' == os.path.basename(f):
        # We don't read the CURRENT db to avoid overwriting with its bad 'Pendiente' values
        if f == r'data\crm_database.db':
            continue
    try:
        conn = sqlite3.connect(f)
        cur = conn.cursor()
        cur.execute("SELECT rut, status_contacto FROM prospects WHERE status_contacto IS NOT NULL AND status_contacto != 'Pendiente'")
        rows = cur.fetchall()
        for rut, status in rows:
            # Prefer 'Contactado', 'Descartado', 'Cierre / Cliente' over 'No Contactar' or anything empty
            if rut not in recovered_status:
                recovered_status[rut] = status
            else:
                if status in ['Cierre / Cliente', 'Contactado', 'En Reunión', 'Propuesta Enviada']:
                    recovered_status[rut] = status
        conn.close()
    except Exception as e:
        pass

print(f'Total recovered non-Pendiente statuses: {len(recovered_status)}')

# Now apply to current DB
if len(recovered_status) > 0:
    conn = sqlite3.connect(r'data\crm_database.db')
    cur = conn.cursor()
    updates = 0
    for rut, status in recovered_status.items():
        # Check current status
        cur.execute("SELECT status_contacto FROM prospects WHERE rut = ?", (rut,))
        row = cur.fetchone()
        if row and row[0] == 'Pendiente':
            cur.execute("UPDATE prospects SET status_contacto = ? WHERE rut = ?", (status, rut))
            updates += 1
    conn.commit()
    conn.close()
    print(f'Successfully updated {updates} records in current DB.')
