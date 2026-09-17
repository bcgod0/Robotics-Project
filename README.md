# 📄 AI Resume Analyzer & Job Matching Agent

An Agentic AI application powered by **Groq LLM**, **ChromaDB Vector Database**, and **Gradio** that analyzes resumes, retrieves matching jobs using RAG (Retrieval-Augmented Generation), and performs skill gap analysis with actionable course recommendations.

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install groq chromadb sentence-transformers pdfplumber gradio pandas
```

### 2. Configure API Key
Add your Groq API key to `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run Application
```powershell
python resume_analyzer.py
```
Open the printed local URL (`http://127.0.0.1:7860`) or public `.gradio.live` link in your browser, upload a PDF resume, and click **Submit**.

---

## 📖 Code Notes & Explanations

For a complete line-by-line guide explaining how every part of the code works in simple English, check out:
👉 **[NOTES.md](file:///c:/Users/rijul/Desktop/Robotics%20Project/NOTES.md)**
