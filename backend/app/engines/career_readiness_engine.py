from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

READINESS_WEIGHTS = {
    "resume_quality": 0.20,
    "technical_skills": 0.25,
    "dsa_readiness": 0.20,
    "project_readiness": 0.15,
    "interview_readiness": 0.10,
    "target_jd_match": 0.10,
}


def calculate_career_readiness(
    ats_score: Optional[float],
    candidate_skills: List[Dict[str, Any]],
    dsa_attempts: List[Dict[str, Any]],
    interview_responses: List[Dict[str, Any]],
    resume_projects_count: int,
    jd_match_ratio: Optional[float]
) -> Dict[str, Any]:
    """
    Computes Career Readiness score across 6 transparent dimensions with explicit evidence.
    Marks components as 'Insufficient evidence' if no activities are logged yet.
    """
    now = datetime.now(timezone.utc).isoformat()
    components = {}

    # 1. Resume Quality (Weight 20%)
    if ats_score is not None:
        rq_score = min(100.0, float(ats_score))
        components["resume_quality"] = {
            "name": "Resume Quality",
            "score": round(rq_score, 1),
            "confidence": "High",
            "evidence": f"Evaluated via ATS parser and section depth ({rq_score:.1f}/100).",
            "last_updated": now,
        }
    else:
        components["resume_quality"] = {
            "name": "Resume Quality",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "Upload a resume to evaluate structure and ATS screening score.",
            "last_updated": now,
        }

    # 2. Technical Skill Readiness (Weight 25%)
    if candidate_skills:
        skill_scores = [float(s.get("score", 50.0)) for s in candidate_skills]
        avg_tech = sum(skill_scores) / len(skill_scores)
        conf = "High" if len(candidate_skills) >= 5 else "Medium"
        components["technical_skills"] = {
            "name": "Technical Skills",
            "score": round(avg_tech, 1),
            "confidence": conf,
            "evidence": f"Aggregated across {len(candidate_skills)} demonstrated technical skills.",
            "last_updated": now,
        }
    else:
        components["technical_skills"] = {
            "name": "Technical Skills",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "No skills extracted or assessed yet.",
            "last_updated": now,
        }

    # 3. DSA Readiness (Weight 20%)
    if dsa_attempts:
        successful = [a for a in dsa_attempts if a.get("execution_result", {}).get("passed", False)]
        success_ratio = len(successful) / max(len(dsa_attempts), 1)
        dsa_score = round(success_ratio * 100.0, 1)
        conf = "High" if len(dsa_attempts) >= 3 else "Medium"
        components["dsa_readiness"] = {
            "name": "DSA Readiness",
            "score": dsa_score,
            "confidence": conf,
            "evidence": f"Attempted {len(dsa_attempts)} problems ({len(successful)} test suite passes).",
            "last_updated": now,
        }
    else:
        components["dsa_readiness"] = {
            "name": "DSA Readiness",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "Complete recommended algorithmic challenges to establish DSA readiness.",
            "last_updated": now,
        }

    # 4. Project Readiness (Weight 15%)
    if resume_projects_count > 0:
        proj_score = min(100.0, 50.0 + (resume_projects_count * 20.0))
        components["project_readiness"] = {
            "name": "Project Readiness",
            "score": round(proj_score, 1),
            "confidence": "Medium",
            "evidence": f"Found {resume_projects_count} verified projects with technical implementations.",
            "last_updated": now,
        }
    else:
        components["project_readiness"] = {
            "name": "Project Readiness",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "Add project achievements with concrete architecture metrics.",
            "last_updated": now,
        }

    # 5. Interview Readiness (Weight 10%)
    if interview_responses:
        eval_scores = []
        for r in interview_responses:
            ev = r.get("evaluation", {})
            if "overall" in ev:
                eval_scores.append(float(ev["overall"]) * 10.0)  # scale 1-10 to 100
        if eval_scores:
            avg_interview = sum(eval_scores) / len(eval_scores)
            components["interview_readiness"] = {
                "name": "Interview Readiness",
                "score": round(avg_interview, 1),
                "confidence": "Medium",
                "evidence": f"Evaluated across {len(eval_scores)} mock interview question responses.",
                "last_updated": now,
            }
        else:
            components["interview_readiness"] = {
                "name": "Interview Readiness",
                "score": 0.0,
                "confidence": "Insufficient evidence",
                "evidence": "Practice mock technical and behavioral rounds.",
                "last_updated": now,
            }
    else:
        components["interview_readiness"] = {
            "name": "Interview Readiness",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "Practice mock technical and behavioral rounds.",
            "last_updated": now,
        }

    # 6. Target JD Match (Weight 10%)
    if jd_match_ratio is not None:
        jd_score = round(jd_match_ratio * 100.0, 1)
        components["target_jd_match"] = {
            "name": "Target JD Match",
            "score": jd_score,
            "confidence": "High",
            "evidence": f"Semantic role requirement coverage is {jd_score:.1f}%.",
            "last_updated": now,
        }
    else:
        components["target_jd_match"] = {
            "name": "Target JD Match",
            "score": 0.0,
            "confidence": "Insufficient evidence",
            "evidence": "Supply a target job description to measure direct fit.",
            "last_updated": now,
        }

    # Calculate overall weighted average considering active components
    active_weight_sum = 0.0
    weighted_score_sum = 0.0

    for key, weight in READINESS_WEIGHTS.items():
        comp = components[key]
        if comp["confidence"] != "Insufficient evidence":
            active_weight_sum += weight
            weighted_score_sum += comp["score"] * weight

    if active_weight_sum > 0:
        overall = round(weighted_score_sum / active_weight_sum, 1)
        confidence = "High" if active_weight_sum >= 0.7 else "Medium"
    else:
        overall = 0.0
        confidence = "Insufficient evidence"

    return {
        "overall_score": overall,
        "confidence": confidence,
        "components": components,
    }
