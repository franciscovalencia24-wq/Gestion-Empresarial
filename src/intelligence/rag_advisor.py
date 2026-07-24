import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma


class RAGAdvisorV2:
    """
    Motor Académico (RAG) basado en documentación oficial (CAMV) u otras fuentes.
    Escanea recursivamente múltiples carpetas de conocimiento, añade metadatos de
    categoría por subcarpeta, y utiliza LLMs (Gemini) para responder consultas
    técnicas usando únicamente el conocimiento indexado.
    """

    # ─── Rutas de conocimiento por defecto ───────────────────────────────────────
    DEFAULT_KNOWLEDGE_PATHS = [
        "data/knowledge/camv_pdfs/",
        "DOCUMENTACIÓN CMV/",
    ]

    def __init__(self, data_paths=None, persist_dir="data/vector_db_local"):
        from dotenv import load_dotenv
        load_dotenv(override=True)

        self.persist_dir = os.path.abspath(persist_dir)
        self.api_key = os.getenv("GOOGLE_API_KEY")

        # Resolver lista de directorios de conocimiento
        if data_paths is None:
            raw_paths = self.DEFAULT_KNOWLEDGE_PATHS
        else:
            raw_paths = data_paths if isinstance(data_paths, list) else [data_paths]

        self.data_paths = [os.path.abspath(p) for p in raw_paths]

        # ── Embeddings locales (sin cuota de API) ────────────────────────────────
        print("[RAG] Cargando motor de embeddings local (HuggingFace all-MiniLM-L6-v2)...")
        from langchain_huggingface import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # ── LLM para generación de respuestas ────────────────────────────────────
        if not self.api_key:
            print("[Advertencia] GOOGLE_API_KEY no encontrada. El motor de respuesta (LLM) estará desactivado.")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-flash-lite-latest",
                temperature=0.1,
                google_api_key=self.api_key
            )

        self.vector_store = None

    # ─────────────────────────────────────────────────────────────────────────────
    # INDEXACIÓN
    # ─────────────────────────────────────────────────────────────────────────────
    def index_documents(self, force_reload=False):
        """
        Escanea recursivamente todos los directorios de conocimiento en busca de PDFs,
        añade metadatos de categoría derivados del subdirectorio padre,
        y los almacena vectorizados en ChromaDB.
        """
        if not self.api_key:
            print("[RAG] Sin GOOGLE_API_KEY no se puede usar el LLM, pero sí indexar.")

        # Si ya existe la base y no se fuerza recarga, cargarla directamente
        if os.path.exists(self.persist_dir) and not force_reload:
            print("[RAG] Cargando base de conocimiento existente desde disco...")
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            return True

        print(f"[RAG] Iniciando escaneo recursivo de {len(self.data_paths)} carpeta(s)...")
        all_docs = []
        from langchain_community.document_loaders import PyPDFLoader

        for data_path in self.data_paths:
            if not os.path.exists(data_path):
                print(f"[!] Carpeta no encontrada: {data_path} → Saltando.")
                continue

            print(f"[RAG] >> Escaneando: {data_path}")
            for root, _dirs, files in os.walk(data_path):
                pdf_files = [f for f in files if f.lower().endswith(".pdf")]
                if not pdf_files:
                    continue

                # Categoría = nombre de la subcarpeta inmediata (o "General" si es la raíz)
                category = os.path.basename(root) if os.path.abspath(root) != data_path else "General"

                for pdf_name in pdf_files:
                    pdf_path = os.path.join(root, pdf_name)
                    try:
                        print(f"    [+] [{category}] {pdf_name}")
                        loader = PyPDFLoader(pdf_path)
                        loaded_docs = loader.load()

                        # Enriquecer metadatos en cada fragmento
                        for doc in loaded_docs:
                            doc.metadata["category"] = category
                            doc.metadata["source"]   = pdf_name
                            doc.metadata["full_path"] = pdf_path

                        all_docs.extend(loaded_docs)

                    except Exception as e:
                        print(f"    [!] Error cargando {pdf_name}: {e}")

        if not all_docs:
            print("[!] No se extrajo texto de ningún PDF. Verifica que las carpetas existan y contengan PDFs.")
            return False

        total_pages = len(all_docs)
        print(f"\n[RAG] Total de páginas cargadas: {total_pages}")

        # ── Fragmentación para no saturar la ventana de contexto ─────────────────
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        splits = text_splitter.split_documents(all_docs)

        if not splits:
            print("[!] No se generaron fragmentos tras el split.")
            return False

        total_chunks = len(splits)
        print(f"[RAG] Documentos divididos en {total_chunks} vectores de conocimiento.")

        # ── Vectorización en bloques ──────────────────────────────────────────────
        print(f"[RAG] Iniciando vectorización local ({total_chunks} fragmentos)...")
        BATCH_SIZE = 200

        try:
            self.vector_store = Chroma.from_documents(
                documents=splits[:BATCH_SIZE],
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )

            for i in range(BATCH_SIZE, total_chunks, BATCH_SIZE):
                batch = splits[i:i + BATCH_SIZE]
                bloque_n = i // BATCH_SIZE + 1
                total_bloques = (total_chunks - 1) // BATCH_SIZE + 1
                print(f" -> Bloque {bloque_n}/{total_bloques} ({len(batch)} fragmentos)...")
                self.vector_store.add_documents(batch)

            self.vector_store.persist()
            print("[RAG] OK Base de conocimiento creada y guardada exitosamente.")
            return True

        except Exception as e:
            import traceback
            print(f"[CRÍTICO] Error en vectorización: {e}\n{traceback.format_exc()}")
            raise

    # ─────────────────────────────────────────────────────────────────────────────
    # CONSULTA (síncrona)
    # ─────────────────────────────────────────────────────────────────────────────
    def ask(self, question: str, chat_history: list = None):
        """Consulta técnica avanzada con re-escritura semántica y síntesis contextual."""
        if not self.api_key:
            return "Falta configurar la GOOGLE_API_KEY en el archivo .env."

        if not self.vector_store:
            if os.path.exists(self.persist_dir):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                return "La base de conocimientos aún no ha sido creada. Ejecuta el indexador primero."

        try:
            # 1. RE-ESCRITURA SEMÁNTICA (solo si hay historial largo)
            standalone_query = question
            if chat_history and len(chat_history) > 3:
                history_str = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-3:]])
                rephrase_prompt = (
                    f"Dada esta conversación:\n{history_str}\n\n"
                    f"Pregunta: {question}\n"
                    f"Reescribe como consulta de búsqueda independiente (en español):"
                )
                rephrase_res = self.llm.invoke(rephrase_prompt)
                res_content = rephrase_res.content if hasattr(rephrase_res, "content") else str(rephrase_res)
                standalone_query = (
                    " ".join([p["text"] if isinstance(p, dict) and "text" in p else str(p) for p in res_content])
                    if isinstance(res_content, list)
                    else str(res_content)
                )

            # 2. RECUPERACIÓN MULTI-FUENTE (k=8 para mayor cobertura con más documentos)
            docs = self.vector_store.similarity_search(str(standalone_query), k=8)
            context_parts = []
            for d in docs:
                cat  = d.metadata.get("category", "General")
                src  = d.metadata.get("source", "Desconocido")
                context_parts.append(f"[{cat} | {src}]\n{d.page_content}")
            context = "\n---\n".join(context_parts)

            # 3. PROMPT DEL ASESOR SENIOR
            prompt = f"""
Eres el Asesor Jurídico y Tributario Senior de FV ASESORIAS E INVERSIONES impulsada por Altus AI.
Eres el mayor experto disponible en normativa financiera chilena: CMF, SII, AFP, seguros de vida, APV,
herencias, sucesión, impuesto a la renta, beneficio Art. 107 LIR, Circular 21 SII,
prevención de lavado de activos (UAF) y marcos de cumplimiento regulatorio.

INSTRUCCIONES:
1. Usa el contexto de los documentos proporcionados para responder de forma precisa y completa.
2. Cita siempre la fuente del fragmento (ej: "Circular 1578", "Marco Jurídico Vigente.pdf").
3. Incluye la categoría del documento si es relevante (ej: "CIRCULARES", "MANUALES DE ESTUDIO").
4. Si el contexto no cubre la pregunta, indica qué norma o manual debería revisarse.
5. Mantén un tono ejecutivo, directo y sin ambigüedades legales.

CONTEXTO DE DOCUMENTOS INDEXADOS:
{context}

PREGUNTA:
{question}

RESPUESTA DEL ASESOR SENIOR:"""

            response = self.llm.invoke(prompt)
            output = ""
            if hasattr(response, "content"):
                content = response.content
                if isinstance(content, list):
                    for part in content:
                        output += part["text"] if isinstance(part, dict) and "text" in part else str(part)
                else:
                    output = str(content)
            else:
                output = str(response)

            return output.strip()

        except Exception as e:
            import traceback, datetime
            error_details = traceback.format_exc()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "..",
                f"rag_error_{datetime.datetime.now().strftime('%H%M%S')}.txt"
            )
            try:
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(f"Timestamp: {now}\n{error_details}")
            except Exception:
                pass
            return f"Error [{now}]: {e}\nLog guardado en: {os.path.basename(debug_path)}"

    # ─────────────────────────────────────────────────────────────────────────────
    # CONSULTA (streaming)
    # ─────────────────────────────────────────────────────────────────────────────
    def stream_ask(self, question: str, chat_history: list = None):
        """Versión streaming de la consulta técnica para interfaces reactivas."""
        if not self.api_key:
            yield "Falta configurar la GOOGLE_API_KEY."
            return

        if not self.vector_store:
            if os.path.exists(self.persist_dir):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                yield "Base de conocimientos no encontrada. Ejecuta el indexador primero."
                return

        try:
            # Re-escritura semántica
            standalone_query = question
            if chat_history and len(chat_history) > 3:
                history_str = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-3:]])
                rephrase_prompt = (
                    f"Conversación:\n{history_str}\n\n"
                    f"Pregunta: {question}\nReescribe (en español):"
                )
                rephrase_res = self.llm.invoke(rephrase_prompt)
                res_content = rephrase_res.content if hasattr(rephrase_res, "content") else str(rephrase_res)
                standalone_query = (
                    " ".join([p["text"] if isinstance(p, dict) and "text" in p else str(p) for p in res_content])
                    if isinstance(res_content, list)
                    else str(res_content)
                )

            # Recuperación
            docs = self.vector_store.similarity_search(str(standalone_query), k=8)
            context_parts = []
            for d in docs:
                cat = d.metadata.get("category", "General")
                src = d.metadata.get("source", "Desconocido")
                context_parts.append(f"[{cat} | {src}]\n{d.page_content}")
            context = "\n---\n".join(context_parts)

            prompt = f"""Eres el Asesor Jurídico y Tributario Senior de FV ASESORIAS E INVERSIONES impulsada por Altus AI.
Responde usando exclusivamente este contexto de documentos normativos chilenos (CMF, SII, UAF):
{context}

Pregunta: {question}"""

            for chunk in self.llm.stream(prompt):
                if hasattr(chunk, "content"):
                    content = chunk.content
                    if isinstance(content, list):
                        yield "".join([p["text"] if isinstance(p, dict) and "text" in p else str(p) for p in content])
                    else:
                        yield str(content)
                else:
                    yield str(chunk)

        except Exception as e:
            yield f"Error en streaming: {e}"

    # ─────────────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────────────
    def get_knowledge_summary(self) -> dict:
        """Retorna un resumen de los documentos indexados en la base de vectores."""
        if not self.vector_store:
            if os.path.exists(self.persist_dir):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                return {"error": "Base de conocimiento no encontrada."}

        try:
            collection = self.vector_store._collection
            count = collection.count()
            return {
                "total_chunks": count,
                "persist_dir": self.persist_dir,
                "status": "activa"
            }
        except Exception as e:
            return {"error": str(e)}


# ─── Ejecución directa para pruebas ──────────────────────────────────────────
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    advisor = RAGAdvisorV2()

    print("\n[PASO 1] Indexando documentos (force_reload=True para regenerar)...")
    ok = advisor.index_documents(force_reload=False)

    if ok:
        summary = advisor.get_knowledge_summary()
        print(f"\n[RESUMEN] {summary}")

        print("\n--- PRUEBA DE CONOCIMIENTO ---")
        q = "¿Qué es el Intermediario de Valores y cuáles son sus obligaciones según la normativa CMF?"
        print(f"Pregunta: {q}")
        print(f"Respuesta:\n{advisor.ask(q)}")
