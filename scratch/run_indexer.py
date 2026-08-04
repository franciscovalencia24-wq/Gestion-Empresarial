# Script de indexacion: procesa todos los PDFs de conocimiento y los almacena en ChromaDB.
# Ejecutar desde: BD SENIOR/
import sys
import os

sys.path.insert(0, "src")
from intelligence.rag_advisor import RAGAdvisorV2

print("=" * 60)
print("  BD SENIOR — Indexador de Conocimiento Normativo")
print("=" * 60)

advisor = RAGAdvisorV2()

print("\n[1] Rutas configuradas:")
for p in advisor.data_paths:
    if os.path.exists(p):
        pdf_count = sum(
            len([f for f in files if f.lower().endswith(".pdf")])
            for _, _, files in os.walk(p)
        )
        print(f"    OK  {p}  ({pdf_count} PDFs)")
    else:
        print(f"    --  {p}  (no encontrado)")

print("\n[2] Iniciando indexacion completa (force_reload=True)...")
ok = advisor.index_documents(force_reload=True)

if ok:
    summary = advisor.get_knowledge_summary()
    print("\n" + "=" * 60)
    print("  INDEXACION COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(f"  Total chunks vectorizados : {summary.get('total_chunks', 'N/A')}")
    print(f"  Directorio persistido     : {summary.get('persist_dir', 'N/A')}")
    print(f"  Estado                    : {summary.get('status', 'N/A')}")

    print("\n[3] Prueba de consulta sobre los nuevos documentos...")
    q = "Que es el Articulo 107 y cuales son sus requisitos para exencion de impuesto?"
    print(f"    Pregunta: {q}")
    respuesta = advisor.ask(q)
    print(f"\n    Respuesta:\n{respuesta}")
else:
    print("\n[ERROR] La indexacion fallo. Revisa los mensajes anteriores.")
    sys.exit(1)
