import sqlite3
con = sqlite3.connect('data/processed/prospectos.db')
con.execute("UPDATE prospects SET nombre = 'Lupercio Aristol Briceño Cardenas' WHERE rut = '9536620-1'")
con.commit()
con.close()
print("Fixed Briceño in DB.")
