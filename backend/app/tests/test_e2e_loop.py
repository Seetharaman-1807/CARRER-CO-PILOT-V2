def test_complete_adaptive_career_readiness_lifecycle(client):
    # Step 1: Register User
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@company.com", "password": "SecurePassword999!", "full_name": "Alice Engineer"}
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2 & 3: Upload Resume V1
    resume_v1_text = """
Alice Engineer - alice@company.com
SUMMARY
Software Developer targeting Backend Engineering.

EDUCATION
B.Tech in Computer Science, 2024.

TECHNICAL SKILLS
Languages & Frameworks: Python, FastAPI, SQL.

EXPERIENCE
Junior Developer: Built REST APIs using FastAPI and SQLite.

PROJECTS
Task Manager API: Developed CRUD service using Python and FastAPI.
"""
    upload_res = client.post(
        "/api/v1/resumes",
        data={"raw_text": resume_v1_text, "title": "Alice Backend Resume"},
        headers=headers
    )
    assert upload_res.status_code == 200
    v1_data = upload_res.json()
    assert v1_data["version_number"] == 1
    assert any(s["canonical"] == "FastAPI" for s in v1_data["parsed_content"]["skills"])

    # Step 4: Verify Candidate Skill Profile updated with resume evidence
    skills_res = client.get("/api/v1/skills/profile", headers=headers)
    assert skills_res.status_code == 200
    candidate_skills = skills_res.json()
    assert any(s["canonical_name"] == "FastAPI" for s in candidate_skills)

    # Step 5 & 6: Create Target Job Description
    jd_text = """
Backend Engineer (Senior)
Required Qualifications:
- 3+ years experience with Python and FastAPI
- Hands-on experience with PostgreSQL and Docker
- Deep understanding of Data Structures & Algorithms
- Experience with System Design and CI/CD
"""
    jd_res = client.post(
        "/api/v1/job-descriptions",
        json={"title": "Backend Engineer", "company": "TechCorp", "content": jd_text},
        headers=headers
    )
    assert jd_res.status_code == 200
    jd_id = jd_res.json()["id"]

    # Step 7: Deterministic ATS calculation
    ats_res = client.post(
        "/api/v1/analyses/ats",
        json={"resume_version_id": v1_data["id"], "job_description_id": jd_id},
        headers=headers
    )
    assert ats_res.status_code == 200
    ats_data = ats_res.json()
    assert "overall_score" in ats_data
    assert ats_data["scoring_version"] == "v2.0-deterministic"
    ats_v1_score = ats_data["overall_score"]

    # Step 8 & 9: Skill Gap Analysis
    gap_res = client.post(
        "/api/v1/analyses/skill-gap",
        params={"job_description_id": jd_id},
        headers=headers
    )
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert len(gap_data["gaps"]) > 0

    # Step 10: Career Readiness Baseline
    readiness_res = client.post("/api/v1/analyses/readiness", headers=headers)
    assert readiness_res.status_code == 200
    baseline_readiness = readiness_res.json()["overall_score"]

    # Step 11: Generate Adaptive Roadmap
    roadmap_res = client.post("/api/v1/roadmap/generate", json={}, headers=headers)
    assert roadmap_res.status_code == 200
    roadmap_data = roadmap_res.json()
    assert len(roadmap_data["tasks"]) > 0
    task_id = roadmap_data["tasks"][0]["id"]

    # Step 12: Complete a Roadmap Task (adaptive feedback)
    comp_task_res = client.post(f"/api/v1/roadmap/tasks/{task_id}/complete", headers=headers)
    assert comp_task_res.status_code == 200
    assert comp_task_res.json()["status"] == "completed"

    # Step 13: Practice DSA Challenge
    dsa_problems = client.get("/api/v1/dsa/problems", headers=headers).json()
    prob_id = dsa_problems[0]["id"]
    correct_solution = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    dsa_attempt_res = client.post(
        "/api/v1/dsa/attempts",
        json={"problem_id": prob_id, "code": correct_solution, "hints_used": 0},
        headers=headers
    )
    assert dsa_attempt_res.status_code == 200
    assert dsa_attempt_res.json()["execution_result"]["passed"] is True

    # Step 14: Practice Mock Interview
    int_start_res = client.post("/api/v1/interviews", json={"type": "technical"}, headers=headers)
    assert int_start_res.status_code == 200
    session_id = int_start_res.json()["id"]
    first_q_id = int_start_res.json()["questions"][0]["id"]

    int_sub_res = client.post(
        f"/api/v1/interviews/{session_id}/responses",
        json={
            "question_id": first_q_id,
            "response": "To ensure idempotency in RESTful APIs, clients can send a unique idempotency key or token in HTTP headers. The backend stores this key with the response in a distributed Redis database, ensuring duplicate retries return the original cached state without re-executing transactions."
        },
        headers=headers
    )
    assert int_sub_res.status_code == 200
    assert int_sub_res.json()["evaluation"]["overall"] >= 6.0

    client.post(f"/api/v1/interviews/{session_id}/complete", headers=headers)

    # Step 15: Recalculate Readiness (Should reflect proven performance)
    new_readiness_res = client.post("/api/v1/analyses/readiness", headers=headers)
    assert new_readiness_res.status_code == 200
    updated_readiness = new_readiness_res.json()["overall_score"]
    assert updated_readiness >= baseline_readiness

    # Step 16 & 17: Upload Resume V2 with added skills and achievements
    resume_v2_text = """
Alice Engineer - alice@company.com
SUMMARY
Software Developer specializing in Backend Systems.

EDUCATION
B.Tech in Computer Science, 2024.

TECHNICAL SKILLS
Languages & Frameworks: Python, FastAPI, PostgreSQL, Docker, Redis.

EXPERIENCE
Backend Engineer: Developed distributed services handling 20,000 requests/sec with FastAPI and PostgreSQL.

PROJECTS
Task Manager API: Built containerized CRUD service with Docker, Redis cache, and PostgreSQL.
ACHIEVEMENTS
- Reduced query latency by 45% using database index optimization.
- Improved container boot time by 30% with multi-stage Docker builds.
"""
    upload_v2_res = client.post(
        "/api/v1/resumes",
        data={"raw_text": resume_v2_text, "title": "Alice Backend Resume V2"},
        headers=headers
    )
    assert upload_v2_res.status_code == 200
    v2_data = upload_v2_res.json()
    assert v2_data["version_number"] == 2

    # Step 18: Compare Resume V1 vs V2
    compare_res = client.get(f"/api/v1/resumes/{v1_data['resume_id']}/compare", headers=headers)
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert "Docker" in comp_data["skills_added"] or "PostgreSQL" in comp_data["skills_added"]

    # Step 19: Executive Dashboard verification
    dashboard_res = client.get("/api/v1/dashboard", headers=headers)
    assert dashboard_res.status_code == 200
    dash_data = dashboard_res.json()
    assert "career_readiness" in dash_data
    assert "next_best_action" in dash_data
    assert "todays_plan" in dash_data
    assert len(dash_data["todays_plan"]) >= 3
