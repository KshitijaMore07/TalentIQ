# Architecture
React (Vite) -> Flask REST API (JWT, role-based) -> MySQL (SQLAlchemy) + AI services.
AI services: PyMuPDF / python-docx text extraction -> Google Gemini structured parsing (validated against resume text) -> Sentence Transformers embeddings -> ChromaDB (cosine) for semantic retrieval.
Roles: candidate, admin (recruiter), interviewer. Notifications are stored in-app and emailed when SMTP is configured.
Fallbacks: without GEMINI_API_KEY a rule-based parser runs; without Sentence Transformers a hashing embedding keeps search working (lower quality).
