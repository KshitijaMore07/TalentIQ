import json, re
from config import Config

SKILL_VOCAB = ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "sql", "mysql", "postgresql",
    "mongodb", "flask", "django", "fastapi", "react", "node.js", "html", "css", "docker", "kubernetes", "aws", "azure", "git",
    "linux", "machine learning", "deep learning", "nlp", "llm", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    "rest api", "data analysis", "power bi", "tableau", "excel", "spring boot", "redis", "chromadb", "sentence transformers"]

PROMPT = """You extract structured data from resume text. Return ONLY valid JSON with these keys:
name, email, phone, summary, total_experience_years (number),
education [{"degree","institution"}], skills [string], experience [{"title","company","duration","description"}],
projects [{"name","description"}].
Use only information explicitly present in the resume. Use null or [] when something is missing. Never invent skills or qualifications.

RESUME:
"""


def extract_text(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        import fitz
        with fitz.open(path) as doc:
            return "\n".join(p.get_text() for p in doc)
    if ext == "docx":
        import docx
        d = docx.Document(path)
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for r in t.rows:
                parts.append(" | ".join(c.text for c in r.cells))
        return "\n".join(parts)
    raise ValueError("Unsupported file type")


def _s(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def _items(v, keys):
    return [{k: (_s(i.get(k)) or "") for k in keys} for i in (v if isinstance(v, list) else []) if isinstance(i, dict)]


def normalize(d, text):
    """Validate model output: resume text is the source of truth."""
    low = text.lower()
    email = _s(d.get("email"))
    if email and email.lower() not in low:
        email = None
    skills, seen = [], set()
    for s in d.get("skills") or []:
        s = _s(s)
        if s and s.lower() in low and s.lower() not in seen:
            seen.add(s.lower()); skills.append(s)
    try:
        yrs = max(0.0, min(float(d.get("total_experience_years") or 0), 50))
    except (TypeError, ValueError):
        yrs = 0.0
    return dict(name=_s(d.get("name")), email=email.lower() if email else None, phone=_s(d.get("phone")),
                summary=_s(d.get("summary")), experience_years=yrs, skills=skills,
                education=_items(d.get("education"), ("degree", "institution")),
                experience=_items(d.get("experience"), ("title", "company", "duration", "description")),
                projects=_items(d.get("projects"), ("name", "description")))


def _gemini(text):
    if not Config.GEMINI_API_KEY:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        r = client.models.generate_content(model=Config.GEMINI_MODEL, contents=PROMPT + text[:12000],
                                           config={"response_mime_type": "application/json", "temperature": 0})
        raw = re.sub(r"^```(?:json)?|```$", "", r.text.strip(), flags=re.M).strip()
        return json.loads(raw)
    except Exception as e:
        print("[parser] Gemini failed, using fallback:", e)
        return None


def _fallback(text):
    low = text.lower()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = next((l for l in lines[:6] if 1 < len(l.split()) <= 4 and not re.search(r"[\d@:]", l)), None)
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"(\+?\d[\d\s\-]{8,14}\d)", text)
    skills = [s for s in SKILL_VOCAB if re.search(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])", low)]
    yrs = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", low)]
    edu = [{"degree": l[:120], "institution": ""} for l in lines
           if re.search(r"\b(b\.?sc|m\.?sc|b\.?tech|m\.?tech|bca|mca|mba|bachelor|master|ph\.?d|diploma)\b", l, re.I)][:3]
    return dict(name=name, email=email.group(0) if email else None, phone=phone.group(0) if phone else None,
                summary=None, total_experience_years=max(yrs) if yrs else 0, skills=[s.title() if len(s) > 3 else s.upper() for s in skills],
                education=edu, experience=[], projects=[])


def parse_resume(text):
    data = _gemini(text) or _fallback(text)
    return normalize(data, text)
