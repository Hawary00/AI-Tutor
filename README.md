# 🧑‍🏫 AI Tutor (Nemo)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)  
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange.svg)](https://www.langchain.com/)  
[![LangGraph](https://img.shields.io/badge/LangGraph-agents-purple.svg)](https://www.langchain.com/langgraph)  
[![LangSmith](https://img.shields.io/badge/LangSmith-monitoring-red.svg)](https://www.langchain.com/langsmith)  
[![Gradio](https://img.shields.io/badge/Gradio-4.x-green.svg)](https://www.gradio.app/)  
[![FAISS](https://img.shields.io/badge/VectorDB-FAISS-yellow.svg)](https://faiss.ai/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  

---

## 📖 Project Overview

**AI Tutor (Nemo)** is an intelligent, interactive tutor built for **science and technology students**.  
It combines **Large Language Models (LLMs)** with **retrieval-augmented generation (RAG)** to answer questions both from:  

- **💬 Direct questions** (general tutoring)  
- **📄 Uploaded textbooks/notes (PDFs)** (retrieval mode)  

This system is designed to **simulate a personalized AI tutor**: patient, accurate, and adapted to the student’s level.  

---
## 🎥 Demo Video
https://github.com/user-attachments/assets/87b4eacf-5509-4cf5-afe1-36eec3fa2b2b

---
## ⚡ Key Features

- 🤖 **LLM-powered tutoring** using Google Generative AI (Gemini).  
- 🧠 **Context-aware agents** with **LangChain** and **LangGraph** to manage reasoning steps.  
- 📄 **PDF knowledge ingestion**: Extracts content, splits into chunks, and stores embeddings in **FAISS** for retrieval.  
- 📐 **Math rendering with LaTeX**: All formulas are displayed cleanly in Markdown with `$$...$$`.  
- 🌍 **Multilingual support**: Works in both **English** and **Arabic** (answers in the same language as the question).  
- 🔍 **Hallucination prevention**: Answers are always verified against either the uploaded material or scientific facts.  
- 🎨 **Modern Gradio UI**: Simple interface with separate controls for questions and PDF uploads.  

---

## 🏗️ Architecture

This project leverages **LangChain’s ecosystem** and the **LangGraph orchestration framework**:

- **LangChain** → Provides LLM integration, embeddings, and retrieval utilities.  
- **LangGraph** → Handles agent workflows, memory (conversation state), and branching logic.  
- **LangSmith** → Used for observability, debugging, and evaluating agent responses.  
- **Agents** → React-style agents manage the flow between general Q&A and PDF-based retrieval.  
- **FAISS VectorStore** → Stores embeddings of PDF content for efficient semantic search.  
- **Gradio** → Provides an interactive, user-friendly frontend.  

**Pipeline**:
1. User either asks a question **or uploads a PDF**.  
2. PDF is chunked, embedded (`multilingual-e5-base`), and stored in FAISS.  
3. A LangGraph agent decides:
   - If no PDF exists → answer directly with LLM.  
   - If PDF exists → retrieve relevant chunks and ground the answer.  
4. Answer is formatted in **Markdown** with **LaTeX equations** when needed.  

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/AI-Tutor.git
cd AI-Tutor
```
### 2️⃣ Create and activate environment
```bash
conda create -n AI_tutor python=3.10 -y
conda activate AI_tutor
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

Copy .env.example and insert your Google API Key:
```bash
cp .env.example .env
```
Edit .env:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```
### 5️⃣ Run the app
```bash
python -m src.app
```
Visit http://localhost:

## 🧪 Example Usage

- **General tutoring (no PDF):**  
  _“Explain Newton’s Second Law with an example.”_

- **PDF-based retrieval:**  
  Upload a PDF textbook →  
  _“According to the PDF, what is the formula for Standard Deviation?”_

<!-- ✅ Response includes LaTeX-formatted equations like:

```latex
$$ \sigma = \sqrt{\frac{\sum_{i=1}^{N}(x_i - \mu)^2}{N}} $$
```

 🎉 -->

 ## 📂 Project Structure
```bash
AI-Tutor/
│── src/
│   ├── __init__.py
│   ├── app.py                # Gradio UI (entry point)
│   ├── chat.py               # Chat logic (chat_fn)
│   ├── pdf_processor.py      # PDF processing + FAISS logic
│   ├── prompts.py            # System & retrieval prompts
│   ├── agent.py              # LLM + agent setup
│   └── utils.py              # Helpers (latex formatter, etc.)
│
│── faiss_index/              # Local FAISS storage
│── .env.example              # Example env vars (API keys etc.)
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
│── .gitignore                # Ignore cache, FAISS index, env
```

---

## 🧠 Why This Project Is Powerful

- **Hybrid Q&A System** – Supports both open-domain conversations and PDF-based retrieval-augmented generation (RAG).  
- **Agent-Driven Reasoning** – Uses LangGraph to build structured reasoning workflows with memory and multi-step planning.  
- **Seamless Vector Search** – FAISS-powered retrieval ensures fast and accurate access to large document collections.  
- **Multilingual Support** – Embeddings from `intfloat/multilingual-e5-base` enable tutoring in multiple languages.  
- **Math-Ready Explanations** – LaTeX rendering in Markdown makes equations clear and professional.  
- **Production-Ready Stack** – Built with LangChain, LangGraph, LangSmith, Hugging Face, and Gradio for scalability and deployment.

---
## 📜 License

This project is licensed under the MIT License
.
---
## 🙌 Contributing

Contributions are welcome!

1. Fork the repository  
2. Create a new feature branch (`git checkout -b feature-name`)  
3. Commit your changes (`git commit -m "Add feature"`)  
4. Push to your branch (`git push origin feature-name`)  
5. Open a Pull Request


🔥 With Nemo, students don’t just ask questions…
they learn interactively with an AI tutor grounded in their own study material!