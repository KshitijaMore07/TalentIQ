import hashlib, math, re
from datetime import datetime
from config import Config
from ..extensions import db
from ..models import CandidateEmbedding

_st = {}


def _model():
    if "m" not in _st:
        try:
            from sentence_transformers import SentenceTransformer
            _st["m"] = SentenceTransformer(Config.EMBEDDING_MODEL)
        except Exception as e:
            print("[embeddings] Sentence Transformers unavailable, using hashing fallback:", e)
            _st["m"] = None
    return _st["m"]


def _hash_vec(t, dim=384):
    v = [0.0] * dim
    for w in re.findall(r"[a-z0-9+#.]+", t.lower()):
        v[int(hashlib.md5(w.encode()).hexdigest(), 16) % dim] += 1
    n = math.sqrt(sum(x * x for x in v)) or 1
    return [x / n for x in v]


def embed(texts):
    m = _model()
    return m.encode(texts, normalize_embeddings=True).tolist() if m else [_hash_vec(t) for t in texts]


def _col():
    if "c" not in _st:
        import chromadb
        _st["c"] = chromadb.PersistentClient(path=Config.CHROMA_DIR).get_or_create_collection(
            "candidates", metadata={"hnsw:space": "cosine"})
    return _st["c"]


def candidate_text(c):
    from ..models import jl
    parts = [c.summary or "", "Skills: " + ", ".join(c.skill_list())]
    parts += [f"{e.get('title','')} {e.get('company','')} {e.get('description','')}" for e in jl(c.experience)]
    parts += [f"{p.get('name','')} {p.get('description','')}" for p in jl(c.projects)]
    parts += [f"{e.get('degree','')} {e.get('institution','')}" for e in jl(c.education)]
    return " . ".join(p for p in parts if p.strip())


def index_candidate(c):
    text = candidate_text(c) or (c.name or "candidate")
    _col().upsert(ids=[str(c.id)], embeddings=[embed([text])[0]], documents=[text[:2000]],
                  metadatas=[{"candidate_id": int(c.id), "name": c.name or ""}])
    row = CandidateEmbedding.query.filter_by(candidate_id=c.id).first() or CandidateEmbedding(candidate_id=c.id)
    row.vector_id, row.model, row.updated_at = str(c.id), Config.EMBEDDING_MODEL if _model() else "hashing-fallback", datetime.utcnow()
    db.session.add(row); db.session.commit()


def similarities(text, n=None):
    """Return {candidate_id: cosine similarity 0..1} from ChromaDB."""
    col = _col()
    cnt = col.count()
    if not cnt:
        return {}
    r = col.query(query_embeddings=[embed([text])[0]], n_results=min(n or cnt, cnt))
    return {int(i): max(0.0, 1 - d) for i, d in zip(r["ids"][0], r["distances"][0])}


def reset_index():
    import chromadb
    chromadb.PersistentClient(path=Config.CHROMA_DIR).delete_collection("candidates")
    _st.pop("c", None)
