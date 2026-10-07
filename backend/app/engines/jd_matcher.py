import re
from typing import Dict, List, Any, Optional
from app.engines.skill_taxonomy import normalize_skill, are_skills_related, ALIAS_TO_CANONICAL


def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """Extracts required skills, preferred skills, role title, and responsibilities from JD."""
    lines = jd_text.splitlines()
    title = "Software Engineer"
    
    # Try detecting title from first few lines
    for line in lines[:3]:
        cleaned = line.strip()
        if cleaned and len(cleaned) < 50:
            title = cleaned
            break

    # Extract skills mentioned in JD
    detected_skills = set()
    lower_text = jd_text.lower()
    for alias, canonical in ALIAS_TO_CANONICAL.items():
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        if re.search(pattern, lower_text):
            detected_skills.add(canonical)

    skills_list = list(detected_skills)
    
    # Differentiate required vs preferred based on proximity to phrases
    required = []
    preferred = []
    for skill in skills_list:
        # Check if mentioned near "preferred", "nice to have", "plus"
        pattern = rf"(?i)(preferred|nice to have|plus|bonus).{{1,80}}\b{re.escape(skill)}\b"
        if re.search(pattern, jd_text):
            preferred.append(skill)
        else:
            required.append(skill)

    if not required and skills_list:
        required = skills_list[:5]
        preferred = skills_list[5:]

    return {
        "title": title,
        "required_skills": required,
        "preferred_skills": preferred,
        "all_skills": skills_list,
        "raw_text_length": len(jd_text),
    }


def classify_skill_match(
    required_skill: str,
    candidate_skills_dict: Dict[str, Dict[str, Any]],
    candidate_raw_text: str
) -> Dict[str, Any]:
    """
    Classifies resume-to-JD relationship as:
    1. Exact match
    2. Related/transferable match
    3. Partial evidence
    4. Missing
    5. Ambiguous
    """
    canonical_req = normalize_skill(required_skill)
    
    # 1. Exact match
    if canonical_req in candidate_skills_dict:
        cand_data = candidate_skills_dict[canonical_req]
        score = cand_data.get("score", 50.0)
        confidence = cand_data.get("confidence", "Medium")
        if score < 40.0:
            return {
                "skill": required_skill,
                "canonical_skill": canonical_req,
                "status": "partial",
                "candidate_score": score,
                "reason": f"Directly mentioned, but performance/evidence score is low ({score:.0f}/100)."
            }
        return {
            "skill": required_skill,
            "canonical_skill": canonical_req,
            "status": "exact",
            "candidate_score": score,
            "reason": f"Demonstrated {canonical_req} competency with verified evidence."
        }

    # 2. Related / Transferable match
    for cand_skill, cand_data in candidate_skills_dict.items():
        if are_skills_related(canonical_req, cand_skill):
            score = cand_data.get("score", 50.0)
            return {
                "skill": required_skill,
                "canonical_skill": canonical_req,
                "status": "related",
                "candidate_score": max(25.0, score * 0.65),
                "reason": f"Demonstrated related experience in {cand_skill}; direct {canonical_req} evidence absent."
            }

    # 3. Check if raw text mentions it shallowly without full extraction
    lower_raw = candidate_raw_text.lower()
    if re.search(r"(?<!\w)" + re.escape(required_skill.lower()) + r"(?!\w)", lower_raw):
        return {
            "skill": required_skill,
            "canonical_skill": canonical_req,
            "status": "partial",
            "candidate_score": 30.0,
            "reason": f"Mentioned in resume text without detailed project or assessment depth."
        }

    # 4. Missing
    return {
        "skill": required_skill,
        "canonical_skill": canonical_req,
        "status": "missing",
        "candidate_score": 0.0,
        "reason": f"No direct or transferable evidence found for {canonical_req}."
    }
