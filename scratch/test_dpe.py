import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.simulators.dpe_simulator import DPESimulator
import json
from dotenv import load_dotenv

def test():
    load_dotenv()
    pdf_path = r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\cotizaciones historicas.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
        
    sim = DPESimulator()
    print("Enviando al simulador...")
    res = sim.analyze_file(file_bytes, "cotizaciones historicas.pdf")
    
    if res["success"]:
        print(f"Devolución estimada: {res['total_devolucion_estimada']}")
        print(f"Meses con exceso: {len(res['meses_con_exceso'])}")
        
        # Save raw JSON for inspection
        with open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\dpe_raw.json", "w", encoding="utf-8") as f:
            if res.get('raw_json'):
                f.write(res['raw_json'])
            else:
                json.dump(res, f, indent=4)
        print("Raw JSON guardado.")
    else:
        print("Error:", res.get("error"))

if __name__ == "__main__":
    test()
