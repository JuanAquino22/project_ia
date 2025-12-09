# -*- coding: utf-8 -*-
"""
Sistema de Transformación de Oraciones en Guaraní
Dataset: AmericasNLP 2025
Modelos: GPT-3.5 Turbo vs Claude 3.5 Sonnet
Estrategias: Zero-Shot, Few-Shot, Semantic RAG, Hybrid RAG
"""

import os
import sys
import hashlib
import numpy as np
import requests
import time
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

import gradio as gr
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# ===========================================
# EMBEDDINGS HASH-BASED
# ===========================================
class SimpleHashEmbedding:
    def __init__(self, dim=384):
        self.dim = dim

    def _hash_vector(self, text):
        h = hashlib.sha256(text.encode()).digest()
        arr = np.frombuffer(h, dtype=np.uint8)
        base = np.resize(arr, self.dim)
        return (base / 255).astype(float).tolist()

    def embed_documents(self, docs):
        return [self._hash_vector(d) for d in docs]

    def embed_query(self, text):
        return self._hash_vector(text)

# ===========================================
# CONFIGURACIÓN
# ===========================================
MODELS = {
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet"
}

TRANSFORMATION_RULES = {
    "TYPE:AFF": "Convierte negativa a afirmativa",
    "TYPE:NEG": "Convierte afirmativa a negativa",
    "TENSE:FUT_SIM": "Futuro simple",
    "TENSE:PAST": "Pasado",
    "PERSON:1_PL_INC": "1ª persona plural inclusiva",
    "PERSON:1_PL_EXC": "1ª persona plural exclusiva",
    "PERSON:3": "3ª persona singular"
}

FEW_SHOT_EXAMPLES = """
Ejemplos:
Input: Ore ndorombyai kuri | Change: TYPE:AFF
Output: Ore rombyai kuri

Input: Ore ndorombyai kuri | Change: TENSE:FUT_SIM
Output: Ore ndorombyaita

Input: Ore ndorombyai kuri | Change: PERSON:1_PL_INC
Output: Ñande ñambyai kuri
"""

# ===========================================
# OPENROUTER
# ===========================================
def call_openrouter(prompt: str, api_key: str, model: str, max_tokens: int = 150, temperature: float = 0.2) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/JuanAquino22/project_ia",
        "X-Title": "Guarani Transformation System"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Eres experto en guaraní. Responde SOLO con la oración transformada, sin explicaciones."
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return f"[Error {response.status_code}]"
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip().split("\n")[0] if isinstance(content, str) else str(content).strip()
    except Exception as e:
        return f"[Error de conexión]"

# ===========================================
# SISTEMA DE TRANSFORMACIÓN
# ===========================================
class GuaraniTransformationSystem:
    def __init__(self, retriever=None, api_key: str = None):
        self.retriever = retriever
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

    def _clean(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.strip()
        for tag in ["Output:", "output:", "Respuesta:", "respuesta:", "Target:", "target:"]:
            text = text.replace(tag, "").strip()
        return text.split("\n")[0].replace('"', "").strip()

    def _zero_shot(self, source: str, change: str, model_id: str) -> str:
        rule_expl = TRANSFORMATION_RULES.get(change, "Regla no documentada.")
        prompt = f"""Transforma la oración en guaraní según esta regla:

Regla: {change}
Descripción: {rule_expl}

Oración original: {source}

Responde solo con la oración transformada:"""
        return self._clean(call_openrouter(prompt, self.api_key, model_id))

    def _few_shot(self, source: str, change: str, model_id: str) -> str:
        rule_expl = TRANSFORMATION_RULES.get(change, "Regla no documentada.")
        prompt = f"""Transforma la oración en guaraní según esta regla.

Regla: {change}
Descripción: {rule_expl}

{FEW_SHOT_EXAMPLES}

Ahora transforma esta oración:
Oración original: {source}

Responde solo con la oración transformada:"""
        return self._clean(call_openrouter(prompt, self.api_key, model_id))

    def _semantic_rag(self, source: str, change: str, model_id: str) -> Tuple[str, str]:
        rule_expl = TRANSFORMATION_RULES.get(change, "Regla no documentada.")
        query = f"transformación {change} guaraní negación afirmación tiempo persona"
        docs = []
        page_info = "Sin RAG"
        
        try:
            if self.retriever:
                docs = self.retriever.invoke(query)
        except:
            pass
        
        if docs:
            context = "\n".join([d.page_content[:250] for d in docs[:2]])
            page_info = f"Chunk: {docs[0].metadata.get('chunk_id', 'N/A')}"
        else:
            context = "(Sin contexto)"
            
        prompt = f"""Contexto gramatical:
{context}

Regla: {change}
Descripción: {rule_expl}

Oración original: {source}

Responde solo con la oración transformada:"""

        result = self._clean(call_openrouter(prompt, self.api_key, model_id))
        return result, page_info

    def _hybrid_rag(self, source: str, change: str, model_id: str) -> Tuple[str, str]:
        rule_expl = TRANSFORMATION_RULES.get(change, "Regla no documentada.")
        query = f"transformación {change} guaraní"
        docs = []
        page_info = "Sin RAG"
        
        try:
            if self.retriever:
                docs = self.retriever.invoke(query)
        except:
            pass
        
        if docs:
            context = "\n".join([d.page_content[:250] for d in docs[:2]])
            page_info = f"Chunk: {docs[0].metadata.get('chunk_id', 'N/A')}"
        else:
            context = "(Sin contexto)"
        
        prompt = f"""Contexto:
{context}

{FEW_SHOT_EXAMPLES}

Regla: {change}
Descripción: {rule_expl}

Oración original: {source}

Responde solo con la oración transformada:"""

        result = self._clean(call_openrouter(prompt, self.api_key, model_id))
        return result, page_info

    def transform(self, source: str, change: str, model_name: str, strategy: str) -> Tuple[str, str]:
        model_id = MODELS.get(model_name, "anthropic/claude-3.5-sonnet")
        
        if strategy == "Zero-Shot":
            result = self._zero_shot(source, change, model_id)
            return result, "Sin RAG"
        elif strategy == "Few-Shot":
            result = self._few_shot(source, change, model_id)
            return result, "Sin RAG"
        elif strategy == "Semantic RAG":
            return self._semantic_rag(source, change, model_id)
        elif strategy == "Hybrid RAG":
            return self._hybrid_rag(source, change, model_id)
        else:
            return "Estrategia no reconocida", "Error"

# ===========================================
# INICIALIZACIÓN
# ===========================================
system: Optional[GuaraniTransformationSystem] = None
vectorstore_loaded = False

def initialize():
    global system, vectorstore_loaded
    
    print("🚀 Iniciando Sistema de Transformación de Guaraní...", flush=True)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️ ADVERTENCIA: OPENROUTER_API_KEY no configurada", flush=True)
    
    retriever = None
    try:
        print("📚 Cargando faiss_store...", flush=True)
        embeddings = SimpleHashEmbedding()
        vectorstore = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        vectorstore_loaded = True
        print("✅ faiss_store cargado", flush=True)
    except Exception as e:
        print(f"⚠️ No se pudo cargar faiss_store: {e}", flush=True)
        print("🔄 Sistema funcionará sin RAG", flush=True)
    
    system = GuaraniTransformationSystem(retriever=retriever, api_key=api_key)
    print("✅ Sistema listo!", flush=True)

def transform_sentence(source: str, change: str, model: str, strategy: str):
    if not source.strip():
        return "⚠️ Error: Ingresa una oración"
    if not change:
        return "⚠️ Error: Selecciona una transformación"
    
    if "RAG" in strategy and not vectorstore_loaded:
        fallback_strategy = "Few-Shot" if "Hybrid" in strategy else "Zero-Shot"
        strategy = fallback_strategy
    
    try:
        print(f"🔄 Procesando: {source[:30]}... | {change} | {model} | {strategy}", flush=True)
        result, page_info = system.transform(source, change, model, strategy)
        print(f"✅ Resultado: {result}", flush=True)
        
        output = f"""🎯 RESULTADO

Oración Original: {source}

Regla: {change}

Oración Transformada: {result}

Info RAG: {page_info}

Modelo: {model} | Estrategia: {strategy}
"""
        return output
    except Exception as e:
        print(f"❌ Error: {str(e)}", flush=True)
        return f"❌ ERROR: {str(e)[:200]}"

initialize()

# ===========================================
# INTERFAZ GRADIO
# ===========================================
def create_demo():
    with gr.Blocks(title="Transformación Guaraní 🇵🇾", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("# 🇵🇾 Sistema de Transformación de Oraciones en Guaraní")
        gr.Markdown("**Dataset:** AmericasNLP 2025 | **Modelos:** GPT-3.5 & Claude 3.5")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Entrada")
                source_input = gr.Textbox(label="Oración Original", placeholder="Ore ndorombyai kuri", lines=2)
                change_dropdown = gr.Dropdown(choices=list(TRANSFORMATION_RULES.keys()), label="Regla", value="TYPE:AFF")
                
                with gr.Row():
                    model_dropdown = gr.Dropdown(choices=list(MODELS.keys()), label="Modelo", value="Claude 3.5 Sonnet")
                    strategy_dropdown = gr.Dropdown(choices=["Zero-Shot", "Few-Shot", "Semantic RAG", "Hybrid RAG"], label="Estrategia", value="Few-Shot")
                
                with gr.Row():
                    submit_btn = gr.Button("Transformar", variant="primary")
                    clear_btn = gr.Button("Limpiar")
            
            with gr.Column():
                gr.Markdown("### Resultado")
                result_output = gr.Textbox(label="Transformación", lines=12, value="Esperando...", interactive=False)
        
        with gr.Accordion("📖 Reglas", open=False):
            gr.Markdown("""
**TYPE:AFF** - Negativa → Afirmativa  
**TYPE:NEG** - Afirmativa → Negativa  
**TENSE:FUT_SIM** - Futuro simple  
**TENSE:PAST** - Pasado  
**PERSON:1_PL_INC** - 1ª plural inclusiva  
**PERSON:1_PL_EXC** - 1ª plural exclusiva  
**PERSON:3** - 3ª persona
""")
        
        with gr.Accordion("💡 Ejemplos", open=False):
            gr.Examples(
                examples=[
                    ["Ore ndorombyai kuri", "TYPE:AFF", "Claude 3.5 Sonnet", "Few-Shot"],
                    ["Ore rombyai kuri", "TYPE:NEG", "Claude 3.5 Sonnet", "Hybrid RAG"],
                    ["Ore ndorombyai kuri", "TENSE:FUT_SIM", "GPT-3.5 Turbo", "Semantic RAG"],
                ],
                inputs=[source_input, change_dropdown, model_dropdown, strategy_dropdown]
            )
        
        submit_btn.click(
            fn=transform_sentence,
            inputs=[source_input, change_dropdown, model_dropdown, strategy_dropdown],
            outputs=result_output
        )
        
        clear_btn.click(
            lambda: ("", "TYPE:AFF", "Claude 3.5 Sonnet", "Few-Shot", "Esperando..."),
            outputs=[source_input, change_dropdown, model_dropdown, strategy_dropdown, result_output]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)
