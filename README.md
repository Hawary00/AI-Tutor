# 🧑‍🏫 AI Tutor (Nemo)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/) &nbsp;
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange.svg)](https://www.langchain.com/) &nbsp;
[![LangGraph](https://img.shields.io/badge/LangGraph-agents-purple.svg)](https://www.langchain.com/langgraph) &nbsp;
[![LangSmith](https://img.shields.io/badge/LangSmith-monitoring-red.svg)](https://www.langchain.com/langsmith) &nbsp;
[![Gradio](https://img.shields.io/badge/Gradio-4.x-green.svg)](https://www.gradio.app/) &nbsp;
[![FAISS](https://img.shields.io/badge/VectorDB-FAISS-yellow.svg)](https://faiss.ai/) &nbsp;
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) &nbsp;

---

## 📖 Project Overview

**AI Tutor (Nemo)** is an intelligent, interactive tutor built for **science and technology students**.
It combines **Large Language Models (LLMs)** with **agentic workflows** to provide two core capabilities:

-   **💬 PDF Tutoring (RAG)**: Answers questions from uploaded textbooks/notes (retrieval mode).
-   **🎥 Video Summarization**: Transcribes and summarizes uploaded video files or YouTube links.

This system is designed to **simulate a personalized AI tutor**: patient, accurate, and adapted to a student’s multi-modal learning materials.

---
## 🎥 Demo Video Summarizer(New feature)
https://github.com/user-attachments/assets/4e5c3307-2cc4-4eee-8eae-d26be04b7322

## 🎥 Demo PDF Tutor(old feature)
https://github.com/user-attachments/assets/87b4eacf-5509-4cf5-afe1-36eec3fa2b2b

---
## ⚡ Key Features

### PDF Tutoring (RAG)
-   🤖 **LLM-powered tutoring** using Google Generative AI (Gemini).
-   🧠 **Context-aware agents** with **LangChain** and **LangGraph** to manage reasoning steps.
-   📄 **PDF knowledge ingestion**: Extracts content, splits it, and stores embeddings in **FAISS** for retrieval.
-   📐 **Math rendering with LaTeX**: All formulas are displayed cleanly in Markdown with `$$...$$`.
-   🌍 **Multilingual support**: Works in both **English** and **Arabic**.
-   🔍 **Hallucination prevention**: Answers are verified against the uploaded material.

### Video Summarization (New!)
-   🎬 **Multi-Source Video Input**: Accepts local video files (e.g., `.mp4`) or **YouTube URLs**.
-   🗣️ **Local Transcription**: Uses **Whisper** to accurately transcribe video audio locally. (Uses `yt-dlp` as a fallback for YouTube).
-   🧩 **Chain-of-Thought Summaries**: Uses Gemini to first extract main points, then write a coherent summary from those points.
-   🔄 **Human-in-the-Loop Feedback**: A **LangGraph** agent presents the summary and waits for user feedback. The user can type "save" or provide correction prompts (e.g., "make it more concise") to have the AI rewrite it iteratively.

---

## 🏗️ Architecture

This project leverages **LangChain’s ecosystem** and the **LangGraph orchestration framework** to manage two distinct agentic workflows.

-   **Core Tech**: LangChain, LangGraph, LangSmith, Gemini
-   **PDF RAG**: FAISS VectorStore, `multilingual-e5-base` embeddings
-   **Video Summary**: Whisper, MoviePy, `yt-dlp`
-   **Frontend**: Gradio

### Workflow 1: PDF RAG Agent

![pdf Agent Flowchart](src/agents/graph.png)
1.  User either asks a question **or uploads a PDF**.
2.  PDF is chunked, embedded (`multilingual-e5-base`), and stored in FAISS.
3.  A LangGraph agent decides:
    -   If no PDF exists → answer directly with LLM.
    -   If PDF exists → retrieve relevant chunks and ground the answer.
4.  Answer is formatted in **Markdown** with **LaTeX equations** when needed.

### Workflow 2: Video Summarizer Agent

This workflow is managed by a separate LangGraph agent with a built-in feedback loop.

![Video Summarizer Agent Flowchart](src/agents/summarizer_agent.png)

- **🎥Video**

https://github.com/user-attachments/assets/60d0f2eb-4448-4204-8f2a-22caefa8e7ed

1.  **Start**: User provides a local video path or YouTube URL.
2.  **`video_loader`**: The node transcribes the video.
    -   *Local File*: Extracts audio with **MoviePy** and transcribes with **Whisper**.
    -   *YouTube URL*: Attempts to fetch the transcript. If unavailable, downloads with **`yt-dlp`** and transcribes with **Whisper**.
3.  **`main_point_summarizer`**: Gemini extracts the key points from the transcript.
4.  **`summarizer_writer`**: Gemini writes a full summary based on the key points.
5.  **`user_feedback`**: The graph **interrupts** and waits for human input. The user can approve ("save") or provide feedback.
6.  **Router (Conditional Edge)**:
    -   If "save" → proceed to **END**.
    -   If feedback is given → proceed to `summarizer_rewriter`.
7.  **`summarizer_rewriter`**: Gemini revises the summary based on the user's feedback.
8.  The graph loops back to `user_feedback` for the next round of review.

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
--
## 🧪 Example Usage

- **General tutoring (no PDF):**  
  _“Explain Newton’s Second Law with an example.”_

- **PDF-based retrieval:**  
  Upload a PDF textbook →  
  _“According to the PDF, what is the formula for Standard Deviation?”_
  
- **Video Summarization:**
    > _Upload `lecture_on_cnn.mp4` OR provide URL `https://www.youtube.com/watch?v=...`_
    >
    > **AI:** "Here is the summary: [Summary text]... Provide feedback or type 'save'."
    >
    > **User:** "Focus more on the data augmentation part."
    >
    > **AI:** "Here is the revised summary: [Revised summary text]... Provide feedback or type 'save'."
    >
    > **User:** "save"
    >
    > **AI:** "Summary saved."

---
 ## 📂 Project Structure

```bash
## 📂 Project Structure

```bash
AI-TUTOR/
├── assets/             # Demo videos, images, etc. 
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent.py            # PDF RAG agent logic
│   │   └── summarizer_agent.py # Video summarizer agent (LangGraph)
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── transcript_tool.py  # Whisper transcription helper
│   │
│   ├── __init__.py
│   ├── app.py                # Gradio UI (entry point)
│   ├── chat.py               # Main chat logic
│   ├── pdf_processor.py      # PDF processing + FAISS logic
│   ├── prompts.py            # System & retrieval prompts
│   └── utils.py              # Helper functions
│
├── .env                  # Local environment variables (GITIGNORED)
├── .env.example          # Example env file
├── .gitignore            # Git ignore file
├── langgraph.json        # LangGraph configuration
├── LICENSE               # Project license
├── requirements.txt      # Python dependencies (I'm assuming this is where your deps are)
└── README.md             
```
---

## 🧠 Why This Project Is Powerful
- **🚀 Multi-Modal Learning** – Now supports both text (PDF) and video, making it a comprehensive study tool.
- **Hybrid Q&A System** – Supports open-domain conversations and PDF-based retrieval-augmented generation (RAG).
- **Agent-Driven Reasoning** – Uses LangGraph to build structured reasoning workflows with memory, multi-step planning, and human-in-the-loop feedback. 
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