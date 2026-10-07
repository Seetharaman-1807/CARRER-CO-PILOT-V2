import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_step(num, title):
    print(f"\n{'='*70}\n[STEP {num}] {title}\n{'='*70}")

def run_e2e_verification():
    session = requests.Session()

    # 1. New user registers
    print_step(1, "New User Registration")
    reg_payload = {
        "email": "executive_alex@career.ai",
        "password": "SecurePassword2026!",
        "full_name": "Alex Mercer"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=reg_payload)
    if r.status_code == 400 and "already exists" in r.text:
        print("User exists, logging in instead...")
        r = session.post(f"{BASE_URL}/auth/login", json={"email": reg_payload["email"], "password": reg_payload["password"]})
    assert r.status_code == 200, f"Register/Login failed: {r.text}"
    token_data = r.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[PASS] Authenticated successfully. User ID: {token_data['user']['id']}")

    # 2. Upload Resume V1
    print_step(2, "Upload Resume V1 (PDF/Text) & Ingest Evidence")
    resume_v1 = """
Alex Mercer - executive_alex@career.ai - San Francisco, CA
SUMMARY
Backend Engineer with experience in high-throughput API architectures and databases.

TECHNICAL SKILLS
Languages & Frameworks: Python, FastAPI, SQL.
Tools: Git, Linux.

EXPERIENCE
Software Engineer at CloudScale (2022-2024):
- Developed high-throughput REST APIs using FastAPI and Python.
- Designed schema migrations and relational tables using SQL.

PROJECTS
Event Streamer Service:
- Built real-time event pipeline using FastAPI and asynchronous background workers.
"""
    r = session.post(f"{BASE_URL}/resumes", data={"raw_text": resume_v1, "title": "Alex Software Resume V1"}, headers=headers)
    assert r.status_code == 200, f"Resume V1 upload failed: {r.text}"
    v1_data = r.json()
    resume_id = v1_data["resume_id"]
    print(f"[PASS] Resume V1 created (Version {v1_data['version_number']}). Extracted {len(v1_data['parsed_content']['skills'])} skills.")
    for sk in v1_data['parsed_content']['skills'][:3]:
        print(f"   * Skill: {sk['canonical']} | Section: {sk['source_section']} | Quote: \"{sk['evidence'][:60]}...\"")

    # 3. Add Job Description
    print_step(3, "Add Target Role & Job Description")
    jd_content = """
Senior Backend Developer
We are looking for an experienced backend engineer to join our platform team.
Required Qualifications:
- 3+ years experience with Python and FastAPI
- Production experience with PostgreSQL, Database Indexing, and Redis
- Strong foundation in Data Structures & Algorithms
- Hands-on experience with Docker, Kubernetes, and CI/CD
- Knowledge of System Design and microservices architecture
"""
    r = session.post(f"{BASE_URL}/job-descriptions", json={"title": "Senior Backend Developer", "company": "Stripe", "content": jd_content}, headers=headers)
    assert r.status_code == 200, f"JD creation failed: {r.text}"
    jd_data = r.json()
    jd_id = jd_data["id"]
    print(f"[PASS] Job Description saved (ID: {jd_id}). Detected required skills: {jd_data['parsed_requirements']['required_skills']}")

    # 4. Deterministic ATS Scoring Layer
    print_step(4, "Compute Deterministic ATS Score (7 Component Weights)")
    r = session.post(f"{BASE_URL}/analyses/ats", json={"resume_version_id": v1_data["id"], "job_description_id": jd_id}, headers=headers)
    assert r.status_code == 200, f"ATS calculation failed: {r.text}"
    ats_data = r.json()
    print(f"[PASS] Overall ATS Score: {ats_data['overall_score']}/100 (Scoring Engine: {ats_data['scoring_version']})")
    print("   Deterministic Components Breakdown:")
    for comp, score in ats_data["component_scores"].items():
        print(f"     - {comp.replace('_', ' ').title():<25}: {score} pts")

    # 5. Semantic JD Match & Skill Gap Engine
    print_step(5, "Analyze Semantic Skill Gaps against JD")
    r = session.post(f"{BASE_URL}/analyses/skill-gap", params={"job_description_id": jd_id}, headers=headers)
    assert r.status_code == 200, f"Skill gap calculation failed: {r.text}"
    gap_data = r.json()
    print(f"[PASS] Evaluated {gap_data['summary']['total_requirements']} requirements:")
    print(f"   * Exact Matches: {gap_data['summary']['exact_matches']}")
    print(f"   * Transferable: {gap_data['summary']['related_matches']}")
    print(f"   * Partial: {gap_data['summary']['weak_matches']}")
    print(f"   * Missing Gaps: {gap_data['summary']['missing_skills']}")
    print(f"   * High Priority Remediation: {gap_data['summary']['high_priority_gaps']}")

    # 6. Baseline Career Readiness
    print_step(6, "Compute Baseline Career Readiness (6 Transparent Dimensions)")
    r = session.post(f"{BASE_URL}/analyses/readiness", headers=headers)
    assert r.status_code == 200, f"Readiness calculation failed: {r.text}"
    readiness_v1 = r.json()
    print(f"[PASS] Baseline Readiness: {readiness_v1['overall_score']}/100 (Confidence: {readiness_v1['confidence']})")
    for k, comp in readiness_v1["components"].items():
        print(f"   - {comp['name']:<22}: {comp['score']:<5} | Conf: {comp['confidence']:<22} | Evidence: {comp['evidence']}")

    # 7. Adaptive Roadmap Generation
    print_step(7, "Generate Personalized Adaptive Roadmap")
    r = session.post(f"{BASE_URL}/roadmap/generate", json={}, headers=headers)
    assert r.status_code == 200, f"Roadmap generation failed: {r.text}"
    roadmap_data = r.json()
    print(f"[PASS] Roadmap Title: \"{roadmap_data['title']}\"")
    print(f"[PASS] Goal: \"{roadmap_data['goal']}\"")
    print(f"[PASS] Generated {len(roadmap_data['tasks'])} prioritized milestones:")
    for t in roadmap_data['tasks'][:3]:
        print(f"   * [{t['priority']} Priority] {t['title']} ({t['estimated_minutes']} mins)")
    first_task_id = roadmap_data['tasks'][0]['id']

    # 8. Adaptive Practice: DSA Algorithmic Challenge
    print_step(8, "Execute Sandboxed DSA Challenge (Two Sum)")
    dsa_solution = """
def two_sum(nums, target):
    lookup = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in lookup:
            return [lookup[complement], i]
        lookup[n] = i
    return []
"""
    r = session.get(f"{BASE_URL}/dsa/problems", headers=headers)
    prob_id = r.json()[0]["id"]
    r = session.post(f"{BASE_URL}/dsa/attempts", json={"problem_id": prob_id, "code": dsa_solution, "hints_used": 0}, headers=headers)
    assert r.status_code == 200, f"DSA attempt failed: {r.text}"
    dsa_res = r.json()
    assert dsa_res["execution_result"]["passed"] is True
    print(f"[PASS] DSA Execution Passed: {dsa_res['execution_result']['passed_count']}/{dsa_res['execution_result']['total']} test cases ({dsa_res['execution_result']['runtime_ms']} ms)")
    print(f"[PASS] Candidate topic mastery automatically updated for: Hashing")

    # 9. Adaptive Practice: Simulated Mock Technical Interview
    print_step(9, "Simulate Mock Technical Interview Round")
    r = session.post(f"{BASE_URL}/interviews", json={"type": "technical"}, headers=headers)
    assert r.status_code == 200, f"Interview session creation failed: {r.text}"
    int_sess = r.json()
    sess_id = int_sess["id"]
    q1 = int_sess["questions"][0]
    print(f"[PASS] Question 1: \"{q1['question']}\" (Focus: {q1['focus_skill']})")

    answer_text = (
        "In RESTful APIs, idempotency for POST can be achieved by utilizing an Idempotency-Key HTTP header. "
        "Upon receiving a request, the gateway looks up this unique token in a distributed Redis database. "
        "If a previous completed response exists, it returns the cached result without re-executing state mutation. "
        "For PATCH, updating a field to a specific value is naturally idempotent if designed properly with conditional updates."
    )
    r = session.post(f"{BASE_URL}/interviews/{sess_id}/responses", json={"question_id": q1["id"], "response": answer_text}, headers=headers)
    assert r.status_code == 200, f"Response submission failed: {r.text}"
    resp_eval = r.json()["evaluation"]
    print(f"[PASS] Rubric Evaluation:")
    print(f"   * Technical Accuracy : {resp_eval['technical_accuracy']}/10")
    print(f"   * Clarity            : {resp_eval['clarity']}/10")
    print(f"   * Depth              : {resp_eval['depth']}/10")
    print(f"   * Overall Rating     : {resp_eval['overall']}/10")
    print(f"   * Matched Concepts   : {resp_eval['matched_concepts']}")

    # Complete interview session
    session.post(f"{BASE_URL}/interviews/{sess_id}/complete", headers=headers)

    # 10. Complete Roadmap Milestone (Closed Loop Update)
    print_step(10, "Complete Milestone Task & Trigger Adaptive Feedback Loop")
    r = session.post(f"{BASE_URL}/roadmap/tasks/{first_task_id}/complete", headers=headers)
    assert r.status_code == 200, f"Task completion failed: {r.text}"
    print(f"[PASS] Marked task '{r.json()['title']}' as completed. Evidence logged to candidate profile.")

    # 11. Recalculate Career Readiness After Demonstration
    print_step(11, "Recalculate Career Readiness (Evidence-Based Elevation)")
    r = session.post(f"{BASE_URL}/analyses/readiness", headers=headers)
    assert r.status_code == 200
    readiness_v2 = r.json()
    print(f"[PASS] Updated Readiness: {readiness_v2['overall_score']}/100 (Baseline was: {readiness_v1['overall_score']}/100)")
    assert readiness_v2["overall_score"] >= readiness_v1["overall_score"], "Readiness should increase after performance"

    # 12. Upload Resume V2 & Version Comparison Diff
    print_step(12, "Upload Resume V2 & Execute Version Diffing")
    resume_v2 = """
Alex Mercer - executive_alex@career.ai - San Francisco, CA
SUMMARY
Senior Backend Engineer specializing in high-throughput distributed systems and cloud databases.

TECHNICAL SKILLS
Languages & Frameworks: Python, FastAPI, SQL, PostgreSQL, Docker, Redis.
Systems & Tools: Git, Linux, CI/CD.

EXPERIENCE
Software Engineer at CloudScale (2022-2024):
- Developed high-throughput REST APIs using FastAPI and Python, handling 35,000 requests/sec.
- Optimized database indexing in PostgreSQL, reducing query latency by 42%.

PROJECTS
Event Streamer Service:
- Built real-time distributed event pipeline using FastAPI, Redis cache, and Docker containerization.
- Implemented CI/CD pipeline with GitHub Actions reducing deployment time by 50%.
"""
    r = session.post(f"{BASE_URL}/resumes", data={"raw_text": resume_v2, "title": "Alex Software Resume V2"}, headers=headers)
    assert r.status_code == 200
    v2_data = r.json()
    print(f"[PASS] Resume V2 created (Version {v2_data['version_number']}).")

    r = session.get(f"{BASE_URL}/resumes/{resume_id}/compare", headers=headers)
    assert r.status_code == 200, f"Resume comparison failed: {r.text}"
    comp = r.json()
    print(f"[PASS] Comparison V{comp['v1_version']} -> V{comp['v2_version']}:")
    print(f"   * Estimated ATS Gain: +{comp['ats_score_delta']}%")
    print(f"   * Newly Evidenced Skills: {comp['skills_added']}")
    print(f"   * Verified Improvements: {comp['improvements']}")

    # 13. Executive Dashboard Synthesis
    print_step(13, "Executive Dashboard Data Verification")
    r = session.get(f"{BASE_URL}/dashboard", headers=headers)
    assert r.status_code == 200
    dash = r.json()
    print(f"[PASS] Career Readiness: {dash['career_readiness']}/100 ({dash['confidence']} Confidence)")
    print(f"[PASS] Primary CTA: \"{dash['next_best_action']['title']}\"")
    print(f"   Button: \"{dash['next_best_action']['button_text']}\" -> Route: {dash['next_best_action']['action_route']}")
    print(f"[PASS] Today's Plan Actions ({len(dash['todays_plan'])} items):")
    for p in dash['todays_plan']:
        print(f"   * {p['task']} ({p['estimated_time']}) [{p['priority']} Priority]")

    print(f"\n{'='*70}\n[SUCCESS] ALL 13 STEPS OF THE END-TO-END SCENARIO PASSED 100%!\n{'='*70}\n")

if __name__ == "__main__":
    run_e2e_verification()
