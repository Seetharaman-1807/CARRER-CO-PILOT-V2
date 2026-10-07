from app.engines.ats_scorer import calculate_ats_score, ATS_WEIGHTS


def test_deterministic_ats_scoring_weights_sum_to_one():
    total_weight = sum(ATS_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6


def test_deterministic_ats_scoring_output():
    mock_resume_parsed = {
        "skills": [
            {"skill": "Python", "canonical": "Python", "source_section": "Skills"},
            {"skill": "FastAPI", "canonical": "FastAPI", "source_section": "Projects"},
            {"skill": "PostgreSQL", "canonical": "PostgreSQL", "source_section": "Skills"},
        ],
        "experience": ["Backend Engineer at Acme Corp, building APIs with Python and FastAPI."],
        "education": ["B.Tech in Computer Science and Engineering."],
        "projects": ["Distributed task queue built using FastAPI, Redis, and PostgreSQL."],
        "sections_found": ["skills", "experience", "education", "projects"],
        "achievements": ["Improved API response latency by 35% across 500k requests."],
    }
    raw_text = (
        "Backend Engineer with 3 years experience. Skills: Python, FastAPI, PostgreSQL, Redis. "
        "Built distributed task queue with FastAPI and PostgreSQL. B.Tech in Computer Science."
    )
    jd_text = (
        "We are looking for a Backend Engineer with experience in Python, FastAPI, and PostgreSQL. "
        "Must have experience designing RESTful APIs and databases. 2+ years of experience required."
    )
    required_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]

    result = calculate_ats_score(
        resume_parsed=mock_resume_parsed,
        resume_raw_text=raw_text,
        jd_text=jd_text,
        jd_required_skills=required_skills
    )

    assert "overall_score" in result
    assert "components" in result
    assert "scoring_version" in result
    assert result["scoring_version"] == "v2.0-deterministic"

    components = result["components"]
    assert "keyword_match" in components
    assert "technical_skill_match" in components
    assert "experience_match" in components
    assert "education_match" in components
    assert "project_relevance" in components
    assert "formatting" in components
    assert "section_completeness" in components

    # The sum of components must match overall_score within rounding tolerance
    component_sum = sum(components.values())
    assert abs(result["overall_score"] - round(component_sum, 1)) <= 0.2

    # Determinism check: repeated execution yields exact same score
    result2 = calculate_ats_score(
        resume_parsed=mock_resume_parsed,
        resume_raw_text=raw_text,
        jd_text=jd_text,
        jd_required_skills=required_skills
    )
    assert result["overall_score"] == result2["overall_score"]
    assert result["components"] == result2["components"]
