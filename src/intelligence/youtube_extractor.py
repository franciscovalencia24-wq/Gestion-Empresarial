import os
from youtube_transcript_api import YouTubeTranscriptApi
from src.intelligence.rag_advisor import RAGAdvisorV2

class YouTubeWisdomExtractor:
    def __init__(self):
        # Inicializa la conexión al RAG
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        _PERSIST_DIR  = os.path.join(_PROJECT_ROOT, "data", "vector_db_local")
        self.rag_engine = RAGAdvisorV2(persist_dir=_PERSIST_DIR)

    def extract_video_id(self, url: str) -> str:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return url # Asumimos que es el ID directo si no hay formato de URL

    def download_transcript(self, video_id: str) -> str:
        try:
            # Obtener lista de transcripciones (intenta en español primero)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                transcript = transcript_list.find_transcript(['es', 'en'])
            except:
                # Si no encuentra es o en, trae la primera disponible
                transcript = transcript_list.find_transcript([t.language_code for t in transcript_list])
            
            # Descargar
            data = transcript.fetch()
            
            # Formatear el texto
            full_text = " ".join([item['text'] for item in data])
            return full_text
            
        except Exception as e:
            raise Exception(f"No se pudo descargar la transcripción del video {video_id}: {e}")

    def ingest_video_to_rag(self, url_or_id: str, title: str = "Video de YouTube"):
        video_id = self.extract_video_id(url_or_id)
        print(f"[YouTubeExtractor] Descargando transcripción para {video_id}...")
        
        try:
            text = self.download_transcript(video_id)
            
            # Formatear para el RAG
            document_content = f"TÍTULO: {title}\nFUENTE: YouTube ({video_id})\n\nCONTENIDO (Transcripción):\n{text}"
            
            # Aquí podríamos guardar a un archivo PDF o txt en la carpeta de knowledge, o inyectar directo a Langchain.
            # Como RAGAdvisorV2 carga desde PDFs, lo más fácil es guardarlo como un .txt en el directorio de knowledge
            # y luego llamar a index_documents().
            _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            knowledge_dir = os.path.join(_PROJECT_ROOT, "data", "knowledge", "camv_pdfs")
            os.makedirs(knowledge_dir, exist_ok=True)
            
            # Guardamos como TXT
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            filename = f"YOUTUBE_{safe_title}_{video_id}.txt"
            filepath = os.path.join(knowledge_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document_content)
                
            print(f"[YouTubeExtractor] Archivo guardado en {filepath}. Forzando recarga del RAG...")
            # Forzamos recarga
            self.rag_engine.data_paths = [knowledge_dir]
            self.rag_engine.index_documents(force_reload=True)
            
            return True, f"Video '{title}' procesado e inyectado a la base de conocimiento exitosamente."
        except Exception as e:
            return False, str(e)
