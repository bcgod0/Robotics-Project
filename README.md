# 🚀 AI Resume Analyzer & Job Matching Agent

An Agentic AI application powered by **Groq LLM (`openai/gpt-oss-120b`)**, **EasyOCR**, and a **Tailwind + Neumorphic Dual-Tone Dashboard** that analyzes resumes and provides deep 1-on-1 gap analysis against **any target Job Description (copied text or screenshot)**.

---

## ✨ Features

- 📄 **Resume Input Flexibility**: Upload a PDF or paste plain resume text.
- 📋 **Target Job from Pasted Text**: Paste any job posting from LinkedIn, Indeed, etc.
- 🖼️ **Target Job from Screenshot**: Upload a screenshot of a job posting; EasyOCR extracts requirements automatically.
- 🎯 **Deep 1-on-1 Matching**:
  - Exact Match Score (0–100%)
  - Matching Skills vs. Missing Skills
  - Critical ATS Keywords to add
  - Actionable Resume Tailoring bullet points
  - Concrete Learning Roadmap & actionable upskilling steps
- ⚡ **Instant Boot & Low Latency**: Powered directly by Groq LPU with zero heavy model downloads or database indexing.

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install groq pdfplumber gradio fastapi uvicorn easyocr
```

### 2. Configure API Key
Create a `.env` file in the project folder:
```env
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run Application
```powershell
python resume_analyzer.py
```
Open the printed local URL (`http://127.0.0.1:7860`) or public `.gradio.live` link in your browser.

---

## 📖 Code Notes & Explanations

For a complete line-by-line guide explaining how every part of the code works in simple English, check out:
👉 **[NOTES.md](file:///c:/Users/rijul/Desktop/Robotics%20Project/NOTES.md)**
