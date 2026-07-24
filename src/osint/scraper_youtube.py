import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeSabiduria:
    """
    Agente OSINT para Extracción de Sabiduría (FASE 1).
    Extrae la transcripción de videos de YouTube para integrarlos al RAG del Agente OmniAdvisor.
    """
    def __init__(self):
        self.vault_path = "data/knowledge_base/youtube/"
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)

    def _extract_video_id(self, url: str):
        # Extract ID from normal or short URLs
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None

    def extraer_conocimiento(self, url: str, titulo_custom: str = None):
        """
        Descarga la transcripción del video y la guarda en la bóveda de sabiduría.
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            return {"exito": False, "mensaje": "URL de YouTube no válida."}
            
        try:
            print(f"[*] Extrayendo sabiduría del video ID: {video_id}...")
            # Try to get the transcript in Spanish, fallback to English
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
            
            # Formatear el texto plano
            texto_completo = ""
            for frase in transcript_list:
                texto_completo += frase['text'] + " "
                
            # Limpieza básica
            texto_completo = texto_completo.replace("\n", " ").strip()
            
            # Nombre de archivo
            nombre_archivo = titulo_custom if titulo_custom else f"youtube_sabiduria_{video_id}"
            nombre_archivo = "".join([c for c in nombre_archivo if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            nombre_archivo = nombre_archivo.replace(" ", "_").lower()
            
            ruta_final = os.path.join(self.vault_path, f"{nombre_archivo}.txt")
            
            with open(ruta_final, "w", encoding="utf-8") as f:
                f.write(f"FUENTE: YouTube ({url})\n")
                f.write(f"SABIDURIA EXTRAIDA:\n")
                f.write(texto_completo)
                
            peso_kb = os.path.getsize(ruta_final) / 1024
            
            return {
                "exito": True,
                "ruta": ruta_final,
                "peso_kb": peso_kb,
                "mensaje": f"Se extrajeron {peso_kb:.1f} KB de conocimiento puro."
            }
            
        except Exception as e:
            return {"exito": False, "mensaje": f"No se pudo extraer la transcripción: {e}. (Asegúrate de que el video tenga subtítulos automáticos o manuales)."}

if __name__ == "__main__":
    scraper = YouTubeSabiduria()
    # Test con un video genérico o dejarlo listo para la UI
    # res = scraper.extraer_conocimiento("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Prueba Rick")
    # print(res)
