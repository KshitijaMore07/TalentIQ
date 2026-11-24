# Matching methodology
Final = Required skills x0.40 + Experience x0.20 + Education x0.10 + Preferred skills x0.10 + Semantic similarity x0.20 (each 0-100).
The score is computed in code (`services/matching.py`), never taken from an LLM.
Semantic: cosine similarity from ChromaDB rescaled from the 0.10-0.65 range to 0-100.
Experience: 100 if years >= minimum, otherwise proportional. Education: compares degree level (diploma < bachelor < master < PhD).
Each result lists matched/missing skills and a plain-language explanation. Recruiters always make the final decision.
