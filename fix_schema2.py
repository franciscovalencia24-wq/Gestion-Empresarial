from src.database.connection import engine
import sqlalchemy

def run():
    con = engine.connect()
    try:
        con.execute(sqlalchemy.text('ALTER TABLE client_profiles ADD COLUMN segmento_cliente VARCHAR(50);'))
    except Exception as e:
        print(e)
    try:
        con.execute(sqlalchemy.text('ALTER TABLE client_profiles ADD COLUMN nivel_riesgo VARCHAR(50);'))
    except Exception as e:
        print(e)
    try:
        con.execute(sqlalchemy.text('ALTER TABLE client_profiles ADD COLUMN experiencia_inversiones VARCHAR(50);'))
    except Exception as e:
        print(e)
    con.commit()
    con.close()

if __name__ == "__main__":
    run()
