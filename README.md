# 🇵🇾 Sistema de Transformación de Oraciones en Guaraní con RAG

Sistema de procesamiento de lenguaje natural para transformar oraciones en guaraní según reglas gramaticales específicas, comparando el rendimiento de modelos de lenguaje con y sin **RAG (Retrieval-Augmented Generation)**.

---

## 📖 ¿Qué hace este sistema?

Este proyecto implementa un sistema capaz de transformar oraciones en guaraní aplicando reglas gramaticales específicas (negación → afirmación, tiempo verbal, etc.).

**Objetivo principal:** Evaluar si el uso de RAG (recuperación de documentación gramatical) mejora la capacidad de los LLMs para generar transformaciones correctas en **idiomas de bajo recursos** como el guaraní.

### Dataset: AmericasNLP 2025

Utilizamos el dataset oficial de AmericasNLP para la tarea de transformación educativa:
- **Input:** Oración base (`Source`) + Regla de transformación (`Change`)
- **Output:** Oración transformada (`Target`)

**Ejemplo:**
```
Source: "Ore ndorombyai kuri"
Change: "TYPE:AFF" (convertir a afirmativo)
Target: "Ore rombyai kuri"
```

### ¿Por qué Guaraní?

El guaraní es un **idioma de bajo recursos** en PLN, lo que significa que los modelos de lenguaje tienen conocimiento limitado sobre él. Este proyecto demuestra cómo RAG puede mejorar el rendimiento de los LLMs en estas lenguas.

---

## 🛠️ Metodología

### 1. Dataset y Tarea

**Dataset:** AmericasNLP 2025 - Educational Materials Transformation
- **Train:** Para ajuste de prompts y experimentación
- **Dev:** Para validación y ajuste de hiperparámetros
- **Test:** Para evaluación final

**Splits:**
```
├── guarani-train.tsv
├── guarani-dev.tsv
└── guarani-test.tsv
```

### 2. Base de Conocimiento (RAG)

**Documentos utilizados:**
- `Gramática guaraní.pdf` (Edición 2020)
- `Diccionario Guaraní-Español.pdf` (opcional)

**Proceso de construcción:**
```
PDF → Extracción de texto → Chunking (1000 chars) → Embeddings → FAISS Vector Store
```

| Parámetro | Valor |
|-----------|-------|
| Modelo de embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Tamaño de chunk | 1000 caracteres |
| Overlap entre chunks | 200 caracteres |
| Vector Store | FAISS |
| Documentos recuperados (k) | 3 |

### 3. Modelos Evaluados

| Modelo | Proveedor | Características |
|--------|-----------|-----------------|
| **GPT-3.5 Turbo** | OpenAI | Rápido, económico |
| **Claude 3.5 Sonnet** | Anthropic | Más potente, respuestas detalladas |

### 4. Estrategias Comparadas

| Estrategia | Descripción |
|------------|-------------|
| **Sin RAG** | El modelo usa solo su conocimiento previo del guaraní |
| **Con RAG** | El modelo recibe fragmentos relevantes de la gramática guaraní |

---

## 📊 Resultados

### Métricas Evaluadas

- **Accuracy:** Porcentaje de transformaciones exactamente correctas
- **BLEU Score:** Similitud entre la transformación generada y la esperada

### Tabla Comparativa (Ejemplo)

| Modelo | Estrategia | Accuracy (%) | BLEU Score |
|--------|------------|--------------|------------|
| GPT-3.5 Turbo | Sin RAG | XX.XX% | XX.XX |
| GPT-3.5 Turbo | Con RAG | XX.XX% | XX.XX |
| Claude 3.5 Sonnet | Sin RAG | XX.XX% | XX.XX |
| Claude 3.5 Sonnet | Con RAG | XX.XX% | XX.XX |

*Nota: Los resultados se generan ejecutando el notebook completo.*

### Ejemplo de Transformación

**Input:**
```
Source: "Ore ndorombyai kuri"
Change: "TYPE:AFF"
```

**Sin RAG (GPT-3.5):**
```
Prediction: "Ore rombyai" ❌ (incompleto)
```

**Con RAG (GPT-3.5):**
```
Prediction: "Ore rombyai kuri" ✅ (correcto)
```

---

## 📈 Conclusiones

### 1. ¿Qué modelo es mejor?

Analizar según las métricas obtenidas:
- **Accuracy:** Qué modelo acierta más transformaciones
- **BLEU:** Qué modelo genera texto más similar al esperado
- **Velocidad y costo:** GPT-3.5 es más rápido y económico

### 2. ¿RAG mejora el rendimiento?

- **Sin RAG:** Los modelos dependen solo de su conocimiento previo (limitado para guaraní)
- **Con RAG:** Los modelos acceden a reglas gramaticales específicas
- **Hipótesis:** RAG debería mejorar significativamente el accuracy en idiomas de bajo recursos

### 3. Importancia para idiomas de bajo recursos

- El guaraní tiene escasa representación en los datos de entrenamiento de LLMs
- RAG permite "enseñar" al modelo información específica sin fine-tuning
- Método escalable para otros idiomas indígenas

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción 1: Google Colab (Recomendado)

1. Abre el notebook en Colab:
   - Clic en el badge "Open in Colab" al inicio del notebook
   - O visita: https://colab.research.google.com/github/JuanAquino22/project_ia/blob/main/project_nuevo.ipynb

2. Configura tu API Key de OpenRouter:
   ```python
   # En Colab Secrets o en el notebook
   OPENROUTER_API_KEY = "tu_api_key_aqui"
   ```

3. Sube el archivo `Gramática guaraní.pdf` cuando se te pida

4. Ejecuta todas las celdas secuencialmente

### Opción 2: Local

```bash
git clone https://github.com/JuanAquino22/project_ia.git
cd project_ia

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key
echo "OPENROUTER_API_KEY=tu_api_key" > .env

# Ejecutar notebook
jupyter notebook project_nuevo.ipynb
```

---

## 🛠️ Tecnologías Utilizadas

- **LangChain** - Framework para RAG
- **FAISS** - Vector store para búsqueda de similitud
- **HuggingFace** - Modelo de embeddings multilingüe
- **OpenRouter** - API unificada para LLMs (GPT-3.5, Claude 3.5)
- **SacreBLEU** - Métricas de evaluación de texto
- **Pandas** - Procesamiento de datos

---

## 📁 Estructura del Proyecto

```
project_ia/
├── project_nuevo.ipynb          # Notebook principal (usar este)
├── project.ipynb                # Versión antigua (chatbot genérico)
├── README.md                    # Este archivo
├── proyecto.txt                 # Requisitos oficiales del profesor
├── requirements.txt             # Dependencias Python
├── Gramática guaraní.pdf        # Documento para RAG (subir manualmente)
├── Diccionario Guaraní-Español.pdf  # Opcional
└── app.py                       # Chatbot Gradio (demo, no usar para evaluación)
```

---

## 👥 Autor

**Juan Aquino** - [@JuanAquino22](https://github.com/JuanAquino22)

---

## 📚 Referencias

- [AmericasNLP 2025 - Educational Materials Task](https://turing.iimas.unam.mx/americasnlp/2025_st_2.html)
- [Dataset GitHub](https://github.com/AmericasNLP/americasnlp2025/tree/main/ST2_EducationalMaterials/data)
- Gramática guaraní (Edición 2020)

---

> ⚠️ **Nota Importante**: Este es el proyecto correcto según los requisitos del profesor. Usa `project_nuevo.ipynb`, no `project.ipynb`.