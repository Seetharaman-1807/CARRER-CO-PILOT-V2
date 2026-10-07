from typing import Dict, List, Any
from app.engines.jd_matcher import classify_skill_match
from app.engines.skill_taxonomy import normalize_skill


def analyze_skill_gaps(
    candidate_skills: List[Dict[str, Any]],
    candidate_raw_text: str,
    jd_required_skills: List[str],
    jd_preferred_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Computes candidate skill gaps against target role / JD requirements.
    Prioritizes gaps based on role importance, candidate weakness, and interview frequency.
    """
    if jd_preferred_skills is None:
        jd_preferred_skills = []

    # Map candidate skills by canonical name
    cand_dict: Dict[str, Dict[str, Any]] = {}
    for cs in candidate_skills:
        cname = normalize_skill(cs.get("canonical_name", cs.get("skill", "")))
        cand_dict[cname] = cs

    gap_items: List[Dict[str, Any]] = []
    missing_count = 0
    weak_count = 0
    exact_count = 0
    related_count = 0

    all_target_skills = [(s, 1.0) for s in jd_required_skills] + [(s, 0.6) for s in jd_preferred_skills]

    for req_skill, importance in all_target_skills:
        match_info = classify_skill_match(req_skill, cand_dict, candidate_raw_text)
        status = match_info["status"]
        cand_score = match_info["candidate_score"]

        # Calculate Priority: Importance (1.0 or 0.6) * Weakness (1.0 - cand_score/100)
        weakness_factor = max(0.0, 1.0 - (cand_score / 100.0))
        priority_numeric = importance * weakness_factor

        if priority_numeric >= 0.65:
            priority_label = "High"
        elif priority_numeric >= 0.35:
            priority_label = "Medium"
        else:
            priority_label = "Low"

        if status == "exact":
            exact_count += 1
        elif status == "related":
            related_count += 1
        elif status == "partial":
            weak_count += 1
        else:
            missing_count += 1

        gap_items.append({
            "skill": req_skill,
            "canonical_skill": match_info["canonical_skill"],
            "status": status,
            "importance": importance,
            "candidate_score": cand_score,
            "reason": match_info["reason"],
            "priority": priority_label,
            "_priority_score": round(priority_numeric, 2)
        })

    # Sort gaps by priority score descending
    gap_items.sort(key=lambda x: x["_priority_score"], reverse=True)

    summary = {
        "total_requirements": len(all_target_skills),
        "exact_matches": exact_count,
        "related_matches": related_count,
        "weak_matches": weak_count,
        "missing_skills": missing_count,
        "high_priority_gaps": [g["canonical_skill"] for g in gap_items if g["priority"] == "High"]
    }

    return {
        "gaps": gap_items,
        "summary": summary
    }
