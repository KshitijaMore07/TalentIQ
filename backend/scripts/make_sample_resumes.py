"""Generate 5 fictional sample resumes (DOCX) into ../sample_data/resumes for testing bulk upload."""
import os
import docx

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "resumes")
os.makedirs(OUT, exist_ok=True)
PEOPLE = [
    ("Rahul Sharma", "rahul.sharma@example.com", "9876543210", "B.Sc Computer Science, ABC College", 3,
     "Python, Flask, SQL, MySQL, Git, Docker, REST API", "Backend Developer at Nimbus Soft (3 years): built Flask REST APIs and MySQL schemas.", "Student Management System - Flask web application"),
    ("Priya Nair", "priya.nair@example.com", "9123456780", "M.Tech Artificial Intelligence, XYZ Institute", 4,
     "Python, Machine Learning, NLP, PyTorch, LLM, SQL, Pandas", "ML Engineer at Lexi Labs (4 years): built NLP classifiers and semantic search using embeddings.", "Resume ranker using Sentence Transformers"),
    ("Amit Deshmukh", "amit.deshmukh@example.com", "9988776655", "B.Tech Information Technology, PQR University", 2,
     "Java, Spring Boot, MySQL, AWS, Git", "Software Engineer at Orbit Systems (2 years): Java microservices.", "Online voting system in Spring Boot"),
    ("Sneha Kulkarni", "sneha.kulkarni@example.com", "9012345678", "BCA, Pune College", 1,
     "HTML, CSS, JavaScript, React, Git", "Frontend Intern at Pixel Works (1 year): React dashboards.", "Portfolio website and weather app"),
    ("Karan Mehta", "karan.mehta@example.com", "9345612780", "MCA, Mumbai Institute", 5,
     "Python, Django, SQL, PostgreSQL, Docker, AWS, Machine Learning", "Senior Developer at DataBridge (5 years): data platforms and ML pipelines.", "Demand forecasting service"),
]
for n, e, p, edu, yrs, sk, exp, prj in PEOPLE:
    d = docx.Document()
    d.add_heading(n, 0); d.add_paragraph(f"Email: {e}  |  Phone: {p}")
    d.add_heading("Summary", 1); d.add_paragraph(f"Software professional with {yrs} years of experience.")
    d.add_heading("Education", 1); d.add_paragraph(edu)
    d.add_heading("Skills", 1); d.add_paragraph(sk)
    d.add_heading("Experience", 1); d.add_paragraph(exp)
    d.add_heading("Projects", 1); d.add_paragraph(prj)
    d.save(os.path.join(OUT, n.split()[0].lower() + "_resume.docx"))
print("Created", len(PEOPLE), "sample resumes in", os.path.abspath(OUT))
