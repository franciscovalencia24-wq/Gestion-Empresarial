import os
from playwright.sync_api import sync_playwright

import json
from langchain_google_genai import ChatGoogleGenerativeAI

def extract_intel_from_url(url: str):
    """
    Toma cualquier URL de internet, extrae el texto puro
    y lo procesa con IA para encontrar prospectos.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            
            # Extraemos todo el texto visible de la página
            page_text = page.evaluate("() => document.body.innerText")
            browser.close()
            
            # Llamada real a Gemini API
            return real_ia_extraction(page_text, url)
            
    except Exception as e:
        return {"error": str(e)}

def real_ia_extraction(text, url):
    """
    Invocación a Gemini para extracción estructurada.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "GOOGLE_API_KEY no configurada en el entorno."
        }
        
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0.1, google_api_key=api_key)
        
        prompt = f"""
        Analiza el siguiente texto extraído de la URL {url} y extrae una lista estructurada de personas o prospectos.
        Para cada persona identificada, extrae si está disponible:
        - Nombre completo
        - RUT (con guion o normalizado si es posible)
        - Monto suscrito o patrimonio/capital estimado en CLP (solo números enteros)
        - Observaciones (cargo, empresa o contexto patrimonial)
        
        Responde estrictamente en formato JSON válido con el siguiente esquema:
        {{
            "prospects": [
                {{
                    "nombre": "Nombre completo",
                    "rut": "RUT o null",
                    "monto_suscrito": 120000000,
                    "observaciones": "Contexto/cargo/sociedad"
                }}
            ]
        }}
        
        TEXTO A ANALIZAR:
        {text[:8000]}
        """
        
        response = llm.invoke(prompt)
        res_text = response.content if hasattr(response, 'content') else str(response)
        
        # Limpieza de la respuesta para parsear JSON
        cleaned_res = res_text.strip()
        if cleaned_res.startswith("```json"):
            cleaned_res = cleaned_res[7:]
        elif cleaned_res.startswith("```"):
            cleaned_res = cleaned_res[3:]
            
        if cleaned_res.endswith("```"):
            cleaned_res = cleaned_res[:-3]
        cleaned_res = cleaned_res.strip()
        
        data = json.loads(cleaned_res)
        data["status"] = "success"
        data["raw_text_preview"] = text[:500]
        return data
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en la extracción con Gemini: {str(e)}",
            "raw_text_preview": text[:500]
        }
