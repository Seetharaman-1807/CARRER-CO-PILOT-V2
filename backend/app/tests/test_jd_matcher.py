from app.engines.jd_matcher import parse_job_description, classify_skill_match
from app.engines.skill_gap_engine import analyze_skill_gaps


def test_parse_job_description():
    jd_text = """Senior Backend Developer
We require strong knowledge of Python and FastAPI.
Must have experience with Docker and PostgreSQL.
Knowledge of Kubernetes and Redis is preferred."""

    parsed = parse_job_description(jd_text)
    assert "Python" in parsed["required_skills"] or "Python" in parsed["all_skills"]
    assert "FastAPI" in parsed["all_skills"]
    assert "Docker" in parsed["all_skills"]
    assert len(parsed["all_skills"]) >= 4


def test_classify_skill_match_exact_and_related():
    candidate_skills = {
        "FastAPI": {"score": 85.0, "confidence": "High"},
        "PostgreSQL": {"score": 70.0, "confidence": "Medium"}
    }
    raw_resume = "Built APIs with FastAPI and PostgreSQL."

    # Exact match
    match_fastapi = classify_skill_match("FastAPI", candidate_skills, raw_resume)
    assert match_fastapi["status"] == "exact"

    # Related match: candidate knows FastAPI, JD requires Django
    match_django = classify_skill_match("Django", candidate_skills, raw_resume)
    assert match_django["status"] == "related"

    # Missing match: Kubernetes not present
    match_k8s = classify_skill_match("Kubernetes", candidate_skills, raw_resume)
    assert match_k8s["status"] == "missing"


def test_analyze_skill_gaps_prioritization():
    candidate_skills = [
        {"canonical_name": "FastAPI", "score": 85.0, "confidence": "High"}
    ]
    raw_resume = "FastAPI backend developer."
    jd_required = ["FastAPI", "Docker", "System Design"]

    gap_result = analyze_skill_gaps(candidate_skills, raw_resume, jd_required)
    gaps = gap_result["gaps"]

    # Docker and System Design should be high priority missing gaps
    gap_skills = [g["canonical_skill"] for g in gaps if g["priority"] == "High"]
    assert "Docker" in gap_skills or "System Design" in gap_skills
