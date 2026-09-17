# 📚 Complete Line-by-Line Code Notes & Explanation

Welcome to the beginner-friendly guide for the upgraded **AI Resume Analyzer & Job Matching Agent** (`resume_analyzer.py`).

This document breaks down every section, function, and line of code into simple, plain English.

---

## 🗺️ High-Level System Architecture

The application supports **two powerful modes**:

### Mode A: Target Job Mode (1-on-1 Deep Matching)
When you have a specific job posting from LinkedIn, Indeed, or a company careers page:

```
[Resume: PDF or Pasted Text]        [Job Description: Pasted Text OR Screenshot Image]
            │                                              │
            ▼                                              ▼
[pdfplumber / Text Input]                      [EasyOCR extracts text from image]
            │                                              │
            ▼                                              ▼
[Groq LLM extracts Candidate Profile]          [Groq LLM structures Job Requirements]
            │                                              │
            └──────────────────────┬───────────────────────┘
                                   ▼
          [Groq LLM 1-on-1 Gap & ATS Tailoring Analysis]
          - Match Score (0–100%)
          - Matched Skills vs Missing Skills
          - Critical ATS Keywords to add
          - Specific bullet-point tailoring advice
          - Skill Gap Roadmap & Learning Resources
                                   │
                                   ▼
          [Formatted Markdown Report displayed on Gradio UI]
```

### Mode B: Database Discovery Mode (Auto-Match Across 30 Curated Roles)
If you leave the Job Description empty:

```
[Resume PDF / Text] ➔ [Extract Skills] ➔ [SentenceTransformer Vectors] ➔ [ChromaDB RAG Search] ➔ [Top 5 Matches]
```

---

## 📑 Detailed Code Breakdown

---

### Section 1: Imports, Console Encoding & Groq Client Setup

```python
import os
import sys
import json as _json
```
- `import os`: Operating system utilities (reading environment variables, checking file paths).
- `import sys`: System environment control (setting console encodings, exiting cleanly on errors).
- `import json as _json`: Serializing and deserializing JSON data exchanged with the LLM.

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```
- **Why this is here:** Windows PowerShell defaults to `cp1252` encoding. Printing Unicode emojis like `✅`, `🧠`, or `🎯` crashes with a `UnicodeEncodeError`. Reconfiguring `sys.stdout` to `utf-8` fixes this.

```python
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"\'')
                if val:
                    os.environ["GROQ_API_KEY"] = val
            elif line.startswith("GROQ_MODEL="):
                val = line.split("=", 1)[1].strip().strip('"\'')
                if val:
                    os.environ["GROQ_MODEL"] = val
```
- **Why `.env` is loaded first:** If you had an old or invalid key in your PowerShell session (`$env:GROQ_API_KEY`), checking `.env` first guarantees that the newly pasted key takes precedence over the stale terminal session.

```python
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_NAME = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
```
- Initializes the Groq client and sets the model to `openai/gpt-oss-120b`, the ultra-fast reasoning model available on your Groq tier.

```python
try:
    client.models.list()
    print(f"✅ Groq API key verified successfully! Using model: {MODEL_NAME}")
except Exception as _auth_err:
    ...
    sys.exit(1)
```
- **Instant Validation:** Tests the API key with Groq immediately upon launch. If the key is invalid, it prints a clear banner and exits, saving you from waiting for models to load only to encounter an error later.

```python
def call_llm(system_prompt: str, user_prompt: str,
             json_mode: bool = False, temperature: float = 0.2) -> str:
```
- Standard wrapper for chat completions:
  - `json_mode=True`: Forces the LLM to return strict, machine-readable JSON.
  - `temperature=0.2`: Ensures deterministic, factual responses without hallucinations.

---

### Section 2: PDF Resume Parser (`parse_resume_pdf`)

```python
import pdfplumber

def parse_resume_pdf(file_path: str) -> str:
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()
```
- Opens the PDF file with `pdfplumber`, iterates over each page, extracts the text while preserving line spacing, and returns the full resume text.

---

### Section 3: OCR Engine for Screenshots & Images

```python
_ocr_reader = None

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        print("🔍 Initializing OCR reader for image text extraction...")
        import easyocr
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _ocr_reader

def extract_text_from_image(image_input) -> str:
    if image_input is None:
        return ""
    try:
        reader = get_ocr_reader()
        results = reader.readtext(image_input, detail=0)
        extracted = "\n".join(results).strip()
        return extracted
    except Exception as e:
        return ""
```
- **Lazy-Loading:** The EasyOCR model is only loaded into memory when the user actually uploads an image. If the user only pastes text or uploads a PDF, OCR overhead is zero!
- `reader.readtext(image_input, detail=0)`: Scans the screenshot, performs optical character recognition, and returns plain text lines.

---

### Section 4: AI Skill & Job Description Structuring

#### A. Candidate Skill Extraction
```python
def extract_skills(resume_text: str) -> dict:
```
- Sends the resume to Groq with instructions to extract `name`, `skills`, `education`, `experience`, and `certifications`.
- `_coerce_profile()`: Defensive guard that handles cases where the LLM returns a JSON list instead of an object, preventing `AttributeError`.

#### B. Custom Job Description Parsing
```python
def parse_job_description(raw_text: str) -> dict:
```
- Takes raw text (from clipboard paste or OCR screenshot output).
- Prompts the LLM to structure it into:
  ```json
  {
    "title": "Job Title",
    "company": "Company Name",
    "required_skills": ["Skill1", "Skill2", ...],
    "description": "Clear summary of responsibilities"
  }
  ```
- Normalizes acronyms and extracts both explicit requirements and implicit skills.

---

### Section 5: ChromaDB RAG Search (Database Fallback)

```python
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
job_collection = chroma_client.create_collection("jobs")
```
- Converts 30 curated entry-level tech jobs into 384-dimensional dense vector embeddings.
- When no custom job description is provided, `search_jobs(profile, top_k=5)` embeds the candidate's skills and performs cosine similarity search to find the 5 closest roles.

---

### Section 6: Deep 1-on-1 Target Job Analysis

```python
TARGET_JOB_GAP_PROMPT = """You are an elite technical recruiter and executive career coach.
Perform an in-depth gap analysis comparing a candidate's resume against a specific target job posting.
Always respond with ONLY a valid JSON object:
{
  "match_percentage": 0-100,
  "matching_skills": [...],
  "missing_skills": [...],
  "ats_keywords_to_add": [...],
  "resume_tailoring_tips": [...],
  "learning_suggestions": [...],
  "verdict_summary": "..."
}
"""
```
- Directly evaluates candidate fit for the exact position applied for:
  - **`ats_keywords_to_add`**: Specific terms from the posting missing in the resume that automated applicant tracking systems look for.
  - **`resume_tailoring_tips`**: Advice on how to rephrase bullet points to emphasize relevant experience.
  - **`learning_suggestions`**: High-yield courses/tutorials to bridge skill gaps.

---

### Section 7: ReAct Agent (`ResumeMatchingAgent`)

```python
class ResumeMatchingAgent:
    def run(self, resume_text: str, custom_job: dict = None) -> dict:
```
- Step 1: Extracts structured skills from the resume.
- Early exit check: If fewer than 2 skills are detected, stops early and asks for more details.
- **Branching Decision:**
  - If `custom_job` is provided: Runs deep 1-on-1 target analysis.
  - If `custom_job` is None: Runs RAG retrieval across ChromaDB and evaluates the top 5 matches.

---

### Section 8: Report Generator & Gradio UI

- `generate_report()`: Formats results into clean Markdown with badges, tables, and bullet points.
- `run_pipeline()`: Unified entry point supporting PDF upload, pasted resume text, pasted job description, and screenshot image.
- `gr.Blocks()`: Modern tabbed UI with drag-and-drop file uploaders, screenshot dropzone, and responsive layout.

---

## 💡 Summary of New Capabilities

| Feature | How It Works |
|---|---|
| **Pasted Job Description** | Paste text from LinkedIn / Indeed ➔ Parsed into structured requirements ➔ Analyzed 1-on-1 |
| **Screenshot Job Description** | Upload image ➔ EasyOCR reads text ➔ LLM cleans and structures it ➔ Analyzed 1-on-1 |
| **Resume Text Paste** | Don't have a PDF? Paste raw resume text directly into the text box |
| **ATS Tailoring Advice** | Pinpoints exact missing keywords to beat Applicant Tracking Systems |
| **Database Auto-Match** | Leave the job description blank to automatically find matches across 30 curated jobs |
