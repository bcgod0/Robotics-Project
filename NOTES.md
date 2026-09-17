# 📚 Complete Line-by-Line Code Notes & Explanation

Welcome to the beginner-friendly guide for the **AI Resume Analyzer & Job Matching Agent** (`resume_analyzer.py`).

This document breaks down every section, function, and critical line of code into simple, plain English.

---

## 🗺️ High-Level System Architecture

Before diving into the code, here is what the program does from start to finish:

```
[1. User uploads Resume PDF]
              │
              ▼
[2. pdfplumber extracts raw text]
              │
              ▼
[3. Groq LLM extracts structured profile (Skills, Experience, Education)]
              │
              ▼
[4. SentenceTransformer converts skills into numerical vector embeddings]
              │
              ▼
[5. ChromaDB vector database performs RAG semantic search across 30 jobs]
              │
              ▼
[6. Groq LLM runs Gap Analysis: compares skills, finds missing ones & course tips]
              │
              ▼
[7. Formatted Markdown Report generated & displayed on Gradio Web Interface]
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
- `import os`: Gives access to operating system functions, such as reading environment variables and checking if files exist.
- `import sys`: Used to interact with Python's runtime environment, such as reconfiguring terminal text output and exiting the program on critical errors.
- `import json as _json`: Used to convert Python dictionaries to JSON strings and parse JSON strings returned by the AI into Python dictionaries.

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```
- **Why this is here:** Windows terminals default to an old character encoding called `cp1252`. When Python prints emojis like `✅` or `🧠`, Windows crashes with a `UnicodeEncodeError`.
- `reconfigure(encoding="utf-8", errors="replace")` forces the terminal to accept modern UTF-8 text so emojis print without errors.

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
- **What this does:** Checks if a `.env` file exists in the folder.
- If it does, it opens and reads it line-by-line.
- It looks for `GROQ_API_KEY=` and `GROQ_MODEL=`, strips away any extra spaces or quotes, and saves them to `os.environ`.
- **Why it's written this way:** It loads `.env` **first**, ensuring that any newly pasted key overrides any old or expired key cached in your PowerShell session.

```python
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = input("Enter your Groq API key: ").strip()

_key = os.environ["GROQ_API_KEY"]
print(f"Loaded Groq API key: {_key[:8]}...{_key[-4:] if len(_key) > 12 else ''}")
```
- If no key was found in `.env`, it asks you to type or paste it into the console using `input()`.
- It then prints a masked preview (e.g. `gsk_N5sk...2tp0`) so you know which key is active without exposing the secret.

```python
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_NAME = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
```
- `from groq import Groq`: Imports the official client library for communicating with Groq's high-speed AI chips (LPU).
- `client = Groq(...)`: Initializes the client object using your API key.
- `MODEL_NAME`: Defaults to `"openai/gpt-oss-120b"`, the ultra-fast 120B reasoning model available on your Groq tier.

```python
try:
    client.models.list()
    print(f"✅ Groq API key verified successfully! Using model: {MODEL_NAME}")
except Exception as _auth_err:
    err_msg = str(_auth_err)
    if "401" in err_msg or "invalid_api_key" in err_msg.lower():
        print("\n" + "=" * 65)
        print("❌ [GROQ AUTHENTICATION FAILED - 401 Invalid API Key]")
        print("=" * 65)
        print("The Groq API key in your .env file is invalid or was revoked.")
        ...
        sys.exit(1)
```
- **Instant Health-Check:** Makes a quick test call to Groq (`client.models.list()`) right when the program starts.
- If the key is invalid or revoked, it halts immediately with clear instructions rather than crashing later in the middle of analyzing a resume.

```python
def call_llm(system_prompt: str, user_prompt: str,
             json_mode: bool = False, temperature: float = 0.2) -> str:
    """Thin wrapper around the Groq chat completion endpoint."""
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return resp.choices[0].message.content
```
- This helper function sends a prompt to the Groq LLM:
  - `system_prompt`: Instructions that define the AI's role and rules (e.g., "You are an expert resume parser").
  - `user_prompt`: The actual resume text or job details to process.
  - `json_mode=True`: Forces the LLM to reply strictly with a machine-readable JSON object (no chit-chat or code fences).
  - `temperature=0.2`: Low temperature ensures factual, reliable, and consistent responses without hallucinating.

---

### Section 2: Sample Job Postings Database

```python
SAMPLE_JOBS = [
    {"title": "Junior Data Analyst", "company": "Northwind Analytics",
     "required_skills": ["SQL", "Excel", "Python", "Data Visualization", "Statistics"],
     "description": "Analyze business data, build dashboards, and generate insights..."},
    ...
]

with open("sample_jobs.json", "w") as f:
    _json.dump(SAMPLE_JOBS, f, indent=2)
```
- Defines a list of 30 entry-level and internship tech jobs across Data Science, Software Engineering, AI/ML, DevOps, UI/UX, Cloud, and Cybersecurity.
- Each job contains:
  - `title`: Job role.
  - `company`: Company name.
  - `required_skills`: List of required technologies and competencies.
  - `description`: Overview of job duties.
- `_json.dump(...)`: Saves these 30 jobs to a local file (`sample_jobs.json`).

---

### Section 3: PDF Resume Parser

```python
import pdfplumber

def parse_resume_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()
```
- `pdfplumber.open(file_path)`: Opens the PDF document file.
- `for page in pdf.pages`: Loops through every page of the resume.
- `page.extract_text()`: Reads text lines preserving spacing and layout.
- `"\n".join(text_parts).strip()`: Combines all pages into a single plain text string.

---

### Section 4: LLM Skill Extraction & Coercion

```python
SKILL_EXTRACTION_SYSTEM_PROMPT = """You are an expert resume parser. Extract structured information
from the resume text the user gives you. Always respond with ONLY a valid JSON object - no markdown,
no commentary, no code fences. Use this exact schema:

{
  "name": "string",
  "skills": ["skill1", "skill2", ...],
  "education": ["degree, institution, year"],
  "experience": ["short description of each experience/project"],
  "certifications": ["cert1", ...]
}

Rules:
- Normalize skill names (e.g. "ML" -> "Machine Learning").
- Include skills implied by projects/experience, not just an explicit "Skills:" line.
- If a field has no data, return an empty list (never null, never omit the key).
"""
```
- Tells the LLM to act as a resume parser and specifies the strict JSON structure required.
- **Normalization Rule:** Normalizes acronyms (e.g. converting `ML` to `Machine Learning`, `AWS` to standard naming) to maximize match accuracy.

```python
def _coerce_profile(result) -> dict:
    if isinstance(result, list):
        return {
            "name": "",
            "skills": result,
            "education": [],
            "experience": [],
            "certifications": [],
        }
    if not isinstance(result, dict):
        return {
            "name": "",
            "skills": [],
            "education": [],
            "experience": [],
            "certifications": [],
        }
    return result
```
- **Defensive Type Guard:** LLMs sometimes return a bare JSON list `["Python", "SQL"]` instead of a dictionary `{"skills": ["Python", ...]}`.
- If left unguarded, `profile.get("skills")` crashes with `AttributeError: 'list' object has no attribute 'get'`.
- `_coerce_profile` catches this and wraps lists into a dictionary so downstream functions never crash.

```python
def extract_skills(resume_text: str) -> dict:
    raw = call_llm(SKILL_EXTRACTION_SYSTEM_PROMPT, resume_text, json_mode=True)
    try:
        return _coerce_profile(_json.loads(raw))
    except _json.JSONDecodeError:
        fixed = call_llm(
            "Fix this into strictly valid JSON matching the required schema. Return ONLY JSON.",
            raw,
            json_mode=True,
        )
        return _coerce_profile(_json.loads(fixed))
```
- Calls Groq with the resume text and the prompt.
- `_json.loads(raw)`: Parses the AI's string response into a Python dictionary.
- **Self-Healing Fallback:** If the JSON response is ever slightly corrupted, it automatically sends it back to the LLM asking it to fix the JSON syntax, then parses it again.

---

### Section 5: RAG Vector Search with SentenceTransformers & ChromaDB

```python
import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
```
- `SentenceTransformer("all-MiniLM-L6-v2")`: A lightweight NLP embedding model that maps any sentence or skill list into a 384-dimensional mathematical vector (coordinates).
- Similar concepts (e.g., "Python Developer" and "Backend Engineer") are placed close together in vector space.

```python
chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("jobs")
except Exception:
    pass
job_collection = chroma_client.create_collection("jobs")
```
- Initializes **ChromaDB**, an in-memory vector database.
- Deletes any old collection named `"jobs"` and creates a clean new one.

```python
job_docs, job_ids, job_metadatas = [], [], []
for i, job in enumerate(SAMPLE_JOBS):
    doc_text = f"{job['title']}. Required skills: {', '.join(job['required_skills'])}. {job['description']}"
    job_docs.append(doc_text)
    job_ids.append(str(i))
    job_metadatas.append({
        "title": job["title"],
        "company": job["company"],
        "required_skills": ", ".join(job["required_skills"]),
        "description": job["description"],
    })

job_embeddings = embedder.encode(job_docs).tolist()

job_collection.add(
    ids=job_ids,
    embeddings=job_embeddings,
    documents=job_docs,
    metadatas=job_metadatas,
)
```
- Prepares text representations for all 30 jobs.
- `embedder.encode(job_docs)`: Converts all 30 job descriptions into vector embeddings.
- Stores the vectors, document text, and metadata (title, company, required skills) in ChromaDB.

```python
def search_jobs(profile: dict, top_k: int = 5) -> list:
    query_text = (
        f"Skills: {', '.join(profile.get('skills', []))}. "
        f"Experience: {'; '.join(profile.get('experience', []))}"
    )
    query_embedding = embedder.encode([query_text]).tolist()
    results = job_collection.query(query_embeddings=query_embedding, n_results=top_k)

    matches = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        similarity = max(0.0, 1 - distance / 2)
        matches.append({**meta, "similarity": round(similarity * 100, 1)})
    return matches
```
- Converts the candidate's extracted skills and experience into a single search query vector.
- Queries ChromaDB to find the **`top_k` (default 5)** closest jobs mathematically.
- Converts vector distance into an intuitive percentage similarity (e.g., `85.4%`).

---

### Section 6: LLM Gap Analysis

```python
GAP_ANALYSIS_SYSTEM_PROMPT = """You compare a candidate's skills against a job's required skills.
Respond with ONLY a valid JSON object, no markdown, using this schema:

{
  "match_percentage": 0-100,
  "matching_skills": ["..."],
  "missing_skills": ["..."],
  "learning_suggestions": ["short, concrete suggestion per missing skill"]
}
"""
```
- Asks the LLM to compare the candidate with a specific job.
- Generates:
  1. `match_percentage`: Overall fit score (0–100%).
  2. `matching_skills`: Skills the candidate already possesses.
  3. `missing_skills`: Required skills the candidate lacks.
  4. `learning_suggestions`: Concrete, actionable steps to learn each missing skill.

```python
def analyze_gap(profile: dict, job: dict) -> dict:
    user_prompt = (
        f"Candidate skills: {profile.get('skills', [])}\n"
        f"Candidate experience: {profile.get('experience', [])}\n\n"
        f"Job title: {job['title']}\n"
        f"Job required skills: {job['required_skills']}\n"
        f"Job description: {job['description']}"
    )
    raw = call_llm(GAP_ANALYSIS_SYSTEM_PROMPT, user_prompt, json_mode=True)
    try:
        return _json.loads(raw)
    except _json.JSONDecodeError:
        fixed = call_llm(
            "Fix this into strictly valid JSON matching the schema. Return ONLY JSON.",
            raw,
            json_mode=True,
        )
        return _json.loads(fixed)
```
- Formats the candidate profile and job requirements into a prompt and passes it to `call_llm`.
- Parses the resulting JSON object with self-healing fallback.

---

### Section 7: ReAct-style Agent Workflow

```python
class ResumeMatchingAgent:
    def __init__(self, top_k: int = 5, min_skills: int = 2):
        self.top_k = top_k
        self.min_skills = min_skills
        self.trace = []

    def log(self, msg):
        self.trace.append(msg)
        print(msg)
```
- Implements an autonomous agent following the **ReAct pattern** (Reason + Act):
  - Tracks internal execution steps in `self.trace`.
  - `min_skills`: Guardrail requiring at least 2 detected skills to proceed.

```python
    def run(self, resume_text: str) -> dict:
        self.log("🧠 [Agent] Step 1: Extracting skills from resume...")
        profile = extract_skills(resume_text)

        if len(profile.get("skills", [])) < self.min_skills:
            self.log("⚠️ [Agent] Too few skills detected. Stopping and requesting clarification.")
            return {
                "status": "needs_clarification",
                "message": (
                    "Couldn't confidently extract enough skills. Please provide a more "
                    "detailed resume or list your key skills explicitly."
                ),
                "profile": profile,
            }
```
- **Step 1:** Calls `extract_skills`.
- **Early Exit Guardrail:** If the resume contains fewer than 2 recognizable skills (e.g. blank page or poorly formatted file), it stops early and informs the user rather than running useless searches.

```python
        self.log("🧠 [Agent] Step 2: Retrieving candidate jobs via RAG...")
        matches = search_jobs(profile, top_k=self.top_k)

        if not matches:
            self.log("⚠️ [Agent] No jobs found...")
            return {"status": "no_matches", "profile": profile}

        self.log("🧠 [Agent] Step 3: Running gap analysis for each match...")
        results = []
        for m in matches:
            job_lookup = {
                "title": m["title"],
                "required_skills": m["required_skills"].split(", "),
                "description": m["description"],
            }
            gap = analyze_gap(profile, job_lookup)
            results.append({**m, **gap})

        results.sort(key=lambda r: r.get("match_percentage", 0), reverse=True)
        self.log("✅ [Agent] Gap analysis complete. Compiling final report.")

        return {"status": "ok", "profile": profile, "results": results}
```
- **Step 2:** Uses semantic vector search to find candidate jobs from ChromaDB.
- **Step 3:** For each retrieved job, it runs a deep gap analysis via the LLM.
- Sorts the final matches from highest match percentage to lowest.

---

### Section 8: Markdown Report Generator

```python
def generate_report(agent_output: dict) -> str:
    if agent_output["status"] != "ok":
        return f"⚠️ {agent_output.get('message', 'Could not generate a report.')}"

    profile = agent_output["profile"]
    lines = []
    lines.append(f"# Resume Analysis Report for {profile.get('name', 'Candidate')}\n")
    lines.append(f"**Extracted Skills:** {', '.join(profile.get('skills', []))}\n")
    lines.append("## Top Job Matches\n")

    for i, r in enumerate(agent_output["results"], 1):
        lines.append(f"### {i}. {r['title']} @ {r['company']}")
        lines.append(f"- **Match score:** {r.get('match_percentage', 'N/A')}%  (retrieval similarity: {r['similarity']}%)")
        lines.append(f"- **Matching skills:** {', '.join(r.get('matching_skills', [])) or 'None'}")
        lines.append(f"- **Missing skills:** {', '.join(r.get('missing_skills', [])) or 'None'}")
        if r.get("learning_suggestions"):
            lines.append("- **How to close the gap:**")
            for s in r["learning_suggestions"]:
                lines.append(f"  - {s}")
        lines.append("")

    return "\n".join(lines)
```
- Converts the raw dictionary results from the agent into a readable, formatted Markdown document with headings, bullet points, match percentages, and learning recommendations.

---

### Section 9: Gradio Web Interface

```python
import gradio as gr

def run_pipeline_from_pdf(pdf_file):
    if pdf_file is None:
        return "Please upload a resume PDF."

    # Gradio version compatibility check
    file_path = pdf_file if isinstance(pdf_file, str) else pdf_file.name

    text = parse_resume_pdf(file_path)

    if not text.strip():
        return (
            "Could not extract any text from the uploaded PDF. "
            "Please ensure it is not a scanned image-only document."
        )

    try:
        output = ResumeMatchingAgent(top_k=5).run(text)
        return generate_report(output)
    except Exception as e:
        ...
```
- `run_pipeline_from_pdf`: Callback function executed when the user clicks **Submit** in the web interface.
- Handles differences between Gradio versions (Gradio 4 passes file path as `str`, Gradio 3 as an object with `.name`).
- Guards against image-only/scanned PDFs that contain no extractable text.
- Wraps execution in `try-except` to present clean error messages in the UI.

```python
demo = gr.Interface(
    fn=run_pipeline_from_pdf,
    inputs=gr.File(label="Upload Resume (PDF)", file_types=[".pdf"]),
    outputs=gr.Markdown(label="Recommendation Report"),
    title="AI Resume Analyzer & Job Matching Agent",
    description="Agentic AI: LLM skill extraction + RAG job retrieval + gap analysis (Groq-powered).",
)

if __name__ == "__main__":
    demo.launch(debug=False, share=True)
```
- Builds an interactive web application:
  - Input: File upload box accepting `.pdf` files.
  - Output: Formatted Markdown text area.
- `share=True`: Generates both a local URL (`http://127.0.0.1:7860`) and a temporary public link (`https://xxxx.gradio.live`) so anyone can try your app from their phone or browser.

---

## 💡 Key Machine Learning Concepts Explained

| Concept | What It Means in Simple Terms | Where It Is Used in Code |
| :--- | :--- | :--- |
| **LLM (Large Language Model)** | An advanced neural network trained on massive text to reason, extract information, and write content. | Groq (`openai/gpt-oss-120b`) in `call_llm()` |
| **Vector Embedding** | Turning words and sentences into a list of numbers (coordinates) so computers can calculate mathematical similarity between meanings. | `SentenceTransformer("all-MiniLM-L6-v2")` |
| **RAG (Retrieval-Augmented Generation)** | First retrieving relevant records from a vector database (ChromaDB), then passing them to the LLM to reason over. | `search_jobs()` + `analyze_gap()` |
| **Agentic Workflow / ReAct** | An AI that doesn't just answer once, but takes a step-by-step loop: Reason ➔ Use Tool ➔ Validate Result ➔ Plan next step. | `ResumeMatchingAgent` class |
| **JSON Mode** | Enforcing strict JSON syntax on LLM outputs so programs can parse results without regex or text scraping errors. | `json_mode=True` parameter |
| **Cosine Distance / Similarity** | The angular distance between two vectors. A distance of `0` means identical concepts; `2` means opposites. | `similarity = max(0.0, 1 - distance / 2)` in `search_jobs()` |
