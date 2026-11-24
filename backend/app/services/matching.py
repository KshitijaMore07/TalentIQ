import re
from ..models import jl

WEIGHTS = dict(required=0.40, experience=0.20, education=0.10, preferred=0.10, semantic=0.20)
LEVELS = [(4, ("phd", "ph.d", "doctorate")), (3, ("master", "m.sc", "msc", "m.tech", "mtech", "mca", "mba", "m.e")),
          (2, ("bachelor", "b.sc", "bsc", "b.tech", "btech", "b.e", "bca", "bba", "b.com", "graduate")), (1, ("diploma",))]


def _n(s):
    return re.sub(r"[^a-z0-9+#]", "", s.lower())


def _level(text):
    t = " " + (text or "").lower() + " "
    return next((lv for lv, keys in LEVELS if any(k in t for k in keys)), 0)


def _overlap(wanted, have):
    hs = {_n(h) for h in have}
    out = []
    for w in wanted:
        n = _n(w)
        if n in hs or (len(n) > 3 and any(len(h) > 3 and (n in h or h in n) for h in hs)):
            out.append(w)
    return out


def job_text(j):
    return f"{j.title}. {j.description or ''}. Required: {', '.join(jl(j.required_skills))}. Preferred: {', '.join(jl(j.preferred_skills))}"


def score_candidate(c, job, sim):
    req, pref = jl(job.required_skills), jl(job.preferred_skills)
    have = c.skill_list()
    m_req, m_pref = _overlap(req, have), _overlap(pref, have)
    s_req = 100 * len(m_req) / len(req) if req else 100
    s_pref = 100 * len(m_pref) / len(pref) if pref else 100
    yrs, lo = c.experience_years or 0, job.min_experience or 0
    s_exp = 100 if yrs >= lo else (100 * yrs / lo if lo else 100)
    need = _level(job.education)
    got = max([_level(f"{e.get('degree','')}") for e in jl(c.education)] or [0])
    s_edu = 100 if not need or got >= need else (50 if got else 0)
    s_sem = max(0, min(1, (sim - 0.10) / 0.55)) * 100  # raw cosine ~0.10 (unrelated) .. 0.65 (strong)
    comp = dict(required=s_req, experience=s_exp, education=s_edu, preferred=s_pref, semantic=s_sem)
    final = round(sum(comp[k] * w for k, w in WEIGHTS.items()), 1)
    missing = [s for s in req if s not in m_req]
    why = [f"Matches {len(m_req)} of {len(req)} required skills" + (f"; missing {', '.join(missing)}." if missing else ".")]
    why.append(f"{yrs:g} years of experience against {lo:g}+ required (max {job.max_experience or 0:g}).")
    if need:
        why.append("Education meets the requirement." if s_edu == 100 else "Education is below or unclear against the requirement.")
    why.append(f"Semantic similarity to the job description is {round(s_sem)}%.")
    return dict(candidate_id=c.id, name=c.name, email=c.email, score=final, skills=have, experience_years=yrs,
                matched_skills=m_req, missing_skills=missing, matched_preferred=m_pref,
                breakdown={k: round(v) for k, v in comp.items()}, explanation=" ".join(why),
                recommendation="Strong match" if final >= 75 else "Possible match" if final >= 50 else "Weak match")
