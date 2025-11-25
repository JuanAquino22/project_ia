# 🇵🇾 Chatbot RAG para Guaraní - Idioma de Bajo Recursos

Este proyecto implementa y evalúa un sistema de chatbot con RAG (Retrieval-Augmented Generation) para el idioma guaraní, comparando diferentes estrategias de generación de lenguaje natural en un contexto de bajo recursos.

## 📋 Descripción del Proyecto

El objetivo principal es evaluar si un sistema RAG puede mejorar el rendimiento de LLMs (Large Language Models) para idiomas de bajo recursos como el guaraní. El proyecto compara:

- **Dos modelos de LLM**: GPT-3.5 Turbo y Claude 3.5 Sonnet (via OpenRouter)
- **Tres estrategias**: Zero-shot, Few-shot y RAG
- **Con y sin documentos de gramática**: Para medir el impacto del RAG

## 🎯 Objetivos

1. ✅ Evaluar el rendimiento de LLMs en guaraní (idioma de bajo recursos)
2. ✅ Comparar estrategias: Zero-shot, Few-shot y RAG
3. ✅ Determinar si el RAG beneficia los idiomas de bajo recursos
4. ✅ Proporcionar una interfaz de chatbot funcional con Chainlit

## 🏗️ Estructura del Proyecto

```
project_ia/
├── project.ipynb              # Notebook principal de Colab (entrenamiento y evaluación)
├── app.py                     # Aplicación Chainlit para el chatbot
├── requirements.txt           # Dependencias del proyecto
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos a ignorar en git
├── README.md                 # Este archivo
├── vectorstore_guarani/      # Base de datos vectorial (generada por el notebook)
└── evaluation_results.json   # Resultados de la evaluación (generado por el notebook)
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- GPU (recomendado para entrenamiento, opcional para inferencia)
- Cuenta en [OpenRouter](https://openrouter.ai/) con API Key

### 1. Clonar el repositorio

```bash
git clone https://github.com/JuanAquino22/project_ia.git
cd project_ia
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tu API Key de OpenRouter:

```env
OPENROUTER_API_KEY=tu_api_key_aqui
MODEL_NAME=anthropic/claude-3.5-sonnet  # o openai/gpt-3.5-turbo
```

## 📊 Uso del Proyecto

### Paso 1: Entrenamiento y Evaluación (Google Colab)

1. Sube `project.ipynb` a Google Colab
2. Sube el archivo `dataset/GramaticaGuarani.pdf` a Colab o móntalo desde Google Drive
3. Ejecuta todas las celdas secuencialmente
4. El notebook:
   - Extrae texto del PDF de gramática guaraní
   - Divide el texto en chunks semánticamente coherentes
   - Crea embeddings multilingües y vector store con FAISS
   - Evalúa los dos modelos (GPT-3.5 y Claude) con las tres estrategias
   - Genera visualizaciones comparativas
   - Genera `vectorstore_guarani.zip` y `evaluation_results.json`
5. Descarga los archivos generados

### Paso 2: Configurar el Chatbot Local

1. Descomprime `vectorstore_guarani.zip` en el directorio del proyecto:

```bash
unzip vectorstore_guarani.zip
```

2. Verifica que la estructura sea correcta:

```
project_ia/
├── vectorstore_guarani/
│   ├── index.faiss
│   └── index.pkl
```

### Paso 3: Ejecutar la Aplicación Chainlit

```bash
chainlit run app.py -w
```

La aplicación se abrirá automáticamente en tu navegador (normalmente en `http://localhost:8000`).

## 💬 Uso del Chatbot

### Comandos Disponibles

- `/rag on` - Activar modo RAG (usa documentos de gramática)
- `/rag off` - Desactivar modo RAG (solo conocimiento del modelo)
- `/help` - Mostrar ayuda

### Ejemplos de Preguntas

```
¿Cómo se dice "hola" en guaraní?
¿Cuáles son los pronombres personales en guaraní?
¿Cómo se conjuga el verbo "ir"?
¿Cuál es la estructura de las oraciones en guaraní?
```

## 🔬 Metodología de Evaluación

### Estrategias Comparadas

1. **Zero-shot**: El modelo responde sin ejemplos ni contexto adicional
2. **Few-shot**: El modelo recibe ejemplos de preguntas y respuestas
3. **RAG**: El modelo usa documentos recuperados de la base de conocimiento

### Métricas de Evaluación

El proyecto evalúa:

- **Precisión**: ¿Las respuestas son correctas según la gramática guaraní?
- **Relevancia**: ¿Las respuestas abordan directamente la pregunta?
- **Completitud**: ¿Las respuestas proporcionan información suficiente?
- **Consistencia**: ¿El modelo es consistente en sus respuestas?

### Modelos Evaluados

1. **GPT-3.5 Turbo** (OpenAI): Más rápido y económico
2. **Claude 3.5 Sonnet** (Anthropic): Más potente y contextual

## 📁 Archivos Generados

### `vectorstore_guarani/`

Base de datos vectorial con embeddings de los documentos de gramática guaraní. Utiliza FAISS para búsqueda eficiente de similitud.

### `evaluation_results.json`

Resultados detallados de la evaluación:

```json
{
  "model_1": {
    "model": "GPT-3.5 Turbo",
    "strategies": {
      "zero_shot": [...],
      "few_shot": [...],
      "rag": [...]
    }
  },
  "model_2": {...}
}
```

## 🛠️ Tecnologías Utilizadas

- **LangChain**: Framework para aplicaciones con LLMs
- **FAISS**: Búsqueda eficiente de similitud vectorial
- **HuggingFace Transformers**: Modelos de embeddings multilingües
- **Chainlit**: Framework para interfaces de chat
- **OpenRouter**: API para acceso a múltiples LLMs
- **Google Colab**: Entorno de ejecución con GPU

## 📝 Mejoras Futuras

- [ ] Agregar más documentos de gramática guaraní
- [ ] Implementar fine-tuning de modelos con BERT
- [ ] Agregar dataset de evaluación con respuestas de referencia
- [ ] Implementar métricas automáticas (BLEU, ROUGE, BERTScore)
- [ ] Agregar soporte para más idiomas de bajo recursos
- [ ] Implementar sistema de feedback del usuario
- [ ] Crear dashboard de análisis de resultados

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Juan Aquino** - [@JuanAquino22](https://github.com/JuanAquino22)

## 🙏 Agradecimientos

- Documentos de gramática guaraní de fuentes educativas
- Comunidad de LangChain y Chainlit
- OpenRouter por el acceso a múltiples LLMs
- Google Colab por el acceso gratuito a GPUs

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio o contacta al autor.

---

**⚠️ Nota**: Este proyecto es educativo y de investigación. Las respuestas del chatbot pueden contener errores y no deben considerarse como referencia oficial del idioma guaraní.