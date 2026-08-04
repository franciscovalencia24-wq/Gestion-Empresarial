import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from src.osint.property_lookup_engine import PropertyLookupEngine

def test_lookup():
    print("Testing PropertyLookupEngine...")
    engine = PropertyLookupEngine()
    
    rut_test = "6298500-3"
    results = engine.lookup_properties_by_rut(rut_test, "Test Client")
    print(f"Lookup results for RUT {rut_test}: {len(results)} items found.")
    for r in results:
        print(" - Property:", r.get("Nombre/Alias"), "| ROL:", r.get("ROL"), "| Sugerido UF:", r.get("Valor Sugerido AI (UF)"))

    # Test estimation method directly
    uf_val, factor = engine.estimate_commercial_value_uf(50000000.0, "LAS CONDES", "HABITACIONAL")
    print(f"Estimation test for 50M CLP in Las Condes: {uf_val} UF (factor {factor}x)")

if __name__ == "__main__":
    test_lookup()
