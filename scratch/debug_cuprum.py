import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.simulators.dpe_simulator import DPESimulator

sim = DPESimulator()
with open(r"C:\Users\franc\OneDrive\Documentos\PROYECTOS\BD SENIOR\scratch\cotizaciones historicas.pdf", "rb") as f:
    file_bytes = f.read()

res = sim.analyze_file(file_bytes, "cotizaciones historicas.pdf")
print("Devolución:", res.get("total_devolucion_estimada"))
print("Meses:", len(res.get("meses_con_exceso", [])))
for m in res.get("meses_con_exceso", [])[:5]:
    print(m)
