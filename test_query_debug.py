import os
import langchain
from src.intelligence.query_analyst import MultimodalQueryAnalyst

langchain.debug = True

if __name__ == "__main__":
    analyst = MultimodalQueryAnalyst()
    
    q_text = "Calcula la rentabilidad real del portafolio, sugiere qué vender priorizando impuestos y busca noticias en internet."
    
    pdf_path = "C:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/Cartola Inversión Extranjera TD6003108 (Pershing) - marzo 2026.pdf"
    excel_path = "C:/Users/franc/OneDrive/Documentos/PROYECTOS/BD SENIOR/Calculo Rentabilidad Real Pershing_Gonzalo Bremer.xlsx"
    
    file_bytes_list = []
    filenames = []
    
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            file_bytes_list.append(f.read())
        filenames.append("Cartola.pdf")
        
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            file_bytes_list.append(f.read())
        filenames.append("Calculo.xlsx")
        
    print("Iniciando test DEBUG...")
    try:
        respuesta = analyst.analyze_query(text_input=q_text, file_bytes_list=file_bytes_list, filenames=filenames)
        print("======== RESPUESTA ========")
        print(repr(respuesta))
    except Exception as e:
        print("======== ERROR ========")
        import traceback
        traceback.print_exc()
