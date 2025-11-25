"""
Aplicación Chainlit para Chatbot RAG de Guaraní
Integra OpenRouter y el sistema RAG entrenado
"""

import os
import chainlit as cl
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import requests
from typing import Optional


class OpenRouterLLM:
    """Wrapper para usar OpenRouter con diferentes modelos"""
    
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Genera respuesta del modelo"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error al conectar con OpenRouter: {str(e)}"


class GuaraniChatbotRAG:
    """Sistema de chatbot para guaraní con RAG"""
    
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
    
    def query(self, question: str, use_rag: bool = True) -> dict:
        """
        Procesa una pregunta y devuelve la respuesta
        
        Args:
            question: La pregunta del usuario
            use_rag: Si True, usa RAG; si False, usa zero-shot
        
        Returns:
            dict con 'answer' y 'sources' (si usa RAG)
        """
        if use_rag:
            # Recuperar documentos relevantes
            relevant_docs = self.retriever.get_relevant_documents(question)
            
            # Construir contexto
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            sources = [doc.metadata.get("source", "Desconocido") for doc in relevant_docs]
            
            prompt = f"""Eres un asistente experto en el idioma guaraní. Usa la siguiente información de referencia para responder la pregunta.

CONTEXTO:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
- Basa tu respuesta en la información del contexto proporcionado
- Si la información no está en el contexto, indícalo claramente
- Responde de manera clara y educativa
- Si es apropiado, incluye ejemplos en guaraní

RESPUESTA:"""
            
            answer = self.llm.generate(prompt)
            
            return {
                "answer": answer,
                "sources": sources,
                "context": context
            }
        else:
            # Zero-shot sin RAG
            prompt = f"""Eres un asistente experto en el idioma guaraní.

Pregunta: {question}

Responde de manera clara y concisa."""
            
            answer = self.llm.generate(prompt)
            
            return {
                "answer": answer,
                "sources": [],
                "context": None
            }


# Variables globales para el chatbot
chatbot: Optional[GuaraniChatbotRAG] = None
use_rag_mode: bool = True


@cl.on_chat_start
async def start():
    """Inicializa el chatbot cuando se inicia una sesión"""
    global chatbot, use_rag_mode
    
    # Cargar variables de entorno
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet")
    
    if not api_key:
        await cl.Message(
            content="⚠️ Error: No se encontró OPENROUTER_API_KEY en las variables de entorno."
        ).send()
        return
    
    # Mostrar mensaje de carga
    msg = cl.Message(content="Cargando el chatbot de guaraní...")
    await msg.send()
    
    try:
        # Inicializar embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )
        
        # Cargar vector store
        vectorstore = FAISS.load_local(
            "vectorstore_guarani",
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Inicializar LLM
        llm = OpenRouterLLM(model_name=model_name, api_key=api_key)
        
        # Crear chatbot
        chatbot = GuaraniChatbotRAG(llm, retriever)
        
        # Actualizar mensaje
        msg.content = f"""✅ **Chatbot de Guaraní listo!**

🤖 **Modelo**: {model_name}
📚 **Modo**: RAG activado (usando base de conocimiento)

💡 **Comandos especiales**:
- `/rag on` - Activar modo RAG (con base de conocimiento)
- `/rag off` - Desactivar modo RAG (solo conocimiento del modelo)
- `/help` - Mostrar ayuda

¡Puedes empezar a hacer preguntas sobre el idioma guaraní!
"""
        await msg.update()
        
    except Exception as e:
        msg.content = f"❌ Error al cargar el chatbot: {str(e)}"
        await msg.update()


@cl.on_message
async def main(message: cl.Message):
    """Procesa los mensajes del usuario"""
    global chatbot, use_rag_mode
    
    if chatbot is None:
        await cl.Message(
            content="⚠️ El chatbot no está inicializado. Por favor, recarga la página."
        ).send()
        return
    
    user_message = message.content.strip()
    
    # Comandos especiales
    if user_message.startswith("/"):
        if user_message == "/rag on":
            use_rag_mode = True
            await cl.Message(content="✅ Modo RAG activado").send()
            return
        elif user_message == "/rag off":
            use_rag_mode = False
            await cl.Message(content="✅ Modo RAG desactivado").send()
            return
        elif user_message == "/help":
            help_text = """
**Ayuda del Chatbot de Guaraní**

📝 **Comandos disponibles**:
- `/rag on` - Activar RAG (usa documentos de gramática)
- `/rag off` - Desactivar RAG (solo conocimiento del modelo)
- `/help` - Mostrar esta ayuda

💬 **Ejemplos de preguntas**:
- ¿Cómo se dice "hola" en guaraní?
- ¿Cuáles son los pronombres personales en guaraní?
- ¿Cómo se conjuga el verbo "ir"?
- ¿Cuál es la estructura de las oraciones?
"""
            await cl.Message(content=help_text).send()
            return
    
    # Mostrar mensaje de "pensando"
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # Obtener respuesta del chatbot
        result = chatbot.query(user_message, use_rag=use_rag_mode)
        
        # Formatear respuesta
        response = f"{result['answer']}"
        
        # Agregar fuentes si está en modo RAG
        if use_rag_mode and result['sources']:
            response += f"\n\n📚 **Fuentes consultadas**: {', '.join(set(result['sources']))}"
        
        # Agregar indicador de modo
        mode_indicator = "🔍 RAG" if use_rag_mode else "🧠 Zero-shot"
        response += f"\n\n{mode_indicator}"
        
        msg.content = response
        await msg.update()
        
    except Exception as e:
        msg.content = f"❌ Error al procesar la pregunta: {str(e)}"
        await msg.update()


if __name__ == "__main__":
    # Este archivo se ejecuta con: chainlit run app.py
    pass
