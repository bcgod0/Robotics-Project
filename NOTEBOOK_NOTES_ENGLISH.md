# 📚 Notebook Notes — AI Resume Analyzer & Job Matching Agent
### `AI_Resume_Analyzer_Job_Matching_Agent.ipynb` — Complete Cell-by-Cell Guide (English)

> This is the **original prototype notebook** of the project. It uses ChromaDB + SentenceTransformers for RAG-based job discovery (database mode). The final `resume_analyzer.py` app evolved from this notebook into a direct 1-on-1 target job matcher.

---

## 🗺️ Big Picture — How the Notebook Works

```
[Resume PDF / Pasted Text]
        │
        ▼
[pdfplumber extracts text]
        │
        ▼
[Groq LLM extracts skills & profile as JSON]
        │
        ▼
[SentenceTransformer embeds candidate skills → vector]
        │
        ▼
[ChromaDB RAG search → Top 5 similar jobs from 30-job database]
        │
        ▼
[Groq LLM runs gap analysis on each match → Match %, Missing Skills, Tips]
        │
        ▼
[ReAct Agent ties all steps together]
        │
        ▼
[Markdown Report generated → Displayed in Gradio UI]
```

---

## 📦 Cell 1 — Install Dependencies

```python
!pip install -q groq chromadb sentence-transformers pdfplumber gradio pandas
```

**What it does:**
This is the setup cell. It installs all the Python packages needed to run the notebook:

| Package | Purpose |
|---|---|
| `groq` | API client to call Groq's LLM (our AI brain) |
| `chromadb` | Vector database to store and search job postings |
| `sentence-transformers` | Converts text into number vectors for semantic search |
| `pdfplumber` | Reads and extracts text from PDF resumes |
| `gradio` | Creates the web UI for the app |
| `pandas` | Data handling (used implicitly) |

> The `-q` flag means "quiet" — it suppresses verbose pip output.

---

## 🔑 Cell 2 — Setup Groq API & LLM Wrapper

```python
os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API key: ")
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_NAME = "openai/gpt-oss-120b"
```

**What it does:**
1. **`getpass()`** — Asks you to type your Groq API key securely (hidden input, like a password field).
2. **`Groq(api_key=...)`** — Creates a Groq client. Think of this as "logging into" the Groq service.
3. **`MODEL_NAME = "openai/gpt-oss-120b"`** — Selects the AI model to use.

**`call_llm()` function:**
```python
def call_llm(system_prompt, user_prompt, json_mode=False, temperature=0.2):
```
This is a helper function used by every part of the project that needs to talk to the AI:
- `system_prompt` → Instructions for the AI (its "role" and rules)
- `user_prompt` → The actual data you send to the AI (resume text, job description, etc.)
- `json_mode=True` → Forces the AI to return a strict JSON object (no extra words)
- `temperature=0.2` → Low temperature = more focused, consistent answers (less random)

---

## 💼 Cell 3 — Load 30 Sample Jobs Database

```python
SAMPLE_JOBS = [
    {"title": "Junior Data Analyst", "company": "Northwind Analytics",
     "required_skills": ["SQL", "Excel", "Python", ...], "description": "..."},
    ...  # 30 jobs total
]
```

**What it does:**
Defines a hardcoded list of 30 entry-level tech jobs — a mini job database. Each job has a `title`, `company`, `required_skills` list, and `description`. This list is saved to `sample_jobs.json`.

**Why?** This is the database ChromaDB will search through when the user doesn't provide a specific job description.

---

## 📄 Cell 4 — Resume Input (PDF Upload or Paste Text)

```python
def parse_resume_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()
```

**What it does:**
- Opens a PDF with `pdfplumber` and extracts text from every page.

**Two input modes:**
1. `UPLOAD_RESUME = True` → Google Colab file upload widget
2. `UPLOAD_RESUME = False` (default) → Hardcoded sample resume text (Priya Sharma) for quick testing

**Sample resume used:**
```
Priya Sharma | B.Tech CS, XYZ University (2022-2026)
Skills: Python, SQL, Pandas, Machine Learning, HTML, CSS, Git
Projects: Attendance tracker, COVID analysis, Hackathon chatbot
Certifications: Google Data Analytics (Coursera)
```

---

## 🧠 Cell 5 — AI Skill Extraction from Resume

```python
SKILL_EXTRACTION_SYSTEM_PROMPT = """You are an expert resume parser.
Always respond with ONLY a valid JSON object:
{
  "name": "string",
  "skills": ["skill1", "skill2", ...],
  "education": [...],
  "experience": [...],
  "certifications": [...]
}"""

def extract_skills(resume_text: str) -> dict:
    raw = call_llm(SKILL_EXTRACTION_SYSTEM_PROMPT, resume_text, json_mode=True)
    return _json.loads(raw)
```

**What it does:**
Sends the raw resume text to Groq LLM. The AI reads it like a recruiter and outputs a clean JSON object.

**Smart rules given to the AI:**
- Normalize skills ("ML" → "Machine Learning")
- Infer skills from projects (built a chatbot → add "NLP")
- Return empty lists instead of `null`

**Fallback:** If the AI returns broken JSON, the code calls the AI again and asks it to fix its own output — self-healing!

**Sample Output:**
```json
{
  "name": "Priya Sharma",
  "skills": ["Python", "SQL", "Pandas", "Machine Learning", "NLP", "SQLite", ...],
  "education": ["B.Tech CS, XYZ University, 2026"],
  "certifications": ["Google Data Analytics (Coursera)"]
}
```

---

## 🔍 Cell 6 — ChromaDB RAG Job Search (Vector Similarity)

```python
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
job_collection = chroma_client.create_collection("jobs")
```

**What it does — 3 steps:**

**Step A — Load the Embedder:**
`SentenceTransformer("all-MiniLM-L6-v2")` is a small AI model that converts text → a list of 384 numbers (a "vector"). Similar meaning = similar vectors.

**Step B — Index All 30 Jobs:**
Each job becomes a sentence like:
`"Junior Data Analyst. Required skills: SQL, Excel, Python. Analyze business data..."`
→ Converted to a vector → Stored in ChromaDB.

**Step C — Search for Best Matches:**
```python
def search_jobs(profile, top_k=5):
    query_text = f"Skills: {', '.join(profile['skills'])}. Experience: ..."
    query_embedding = embedder.encode([query_text]).tolist()
    results = job_collection.query(query_embeddings=query_embedding, n_results=top_k)
```
Candidate's skills are vectorized, then ChromaDB finds the 5 closest job vectors via cosine similarity.

**Sample Output:**
```
- Backend Developer (Entry Level) @ CoreStack Systems  (similarity: 59.5%)
- Data Science Intern @ Quantify Labs  (similarity: 56.6%)
- NLP Engineer (Junior) @ LexiSpeak AI  (similarity: 55.3%)
```

---

## 📊 Cell 7 — LLM Gap Analysis for Each Match

```python
GAP_ANALYSIS_SYSTEM_PROMPT = """Compare candidate skills vs job requirements.
Return JSON:
{
  "match_percentage": 0-100,
  "matching_skills": [...],
  "missing_skills": [...],
  "learning_suggestions": [...]
}"""

def analyze_gap(profile, job) -> dict:
    raw = call_llm(GAP_ANALYSIS_SYSTEM_PROMPT, user_prompt, json_mode=True)
    return _json.loads(raw)
```

**What it does:**
For each of the 5 RAG-retrieved jobs, it sends the candidate's profile + job requirements to Groq for a precise, deep analysis.

**Output per job:**
- `match_percentage` — What % of requirements does the candidate meet?
- `matching_skills` — What they already have
- `missing_skills` — What they lack
- `learning_suggestions` — Specific tips to bridge each gap

**Sample Output:**
```
Backend Developer @ CoreStack: 60% match | Missing: REST APIs, Django
Data Science Intern @ Quantify: 80% match | Missing: Statistics
```

---

## 🤖 Cell 8 — ReAct Agent (The Brain)

```python
class ResumeMatchingAgent:
    def run(self, resume_text: str) -> dict:
        # Step 1: Extract skills
        profile = extract_skills(resume_text)
        if len(profile["skills"]) < 2:
            return {"status": "needs_clarification"}  # early exit

        # Step 2: RAG search
        matches = search_jobs(profile, top_k=5)

        # Step 3: Gap analysis
        for m in matches:
            gap = analyze_gap(profile, job_lookup)
            results.append({**m, **gap})

        results.sort(key=lambda r: r["match_percentage"], reverse=True)
        return {"status": "ok", "profile": profile, "results": results}
```

**What it does:**
Implements the **ReAct (Reason + Act)** agent pattern — a structured, step-by-step AI agent.

| Step | Action |
|---|---|
| **1** | Extract skills from resume via LLM |
| **Guard** | If < 2 skills found → stop, ask for better resume |
| **2** | RAG search to find 5 most similar jobs |
| **3** | Gap analysis for each job |
| **Final** | Sort by match % and return results |

`self.trace` keeps a visible log of every step for debugging.

---

## 📋 Cell 9 — Generate Markdown Report

```python
def generate_report(agent_output: dict) -> str:
    lines = ["# 📄 Resume Analysis Report for " + profile['name']]
    for i, r in enumerate(agent_output["results"], 1):
        lines.append(f"### {i}. {r['title']} @ {r['company']}")
        lines.append(f"- Match score: {r['match_percentage']}%")
        lines.append(f"- Missing: {', '.join(r['missing_skills'])}")
    return "\n".join(lines)
```

**What it does:**
Takes the agent's raw dictionary output and formats it into a clean, human-readable Markdown document showing all 5 job matches, scores, missing skills, and learning suggestions.

---

## 📺 Cell 10 — Render Report in Notebook

```python
from IPython.display import Markdown, display
display(Markdown(report_md))
```

**What it does:**
Renders the Markdown report **beautifully inside the Jupyter notebook** — showing actual headings, bold text, and bullet points instead of raw `#` and `**` symbols.

---

## 🖥️ Cell 11 — Gradio Web UI

```python
demo = gr.Interface(
    fn=run_pipeline_from_pdf,
    inputs=gr.File(label="Upload Resume (PDF)", file_types=[".pdf"]),
    outputs=gr.Markdown(label="Recommendation Report"),
    title="AI Resume Analyzer & Job Matching Agent",
)
demo.launch(share=True)
```

**What it does:**
Wraps the entire pipeline in a drag-and-drop web application using Gradio. The user uploads a PDF → the full agent pipeline runs → the report appears in the browser.

**`share=True`** → Generates a public temporary URL (e.g., `https://abc123.gradio.live`) so it can be accessed from anywhere.

**Real demo output (actual test):**
```
Extracted 17 skills: ['Java', 'Selenium', 'Spring Boot', 'React',
                      'Tailwind CSS', 'REST APIs', 'Git', ...]
```

---

## 💡 Summary of All Cells

| Cell | What It Does | Key Tech |
|---|---|---|
| 1 | Install packages | `pip` |
| 2 | Connect to Groq LLM | `groq`, `call_llm()` |
| 3 | Load 30 sample jobs | Python list + JSON |
| 4 | Read resume from PDF or text | `pdfplumber` |
| 5 | Extract skills with AI | Groq LLM (json_mode) |
| 6 | Find similar jobs via vector search | `SentenceTransformer` + ChromaDB |
| 7 | Gap analysis for each job | Groq LLM (json_mode) |
| 8 | ReAct Agent ties steps 1–3 | `ResumeMatchingAgent` class |
| 9 | Format results as Markdown | Python string formatting |
| 10 | Display formatted report | `IPython.display.Markdown` |
| 11 | Launch web UI | Gradio |

---

## ⚠️ Notebook vs Final App — Key Differences

| Feature | This Notebook | Final `resume_analyzer.py` |
|---|---|---|
| Job Matching | Auto-RAG from 30-job database | Manual 1-on-1 target job |
| ChromaDB | ✅ Used | ❌ Removed |
| SentenceTransformer | ✅ Used | ❌ Removed |
| Job Description Input | Automatic | Paste text or screenshot |
| Tailored Bullet Points | ❌ Not present | ✅ STAR-format AI bullets |
| Multi-job parallel eval | ❌ Sequential | ✅ ThreadPoolExecutor |
| UI | Simple `gr.Interface` | Full `gr.Blocks` + FastAPI |
| ATS Keywords | ❌ Not present | ✅ Explicit ATS keyword list |
