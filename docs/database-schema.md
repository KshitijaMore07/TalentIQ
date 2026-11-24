# Database schema
users, candidates, resumes, jobs, applications, candidate_skills, candidate_embeddings, shortlists, internal_notes,
interviews, interview_feedback, notifications. Interviewers are users with role `interviewer`.
Relations: users 1-1 candidates; candidates 1-N resumes, skills, applications; jobs 1-N applications; applications link to shortlists
and interviews; interviews 1-1 interview_feedback. Tables are created automatically on first start (db.create_all).
