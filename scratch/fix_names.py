import sys
sys.path.append('.')
from src.database.connection import SessionLocal
from src.database.models import Prospect

def fix_names():
    db = SessionLocal()
    prospects = db.query(Prospect).all()
    count = 0
    for p in prospects:
        if p.nombre and p.nombre.isupper():
            # Apply title case
            original_name = p.nombre
            fixed_name = ' '.join([word.title() for word in original_name.split()])
            p.nombre = fixed_name
            count += 1
            
    db.commit()
    print(f"Fixed {count} names.")
    db.close()

if __name__ == '__main__':
    fix_names()
