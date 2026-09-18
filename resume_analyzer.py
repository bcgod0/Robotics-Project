"""
AI Resume Analyzer & Job Matching Agent (Direct 1-on-1 Matching)
================================================================
Supports:
  1. Resume input via PDF file upload or direct text paste.
  2. Target Job Description input via:
     - 📋 Pasted Job Description text (LinkedIn, Indeed, etc.)
     - 🖼️ Job Description Screenshot / Image (PNG, JPG, etc.) with EasyOCR
  3. Deep 1-on-1 gap analysis with match scores, ATS keywords, resume tailoring tips,
     and targeted learning roadmaps.

Run:
    python resume_analyzer.py
"""

# ── 1. Imports & Environment Setup ───────────────────────────────────────────
import os
import sys
import json as _json
from typing import Optional, List, Dict

# Ensure UTF-8 output on Windows consoles to prevent cp1252 UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Always load from .env first so new keys override stale terminal environment variables
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

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = input("Enter your Groq API key: ").strip()

_key = os.environ["GROQ_API_KEY"]
print(f"Loaded Groq API key: {_key[:8]}...{_key[-4:] if len(_key) > 12 else ''}")

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Model choice — openai/gpt-oss-120b is available and tested on this Groq account.
MODEL_NAME = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

# Validate the API key immediately on startup so the user gets instant feedback
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
        print("Steps to resolve:")
        print("  1. Go to https://console.groq.com/keys")
        print("  2. Create a new API key (starts with 'gsk_')")
        print("  3. Paste it into your .env file:")
        print("       GROQ_API_KEY=gsk_your_new_key_here")
        print("  4. Save .env and re-run python resume_analyzer.py")
        print("=" * 65 + "\n")
        sys.exit(1)
    else:
        print(f"⚠️ [Groq Warning]: {_auth_err}")


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


# ── 2. PDF Resume Parser ─────────────────────────────────────────────────────
import pdfplumber


def parse_resume_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


# ── 3. OCR Engine (Screenshot / Image Input) ──────────────────────────────────
_ocr_reader = None


def get_ocr_reader():
    """Lazy-load the EasyOCR reader so startup remains instantaneous."""
    global _ocr_reader
    if _ocr_reader is None:
        print("🔍 Initializing OCR reader for image text extraction...")
        import easyocr
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _ocr_reader


def extract_text_from_image(image_input) -> str:
    """Extract raw text from a screenshot or image file using EasyOCR."""
    if image_input is None:
        return ""
    try:
        reader = get_ocr_reader()
        # image_input can be a string filepath or a numpy array/PIL image from Gradio
        results = reader.readtext(image_input, detail=0)
        extracted = "\n".join(results).strip()
        print(f"✅ OCR extracted {len(extracted)} characters from image.")
        return extracted
    except Exception as e:
        print(f"⚠️ OCR extraction failed: {e}")
        return ""


# ── 4. Skill Extraction & Job Parsing Prompts ────────────────────────────────
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
    """Ensure the LLM response is a dict matching the expected resume schema."""
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


def extract_skills(resume_text: str) -> dict:
    """Extract a candidate's structured profile from resume text."""
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


JOB_PARSING_SYSTEM_PROMPT = """You are an expert recruitment analyst.
Extract structured job information from the provided job description text (which may be from copied text or OCR output).
Always respond with ONLY a valid JSON object - no markdown, no commentary, no code fences.
Use this exact schema:

{
  "title": "Job Title",
  "company": "Company Name (or 'Target Company' if omitted)",
  "required_skills": ["Skill1", "Skill2", ...],
  "description": "Clear, concise summary of key responsibilities and qualifications"
}

Rules:
- Extract all explicitly mentioned and strongly implied technical and domain skills into 'required_skills'.
- Normalize skill names (e.g. 'React.js' -> 'React', 'JS' -> 'JavaScript', 'AWS services' -> 'AWS').
- If the title or company is missing, infer a realistic title or use 'Target Role' and 'Target Company'.
"""


def parse_job_description(raw_text: str) -> dict:
    """Extract structured job details (title, company, required skills) from raw text or OCR."""
    if not raw_text or not raw_text.strip():
        return None
    raw = call_llm(JOB_PARSING_SYSTEM_PROMPT, raw_text, json_mode=True)
    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError:
        fixed = call_llm(
            "Fix this into strictly valid JSON matching the schema. Return ONLY JSON.",
            raw,
            json_mode=True,
        )
        data = _json.loads(fixed)

    if not isinstance(data, dict):
        data = {
            "title": "Target Role",
            "company": "Target Company",
            "required_skills": [],
            "description": raw_text[:300],
        }

    data.setdefault("title", "Target Role")
    data.setdefault("company", "Target Company")
    data.setdefault("required_skills", [])
    data.setdefault("description", raw_text[:300])
    return data


# ── 5. Target Job Gap Analysis ───────────────────────────────────────────────
TARGET_JOB_GAP_PROMPT = """You are an elite technical recruiter, resume writer, and executive career coach.
Perform an in-depth gap analysis comparing a candidate's resume against a specific target job posting, and generate tailored resume bullet points.
Always respond with ONLY a valid JSON object - no markdown, no code fences, using this exact schema:

{
  "match_percentage": 0-100,
  "matching_skills": ["skills the candidate clearly possesses that match the job"],
  "missing_skills": ["required skills from the job description that the candidate lacks"],
  "ats_keywords_to_add": ["crucial keywords, acronyms, or phrases from the job description to add to the resume"],
  "tailored_bullet_points": [
    {
      "bullet": "Rewritten resume bullet point using STAR framework (Situation, Task, Action, Result) with strong action verbs (e.g. Engineered, Spearheaded, Architected, Optimized), quantifying impact or metrics, and naturally infusing missing ATS keywords and technologies required for this specific role.",
      "keywords_infused": ["Keyword1", "Keyword2"],
      "action_verb": "Architected"
    }
  ],
  "resume_tailoring_tips": [
    "Specific advice on how the candidate can rewrite existing project/experience bullet points to highlight relevancy for this specific job"
  ],
  "learning_suggestions": [
    "Concrete, high-impact recommendations or courses to quickly learn missing skills"
  ],
  "verdict_summary": "A 2-3 sentence honest, encouraging assessment of how competitive the candidate is for this role."
}

Rules for tailored_bullet_points:
- Provide 3 to 4 strong, impactful STAR-format bullet points tailored specifically for this target job.
- Base them on the candidate's actual background/projects, but elevate the phrasing and integrate the target role's key technical requirements.
- Highlight metrics or quantifiable impact where plausible.
"""


def analyze_target_job(profile: dict, job: dict) -> dict:
    """Deep 1-on-1 evaluation of candidate against a target job."""
    user_prompt = f"""Candidate Name: {profile.get('name', 'Candidate')}
Candidate Skills: {profile.get('skills', [])}
Candidate Experience: {profile.get('experience', [])}
Candidate Education: {profile.get('education', [])}
Candidate Certifications: {profile.get('certifications', [])}

Target Job Title: {job.get('title', 'Target Role')}
Target Company: {job.get('company', 'Target Company')}
Required Skills: {job.get('required_skills', [])}
Job Description: {job.get('description', '')}"""

    raw = call_llm(TARGET_JOB_GAP_PROMPT, user_prompt, json_mode=True)
    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError:
        fixed = call_llm(
            "Fix this into strictly valid JSON matching the schema. Return ONLY JSON.",
            raw,
            json_mode=True,
        )
        data = _json.loads(fixed)

    if not isinstance(data, dict):
        data = {}

    data.setdefault("match_percentage", 50)
    data.setdefault("matching_skills", [])
    data.setdefault("missing_skills", [])
    data.setdefault("ats_keywords_to_add", [])
    data.setdefault("tailored_bullet_points", [])
    data.setdefault("resume_tailoring_tips", [])
    data.setdefault("learning_suggestions", [])
    data.setdefault("verdict_summary", "Evaluation complete.")
    return data


# ── 6. ReAct-style Agent ─────────────────────────────────────────────────────
class ResumeMatchingAgent:
    """ReAct-style agent that evaluates candidate fit against one or more target job descriptions."""

    def __init__(self, min_skills: int = 2):
        self.min_skills = min_skills
        self.trace = []

    def log(self, msg):
        self.trace.append(msg)
        print(msg)

    def run(
        self,
        resume_text: str,
        custom_job: Optional[dict] = None,
        custom_jobs: Optional[List[dict]] = None,
    ) -> dict:
        # 1. Normalize target jobs list
        jobs_to_process = []
        if custom_jobs and isinstance(custom_jobs, list) and len(custom_jobs) > 0:
            jobs_to_process = [j for j in custom_jobs if j and isinstance(j, dict)]
        elif custom_job and isinstance(custom_job, dict):
            jobs_to_process = [custom_job]

        if not jobs_to_process:
            return {
                "status": "error",
                "message": "Please provide at least one job description (paste text or upload a screenshot) to match against.",
            }

        # 2. Extract Candidate Profile (Single Pass)
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

        self.log(f"✅ [Agent] Extracted {len(profile['skills'])} skills: {profile['skills']}")

        # 3. Analyze job description(s) against the resume profile (in parallel if multiple)
        total = len(jobs_to_process)

        def _evaluate_job(indexed_job):
            idx, job = indexed_job
            title = job.get("title", "Target Role")
            company = job.get("company", "Target Company")
            self.log(f"🎯 [Agent] Analyzing job {idx}/{total}: '{title}' @ '{company}'...")
            target_analysis = analyze_target_job(profile, job)
            score = target_analysis.get("match_percentage", 0)
            return {
                "job": job,
                "analysis": target_analysis,
                "match_percentage": score,
                "matching_skills_count": len(target_analysis.get("matching_skills", [])),
                "missing_skills_count": len(target_analysis.get("missing_skills", [])),
            }

        if total == 1:
            ranked_jobs = [_evaluate_job((1, jobs_to_process[0]))]
        else:
            self.log(f"⚡ [Agent] Launching parallel evaluation for {total} roles simultaneously via ThreadPoolExecutor...")
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(total, 6)) as executor:
                ranked_jobs = list(executor.map(_evaluate_job, enumerate(jobs_to_process, 1)))

        # 4. Sort ranked jobs descending by match_percentage
        ranked_jobs.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
        best_match = ranked_jobs[0]
        self.log(f"✅ [Agent] Parallel analysis complete for {total} job(s). Top match: '{best_match['job'].get('title')}' ({best_match['match_percentage']}%).")

        return {
            "status": "ok",
            "mode": "multi_job" if len(ranked_jobs) > 1 else "target_job",
            "profile": profile,
            "ranked_jobs": ranked_jobs,
            "best_match": best_match,
            "total_jobs": len(ranked_jobs),
            # Backward-compatibility fields:
            "job": best_match["job"],
            "analysis": best_match["analysis"],
        }


# ── 7. Report Generator ──────────────────────────────────────────────────────
def generate_report(agent_output: dict) -> str:
    """Generate Markdown report for Target Job or Multi-Job Mode."""
    if agent_output.get("status") != "ok":
        return f"### ⚠️ {agent_output.get('message', 'Could not generate a report.')}"

    profile = agent_output["profile"]
    candidate_name = profile.get("name") or "Candidate"
    mode = agent_output.get("mode", "target_job")

    lines = []
    if mode == "multi_job":
        ranked_jobs = agent_output.get("ranked_jobs", [])
        lines.append(f"# 🏆 Multi-Job Match Leaderboard")
        lines.append(f"**Candidate:** {candidate_name} | **Total Evaluated Roles:** {len(ranked_jobs)}\n")
        lines.append("| Rank | Role / Company | Match % | Matching Skills | Missing Skills |")
        lines.append("| :--- | :--- | :---: | :--- | :--- |")
        for rank, item in enumerate(ranked_jobs, 1):
            j = item["job"]
            a = item["analysis"]
            score = item["match_percentage"]
            matching_preview = ", ".join(a.get("matching_skills", [])[:3]) or "None"
            missing_preview = ", ".join(a.get("missing_skills", [])[:3]) or "None"
            badge = "🥇 " if rank == 1 else ("🥈 " if rank == 2 else ("🥉 " if rank == 3 else f"#{rank} "))
            lines.append(f"| {badge} | **{j.get('title')}**<br>*{j.get('company')}* | **{score}%** | {matching_preview} | {missing_preview} |")
        lines.append("\n---\n")

    job = agent_output.get("job", {})
    analysis = agent_output.get("analysis", {})
    match_score = analysis.get("match_percentage", "N/A")

    lines.extend([
        f"# 🎯 Target Job Match Report: {job.get('title')} @ {job.get('company')}",
        f"**Candidate:** {candidate_name} | **Role:** {job.get('title')}\n",
        f"### 📊 Overall Match Score: **{match_score}%**",
        f"> {analysis.get('verdict_summary', '')}\n",
        "---",
        "## 🔍 Skills Breakdown",
        f"- **✅ Matching Skills Found:** {', '.join(analysis.get('matching_skills', [])) or 'None detected'}",
        f"- **❌ Missing Required Skills:** {', '.join(analysis.get('missing_skills', [])) or 'None! You meet all listed skill requirements'}",
        f"- **🏷️ Key ATS Keywords to Include:** {', '.join(analysis.get('ats_keywords_to_add', [])) or 'None'}\n",
        "---",
        "## 📝 Actionable Resume Tailoring Suggestions",
    ])

    bullet_tips = analysis.get("resume_tailoring_tips", [])
    if bullet_tips:
        for tip in bullet_tips:
            lines.append(f"- 💡 {tip}")
    else:
        lines.append("- Your resume already closely aligns with this job posting.")

    tailored_bullets = analysis.get("tailored_bullet_points", [])
    if tailored_bullets:
        lines.append("\n---")
        lines.append("## ✍️ AI-Tailored Resume Bullet Points (STAR Framework)")
        for b in tailored_bullets:
            bullet_text = b.get("bullet") if isinstance(b, dict) else str(b)
            keywords = b.get("keywords_infused", []) if isinstance(b, dict) else []
            kw_tag = f" *(ATS Keywords: {', '.join(keywords)})*" if keywords else ""
            lines.append(f"- ✦ **{bullet_text}**{kw_tag}")

    lines.append("\n---")
    lines.append("## 📚 Skill Gap Roadmap & Learning Resources")
    learn_tips = analysis.get("learning_suggestions", [])
    if learn_tips:
        for tip in learn_tips:
            lines.append(f"- 🚀 {tip}")
    else:
        lines.append("- No critical skill gaps identified!")

    return "\n".join(lines)


# ── 8. Unified Pipeline Callback ────────────────────────────────────────────
def run_pipeline(resume_file, resume_pasted_text, job_pasted_text, job_image_file):
    """
    Main pipeline entrypoint handling:
      - Resume from PDF or pasted text
      - Target Job from pasted text or image screenshot (EasyOCR)
    """
    # 1. Resolve Resume Text
    resume_text = ""
    if resume_file is not None:
        file_path = resume_file if isinstance(resume_file, str) else resume_file.name
        resume_text = parse_resume_pdf(file_path)

    if not resume_text.strip() and resume_pasted_text and resume_pasted_text.strip():
        resume_text = resume_pasted_text.strip()

    if not resume_text.strip():
        return (
            "### ⚠️ Please provide a resume!\n\n"
            "Upload a resume PDF or paste your resume text in the box."
        ), {}

    # 2. Resolve Target Job Description
    raw_job_text = ""

    # Check if a screenshot/image of the job description was uploaded
    if job_image_file is not None:
        img_path = job_image_file if isinstance(job_image_file, str) else getattr(job_image_file, "name", None)
        raw_job_text = extract_text_from_image(img_path or job_image_file)

    # Check if job description text was pasted (pasted text overrides or supplements image)
    if job_pasted_text and job_pasted_text.strip():
        raw_job_text = job_pasted_text.strip()

    if not raw_job_text.strip():
        return (
            "### ⚠️ Please provide a target job description!\n\n"
            "Paste the job description text or upload a screenshot to match against."
        ), {}

    print("📋 Parsing custom Job Description...")
    custom_job = parse_job_description(raw_job_text)
    print(f"🎯 Target Job parsed: {custom_job.get('title')} @ {custom_job.get('company')}")

    # 3. Run Agent
    try:
        agent = ResumeMatchingAgent()
        output = agent.run(resume_text, custom_job=custom_job)
        report_md = generate_report(output)
        return report_md, output
    except Exception as e:
        err_str = str(e)
        if "invalid_api_key" in err_str.lower() or "401" in err_str:
            return (
                "### ❌ Groq Authentication Error (Invalid API Key)\n\n"
                "Groq rejected your API key (`401 Invalid API Key`).\n\n"
                "**How to fix:**\n"
                "1. Go to [Groq Console API Keys](https://console.groq.com/keys)\n"
                "2. Create a new API key (starts with 'gsk_')\n"
                "3. Open `.env` in this project and paste it:\n"
                "   ```env\n"
                "   GROQ_API_KEY=gsk_your_new_key_here\n"
                "   ```\n"
                "4. Restart `python resume_analyzer.py`"
            ), {}
        return f"### ⚠️ An error occurred during analysis:\n\n`{err_str}`", {}


# ── 9. Modern Gradio Interface ──────────────────────────────────────────────
import gradio as gr

custom_css = """
.main-title { text-align: center; margin-bottom: 8px; font-weight: 700; }
.sub-title { text-align: center; color: #888; margin-bottom: 24px; }
"""

with gr.Blocks(title="AI Resume Analyzer & Job Matching Agent") as demo:
    gr.Markdown("# 🚀 AI Resume Analyzer & Job Matching Agent", elem_classes=["main-title"])
    gr.Markdown(
        "Upload your resume and match it against **any target Job Description** (pasted text or screenshot).",
        elem_classes=["sub-title"],
    )

    with gr.Row():
        # ── Left Column: Inputs ──
        with gr.Column(scale=1):
            gr.Markdown("### 📄 1. Your Resume")
            resume_file_input = gr.File(
                label="Upload Resume (PDF)",
                file_types=[".pdf"],
            )
            with gr.Accordion("Or paste resume text directly", open=False):
                resume_text_input = gr.Textbox(
                    label="Pasted Resume Text",
                    placeholder="Paste your raw resume text here if you don't have a PDF...",
                    lines=6,
                )

            gr.Markdown("### 🎯 2. Target Job Description")
            with gr.Tabs():
                with gr.Tab("📋 Paste Job Description"):
                    job_text_input = gr.Textbox(
                        label="Job Posting Text",
                        placeholder="Paste the job title, requirements, or full posting from LinkedIn, Indeed, etc...",
                        lines=7,
                    )
                with gr.Tab("🖼️ Upload Job Screenshot"):
                    job_image_input = gr.Image(
                        label="Screenshot of Job Posting (PNG, JPG)",
                        type="filepath",
                    )
                    gr.Markdown("💡 *Takes a screenshot from LinkedIn or job boards. EasyOCR extracts the requirements automatically.*")

            with gr.Row():
                submit_btn = gr.Button("🚀 Analyze & Match", variant="primary", size="lg")
                clear_btn = gr.Button("🔄 Clear All", size="lg")

        # ── Right Column: Outputs ──
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Recommendation & Gap Analysis Report")
            report_output = gr.Markdown(
                value="*Your detailed match report and recommendations will appear here after clicking **Analyze & Match**.*"
            )
            with gr.Accordion("🔍 View Extracted Structured Data (JSON)", open=False):
                json_output = gr.JSON(label="Agent Raw Output")

    # Wire event handlers
    submit_btn.click(
        fn=run_pipeline,
        inputs=[resume_file_input, resume_text_input, job_text_input, job_image_input],
        outputs=[report_output, json_output],
    )

    def clear_all():
        return None, "", "", None, "*Cleared. Ready for new analysis.*", {}

    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[resume_file_input, resume_text_input, job_text_input, job_image_input, report_output, json_output],
    )


# ── 10. FastAPI Application & Stitch Dashboard Server ────────────────────────
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict
import uvicorn
import tempfile
import os
import shutil
import socket
import webbrowser

app = FastAPI(title="AI Resume Analyzer & Job Matching Agent")

# Mount static files for Stitch assets (images, logos, styles)
stitch_assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stitch_assets")
if os.path.isdir(stitch_assets_dir):
    app.mount("/stitch_assets", StaticFiles(directory=stitch_assets_dir), name="stitch_assets")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the AI Resume Match Agent Dashboard."""
    dashboard_path = os.path.join(stitch_assets_dir, "dashboard_dualtone.html")
    if not os.path.exists(dashboard_path):
        return HTMLResponse("<h1>Error: dashboard template not found.</h1>", status_code=404)
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.post("/api/analyze")
async def api_analyze(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: str = Form(""),
    job_text: str = Form(""),
    job_image: Optional[UploadFile] = File(None),
    jobs_payload: Optional[str] = Form(None),
    job_images: Optional[List[UploadFile]] = File(None),
):
    """
    Unified API endpoint powering the Stitch UI:
      - Accepts PDF or raw text resumes
      - Accepts single target job (text or screenshot)
      - Accepts multiple staged target jobs (mix of text and screenshots)
    """
    try:
        # 1. Extract Resume Text
        extracted_resume = ""
        if resume_file is not None and getattr(resume_file, "filename", None):
            suffix = os.path.splitext(resume_file.filename)[1] or ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(resume_file.file, tmp)
                tmp_path = tmp.name
            try:
                extracted_resume = parse_resume_pdf(tmp_path)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        if not extracted_resume.strip() and resume_text and resume_text.strip():
            extracted_resume = resume_text.strip()

        if not extracted_resume.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Please upload a resume PDF or paste resume text before analyzing."
                }
            )

        # 2. Extract Job Descriptions (Multi-Job or Single-Job)
        all_jobs = []

        # Check if staged jobs payload was provided
        if jobs_payload and jobs_payload.strip():
            try:
                staged_items = _json.loads(jobs_payload)
                if isinstance(staged_items, list):
                    # Cache uploaded images if job_images provided
                    saved_image_paths = []
                    if job_images:
                        for img_upload in job_images:
                            if getattr(img_upload, "filename", None):
                                suffix = os.path.splitext(img_upload.filename)[1] or ".png"
                                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                                    shutil.copyfileobj(img_upload.file, tmp_img)
                                    saved_image_paths.append(tmp_img.name)

                    try:
                        for item in staged_items:
                            item_type = item.get("type", "text")
                            raw_content = ""
                            if item_type == "text":
                                raw_content = item.get("text", "").strip()
                            elif item_type == "image":
                                img_idx = item.get("image_index", 0)
                                if 0 <= img_idx < len(saved_image_paths):
                                    raw_content = extract_text_from_image(saved_image_paths[img_idx])

                            if raw_content:
                                parsed = parse_job_description(raw_content)
                                if parsed:
                                    all_jobs.append(parsed)
                    finally:
                        for p in saved_image_paths:
                            try:
                                os.remove(p)
                            except Exception:
                                pass
            except Exception as pe:
                print(f"Notice: failed to parse jobs_payload: {pe}")

        # Fallback to single job inputs if no staged jobs
        if not all_jobs:
            raw_job_text = ""
            if job_image is not None and getattr(job_image, "filename", None):
                suffix = os.path.splitext(job_image.filename)[1] or ".png"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    shutil.copyfileobj(job_image.file, tmp)
                    tmp_img_path = tmp.name
                try:
                    raw_job_text = extract_text_from_image(tmp_img_path)
                finally:
                    try:
                        os.remove(tmp_img_path)
                    except Exception:
                        pass

            if job_text and job_text.strip():
                raw_job_text = job_text.strip()

            if raw_job_text.strip():
                single_parsed = parse_job_description(raw_job_text)
                if single_parsed:
                    all_jobs.append(single_parsed)

        if not all_jobs:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Please add or paste at least one job description or screenshot to match against."
                }
            )

        # 3. Run Agent Pipeline (single profile extraction, multi-job evaluation)
        agent = ResumeMatchingAgent()
        output = agent.run(extracted_resume, custom_jobs=all_jobs)

        if output.get("status") != "ok":
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": output.get("message", "Could not complete analysis. Check resume details.")
                }
            )

        return JSONResponse(content=output)

    except Exception as e:
        err_msg = str(e)
        if "invalid_api_key" in err_msg.lower() or "401" in err_msg:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Groq rejected your API key (401 Invalid API Key). Please update GROQ_API_KEY in .env."
                }
            )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Server error: {err_msg}"
            }
        )


# Mount Gradio interface under /gradio for backward compatibility
try:
    gr.mount_gradio_app(app, demo, path="/gradio")
except Exception as _mount_err:
    print(f"Notice: Gradio secondary mount warning: {_mount_err}")


def find_free_port(start_port: int = 7860, max_tries: int = 20) -> int:
    """Find the first available TCP port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


if __name__ == "__main__":
    # Check if a custom port was requested, otherwise find first free port starting at 7860
    default_port = int(os.environ.get("PORT", "7860"))
    port = find_free_port(default_port)

    print("\n" + "=" * 70)
    print("  🚀 AI RESUME ANALYZER & JOB MATCHING AGENT")
    print("  🎯 Direct 1-on-1 Matching: Paste Job Description or Screenshot")
    print("  ⚡ Powered by Groq LPU (openai/gpt-oss-120b) + EasyOCR")
    print("=" * 70)
    print(f"  👉 Web Dashboard:             http://127.0.0.1:{port}")
    print(f"  👉 Fallback Gradio Interface: http://127.0.0.1:{port}/gradio")
    print("=" * 70 + "\n")

    # Try opening browser automatically for seamless user experience
    try:
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
