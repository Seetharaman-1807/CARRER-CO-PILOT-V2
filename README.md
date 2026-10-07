# CAREER COPILOT V2
### Adaptive AI-Based Career Readiness and Skill-Gap Assessment System

> **ASSESS → IDENTIFY GAPS → PRACTICE → EVALUATE → ADAPT → IMPROVE**

Career Copilot V2 transforms career preparation from static advice into a production-grade, closed-feedback career acceleration platform. The system continuously evaluates candidate capabilities through evidence from resumes, job descriptions, assessments, algorithmic coding challenges, and mock interviews, dynamically adapting recommendations to reach target-role readiness.

---

## 🚀 Key Architectural Pillars

### 1. Closed Feedback Loop
- **Evidence-First Profiling**: No hallucinated claims. Every candidate skill retains an exact evidence snippet, section source, and confidence score.
- **Continuous State Adaptation**: Solving DSA problems, answering interview rounds, or completing roadmap milestones automatically updates the candidate's skill profile and elevates their readiness score.

### 2. Deterministic ATS Scoring Layer
The final ATS score is never invented arbitrarily by an LLM. It is mathematically calculated across 7 transparent, configurable component weights (Total = 100):
- **Keyword Match**: 25%
- **Technical Skill Match**: 25%
- **Experience Match**: 15%
- **Education Match**: 10%
- **Project Relevance**: 10%
- **Formatting**: 10%
- **Section Completeness**: 5%

### 3. Semantic Job-Description Matching & Gap Engine
Classifies candidate-to-JD requirements into 5 precise states:
1. **Exact Match**: Direct canonical skill match backed by demonstrated evidence.
2. **Related / Transferable**: Identified transferable skills (e.g., candidate has `FastAPI`, JD requires `Django`).
3. **Partial Evidence**: Shallow mention in resume without technical project depth.
4. **Missing Gap**: Requirement absent from candidate profile.
5. **Ambiguous**: Undefined context.

Prioritizes remediation using the formula:
`Priority = Role Importance × Candidate Weakness × Interview Relevance`

### 4. Career Readiness Score (Separate from ATS)
Answers: *"How prepared is this candidate right now based on available evidence?"*
Transparent 6-dimension component model:
- **Resume Quality** (20%)
- **Technical Skills** (25%)
- **DSA Readiness** (20%)
- **Project Readiness** (15%)
- **Interview Readiness** (10%)
- **Target JD Match** (10%)
Displays **"Insufficient evidence"** badges rather than inventing artificial scores when activities are not yet completed.

### 5. Multi-Version Resume Intelligence & Diffs
- Supports **PDF**, **DOCX**, and **TXT** formats.
- Complete versioning history (Resume V1 → V2 → V3).
- Version Comparison Viewer: compares ATS gains, newly evidenced skills, removed skills, and added project metrics.
- Built-in prompt injection defense sanitizing untrusted document content.

### 6. Sandboxed DSA Practice Engine
- Curated progressive challenges across: **Arrays**, **Two Pointers**, **Hashing**, **Binary Search**, and **Sliding Window**.
- Safe AST syntax inspection prohibiting forbidden modules (`os`, `sys`, `subprocess`, file I/O).
- Time-limited execution harness with unit tests, latency measurement (ms), and progressive hint tracking.

### 7. Adaptive Mock Interview Studio
- Multi-turn simulated rounds (Technical, Behavioral, Role-specific).
- Structured Rubric Evaluation: **Technical Accuracy** (1-10), **Clarity** (1-10), **Depth** (1-10), and **Overall Rating** (1-10).
- Actionable feedback and automatic skill evidence logging.

### 8. Executive Dashboard
- **Above the Fold**: Radial Career Readiness Gauge, Target Role, and Primary CTA (**"Next Best Action"**).
- **Below the Fold**: 6-dimension breakdown grid, Top 3 Skill Gaps, "What Should I Do Today?" daily action checklist, and active resume status.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic V2, PyJWT, bcrypt, pypdf, python-docx, pytest, httpx |
| **Frontend** | React 18, Vite, TypeScript, Lucide Icons, Custom Vanilla CSS Glassmorphism Design System |
| **Database** | SQLite (zero-config local development) / 100% PostgreSQL-compatible |
| **Security** | JWT Bearer auth, bcrypt password hashing, multi-tenant user isolation, AST sandbox, prompt injection filtering |

---

## 🏁 Quickstart Guide

### 1. Backend Setup
```bash
cd backend

# Activate virtual environment
venv\Scripts\activate   # Windows

# Run database migrations / start API server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Docs will be available at: `http://127.0.0.1:8000/api/v1/docs`

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev -- --host 127.0.0.1 --port 5173
```
Open web application at: `http://127.0.0.1:5173`

### 3. Run Automated Test Suites
```bash
# Run 13 unit & integration tests
cd backend
venv\Scripts\pytest -v

# Run full 13-step live end-to-end scenario test
venv\Scripts\python verify_live_scenario.py
```
