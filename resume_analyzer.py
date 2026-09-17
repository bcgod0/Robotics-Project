"""
AI Resume Analyzer & Job Matching Agent
========================================
Standalone Python script converted from the Jupyter notebook.

Fixes applied vs. the original notebook:
  1. extract_skills() – added _coerce_profile() guard so that when the LLM
     returns a JSON array (instead of a dict) the pipeline no longer crashes
     with  AttributeError: 'list' object has no attribute 'get'.
  2. run_pipeline_from_pdf() – fixed Gradio file-object handling to support
     both Gradio <= 3.x (NamedString with .name) and Gradio >= 4.x (plain str
     path), preventing AttributeError: 'str' object has no attribute 'name'.
  3. run_pipeline_from_pdf() – added a guard for empty/image-only PDFs so the
     user gets a clear warning instead of a silent crash.

Run:
    python resume_analyzer.py
"""

# ── 1. Imports & Groq client ─────────────────────────────────────────────────
import os
import json as _json

# Read API key from environment variable, or prompt via plain input().
# (getpass is avoided because it breaks in Windows terminals like VS Code / PowerShell)
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = input("Enter your Groq API key: ").strip()

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL_NAME = "openai/gpt-oss-120b"


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


print("Groq client ready. Model:", MODEL_NAME)


# ── 2. Sample job postings ───────────────────────────────────────────────────
SAMPLE_JOBS = [
    {"title": "Junior Data Analyst", "company": "Northwind Analytics",
     "required_skills": ["SQL", "Excel", "Python", "Data Visualization", "Statistics"],
     "description": "Analyze business data, build dashboards, and generate insights for stakeholders. Entry-level role, training provided on internal tools."},
    {"title": "Machine Learning Intern", "company": "Vertex AI Labs",
     "required_skills": ["Python", "Machine Learning", "NumPy", "Pandas", "Scikit-learn"],
     "description": "Assist the ML team in building and evaluating models for recommendation systems. Exposure to production ML pipelines."},
    {"title": "Frontend Developer (Junior)", "company": "PixelForge",
     "required_skills": ["JavaScript", "React", "HTML", "CSS", "Git"],
     "description": "Build responsive UI components for a SaaS product. Work closely with designers and backend engineers."},
    {"title": "Backend Developer (Entry Level)", "company": "CoreStack Systems",
     "required_skills": ["Python", "REST APIs", "SQL", "Django", "Git"],
     "description": "Develop and maintain backend services and APIs for a growing fintech platform."},
    {"title": "Business Intelligence Trainee", "company": "Insight Metrics",
     "required_skills": ["SQL", "Power BI", "Excel", "Data Modeling"],
     "description": "Support the BI team in building reports and dashboards for leadership decision-making."},
    {"title": "AI/ML Research Assistant", "company": "Cognivance Research",
     "required_skills": ["Python", "PyTorch", "Deep Learning", "Research Writing"],
     "description": "Support ongoing NLP research projects, run experiments, and help prepare publications."},
    {"title": "Cloud Support Engineer (Junior)", "company": "SkyNet Cloud Services",
     "required_skills": ["AWS", "Linux", "Networking Basics", "Python", "Troubleshooting"],
     "description": "Provide first-line support for cloud infrastructure customers and escalate complex issues."},
    {"title": "QA/Automation Tester", "company": "Bright Software Co",
     "required_skills": ["Selenium", "Python", "Test Case Design", "Git", "Agile"],
     "description": "Write and execute automated test scripts to ensure product quality before releases."},
    {"title": "RPA Developer (UiPath) - Fresher", "company": "AutomateX",
     "required_skills": ["UiPath", "RPA Concepts", "C#", ".NET Basics", "Process Analysis"],
     "description": "Design, build, and maintain RPA bots using UiPath to automate business workflows."},
    {"title": "Data Engineering Intern", "company": "PipelineWorks",
     "required_skills": ["Python", "SQL", "ETL", "Airflow", "Cloud Basics"],
     "description": "Help build and maintain data pipelines feeding analytics and ML systems."},
    {"title": "NLP Engineer (Junior)", "company": "LexiSpeak AI",
     "required_skills": ["Python", "NLP", "Transformers", "Hugging Face", "Prompt Engineering"],
     "description": "Build and fine-tune NLP models for a conversational AI product."},
    {"title": "Full Stack Developer (Entry Level)", "company": "AppNova",
     "required_skills": ["JavaScript", "Node.js", "React", "MongoDB", "REST APIs"],
     "description": "Work across the stack to ship features for a fast-growing consumer app."},
    {"title": "DevOps Intern", "company": "InfraLoop",
     "required_skills": ["Docker", "CI/CD", "Linux", "Git", "Cloud Basics"],
     "description": "Support deployment pipelines and infrastructure automation for engineering teams."},
    {"title": "Product Analyst Intern", "company": "Metricly",
     "required_skills": ["SQL", "Excel", "A/B Testing", "Data Visualization"],
     "description": "Analyze product usage data to support feature prioritization decisions."},
    {"title": "Cybersecurity Analyst Trainee", "company": "SentinelGuard",
     "required_skills": ["Networking", "Linux", "Security Fundamentals", "Python"],
     "description": "Monitor systems for security threats and assist in incident response under supervision."},
    {"title": "Mobile App Developer (Android) - Junior", "company": "AppSprout",
     "required_skills": ["Kotlin", "Android SDK", "Git", "REST APIs"],
     "description": "Develop and maintain features for a consumer Android application."},
    {"title": "Computer Vision Intern", "company": "VisionEdge AI",
     "required_skills": ["Python", "OpenCV", "Deep Learning", "PyTorch"],
     "description": "Work on object detection and image classification models for retail analytics."},
    {"title": "Technical Support Engineer", "company": "HelpDesk Pro",
     "required_skills": ["Troubleshooting", "SQL Basics", "Communication", "Linux Basics"],
     "description": "Resolve customer-reported technical issues and escalate as needed."},
    {"title": "Automation Engineer (Python)", "company": "ScriptWorks",
     "required_skills": ["Python", "Automation Scripting", "APIs", "Git"],
     "description": "Build internal automation tools to streamline repetitive business processes."},
    {"title": "Data Science Intern", "company": "Quantify Labs",
     "required_skills": ["Python", "Pandas", "Machine Learning", "Statistics", "Data Visualization"],
     "description": "Work on real datasets to build predictive models and present findings to stakeholders."},
    {"title": "UI/UX Designer (Junior)", "company": "DesignHive",
     "required_skills": ["Figma", "Wireframing", "User Research", "Prototyping"],
     "description": "Design intuitive interfaces for web and mobile products in collaboration with developers."},
    {"title": "IT Support Analyst", "company": "GlobalTech Services",
     "required_skills": ["Windows Admin", "Networking Basics", "Troubleshooting", "Ticketing Systems"],
     "description": "Provide day-to-day IT support to internal employees across departments."},
    {"title": "Generative AI Engineer (Junior)", "company": "PromptForge AI",
     "required_skills": ["Python", "Prompt Engineering", "LLMs", "RAG", "LangChain"],
     "description": "Build LLM-powered applications and agentic workflows for enterprise clients."},
    {"title": "Database Administrator Trainee", "company": "DataVault Inc",
     "required_skills": ["SQL", "Database Design", "Backup & Recovery", "Linux Basics"],
     "description": "Assist senior DBAs in maintaining and optimizing production databases."},
    {"title": "Software Test Engineer", "company": "QualityFirst Labs",
     "required_skills": ["Manual Testing", "Selenium", "Java", "Bug Tracking"],
     "description": "Ensure software quality through manual and automated testing cycles."},
    {"title": "Data Annotation Specialist", "company": "LabelWorks AI",
     "required_skills": ["Attention to Detail", "Basic Python", "Data Labeling Tools"],
     "description": "Prepare and label datasets used to train machine learning models."},
    {"title": "Blockchain Developer Intern", "company": "ChainForge",
     "required_skills": ["Solidity", "JavaScript", "Web3.js", "Smart Contracts"],
     "description": "Assist in building and testing smart contracts for decentralized applications."},
    {"title": "Growth/Marketing Analyst (Tech)", "company": "ScaleUp Metrics",
     "required_skills": ["SQL", "Excel", "A/B Testing", "Google Analytics"],
     "description": "Analyze marketing funnel data to identify growth opportunities."},
    {"title": "Embedded Systems Intern", "company": "CircuitCore",
     "required_skills": ["C", "Embedded C", "Microcontrollers", "Debugging"],
     "description": "Support firmware development for IoT hardware products."},
    {"title": "Junior Prompt Engineer", "company": "DialogueWorks AI",
     "required_skills": ["Prompt Engineering", "Python", "LLMs", "API Integration"],
     "description": "Design and optimize prompts for production LLM-powered features."},
]

with open("sample_jobs.json", "w") as f:
    _json.dump(SAMPLE_JOBS, f, indent=2)

print(f"Loaded {len(SAMPLE_JOBS)} sample jobs.")


# ── 3. PDF parser ────────────────────────────────────────────────────────────
import pdfplumber


def parse_resume_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


# ── 4. Skill extraction ──────────────────────────────────────────────────────
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


def _coerce_profile(result) -> dict:
    """
    FIX 1 - Guard against the LLM returning a JSON array instead of a dict.
    Previously caused: AttributeError: 'list' object has no attribute 'get'
    """
    if isinstance(result, list):
        # LLM returned a bare list of skills - wrap it into the expected schema
        return {
            "name": "",
            "skills": result,
            "education": [],
            "experience": [],
            "certifications": [],
        }
    if not isinstance(result, dict):
        # Unexpected type - return a safe empty profile
        return {
            "name": "",
            "skills": [],
            "education": [],
            "experience": [],
            "certifications": [],
        }
    return result


def extract_skills(resume_text: str) -> dict:
    raw = call_llm(SKILL_EXTRACTION_SYSTEM_PROMPT, resume_text, json_mode=True)
    try:
        return _coerce_profile(_json.loads(raw))
    except _json.JSONDecodeError:
        # Fallback: ask the model to fix its own output
        fixed = call_llm(
            "Fix this into strictly valid JSON matching the required schema. Return ONLY JSON.",
            raw,
            json_mode=True,
        )
        return _coerce_profile(_json.loads(fixed))


# ── 5. RAG job retrieval ─────────────────────────────────────────────────────
import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client()
# Fresh collection each run (safe to re-run)
try:
    chroma_client.delete_collection("jobs")
except Exception:
    pass
job_collection = chroma_client.create_collection("jobs")

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

print(f"Indexed {len(job_docs)} job postings into ChromaDB.")


def search_jobs(profile: dict, top_k: int = 5) -> list:
    """Embed the candidate's skill profile and retrieve the most similar jobs."""
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
        similarity = max(0.0, 1 - distance / 2)  # rough cosine-ish similarity for display
        matches.append({**meta, "similarity": round(similarity * 100, 1)})
    return matches


# ── 6. Gap analysis ──────────────────────────────────────────────────────────
GAP_ANALYSIS_SYSTEM_PROMPT = """You compare a candidate's skills against a job's required skills.
Respond with ONLY a valid JSON object, no markdown, using this schema:

{
  "match_percentage": 0-100,
  "matching_skills": ["..."],
  "missing_skills": ["..."],
  "learning_suggestions": ["short, concrete suggestion per missing skill"]
}
"""


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


# ── 7. ReAct-style Agent ─────────────────────────────────────────────────────
class ResumeMatchingAgent:
    """A minimal ReAct-style agent: reason about state -> pick next tool -> act -> repeat."""

    def __init__(self, top_k: int = 5, min_skills: int = 2):
        self.top_k = top_k
        self.min_skills = min_skills
        self.trace = []

    def log(self, msg):
        self.trace.append(msg)
        print(msg)

    def run(self, resume_text: str) -> dict:
        self.log("🧠 [Agent] Step 1: Extracting skills from resume...")
        profile = extract_skills(resume_text)

        # profile is now guaranteed to be a dict (FIX 1 applied upstream)
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

        self.log(f"✅ [Agent] Extracted {len(profile['skills'])} skills: {profile['skills']}")
        self.log("🧠 [Agent] Step 2: Retrieving candidate jobs via RAG...")
        matches = search_jobs(profile, top_k=self.top_k)

        if not matches:
            self.log("⚠️ [Agent] No jobs found. Broadening search is not possible with current data.")
            return {"status": "no_matches", "profile": profile}

        self.log(f"✅ [Agent] Retrieved {len(matches)} candidate jobs.")
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


# ── 8. Report generator ──────────────────────────────────────────────────────
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
        lines.append(
            f"- **Match score:** {r.get('match_percentage', 'N/A')}%"
            f"  (retrieval similarity: {r['similarity']}%)"
        )
        lines.append(f"- **Matching skills:** {', '.join(r.get('matching_skills', [])) or 'None'}")
        lines.append(f"- **Missing skills:** {', '.join(r.get('missing_skills', [])) or 'None'}")
        if r.get("learning_suggestions"):
            lines.append("- **How to close the gap:**")
            for s in r["learning_suggestions"]:
                lines.append(f"  - {s}")
        lines.append("")

    return "\n".join(lines)


# ── 9. Gradio UI ─────────────────────────────────────────────────────────────
import gradio as gr


def run_pipeline_from_pdf(pdf_file):
    if pdf_file is None:
        return "Please upload a resume PDF."

    # FIX 2 - Gradio >= 4.x passes a plain str path; <= 3.x passes a NamedString with .name
    # Previously crashed with: AttributeError: 'str' object has no attribute 'name'
    file_path = pdf_file if isinstance(pdf_file, str) else pdf_file.name

    text = parse_resume_pdf(file_path)

    # FIX 3 - Guard for image-only / scanned PDFs with no extractable text
    if not text.strip():
        return (
            "Could not extract any text from the uploaded PDF. "
            "Please ensure it is not a scanned image-only document."
        )

    output = ResumeMatchingAgent(top_k=5).run(text)
    return generate_report(output)


demo = gr.Interface(
    fn=run_pipeline_from_pdf,
    inputs=gr.File(label="Upload Resume (PDF)", file_types=[".pdf"]),
    outputs=gr.Markdown(label="Recommendation Report"),
    title="AI Resume Analyzer & Job Matching Agent",
    description="Agentic AI: LLM skill extraction + RAG job retrieval + gap analysis (Groq-powered).",
)

demo.launch(debug=False, share=True)
