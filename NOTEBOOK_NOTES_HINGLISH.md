# 📚 Notebook Notes — AI Resume Analyzer & Job Matching Agent
### `AI_Resume_Analyzer_Job_Matching_Agent.ipynb` — Poora Cell-by-Cell Guide (Hinglish)

> Ye notebook **project ka original prototype** hai. Isme ChromaDB + SentenceTransformers use hote hain RAG-based job search ke liye. Final `resume_analyzer.py` app isse evolve hui — direct 1-on-1 job matching ke saath.

---

## 🗺️ Badi Picture — Notebook Kaise Kaam Karta Hai

```
[Resume PDF ya Paste kiya hua Text]
        │
        ▼
[pdfplumber text nikaalta hai]
        │
        ▼
[Groq LLM skills extract karta hai → JSON format mein]
        │
        ▼
[SentenceTransformer candidate ke skills ko numbers (vectors) mein convert karta hai]
        │
        ▼
[ChromaDB RAG search → 30 jobs mein se Top 5 similar jobs dhundta hai]
        │
        ▼
[Groq LLM har match ke liye gap analysis karta hai → Match %, Missing Skills, Tips]
        │
        ▼
[ReAct Agent saare steps ko aapas mein jodata hai]
        │
        ▼
[Markdown Report banta hai → Gradio UI mein dikhta hai]
```

---

## 📦 Cell 1 — Dependencies Install Karo

```python
!pip install -q groq chromadb sentence-transformers pdfplumber gradio pandas
```

**Kya karta hai:**
Ye setup cell hai. Isme saare Python packages install hote hain jo notebook chalane ke liye chahiye:

| Package | Kaam |
|---|---|
| `groq` | Groq LLM ko call karne ka API client (hamaara AI brain) |
| `chromadb` | Vector database — jobs store aur search karne ke liye |
| `sentence-transformers` | Text ko numbers (vectors) mein convert karta hai semantic search ke liye |
| `pdfplumber` | PDF resume se text nikaalta hai |
| `gradio` | Web UI banata hai |
| `pandas` | Data handling ke liye |

> `-q` ka matlab hai "quiet" — pip ka zyada output nahi dikhata.

---

## 🔑 Cell 2 — Groq API Setup & LLM Wrapper

```python
os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API key: ")
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL_NAME = "openai/gpt-oss-120b"
```

**Kya karta hai:**
1. **`getpass()`** — Aapse Groq API key maangta hai securely (password ki tarah hidden input).
2. **`Groq(api_key=...)`** — Groq service mein "login" ho jaata hai.
3. **`MODEL_NAME`** — Kaunsa AI model use karna hai — yahan `openai/gpt-oss-120b` jo ek powerful reasoning model hai.

**`call_llm()` function:**
```python
def call_llm(system_prompt, user_prompt, json_mode=False, temperature=0.2):
```
Ye ek helper function hai jo project ke har jagah use hota hai jab bhi AI se baat karni ho:

- `system_prompt` → AI ko instructions dete hain ("tu kya karta hai, kaise reply karta hai")
- `user_prompt` → AI ko actual data bhejte hain (resume text, job description, etc.)
- `json_mode=True` → AI ko force karta hai ki woh sirf valid JSON object return kare — koi extra text nahi
- `temperature=0.2` → Kam temperature = zyada focused, consistent jawab (random hallucination kam)

**Output:** AI ka jawab ek plain string ke roop mein.

---

## 💼 Cell 3 — 30 Sample Jobs Ka Database Load Karo

```python
SAMPLE_JOBS = [
    {"title": "Junior Data Analyst", "company": "Northwind Analytics",
     "required_skills": ["SQL", "Excel", "Python", ...], "description": "..."},
    ...  # kul 30 jobs
]
```

**Kya karta hai:**
30 entry-level tech jobs ki ek **hardcoded list** define karta hai — ek mini job database. Har job mein hai:
- `title` → Job ka naam
- `company` → Company ka naam (fictional)
- `required_skills` → Job ke liye zaruri skills ki list
- `description` → Responsibilities ka short summary

Ant mein yeh list `sample_jobs.json` file mein save ho jaati hai.

**Kyun 30 jobs?** Ye woh "database" hai jisme ChromaDB search karega jab user koi specific job description nahi deta. Isme alag-alag roles hain: Data Analyst, ML Intern, Frontend Dev, Backend Dev, DevOps, NLP Engineer, etc.

---

## 📄 Cell 4 — Resume Input (PDF Upload ya Text Paste)

```python
def parse_resume_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()
```

**Kya karta hai:**
- `pdfplumber.open()` → PDF file kholta hai
- `page.extract_text()` → Har page se text nikaalta hai
- Saare pages ko ek bade string mein jodta hai aur return karta hai

**Do input options:**
1. `UPLOAD_RESUME = True` → Google Colab mein file upload widget se actual PDF upload karo
2. `UPLOAD_RESUME = False` (default) → Ek hardcoded sample resume text use hota hai (Priya Sharma ka) — bina PDF ke test karne ke liye

**Sample Resume (Priya Sharma):**
```
B.Tech Computer Science, XYZ University (2022-2026)
Skills: Python, SQL, Pandas, Basic Machine Learning, HTML, CSS, Git
Experience: Attendance tracker banaya, COVID data analysis kiya, Hackathon chatbot
Certifications: Google Data Analytics (Coursera)
```

---

## 🧠 Cell 5 — AI Se Resume Ke Skills Extract Karo

```python
SKILL_EXTRACTION_SYSTEM_PROMPT = """Tu ek expert resume parser hai.
SIRF valid JSON object return kar:
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

**Kya karta hai:**
Raw resume text ko Groq LLM ko bhejta hai. AI ek professional recruiter ki tarah resume padhta hai aur structured JSON output deta hai.

**AI ko diye gaye smart rules:**
- Skill names normalize karo ("ML" → "Machine Learning")
- Projects se implied skills bhi dhundo (chatbot banaya → "NLP" add karo)
- Missing fields ke liye `null` nahi, empty list `[]` return karo

**Fallback (self-healing):** Agar AI broken/invalid JSON deta hai, toh code dobara AI ko call karta hai aur kehta hai "apna JSON khud fix karo" — AI apni galti khud theek karta hai!

**Sample Output (Priya Sharma ke liye):**
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

**Kya karta hai — 3 steps mein:**

**Step A — Embedder Load Karo:**
`SentenceTransformer("all-MiniLM-L6-v2")` ek chhota AI model hai jo kisi bhi text ko 384 numbers ki list mein convert karta hai (ise "vector" ya "embedding" kehte hain). Similar meaning wale texts ke vectors bhi similar hote hain — yahi magic hai!

**Step B — Saare 30 Jobs Index Karo:**
Har job ek sentence banta hai jaise:
`"Junior Data Analyst. Required skills: SQL, Excel, Python. Analyze business data..."`
→ Phir is sentence ko vector mein convert karo → ChromaDB mein store karo.

**Step C — Best Matching Jobs Dhundo:**
```python
def search_jobs(profile, top_k=5):
    query_text = f"Skills: {', '.join(profile['skills'])}. Experience: ..."
    query_embedding = embedder.encode([query_text]).tolist()
    results = job_collection.query(query_embeddings=query_embedding, n_results=top_k)
```
Candidate ke skills ka bhi vector banta hai. ChromaDB cosine similarity se 5 closest job vectors dhundta hai.

**Similarity kya hoti hai?** Aise samjho — do arrows ki direction kitni milti-julti hai, utna unka similarity score. Same direction = same meaning.

**Sample Output:**
```
- Backend Developer (Entry Level) @ CoreStack Systems  (similarity: 59.5%)
- Data Science Intern @ Quantify Labs  (similarity: 56.6%)
- NLP Engineer (Junior) @ LexiSpeak AI  (similarity: 55.3%)
```

> **Note:** Ye sirf "vector similarity" hai — approximate matching. Precise analysis aage LLM karta hai.

---

## 📊 Cell 7 — Har Match Ke Liye LLM Gap Analysis

```python
GAP_ANALYSIS_SYSTEM_PROMPT = """Tu candidate ke skills ko job ke requirements se compare karta hai.
Return kar sirf JSON:
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

**Kya karta hai:**
RAG se mili 5 jobs mein se har ek ke liye, candidate ka profile aur job requirements dono Groq ko bheje jaate hain — aur AI ek detailed gap analysis karta hai.

**Har job ke liye output:**
- `match_percentage` → Candidate job ki kitni requirements meet karta hai (0-100%)
- `matching_skills` → Candidate ke paas pehle se kya hai jo job chahta hai
- `missing_skills` → Job chahta kya hai jo candidate ke paas nahi
- `learning_suggestions` → Har missing skill ke liye specific resources/tips

**Sample Output:**
```
Backend Developer @ CoreStack: 60% match | Missing: REST APIs, Django
Data Science Intern @ Quantify: 80% match | Missing: Statistics
NLP Engineer @ LexiSpeak: 40% match | Missing: Transformers, Hugging Face
```

---

## 🤖 Cell 8 — ReAct Agent (Project Ka Dimag)

```python
class ResumeMatchingAgent:
    def run(self, resume_text: str) -> dict:
        # Step 1: Skills extract karo
        profile = extract_skills(resume_text)
        if len(profile["skills"]) < 2:
            return {"status": "needs_clarification"}  # jaldi rokna

        # Step 2: RAG se jobs dhundo
        matches = search_jobs(profile, top_k=5)

        # Step 3: Har job ke liye gap analysis
        for m in matches:
            gap = analyze_gap(profile, job_lookup)
            results.append({**m, **gap})

        results.sort(key=lambda r: r["match_percentage"], reverse=True)
        return {"status": "ok", "profile": profile, "results": results}
```

**Kya karta hai:**
Ye **ReAct (Reason + Act)** agent pattern implement karta hai — ek structured AI agent jo step-by-step kaam karta hai:

| Step | Kaam |
|---|---|
| **Step 1** | LLM se resume ke skills extract karo |
| **Guard Check** | Agar 2 se kam skills mile → ruk jao, user se better resume maango |
| **Step 2** | ChromaDB RAG se 5 best matching jobs dhundo |
| **Step 3** | Har job ke liye LLM se gap analysis chalaao |
| **Final** | Results ko match % ke hisaab se sort karo (best pehle) |

**`self.trace`** — Agent ke har step ka log rakhta hai debugging ke liye.

**Yeh "ReAct" kyun hai?**
- **Reason** → "Skills extract kiye, 11 mili, RAG search karta hoon"
- **Act** → Actually tool use karta hai (RAG search, gap analysis)
- **Observe** → Result dekhta hai
- **Repeat** → Agle step pe jaata hai

---

## 📋 Cell 9 — Markdown Report Generate Karo

```python
def generate_report(agent_output: dict) -> str:
    lines = ["# 📄 Resume Analysis Report for " + profile['name']]
    lines.append(f"**Extracted Skills:** {', '.join(profile['skills'])}")
    for i, r in enumerate(agent_output["results"], 1):
        lines.append(f"### {i}. {r['title']} @ {r['company']}")
        lines.append(f"- Match score: {r['match_percentage']}%")
        lines.append(f"- Missing: {', '.join(r['missing_skills'])}")
    return "\n".join(lines)
```

**Kya karta hai:**
Agent ke raw Python dictionary output ko ek clean, human-readable **Markdown document** mein format karta hai — jisme saare 5 job matches, scores, missing skills, aur learning tips dikhte hain.

**Sample Report:**
```
# 📄 Resume Analysis Report for Priya Sharma

**Extracted Skills:** Python, SQL, Pandas, Machine Learning...

## 🎯 Top Job Matches

### 1. Backend Developer (Entry Level) @ CoreStack Systems
- Match score: 60%
- Matching skills: Python, SQL, Git
- Missing skills: REST APIs, Django
- How to close the gap:
  - REST APIs FastAPI ya Flask se seekho — Real Python tutorial free hai
  - Django tutorial Django Girls ya Coursera pe karo
```

---

## 📺 Cell 10 — Notebook Mein Report Render Karo

```python
from IPython.display import Markdown, display
display(Markdown(report_md))
```

**Kya karta hai:**
Markdown text ko Jupyter notebook ke andar **beautifully render** karta hai — `#` aur `**` symbols dikhne ki jagah actual headings, bold text, aur bullet points nazar aate hain. Bilkul ek proper document jaisi dikh jaati hai.

---

## 🖥️ Cell 11 — Gradio Web UI Launch Karo

```python
demo = gr.Interface(
    fn=run_pipeline_from_pdf,
    inputs=gr.File(label="Upload Resume (PDF)", file_types=[".pdf"]),
    outputs=gr.Markdown(label="Recommendation Report"),
    title="AI Resume Analyzer & Job Matching Agent",
)
demo.launch(share=True)
```

**Kya karta hai:**
Poore pipeline ko ek **drag-and-drop web app** mein wrap kar deta hai Gradio use karke — HTML/CSS likhne ki zarurat nahi!

- **Input:** PDF upload box — drag karo ya click karo
- **Output:** Markdown match report browser mein render hoti hai
- **`share=True`** → Ek temporary public URL generate hoti hai (jaise `https://abc123.gradio.live`) — kisi bhi device se access karo bina kuch install kiye

**PDF upload karne par kya hota hai:**
1. `run_pipeline_from_pdf()` call hoti hai
2. PDF text extract → Agent ke teen steps chalte hain → Report banti hai
3. Report screen ke right side pe real-time mein appear hoti hai

**Real demo mein actual output (kisi ka actual resume upload karke):**
```
Extracted 17 skills: ['Java', 'Selenium', 'Spring Boot', 'React',
                      'Tailwind CSS', 'REST APIs', 'Git', 'MySQL', ...]
```

---

## 💡 Saare Cells Ka Summary — Ek Nazar Mein

| Cell | Kya Karta Hai | Key Technology |
|---|---|---|
| **1** | Packages install karo | `pip` |
| **2** | Groq LLM se connect karo | `groq`, `call_llm()` |
| **3** | 30 sample jobs load karo | Python list + JSON |
| **4** | Resume PDF ya text se padhо | `pdfplumber` |
| **5** | AI se skills extract karo | Groq LLM (json_mode) |
| **6** | Similar jobs dhundo vector search se | `SentenceTransformer` + ChromaDB |
| **7** | Har job ke liye gap analysis | Groq LLM (json_mode) |
| **8** | ReAct Agent saare steps jodata hai | `ResumeMatchingAgent` class |
| **9** | Results ko Markdown mein format karo | Python string formatting |
| **10** | Report notebook mein render karo | `IPython.display.Markdown` |
| **11** | Web UI launch karo | Gradio |

---

## ⚠️ Notebook vs Final App — Kya Farq Hai?

| Feature | Ye Notebook (`.ipynb`) | Final App (`resume_analyzer.py`) |
|---|---|---|
| **Job Matching Mode** | RAG auto-search (30-job database) | Direct 1-on-1 target job |
| **ChromaDB** | ✅ Use hota hai | ❌ Hata diya gaya |
| **SentenceTransformer** | ✅ Use hota hai | ❌ Hata diya gaya |
| **Job Description Input** | Automatic (database se) | Manual (paste ya screenshot) |
| **Tailored Bullet Points** | ❌ Nahi hai | ✅ STAR-format AI bullets |
| **Multi-job parallel eval** | ❌ Sequential | ✅ ThreadPoolExecutor |
| **UI** | Simple `gr.Interface` | Full `gr.Blocks` + FastAPI dashboard |
| **ATS Keywords** | ❌ Nahi hai | ✅ Specific ATS keywords list |
| **EasyOCR (screenshot)** | ❌ Nahi hai | ✅ Job screenshot se text nikalta hai |

---

## 🧠 Key Concepts — Simple Bhasha Mein

| Term | Simple Explanation |
|---|---|
| **LLM** | Ek bahut bada AI model jo human-jaise text samajhta aur likhta hai |
| **Groq** | Ek company jo LLMs ko bahut fast run karti hai — local download ki zarurat nahi |
| **JSON** | Ek standard format data store karne ka — key: value pairs mein structured hota hai |
| **Vector/Embedding** | Text ko numbers ki list mein convert karna — similar words = similar numbers |
| **ChromaDB** | Ek database jo vectors store karta hai aur similar vectors quickly dhundta hai |
| **RAG** | Retrieval Augmented Generation — pehle relevant data dhundo, phir AI usse use kare |
| **Cosine Similarity** | Do vectors kitne "same direction" mein hain, iske basis pe similarity score |
| **ReAct Agent** | Ek AI agent jo step-by-step reason karta hai aur tools use karta hai |
| **Gradio** | Python library jo bina HTML/CSS ke web UI banati hai |
| **pdfplumber** | Library jo PDF files se text nikaalne mein expert hai |
