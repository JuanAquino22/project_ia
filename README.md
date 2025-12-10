# 🇵🇾 Sistema de Transformación de Oraciones en Guaraní

Sistema de PLN que transforma oraciones en guaraní según reglas gramaticales, comparando GPT-3.5 Turbo vs Claude 3.5 Sonnet con 4 estrategias (Zero-Shot, Few-Shot, Semantic RAG, Hybrid RAG).

**Dataset:** AmericasNLP 2025 - Educational Materials Transformation  
**Tarea:** Transformar oraciones en guaraní según reglas morfológicas específicas

---

## 📋 Descripción del Proyecto

### Objetivo
Comparar el rendimiento de **LLMs con prompting (sin RAG)** vs **Agentes con RAG** para transformar oraciones en guaraní según reglas gramaticales específicas.

### Desafío
El guaraní es una **lengua de bajos recursos** con:
- Escasez de datos lingüísticos anotados
- Variación dialectal y ortográfica (Jopará - mezcla guaraní-español)
- Poca representación en modelos de lenguaje pre-entrenados

### Metodología
1. **Dataset:** AmericasNLP 2025 (train/dev/test splits)
2. **Base de conocimiento RAG:**
   - Gramática Guaraní (Edición 2020) - 200+ páginas
   - Diccionario Guaraní-Español / Español-Guaraní
   - 1400+ chunks indexados en FAISS
3. **Modelos evaluados:**
   - GPT-3.5 Turbo (OpenAI)
   - Claude 3.5 Sonnet (Anthropic)
4. **Estrategias comparadas:**
   - Zero-Shot (sin ejemplos)
   - Few-Shot (con ejemplos)
   - Semantic RAG (FAISS)
   - Hybrid RAG (BM25 + FAISS + Few-Shot)
5. **Métricas:** Accuracy (exact match) y BLEU Score

---

## 📊 Resultados

| Modelo | Estrategia | Accuracy | Correctas |
|--------|------------|----------|-----------|
| GPT-3.5 Turbo | Zero-Shot | 0% | 0/10 |
| GPT-3.5 Turbo | Few-Shot | 10% | 1/10 |
| GPT-3.5 Turbo | Semantic RAG | 0% | 0/10 |
| GPT-3.5 Turbo | Hybrid RAG | 10% | 1/10 |
| Claude 3.5 Sonnet | Zero-Shot | 30% | 3/10 |
| **Claude 3.5 Sonnet** | **Few-Shot** | **🏆 50%** | **5/10** |
| Claude 3.5 Sonnet | Semantic RAG | 20% | 2/10 |
| Claude 3.5 Sonnet | Hybrid RAG | 40% | 4/10 |

**🏆 Mejor configuración:** Claude 3.5 Sonnet + Few-Shot (50% accuracy)

### Interpretación de Resultados

**¿Por qué Claude es mejor que GPT-3.5?**
- Mayor capacidad de comprensión morfológica
- Mejor seguimiento de instrucciones en guaraní
- Más consistente en todas las estrategias

**¿Por qué Few-Shot supera a RAG?**
- Los ejemplos directos son más relevantes que la teoría gramatical
- La gramática contiene descripciones abstractas, no transformaciones prácticas
- Los chunks recuperados son demasiado genéricos para guiar al modelo

---

## 📚 Base de Conocimiento (RAG)

### Documentos Utilizados
1. **Gramática Guaraní 2020** (Academia de la Lengua Guaraní)
   - 200+ páginas de teoría gramatical
   - Reglas de morfología, sintaxis y fonética
   
2. **Diccionario Guaraní-Español / Español-Guaraní**
   - Vocabulario bilingüe
   - Traducciones y ejemplos de uso

### Proceso de Construcción del Vector Store
```
PDF → Extracción de texto → Limpieza → Chunking → Embeddings → FAISS
```

**Parámetros:**
- Chunk size: 650 caracteres
- Overlap: 120 caracteres
- Total chunks: 1400+
- Embedding: Hash-based (SHA-256, 384 dims)
- Vector store: FAISS + BM25 (Hybrid)

---

## 🧪 Experimentos Realizados

### 1. Comparación de Modelos (GPT-3.5 vs Claude 3.5)
Evaluamos ambos modelos en las 4 estrategias usando 10 ejemplos del dev set.

### 2. Comparación de Estrategias
- **Zero-Shot:** Solo instrucciones, sin ejemplos ni contexto
- **Few-Shot:** 3 ejemplos de transformaciones en el prompt
- **Semantic RAG:** Recuperación de 3 chunks relevantes con FAISS
- **Hybrid RAG:** BM25 (60%) + FAISS (40%) + Few-Shot

### 3. Tipos de Transformaciones Evaluadas
- `TYPE:AFF` - Negativa → Afirmativa (remover ndo-...-i)
- `TYPE:NEG` - Afirmativa → Negativa (agregar ndo-...-i)
- `TENSE:FUT_SIM` - Agregar marcador futuro (-ta)
- `TENSE:PAST` - Agregar marcador pasado (kuri)
- `PERSON:1_PL_INC` - 1ª persona plural inclusiva (ñande)
- `PERSON:1_PL_EXC` - 1ª persona plural exclusiva (ore)
- `PERSON:3` - 3ª persona singular (ha'e)

### 4. Notebook Completo
Todos los experimentos están documentados en `projectIA.ipynb` que incluye:
- Código de construcción del RAG
- Implementación de las 4 estrategias
- Evaluación de ambos modelos
- Cálculo de métricas (Accuracy, BLEU)
- Análisis de resultados

**Ejecutar en Colab:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JuanAquino22/project_ia/blob/main/projectIA.ipynb)

---

## 🚀 Instalación y Uso

### Requisitos
- Python 3.11+
- Docker (opcional)
- API Key de OpenRouter

### Configuración Rápida

```bash
# Clonar repositorio
git clone https://github.com/JuanAquino22/project_ia.git
cd project_ia

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y agregar tu OPENROUTER_API_KEY
```

### Ejecutar

**Opción A - Local:**
```bash
python app.py
# Abrir: http://localhost:7860
```

**Opción B - Docker:**
```bash
docker-compose up --build
# Abrir: http://localhost:7860
```

---

## 📁 Estructura del Proyecto

```
project_ia/
├── app.py                              # Aplicación Gradio
├── projectIA.ipynb                     # Notebook con experimentos
├── finetuning_guarani.ipynb           # Fine-tuning BLOOM-560M + LoRA
├── requirements.txt
├── docker-compose.yml
├── faiss_store/                        # Vector store (1400 chunks)
├── guarani_transformation_results.json # Resultados detallados
└── comparison_table.csv                # Tabla resumen
```
---

## 📝 Ejemplo de Transformación

**Input:**
```
Oración: "Ore ndorombyai kuri"
Regla: TYPE:AFF (convertir a afirmativo)
```

**Output esperado:**
```
"Ore rombyai kuri"
```

**Resultados por estrategia:**
- ✅ Claude Few-Shot: "Ore rombyai kuri" (correcto)
- ✅ GPT-3.5 Few-Shot: "Ore rombyai kuri" (1/10 correctas)
- ❌ Claude Zero-Shot: "Ore rombyai" (incompleto)

---

## 🔍 Conclusiones Principales

### 1. Claude 3.5 Sonnet > GPT-3.5 Turbo
- **Accuracy:** 50% vs 10% (5x mejor)
- **Consistencia:** Mejores resultados en todas las estrategias
- **Comprensión morfológica:** Superior manejo de reglas guaraníes

### 2. Few-Shot > RAG
- **Few-Shot:** 50% accuracy (mejor)
- **Hybrid RAG:** 40%
- **Zero-Shot:** 30%
- **Semantic RAG:** 20% (peor)

**🔑 Hallazgo crítico:** RAG con gramática teórica NO mejora el rendimiento. Los ejemplos directos (Few-Shot) son más efectivos.

### 3. ¿Por qué RAG no funcionó?
- Gramática contiene **teoría abstracta**, no **transformaciones prácticas**
- Chunks recuperados son demasiado genéricos
- Contexto adicional confunde al modelo
- Few-Shot directo proporciona ejemplos más relevantes

**Implicación para lenguas de bajo recurso:**
- RAG es útil SOLO si la base de conocimiento contiene ejemplos prácticos
- Para lenguas indígenas, priorizar few-shot learning con ejemplos reales
- La calidad del corpus importa más que la técnica de recuperación

---

## 🎯 Hallazgos Principales

### 1. Comparación Sin RAG vs Con RAG

| Enfoque | Mejor Accuracy | Modelo |
|---------|----------------|--------|
| **Sin RAG (Few-Shot)** | **50%** | Claude 3.5 Sonnet |
| Con RAG (Hybrid) | 40% | Claude 3.5 Sonnet |
| Con RAG (Semantic) | 20% | Claude 3.5 Sonnet |

**Conclusión:** Para esta tarea, **Few-Shot supera a RAG** porque:
- Los ejemplos directos son más específicos que la teoría gramatical
- RAG no aporta información útil para transformaciones morfológicas exactas

### 2. Lecciones Aprendidas

**✅ Lo que funcionó:**
- Claude 3.5 Sonnet > GPT-3.5 en morfología guaraní
- Few-Shot con ejemplos reales del dataset
- Temperatura baja (0.2) para salidas determinísticas

**❌ Lo que NO funcionó:**
- RAG con gramática teórica (sin ejemplos prácticos)
- Zero-Shot (modelos sin conocimiento previo de guaraní)
- GPT-3.5 (rendimiento muy bajo: 0-10%)

### 3. Recomendaciones para Mejorar

**A corto plazo:**
- Usar Claude 3.5 Sonnet con Few-Shot (configuración óptima actual)
- Aumentar ejemplos few-shot del train set completo

**A mediano plazo:**
- **Fine-tuning supervisado (SFT)** con BLOOM-560M o similar (ver `finetuning_guarani.ipynb`)
- Crear base de conocimiento con transformaciones reales (no teoría)

---

## 📊 Archivos Generados

- `guarani_transformation_results.json` - Resultados completos de evaluación
- `comparison_table.csv` - Tabla resumen con métricas
- `faiss_store/` - Vector store con gramática indexada
- `rag_documents.json` - 1400+ chunks del corpus
- `rag_metadata.json` - Metadatos del RAG

---

## 📚 Tecnologías

- **LLMs:** OpenRouter API (GPT-3.5 Turbo, Claude 3.5 Sonnet)
- **RAG:** LangChain + FAISS + BM25
- **Embeddings:** Hash-based (SHA-256, custom)
- **Interfaz:** Gradio 3.50.2
- **Métricas:** SacreBLEU
- **Dataset:** AmericasNLP 2025 - Guaraní

---

## 📖 Referencias

- [AmericasNLP 2025 - Shared Task 2](https://github.com/AmericasNLP/americasnlp2025/tree/main/ST2_EducationalMaterials)
- Gramática Guaraní (Academia de la Lengua Guaraní, 2020)
- [OpenRouter API](https://openrouter.ai/)
- [LangChain Documentation](https://python.langchain.com/)

---

## 👤 Autor

**Juan Aquino**  
Proyecto Final - Diplomado en Procesamiento de Lenguaje Natural e Inteligencia Artificial  
Facultad Politécnica, Universidad Nacional de Asunción (FPUNA)  
Diciembre 2025

---

## 📄 Licencia

Proyecto educativo desarrollado para el Diplomado en PLN e IA - FPUNA 2025  
Dataset: [AmericasNLP 2025](https://github.com/AmericasNLP/americasnlp2025) (licencia del dataset original)

---

## 🇵🇾 Sobre el Guaraní

El guaraní es una lengua indígena hablada por más de 6 millones de personas en Paraguay, Argentina, Bolivia y Brasil. Es idioma oficial de Paraguay junto al español. Este proyecto busca contribuir al desarrollo de herramientas de PLN para lenguas de bajo recurso.

**Mba'éichapa!** 🇵🇾
