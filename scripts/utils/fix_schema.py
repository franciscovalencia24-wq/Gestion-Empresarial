from src.database.connection import engine
import sqlalchemy

def fix():
    with engine.connect() as con:
        try:
            con.execute(sqlalchemy.text("ALTER TABLE client_profiles ADD COLUMN fecha_nacimiento DATE;"))
            print("Added fecha_nacimiento")
        except Exception as e:
            print(f"Error 1: {e}")
            
        try:
            con.execute(sqlalchemy.text("ALTER TABLE client_profiles ADD COLUMN edad_actuarial INTEGER;"))
            print("Added edad_actuarial")
        except Exception as e:
            print(f"Error 2: {e}")
            
        con.commit()

if __name__ == "__main__":
    fix()
