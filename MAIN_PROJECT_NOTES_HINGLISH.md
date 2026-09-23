# 📚 Main Project Notes — AI Resume Analyzer & Job Matching Agent
### `resume_analyzer.py` — Poora Section-by-Section Guide (Hinglish)

> Ye **final production app** hai. Notebook (`.ipynb`) ka evolved version. Isme ChromaDB/SentenceTransformer hata diye gaye hain — ab ye sirf **direct 1-on-1 target job matching** karta hai — bahut zyada powerful aur focused.

---

## 🗺️ Badi Picture — Poora System Kaise Kaam Karta Hai

```
[User: Resume PDF upload karo ya text paste karo]
                    │
                    ▼
        [pdfplumber: PDF se text nikaalо]
                    │
                    ▼
[User: Job Description paste karo ya Screenshot upload karo]
                    │
           ┌────────┴────────┐
           ▼                 ▼
    [Text input]    [EasyOCR: image se text nikaalо]
           └────────┬────────┘
                    ▼
    [Groq LLM: Job Description ko structure karo]
    → title, company, required_skills, description
                    │
                    ▼
    [Groq LLM: Resume se candidate profile extract karo]
    → name, skills, education, experience, certifications
                    │
                    ▼
    [ReAct Agent: Single job ya multiple jobs?]
           ┌────────┴────────┐
           ▼                 ▼
    [1 job → direct]  [Multiple jobs → ThreadPoolExecutor parallel]
           └────────┬────────┘
                    ▼
    [Groq LLM: Deep 1-on-1 Gap Analysis]
    → match_percentage, matching_skills, missing_skills,
      ats_keywords, tailored_bullet_points, learning_suggestions
                    │
                    ▼
    [Markdown Report generate karo]
                    │
           ┌────────┴────────┐
           ▼                 ▼
  [Gradio UI /gradio]  [FastAPI Dashboard /]
```

---

## 📦 Section 1 — Imports & Environment Setup (Lines 1–76)

```python
import os
import sys
import json as _json
from typing import Optional, List, Dict
```

**Kya karta hai:**
- `os` → Environment variables padhne ke liye (API keys, etc.)
- `sys` → Console ki encoding change karne ke liye
- `json as _json` → LLM se aane wale JSON responses parse karne ke liye
- `typing` → Type hints ke liye (code readable aur bug-free rehta hai)

---

### 🪟 Windows Console Fix

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

**Kyun zaruri hai:**
Windows PowerShell default mein `cp1252` encoding use karta hai. Jab bhi code emojis print karta hai jaise `✅`, `🧠`, `🎯` — PowerShell crash ho jaata hai `UnicodeEncodeError` ke saath. Is fix se console ko `utf-8` pe set karte hain taaki saare emojis properly print hon.

---

### 🔑 `.env` File Se API Key Load Karo

```python
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GROQ_API_KEY="):
                os.environ["GROQ_API_KEY"] = val
            elif line.startswith("GROQ_MODEL="):
                os.environ["GROQ_MODEL"] = val
```

**Kyun `.env` pehle load karte hain:**
Agar tumhare PowerShell session mein puraani/galat API key set hai (`$env:GROQ_API_KEY`), toh `.env` file ko pehle padhne se guarantee hoti hai ki nayi key hi use hogi — terminal ki purani key override ho jaayegi.

**Agar `.env` nahi mila:**
```python
os.environ["GROQ_API_KEY"] = input("Enter your Groq API key: ").strip()
```
Seedha terminal mein maangta hai.

---

### ✅ API Key Instant Validate Karo

```python
try:
    client.models.list()
    print(f"✅ Groq API key verified! Using model: {MODEL_NAME}")
except Exception as _auth_err:
    if "401" in err_msg or "invalid_api_key" in err_msg.lower():
        print("❌ [GROQ AUTHENTICATION FAILED]")
        sys.exit(1)
```

**Kyun ye smart hai:**
App start hote hi API key test hoti hai. Agar key galat hai — turant clear error message aata hai aur app band ho jaata hai. Bina is check ke, user poora resume analyze karta, tab jaake error aati — bahut frustrating hota!

---

### 🤖 `call_llm()` — LLM Wrapper Function

```python
def call_llm(system_prompt: str, user_prompt: str,
             json_mode: bool = False, temperature: float = 0.2) -> str:
```

**Kya karta hai:**
Ye project ka **central nerve** hai — jab bhi AI se baat karni ho, yahi function call hota hai:

| Parameter | Matlab |
|---|---|
| `system_prompt` | AI ko role aur rules batao ("Tu ek expert recruiter hai...") |
| `user_prompt` | AI ko actual data bhejo (resume text, job description) |
| `json_mode=True` | AI ko force karo ki sirf valid JSON return kare |
| `temperature=0.2` | AI ke answers zyada focused aur consistent rahenge (kam random) |

---

## 📄 Section 2 — PDF Resume Parser (Lines 96–107)

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

**Kya karta hai:**
- `pdfplumber.open()` → PDF file kholta hai
- `pdf.pages` pe loop → Har page pe jaata hai
- `page.extract_text()` → Us page se text nikaltta hai
- `or ""` → Agar page blank hai toh crash nahi hota, empty string return hoti hai
- Saare pages ko newlines se jodata hai aur ek bada string return karta hai

**Kyun `pdfplumber`?** Ye PDF libraries mein se best hai table aur complex layouts ke liye — resumes mein aksar columns aur tables hoti hain.

---

## 🖼️ Section 3 — OCR Engine for Screenshots (Lines 110–137)

```python
_ocr_reader = None  # global variable

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _ocr_reader

def extract_text_from_image(image_input) -> str:
    reader = get_ocr_reader()
    results = reader.readtext(image_input, detail=0)
    return "\n".join(results).strip()
```

**Kya karta hai:**
User LinkedIn ya Indeed ka screenshot upload kar sakta hai — EasyOCR us image ko scan karta hai aur text extract karta hai, bilkul waise jaise hum padhte hain.

**Lazy-Loading kyun smart hai:**
EasyOCR model kaafi bada hai. Agar hum ise startup pe load karein, app slow start hoga chahe user screenshot use kare ya na kare. `_ocr_reader = None` se guarantee hoti hai ki **model sirf tab load hoga jab user actually image upload kare** — tab tak zero overhead!

**`gpu=False`** → CPU pe chalata hai taaki GPU na ho tab bhi kaam kare.

---

## 🧠 Section 4 — Skill Extraction & Job Parsing (Lines 140–241)

### A. Resume Se Skills Extract Karo

```python
SKILL_EXTRACTION_SYSTEM_PROMPT = """You are an expert resume parser.
Always respond with ONLY a valid JSON object:
{
  "name": "string",
  "skills": ["skill1", "skill2", ...],
  "education": [...],
  "experience": [...],
  "certifications": [...]
}
Rules:
- Normalize skill names (e.g. "ML" -> "Machine Learning").
- Include skills implied by projects/experience.
- If a field has no data, return an empty list.
"""
```

**Kya karta hai:**
Ye prompt AI ko ek expert recruiter ki tarah behave karata hai. Resume text dene pe structured JSON output milta hai.

**Smart rules ka matlab:**
- "ML" → "Machine Learning" (short forms expand hoti hain)
- Agar resume mein likha hai "Built a chatbot" → AI automatically "NLP" bhi add karta hai (implied skill)
- Koi field nahi hai toh `null` nahi, empty `[]` aata hai — code crash nahi hoga

**`_coerce_profile()` function:**
```python
def _coerce_profile(result) -> dict:
    if isinstance(result, list):
        return {"name": "", "skills": result, ...}
```
Defensive guard — agar AI galti se list return kare dict ki jagah, toh ye usse fix kar deta hai. Bina is function ke `AttributeError` aata.

---

### B. Job Description Ko Structure Karo

```python
JOB_PARSING_SYSTEM_PROMPT = """You are an expert recruitment analyst.
Extract structured job information:
{
  "title": "Job Title",
  "company": "Company Name",
  "required_skills": ["Skill1", "Skill2", ...],
  "description": "Clear summary"
}"""

def parse_job_description(raw_text: str) -> dict:
```

**Kya karta hai:**
Chahe user LinkedIn se text copy-paste kare, ya screenshot se OCR nikaale — dono cases mein raw messy text hota hai. Ye function us raw text ko clean, structured dictionary mein convert karta hai.

**Normalization rules:**
- `"React.js"` → `"React"`
- `"JS"` → `"JavaScript"`
- `"AWS services"` → `"AWS"`

Agar title ya company missing hai → `"Target Role"` / `"Target Company"` use hota hai — code crash nahi hota.

---

## 🎯 Section 5 — Target Job Gap Analysis (Lines 244–312)

```python
TARGET_JOB_GAP_PROMPT = """You are an elite technical recruiter, resume writer, and executive career coach.
Perform an in-depth gap analysis. Return ONLY valid JSON:
{
  "match_percentage": 0-100,
  "matching_skills": [...],
  "missing_skills": [...],
  "ats_keywords_to_add": [...],
  "tailored_bullet_points": [
    {
      "bullet": "STAR-format bullet point with action verbs & metrics...",
      "keywords_infused": ["Keyword1", "Keyword2"],
      "action_verb": "Architected"
    }
  ],
  "resume_tailoring_tips": [...],
  "learning_suggestions": [...],
  "verdict_summary": "2-3 sentence honest assessment..."
}"""
```

**Ye notebook se zyada powerful kyun hai:**
Notebook ka gap analysis sirf basic tha — match %, missing skills, aur kuch tips. Yahan **3 naye major features** hain:

| Feature | Matlab |
|---|---|
| `ats_keywords_to_add` | Exact keywords jo Applicant Tracking System (ATS) dhundta hai — inhe resume mein daalo warna automated screening mein hi reject ho jaoge |
| `tailored_bullet_points` | AI tumhara actual experience lekar STAR format mein **nayi resume bullet points likhta hai** — specific is job ke liye, with action verbs like "Engineered", "Spearheaded", "Architected" |
| `verdict_summary` | 2-3 sentence honest assessment — kitne competitive ho tum is role ke liye |

**`analyze_target_job()` function:**
```python
def analyze_target_job(profile: dict, job: dict) -> dict:
    user_prompt = f"""Candidate Name: {profile.get('name')}
Candidate Skills: {profile.get('skills')}
...
Target Job Title: {job.get('title')}
Required Skills: {job.get('required_skills')}
Job Description: {job.get('description')}"""
```
Candidate ka poora profile + job ki poori details ek saath AI ko bhejta hai for deep analysis.

---

## 🤖 Section 6 — ReAct Agent (Lines 315–404)

```python
class ResumeMatchingAgent:
    def __init__(self, min_skills: int = 2):
        self.min_skills = min_skills
        self.trace = []  # step-by-step log

    def run(self, resume_text: str,
            custom_job: Optional[dict] = None,
            custom_jobs: Optional[List[dict]] = None) -> dict:
```

**Notebook ke agent se kya farq hai:**
Notebook mein agent sirf ek resume leta tha. Yahan agent **teen cheezein accept karta hai:**
- `resume_text` → Candidate ka resume
- `custom_job` → Single job dictionary (ek job analyze karo)
- `custom_jobs` → Multiple jobs ki list (sabko parallel mein analyze karo)

---

### Step 1 — Jobs List Normalize Karo

```python
jobs_to_process = []
if custom_jobs and isinstance(custom_jobs, list) and len(custom_jobs) > 0:
    jobs_to_process = [j for j in custom_jobs if j and isinstance(j, dict)]
elif custom_job and isinstance(custom_job, dict):
    jobs_to_process = [custom_job]

if not jobs_to_process:
    return {"status": "error", "message": "Please provide at least one job description..."}
```

**Kya hota hai:**
- Pehle `custom_jobs` (multiple) check hoti hai
- Agar woh nahi hai toh `custom_job` (single) check hota hai
- Agar kuch bhi nahi diya → error return karo

---

### Step 2 — Resume Se Skills Extract Karo (Single Pass)

```python
self.log("🧠 [Agent] Step 1: Extracting skills from resume...")
profile = extract_skills(resume_text)

if len(profile.get("skills", [])) < self.min_skills:
    return {"status": "needs_clarification", ...}
```

**"Single Pass" kyun important hai:**
Chahe user 1 job compare kare ya 10 jobs, resume **sirf ek baar** parse hota hai. Profile ek baar extract ho, phir saari jobs ke liye reuse. Ye bahut efficient hai — 10x API calls bachte hain!

---

### Step 3 — Parallel Job Evaluation (⚡ Naya Feature!)

```python
if total == 1:
    ranked_jobs = [_evaluate_job((1, jobs_to_process[0]))]
else:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(total, 6)) as executor:
        ranked_jobs = list(executor.map(_evaluate_job, enumerate(jobs_to_process, 1)))
```

**Kya hota hai:**
- **1 job** → Simple direct call
- **Multiple jobs** → `ThreadPoolExecutor` se parallel execution!

**ThreadPoolExecutor ka matlab:**
Maan lo user 5 jobs compare karna chahta hai. Sequential mein (ek ke baad ek) → 5x time lagega. **Parallel mein** → saari 5 jobs ek saath API calls karte hain → almost same time mein sab complete!

`max_workers=min(total, 6)` → Maximum 6 parallel threads — zyada nahi taaki API rate limit na ho.

---

### Step 4 — Results Sort Karo Best Match Pehle

```python
ranked_jobs.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
best_match = ranked_jobs[0]
```

Saare jobs analyze hone ke baad `match_percentage` ke hisaab se descending order mein sort hoti hai — best match sabse upar.

---

### Final Return Dictionary

```python
return {
    "status": "ok",
    "mode": "multi_job" if len(ranked_jobs) > 1 else "target_job",
    "profile": profile,
    "ranked_jobs": ranked_jobs,      # saari jobs sorted by match %
    "best_match": best_match,        # top ranked job
    "total_jobs": len(ranked_jobs),
    # Backward-compatibility:
    "job": best_match["job"],
    "analysis": best_match["analysis"],
}
```

---

## 📋 Section 7 — Report Generator (Lines 407–478)

```python
def generate_report(agent_output: dict) -> str:
```

**Kya karta hai:**
Agent ka raw dictionary output lekar ek beautiful, formatted **Markdown report** banata hai.

**Multi-Job Mode mein (agar multiple jobs compare kiye):**
```
# 🏆 Multi-Job Match Leaderboard
| Rank | Role / Company | Match % | Matching Skills | Missing Skills |
| 🥇  | Software Engineer @ Google | 78% | Python, ML, Git | Kubernetes |
| 🥈  | ML Engineer @ Amazon | 65% | Python, ML | AWS, Docker |
| 🥉  | Data Scientist @ Microsoft | 60% | Python, SQL | Spark |
```

**Single Job Mode mein:**
```
# 🎯 Target Job Match Report: Software Engineer @ Google
### 📊 Overall Match Score: 78%
> Verdict: Strong candidate...

## 🔍 Skills Breakdown
✅ Matching Skills: Python, ML, Git
❌ Missing: Kubernetes, Docker

## ✍️ AI-Tailored Resume Bullet Points (STAR Framework)
✦ **Engineered a distributed ML pipeline processing 10M+ records daily...**
   *(ATS Keywords: Kubernetes, distributed systems)*

## 📚 Skill Gap Roadmap
🚀 Learn Kubernetes via official docs + KodeKloud free course
```

---

## 🔌 Section 8 — Unified Pipeline Callback (Lines 481–546)

```python
def run_pipeline(resume_file, resume_pasted_text, job_pasted_text, job_image_file):
```

**Ye function Gradio UI ka entry point hai.** Jab user "Analyze & Match" button click karta hai, ye function call hota hai.

**4 inputs accept karta hai:**
| Input | Kya hai |
|---|---|
| `resume_file` | Upload kiya hua PDF file |
| `resume_pasted_text` | Text box mein paste kiya hua resume text |
| `job_pasted_text` | Paste ki gayi job description text |
| `job_image_file` | Upload kiya hua job screenshot |

**Logic flow:**

```
Resume resolve karo:
  PDF upload hai? → PDF se text nikaal
  Nahi? → Pasted text use karo
  Kuch bhi nahi? → Error: "Please provide a resume!"

Job resolve karo:
  Screenshot upload hai? → EasyOCR se text nikaal
  Pasted text hai? → Woh use karo (overrides screenshot)
  Kuch bhi nahi? → Error: "Please provide a job description!"

Agent chalao → Report generate karo → Return karo
```

**Error handling:**
```python
if "invalid_api_key" in err_str.lower() or "401" in err_str:
    return "### ❌ Groq Authentication Error..."
```
API key error hone par user ko clear, step-by-step fix instructions milti hain — generic error nahi.

---

## 🖥️ Section 9 — Gradio Interface (Lines 549–621)

```python
import gradio as gr

with gr.Blocks(title="AI Resume Analyzer & Job Matching Agent") as demo:
```

**Notebook ke `gr.Interface` se kya farq hai:**
Notebook mein simple `gr.Interface` tha — ek input, ek output. Yahan `gr.Blocks` use hota hai jo full custom layout deta hai.

**UI Structure:**

```
┌─────────────────────────────────────────────────────┐
│        🚀 AI Resume Analyzer & Job Matching Agent   │
├──────────────────────┬──────────────────────────────┤
│  📄 1. Your Resume   │  📊 Report & Analysis         │
│  ┌──────────────┐    │                               │
│  │ PDF Upload   │    │  [Markdown report yahan       │
│  └──────────────┘    │   appear hogi]                │
│  [Or paste text ▼]   │                               │
│                      │  🔍 View Raw JSON [accordion] │
│  🎯 2. Job Desc      │                               │
│  ┌────┬─────────┐    │                               │
│  │📋  │ 🖼️     │    │                               │
│  │Paste│Screenshot│   │                               │
│  └────┴─────────┘    │                               │
│                      │                               │
│  [🚀 Analyze] [🔄]  │                               │
└──────────────────────┴──────────────────────────────┘
```

**Key UI Components:**
- `gr.Accordion` → "Or paste resume text" section — click karo tab open ho — space save hota hai
- `gr.Tabs` → Job description ke 2 modes: "Paste Text" tab aur "Upload Screenshot" tab
- `gr.JSON` → Raw agent output JSON accordion mein — debug ke liye useful
- `submit_btn.click()` → Button click hone par `run_pipeline()` call hoti hai

---

## ⚡ Section 10 — FastAPI Server & Dashboard (Lines 624–845)

Ye section notebook mein bilkul nahi tha — yeh **completely new** hai.

```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="AI Resume Analyzer & Job Matching Agent")
```

**Kyun FastAPI?**
Gradio sirf ek basic interface hai. FastAPI se ek **proper REST API backend** milta hai jo custom HTML dashboards power kar sakta hai — zyada control, better UI.

---

### `GET /` — Custom Dashboard Serve Karo

```python
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = os.path.join(stitch_assets_dir, "dashboard_dualtone.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)
```

`stitch_assets/dashboard_dualtone.html` file serve karta hai — ye ek custom Tailwind + Neumorphic UI hai jo Gradio se bahut zyada sundar hai.

---

### `POST /api/analyze` — Main REST API Endpoint

```python   
@app.post("/api/analyze")
async def api_analyze(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: str = Form(""),
    job_text: str = Form(""),
    job_image: Optional[UploadFile] = File(None),
    jobs_payload: Optional[str] = Form(None),   # ← multiple jobs JSON
    job_images: Optional[List[UploadFile]] = File(None),  # ← multiple images
):
```

**Ye Gradio `run_pipeline()` se powerful kyun hai:**

| Feature | Gradio Pipeline | FastAPI `/api/analyze` |
|---|---|---|
| Single job | ✅ | ✅ |
| Multiple jobs | ❌ | ✅ (staged jobs payload) |
| Multiple images | ❌ | ✅ |
| REST API (for custom frontends) | ❌ | ✅ |

**`jobs_payload` kya hai:**
```json
[
  {"type": "text", "text": "Software Engineer at Google..."},
  {"type": "image", "image_index": 0},
  {"type": "text", "text": "ML Engineer at Amazon..."}
]
```
Ek JSON array jisme mix of text jobs aur image jobs ho sakte hain. Frontend dashboard se multiple jobs stage karke ek hi API call mein bheji jaati hain.

---

### Gradio Mount as Fallback

```python
gr.mount_gradio_app(app, demo, path="/gradio")
```

Gradio ko `/gradio` route pe mount karta hai — purana interface backward compatibility ke liye available rehta hai.

---

### Auto Port Finding & Browser Launch

```python
def find_free_port(start_port: int = 7860, max_tries: int = 20) -> int:
    for port in range(start_port, start_port + max_tries):
        with socket.socket(...) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port

port = find_free_port(default_port)
webbrowser.open(f"http://127.0.0.1:{port}")
uvicorn.run(app, host="127.0.0.1", port=port)
```

**Kya hota hai:**
- Port 7860 se start karke check karta hai — pehla free port use karta hai
- **Browser automatically khul jaata hai** — user ko manually URL type nahi karna padta
- `uvicorn` FastAPI server ko run karta hai

**Startup Banner:**
```
======================================================================
  🚀 AI RESUME ANALYZER & JOB MATCHING AGENT
  🎯 Direct 1-on-1 Matching: Paste Job Description or Screenshot
  ⚡ Powered by Groq LPU (openai/gpt-oss-120b) + EasyOCR
======================================================================
  👉 Web Dashboard:             http://127.0.0.1:7860
  👉 Fallback Gradio Interface: http://127.0.0.1:7860/gradio
======================================================================
```

---

## 💡 Poore Project Ka Summary — Ek Table Mein

| Section | Kya Karta Hai | Key Tech |
|---|---|---|
| **1** | Imports, `.env` load, API key validate | `groq`, `os`, `sys` |
| **2** | PDF se text nikaalо | `pdfplumber` |
| **3** | Screenshot se text nikaalо (lazy loaded) | `easyocr` |
| **4** | Resume skills + job description structure karo | Groq LLM (json_mode) |
| **5** | Deep 1-on-1 gap analysis + STAR bullets | Groq LLM (json_mode) |
| **6** | ReAct Agent — parallel multi-job evaluation | `ThreadPoolExecutor` |
| **7** | Markdown report generate karo | Python string formatting |
| **8** | Gradio callback — inputs resolve karke agent chalao | Gradio |
| **9** | Custom Gradio UI — tabs, accordions | `gr.Blocks` |
| **10** | FastAPI server, REST API, auto browser launch | `FastAPI`, `uvicorn` |

---

## 🧠 Key Concepts — Simple Bhasha Mein

| Term | Simple Explanation |
|---|---|
| **LLM** | Ek powerful AI model jo human jaisa text samajhta aur likhta hai |
| **Groq** | Company jo LLMs ko ultra-fast run karti hai (bina local download ke) |
| **json_mode** | AI ko force karta hai sirf valid JSON return kare — code parse kar sake |
| **EasyOCR** | Image se text padhne wala AI — jaise hum screenshot padhte hain |
| **pdfplumber** | PDF files se accurately text nikaalне wali library |
| **ReAct Agent** | Step-by-step AI agent jo reason karta hai phir act karta hai |
| **ThreadPoolExecutor** | Multiple tasks ek saath parallel mein chalao — speed badho |
| **ATS Keywords** | Exact words jo automated resume screening software dhundta hai |
| **STAR Format** | Bullet point format: **S**ituation, **T**ask, **A**ction, **R**esult |
| **FastAPI** | Python mein REST API banane ka fastest framework |
| **uvicorn** | FastAPI apps chalane wala ASGI server |
| **Gradio** | Bina HTML/CSS ke web UI banane ki Python library |
| **Lazy Loading** | Resource sirf tab load karo jab actually zarurat ho — startup fast rahe |

---

## ⚠️ Notebook vs Final App — Ek Last Comparison

| Feature | Notebook (`.ipynb`) | Final App (`resume_analyzer.py`) |
|---|---|---|
| Job Matching | Auto RAG (30-job DB) | Direct 1-on-1 target job |
| ChromaDB | ✅ | ❌ Hata diya |
| SentenceTransformer | ✅ | ❌ Hata diya |
| Job Input | Automatic | Paste ya screenshot |
| STAR Bullet Points | ❌ | ✅ AI likhta hai |
| ATS Keywords | ❌ | ✅ |
| Multi-job parallel | ❌ | ✅ |
| UI | Simple `gr.Interface` | Full `gr.Blocks` + FastAPI |
| Screenshot OCR | ❌ | ✅ EasyOCR |
| REST API | ❌ | ✅ `/api/analyze` |
| Custom Dashboard | ❌ | ✅ `dashboard_dualtone.html` |
| Auto browser open | ❌ | ✅ |
