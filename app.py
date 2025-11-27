# -*- coding: utf-8 -*-
"""
Chatbot RAG para Guaraní
Comparación de modelos: GPT-3.5 Turbo vs Claude 3.5 Sonnet
Con y sin RAG para idioma de bajo recursos
"""

import os
import sys
import gradio as gr
import requests
from typing import Optional, List, Tuple

os.environ['PYTHONUNBUFFERED'] = '1'

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ===========================================
# CONFIGURACIÓN DE MODELOS
# ===========================================
MODELS = {
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet"
}

def call_openrouter(prompt: str, api_key: str, model: str, max_tokens: int = 300) -> str:
    """Llama a OpenRouter con el modelo seleccionado."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/JuanAquino22/project_ia",
        "X-Title": "Guarani RAG Chatbot"
    }

    print(f"🌐 Llamando {model}...", flush=True)

    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if 'usage' in result:
                u = result['usage']
                print(
                    f"📊 Tokens: {u.get('prompt_tokens', '?')} entrada, "
                    f"{u.get('completion_tokens', '?')} salida",
                    flush=True
                )
            return result["choices"][0]["message"]["content"]
        else:
            error_text = response.text
            print(f"❌ Error {response.status_code}: {error_text}", flush=True)
            return f"Error al conectar con el modelo: {response.status_code}"
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        return f"Error de conexión: {str(e)}"


class GuaraniChatbot:
    """Chatbot para consultas sobre el idioma guaraní"""

    def __init__(self, retriever, api_key: str):
        self.retriever = retriever
        self.api_key = api_key

    def respond(self, message: str, model_name: str, use_rag: bool) -> str:
        """Genera respuesta usando el modelo y configuración seleccionados"""

        model_id = MODELS.get(model_name, "openai/gpt-3.5-turbo")

        print(f"\n{'=' * 50}", flush=True)
        print(f"📝 Mensaje: {message}", flush=True)
        print(f"🤖 Modelo: {model_name}", flush=True)
        print(f"📚 RAG: {'Activado' if use_rag else 'Desactivado'}", flush=True)

        if use_rag:
            return self._query_with_rag(message, model_id)
        else:
            return self._query_without_rag(message, model_id)

    def _query_without_rag(self, question: str, model_id: str) -> str:
        """Consulta directa al modelo (sin RAG)"""

        prompt = f"""Eres un asistente de idioma guaraní.

PREGUNTA: {question}

REGLAS IMPORTANTES:
- Solo responde si estás MUY seguro de la respuesta
- Si tienes dudas, responde: "Recomiendo activar RAG para obtener información verificada de la gramática guaraní"
- NUNCA inventes palabras en guaraní
- Es preferible decir "no lo sé" que dar información incorrecta

Responde con precisión o indica que necesitas RAG activado."""

        return call_openrouter(prompt, self.api_key, model_id)

    def _query_with_rag(self, question: str, model_id: str) -> str:
        """Consulta con RAG - usa documentos de gramática guaraní"""

        # Buscar documentos relevantes
        print("🔍 Buscando en documentos de gramática...", flush=True)
        docs = self.retriever.invoke(question)
        print(f"📄 Documentos encontrados: {len(docs)}", flush=True)

        # Construir contexto (más grande para tener más información)
        context = "\n\n".join([d.page_content[:800] for d in docs[:3]])

        prompt = f"""Eres un asistente para consultar gramática guaraní.

DOCUMENTOS DE REFERENCIA:
{context}

PREGUNTA DEL USUARIO: {question}

REGLAS ESTRICTAS:
1. Lee cuidadosamente los documentos de referencia
2. Si la respuesta está en los documentos, úsala EXACTAMENTE como aparece
3. Si NO está en los documentos, responde SOLAMENTE: "No encuentro esa información específica en la gramática. ¿Puedes reformular tu pregunta?"
4. NUNCA inventes traducciones, números o vocabulario guaraní
5. Si los documentos mencionan la palabra/concepto pero no dan traducción completa, di: "Los documentos mencionan [concepto] pero no proporcionan la traducción exacta"

Responde de forma clara y precisa."""

        return call_openrouter(prompt, self.api_key, model_id)


# ===========================================
# INICIALIZACIÓN
# ===========================================
chatbot: Optional[GuaraniChatbot] = None


def initialize():
    """Inicializa el chatbot"""
    global chatbot

    print("🚀 Iniciando Chatbot de Guaraní...", flush=True)

    # API Key
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("❌ Falta OPENROUTER_API_KEY en el archivo .env")

    print("✅ API Key configurada", flush=True)

    # Cargar embeddings y vector store
    print("📚 Cargando modelo de embeddings...", flush=True)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    print("💾 Cargando base de conocimiento...", flush=True)
    vectorstore = FAISS.load_local(
        "vectorstore_guarani",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # Crear chatbot
    chatbot = GuaraniChatbot(retriever, api_key)

    print("✅ Chatbot listo!", flush=True)


def chat(message: str, history: List[Tuple[str, str]], model: str, use_rag: bool) -> str:
    """Función del chat para Gradio"""
    if not message.strip():
        return "Por favor, escribe tu pregunta."

    try:
        response = chatbot.respond(message, model, use_rag)
        print(f"📤 Respuesta enviada", flush=True)
        print(f"{'=' * 50}\n", flush=True)
        return response
    except Exception as e:
        print(f"❌ Error: {e}", flush=True)
        return f"Error: {str(e)}"


# Inicializar
initialize()

# ===========================================
# INTERFAZ GRADIO
# ===========================================
with gr.Blocks(title="Chatbot Guaraní 🇵🇾", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🇵🇾 Chatbot de Guaraní (Avañe'ẽ)
    
    Asistente para aprender y consultar sobre el idioma guaraní.
    Basado en documentos de gramática guaraní con sistema RAG.
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot_ui = gr.Chatbot(
                label="Conversación",
                height=450,
                show_label=False
            )
            msg = gr.Textbox(
                label="Tu pregunta",
                placeholder="Escribe tu pregunta sobre guaraní...",
                lines=2,
                show_label=False
            )

            with gr.Row():
                send_btn = gr.Button("Enviar", variant="primary", scale=2)
                clear_btn = gr.Button("Limpiar", scale=1)

        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Configuración")

            model_selector = gr.Dropdown(
                choices=list(MODELS.keys()),
                value="GPT-3.5 Turbo",
                label="Modelo"
            )

            rag_toggle = gr.Checkbox(
                value=True,
                label="Usar RAG (base de conocimiento)"
            )

            gr.Markdown("---")
            gr.Markdown("### 💡 Ejemplos")
            gr.Markdown("""
            - ¿Cómo se dice "hola" en guaraní?
            - ¿Cuáles son los pronombres personales?
            - ¿Cómo se forma el plural?
            - ¿Qué significa "mba'éichapa"?
            - Enséñame los números del 1 al 10
            - ¿Cómo se conjuga el verbo "ir"?
            """)

            gr.Markdown("---")
            gr.Markdown("""
            ### ℹ️ Información
            **RAG activado**: Usa documentos de gramática guaraní para respuestas más precisas.
            
            **RAG desactivado**: Responde solo con el conocimiento del modelo (modo muy conservador).
            """)

    def respond(message, history, model, use_rag):
        answer = chat(message, history, model, use_rag)
        history.append((message, answer))
        return "", history

    # Eventos
    msg.submit(respond, [msg, chatbot_ui, model_selector, rag_toggle], [msg, chatbot_ui])
    send_btn.click(respond, [msg, chatbot_ui, model_selector, rag_toggle], [msg, chatbot_ui])
    clear_btn.click(lambda: (None, []), None, [msg, chatbot_ui])


if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)
