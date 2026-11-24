# TalentIQ – AI-Powered Recruitment & Interview Management Platform

**Intelligent Recruitment. Smarter Hiring.**

TalentIQ is an AI-powered recruitment and interview management platform designed to simplify and automate the hiring process. It uses Artificial Intelligence, Large Language Models (LLMs), and semantic search to extract candidate information from resumes, identify suitable candidates, rank applicants based on job requirements, and streamline interview management.

The platform connects candidates, recruiters, and interviewers through an integrated recruitment workflow.

---

## 1. Project Overview

Traditional recruitment involves manually reviewing hundreds of resumes, comparing candidate skills, shortlisting applicants, and scheduling interviews. This process is time-consuming and often inefficient.

TalentIQ aims to automate these activities using AI-driven technologies.

The platform provides three major modules:

1. **Candidate Portal** – Allows candidates to register, upload resumes, manage profiles, apply for jobs, and track application status.
2. **Admin Recruitment Portal** – Enables recruiters to manage jobs, process bulk resumes, search candidates, analyze AI-generated matching scores, and shortlist applicants.
3. **Interview Management Portal** – Supports interview scheduling, interviewer assignments, feedback collection, and interview status tracking.

### Key Objectives

- Automate resume parsing using AI.
- Extract structured candidate information from PDF and DOCX files.
- Generate candidate profile embeddings.
- Perform semantic candidate searches.
- Implement hybrid AI-based candidate matching.
- Provide explainable candidate recommendations.
- Simplify candidate shortlisting and interview management.
- Maintain secure, role-based access to application data.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js |
| Build Tool | Vite |
| Backend | Python, Flask |
| Database | MySQL |
| ORM | Flask-SQLAlchemy |
| AI / LLM | Google Gemini API |
| Embedding Model | Sentence Transformers |
| Vector Database | ChromaDB |
| Resume Processing | PyMuPDF, python-docx |
| Authentication | JWT |
| API Communication | Axios |
| API Testing | Postman |
| Version Control | Git and GitHub |

---

## 3. System Architecture

TalentIQ follows a modular full-stack architecture.

### High-Level Architecture

```text
                 TALENTIQ PLATFORM
                         |
              +----------+----------+
              |                     |
        React Frontend         User Roles
              |                     |
       +------+------+--------------+
       |      |      |              |
   Candidate Admin Interviewer
       |      |      |
       +------+------+
              |
         Flask REST API
              |
     +--------+---------+
     |        |         |
 Authentication  Business  AI Services
     |          Logic       |
     |            |         |
     |        MySQL DB      |
     |                      |
     |              Gemini API
     |                      |
     |              Resume Parsing
     |                      |
     |             Sentence Transformers
     |                      |
     |                  Embeddings
     |                      |
     |                  ChromaDB
     |                      |
     +----------------------+
```

### Architecture Components

- **Frontend Layer:** Provides user interfaces for candidates, administrators, and interviewers.
- **Backend Layer:** Handles authentication, business logic, resume processing, job management, and interview workflows.
- **Database Layer:** Stores candidate profiles, jobs, applications, interviews, and feedback.
- **AI Layer:** Uses Gemini for structured resume extraction and Sentence Transformers for generating embeddings.
- **Vector Search Layer:** Uses ChromaDB to support semantic candidate retrieval.

---

## 4. Core Features

### A. Candidate Portal

- Candidate registration and login.
- Secure authentication.
- Candidate profile management.
- Single resume upload (PDF/DOCX).
- AI-powered resume parsing.
- Automatic extraction of:
  - Full name
  - Email address
  - Phone number
  - Education
  - Technical skills
  - Work experience
  - Projects
  - Employment history
- Review and correction of extracted information.
- View available job openings.
- Apply for jobs.
- Track application status.
- View scheduled interviews.

### B. Bulk Resume Upload & AI Parsing

Administrators can:

- Upload multiple resumes simultaneously.
- Process resumes individually.
- Extract structured candidate information using Gemini.
- Store candidate profiles in MySQL.
- Detect duplicate candidates.
- Track processing status:
  - Completed
  - Failed
  - Processing
- Handle invalid and corrupted resume files.

### C. Admin Recruitment Portal

#### Admin Dashboard

Displays:

- Total candidates.
- Total resumes.
- Active jobs.
- Total applications.
- Shortlisted candidates.
- Scheduled interviews.
- Selected candidates.

#### Job Management

Supports CRUD operations:

- Create jobs.
- View job details.
- Update job information.
- Delete jobs.

Each job includes:

- Job title and description.
- Required and preferred skills.
- Minimum and maximum experience.
- Education requirements.
- Location.
- Employment type.
- Application deadline.
- Job status.

#### AI-Based Candidate Matching

The matching engine evaluates candidates using:

- Required technical skills.
- Relevant experience.
- Educational qualifications.
- Preferred skills.
- Semantic similarity between resumes and job descriptions.

The system generates:

- Overall matching score (0–100).
- Matched skills.
- Missing skills.
- Experience comparison.
- Explainable matching recommendations.

#### Candidate Management

- View complete candidate profiles.
- Search and filter candidates.
- Sort candidates by matching score.
- Review extracted resume information.
- Correct candidate information.
- Add internal notes.
- Shortlist suitable candidates.
- Override AI recommendations.

### D. Shortlisting & Notifications

- Select multiple candidates for shortlisting.
- Maintain job-specific shortlists.
- Export shortlisted candidates to CSV/Excel.
- Approve candidates for interviews.
- Send email notifications.
- Update application statuses.

### E. Interview Management Portal

Administrators can:

- Schedule interviews.
- Select candidates and interviewers.
- Set interview dates and times.
- Configure interview duration.
- Send interview invitations.
- Reschedule interviews.
- Cancel interviews.
- View upcoming interviews.

Interviewers can:

- View assigned interviews.
- Access authorized candidate profiles.
- Submit interview feedback.

Interview feedback includes:

- Technical skills.
- Communication skills.
- Problem-solving ability.
- Additional remarks.
- Final recommendation.

Candidates can view their scheduled interviews.

---

## 5. AI & LLM Integration

AI is a central component of TalentIQ.

### 5.1 AI-Based Resume Parsing

Google Gemini API is used to extract structured candidate information from resume text.

**Workflow:**

1. Candidate uploads a PDF or DOCX resume.
2. The backend extracts text from the document.
3. Extracted text is passed to the Gemini API.
4. Gemini identifies relevant candidate information.
5. Structured JSON output is validated.
6. Extracted information is stored in MySQL.
7. Candidates and administrators can review the extracted information.

Example structured output:

```json
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "education": [
    {
      "degree": "B.Sc Computer Science",
      "institution": "ABC College"
    }
  ],
  "skills": [
    "Python",
    "SQL",
    "Machine Learning",
    "Flask"
  ],
  "experience": [],
  "projects": [
    {
      "name": "Student Management System",
      "description": "A web-based student management application."
    }
  ]
}
```

*Note: The example above contains fictional data for demonstration.*

### 5.2 Embedding Generation

TalentIQ uses Sentence Transformers to convert candidate profiles and job descriptions into numerical vector representations.

These embeddings capture the semantic meaning of text.

The generated embeddings are stored in ChromaDB.

### 5.3 Semantic Search

Semantic search enables recruiters to search candidates using natural language.

Example query:

"Find candidates with Python development experience and knowledge of machine learning."

Instead of relying only on exact keyword matches, the system retrieves candidates based on semantic similarity.

### 5.4 Hybrid Candidate Matching

TalentIQ combines structured matching and semantic similarity to calculate candidate matching scores.

**Proposed scoring methodology:**

| Matching Factor | Weight |
|---|---:|
| Required Skills | 40% |
| Relevant Experience | 20% |
| Educational Qualifications | 10% |
| Preferred Skills | 10% |
| Semantic Similarity | 20% |
| **Total** | **100%** |

Formula:

```text
Final Score =
    (Required Skills Score × 0.40)
  + (Experience Score × 0.20)
  + (Education Score × 0.10)
  + (Preferred Skills Score × 0.10)
  + (Semantic Similarity Score × 0.20)
```

All component scores are normalized to a scale of 0–100.

The matching score is calculated programmatically and is not accepted directly from an LLM response.

### 5.5 Explainable AI

For each recommendation, the platform displays:

- Skills that match job requirements.
- Missing required or preferred skills.
- Experience comparison.
- Education comparison.
- Semantic relevance.
- Explanation of the recommendation.

### 5.6 Hallucination Handling

To improve the reliability of extracted information:

- Resume content is treated as the source of truth.
- Missing information is represented as null or an empty list.
- Candidate information is validated before database insertion.
- AI-generated information can be reviewed and corrected.
- No unsupported skills or qualifications are added.
- Human administrators can override AI recommendations.

### 5.7 Human-in-the-Loop

AI recommendations are decision-support information, not final hiring decisions.

Administrators review candidate profiles and matching explanations before shortlisting or rejecting candidates.

---

## 6. Database Design

The platform uses MySQL for structured data storage.

### Planned Database Tables

| Table | Purpose |
|---|---|
| users | Authentication and user roles |
| candidates | Candidate personal and professional profiles |
| resumes | Uploaded resume metadata |
| jobs | Job descriptions and requirements |
| applications | Candidate job applications |
| candidate_skills | Candidate technical skills |
| candidate_embeddings | Embedding references and metadata |
| shortlists | Job-specific shortlisted candidates |
| internal_notes | Recruiter notes |
| interviews | Interview schedules |
| interviewers | Interviewer information |
| interview_feedback | Interview evaluation details |
| notifications | Application and interview notifications |

### Entity Relationships

```text
USERS
  |
  +------ CANDIDATES
  |           |
  |           +------ RESUMES
  |           |
  |           +------ CANDIDATE_SKILLS
  |           |
  |           +------ APPLICATIONS
  |                         |
  |                         +------ JOBS
  |                         |
  |                         +------ SHORTLISTS
  |                         |
  |                         +------ INTERVIEWS
  |                                      |
  |                                      +------ INTERVIEW_FEEDBACK
  |
  +------ INTERVIEWERS
```

The final database schema and ER diagram will be maintained in the `docs/` directory.

---

## 7. Project Folder Structure

```text
TalentIQ/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   └── extensions.py
│   │
│   ├── uploads/
│   │   ├── resumes/
│   │   └── temp/
│   │
│   ├── config.py
│   ├── run.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── index.html
│
├── docs/
│   ├── architecture.md
│   ├── database-schema.md
│   └── matching-methodology.md
│
├── sample_data/
│   ├── resumes/
│   └── job_descriptions/
│
├── .gitignore
└── README.md
```

---

## 8. Installation & Setup Instructions

### Prerequisites

Install the following:

- Python 3.11+
- Node.js and npm
- MySQL 8.0+
- Git
- VS Code

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TalentIQ
```

### Step 2: Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file inside the backend folder.

```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=talentiq_db

GEMINI_API_KEY=your_gemini_api_key
```

Never commit actual API keys or passwords.

### Step 4: Create MySQL Database

Open MySQL Workbench and execute:

```sql
CREATE DATABASE talentiq_db;
```

### Step 5: Start Flask Backend

```bash
python run.py
```

Backend URL:

```text
http://localhost:5000
```

### Step 6: Frontend Setup

Open a separate terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## 9. API Documentation

The backend exposes REST APIs for authentication, candidate management, job management, resume processing, matching, shortlisting, and interviews.

Planned API groups:

| Module | Example Endpoint | Method |
|---|---|---|
| Authentication | /api/auth/register | POST |
| Authentication | /api/auth/login | POST |
| Candidates | /api/candidates/profile | GET |
| Candidates | /api/candidates/profile | PUT |
| Resumes | /api/resumes/upload | POST |
| Resumes | /api/resumes/bulk-upload | POST |
| Jobs | /api/jobs | GET |
| Jobs | /api/jobs | POST |
| Jobs | /api/jobs/{id} | PUT |
| Matching | /api/matching/{job_id} | GET |
| Semantic Search | /api/search | POST |
| Shortlisting | /api/shortlists | POST |
| Interviews | /api/interviews | POST |
| Feedback | /api/interviews/{id}/feedback | POST |

The final API documentation and request/response examples will be provided with the completed implementation.

---

## 10. Security & Error Handling

The platform is designed with the following security considerations:

- JWT-based authentication.
- Password hashing.
- Role-based access control.
- Candidate-specific profile access.
- File type and file size validation.
- Secure handling of uploaded resumes.
- Environment-based API key management.
- Input validation.
- Duplicate candidate detection.
- Individual error handling during bulk uploads.
- Protection against unauthorized access to candidate information.

---

## 11. Mandatory Test Scenarios

The following scenarios will be used to validate the application.

| No. | Test Scenario | Expected Result |
|---|---|---|
| 1 | Candidate uploads resume | Candidate profile is created using extracted information |
| 2 | Admin uploads 5 resumes | All resumes are processed individually |
| 3 | Admin uploads invalid file | Error is handled without stopping other uploads |
| 4 | Admin creates job | Job is saved successfully |
| 5 | Admin selects job for matching | Candidates are ranked with matching scores |
| 6 | Admin performs natural language search | Relevant candidates are retrieved |
| 7 | Admin views candidate profile | Profile and matching explanation are displayed |
| 8 | Admin shortlists candidates | Candidates are added to the job-specific shortlist |
| 9 | Admin approves candidate | Interview notification is generated |
| 10 | Admin schedules interview | Interview details are saved and visible to candidate |
| 11 | Interviewer submits feedback | Feedback is stored and visible to authorized admins |
| 12 | Candidate accesses another candidate's profile | Access is denied |

Actual test results will be documented after implementation and execution.

---

## 12. Future Enhancements

Potential future improvements include:

- Multi-agent AI recruitment workflow.
- AI recruitment assistant.
- Automated interview question generation.
- AI-assisted interview feedback summarization.
- Advanced recruitment analytics.
- MCP server integration.
- Live video interviews using WebRTC.
- Docker-based deployment.

---

## 13. Development Status

This project is being developed as part of an AI Intern technical assessment.

Features will be marked complete only after implementation and testing.

| Module | Status |
|---|---|
| Project Architecture | In Progress |
| Database Integration | Pending |
| Candidate Authentication | Pending |
| Resume Upload | Pending |
| AI Resume Parsing | Pending |
| Bulk Resume Processing | Pending |
| Job Management | Pending |
| Embedding Generation | Pending |
| Semantic Search | Pending |
| Hybrid Candidate Matching | Pending |
| Admin Dashboard | Pending |
| Shortlisting | Pending |
| Interview Management | Pending |
| Security & Testing | Pending |
| Documentation | In Progress |

---

## 14. Demo & Credentials

Demo credentials will be provided after the application is configured and tested.

**Frontend:** `http://localhost:5173`

**Backend:** `http://localhost:5000`

**Demo Video:** To be added after implementation.

---

## 15. Author & Project Information

**Project:** TalentIQ – AI-Powered Recruitment & Interview Management Platform

**Developer:** Kshitija Sunil More

**GitHub:** [KshitijaMore07](https://github.com/KshitijaMore07)

**Purpose:** AI Intern Technical Assessment

---

## 16. Acknowledgements

This project uses open-source technologies and AI services to demonstrate practical applications of full-stack development, Large Language Models, embedding generation, semantic search, and intelligent recruitment automation.

**TalentIQ – Intelligent Recruitment. Smarter Hiring.**

