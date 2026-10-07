import re
from typing import Dict, List, Any, Set
from app.engines.skill_taxonomy import normalize_skill, are_skills_related


# Configurable weights as defined in PRD Section 6
ATS_WEIGHTS = {
    "keyword_match": 0.25,
    "technical_skill_match": 0.25,
    "experience_match": 0.15,
    "education_match": 0.10,
    "project_relevance": 0.10,
    "formatting": 0.10,
    "section_completeness": 0.05,
}


def extract_keywords_from_jd(jd_text: str) -> List[str]:
    """Extracts significant keywords and skill mentions from JD."""
    stop_words = {
        "and", "the", "in", "of", "to", "a", "with", "for", "on", "as", "by", "at", "an",
        "be", "is", "are", "from", "that", "this", "or", "you", "will", "our", "team",
        "we", "work", "experience", "years", "candidate", "role", "looking", "working"
    }
    words = re.findall(r"\b[A-Za-z0-9#\+\.\-]{2,}\b", jd_text.lower())
    keyword_freq: Dict[str, int] = {}
    for w in words:
        if w not in stop_words and len(w) > 2:
            keyword_freq[w] = keyword_freq.get(w, 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    return [k for k, _ in sorted_keywords[:40]]


def calculate_ats_score(
    resume_parsed: Dict[str, Any],
    resume_raw_text: str,
    jd_text: str,
    jd_required_skills: List[str]
) -> Dict[str, Any]:
    """
    Computes deterministic ATS score with 7 components (total 100).
    Never modifies numbers via arbitrary LLM hallucinations.
    """
    raw_lower = resume_raw_text.lower()
    
    # 1. Keyword Match (25 max)
    jd_keywords = extract_keywords_from_jd(jd_text)
    if jd_keywords:
        matched_keywords = [kw for kw in jd_keywords if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", raw_lower)]
        keyword_ratio = min(1.0, len(matched_keywords) / max(len(jd_keywords), 1))
    else:
        matched_keywords = []
        keyword_ratio = 0.8
    score_keyword = round(keyword_ratio * 100 * ATS_WEIGHTS["keyword_match"], 1)

    # 2. Technical Skill Match (25 max)
    resume_skills = [s.get("canonical", s.get("skill")) for s in resume_parsed.get("skills", [])]
    resume_canonical_set = {normalize_skill(s) for s in resume_skills}
    
    exact_matches: List[str] = []
    related_matches: List[str] = []
    missing_skills: List[str] = []

    if jd_required_skills:
        for req_skill in jd_required_skills:
            can_req = normalize_skill(req_skill)
            if can_req in resume_canonical_set:
                exact_matches.append(can_req)
            elif any(are_skills_related(can_req, cand_s) for cand_s in resume_canonical_set):
                related_matches.append(can_req)
            else:
                missing_skills.append(can_req)
        
        # Exact = 1.0, Related = 0.65
        total_req = len(jd_required_skills)
        effective_match = len(exact_matches) + (len(related_matches) * 0.65)
        skill_ratio = min(1.0, effective_match / max(total_req, 1))
    else:
        skill_ratio = min(1.0, len(resume_canonical_set) / 10)
    score_tech_skills = round(skill_ratio * 100 * ATS_WEIGHTS["technical_skill_match"], 1)

    # 3. Experience Match (15 max)
    # Check for years of experience or depth in experience section
    exp_entries = resume_parsed.get("experience", [])
    exp_text = " ".join(exp_entries).lower()
    has_experience_section = bool(exp_entries)
    
    # Detect year mentions
    years_detected = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)\b", raw_lower)
    max_years = max([int(y) for y in years_detected], default=0)
    
    exp_ratio = 0.5  # default baseline
    if has_experience_section:
        exp_ratio += 0.3
    if len(exp_entries) >= 2 or max_years >= 2:
        exp_ratio += 0.2
    exp_ratio = min(1.0, exp_ratio)
    score_experience = round(exp_ratio * 100 * ATS_WEIGHTS["experience_match"], 1)

    # 4. Education Match (10 max)
    edu_entries = resume_parsed.get("education", [])
    edu_ratio = 0.5
    edu_text = " ".join(edu_entries).lower()
    degree_keywords = ["bachelor", "b.tech", "b.e", "master", "m.tech", "ms", "bs", "computer science", "engineering"]
    if edu_entries:
        edu_ratio += 0.3
    if any(k in edu_text for k in degree_keywords):
        edu_ratio += 0.2
    edu_ratio = min(1.0, edu_ratio)
    score_education = round(edu_ratio * 100 * ATS_WEIGHTS["education_match"], 1)

    # 5. Project Relevance (10 max)
    project_entries = resume_parsed.get("projects", [])
    proj_ratio = 0.4
    if len(project_entries) >= 1:
        proj_ratio += 0.3
    if len(project_entries) >= 2:
        proj_ratio += 0.3
    # Check if any project mentions required skills
    proj_text = " ".join(project_entries).lower()
    if any(normalize_skill(s).lower() in proj_text for s in jd_required_skills):
        proj_ratio = min(1.0, proj_ratio + 0.1)
    proj_ratio = min(1.0, proj_ratio)
    score_projects = round(proj_ratio * 100 * ATS_WEIGHTS["project_relevance"], 1)

    # 6. Formatting (10 max)
    # Standard format checks: length reasonable, has bullet points, clear lines, no crazy characters
    format_penalties = 0
    if len(raw_lower) < 200:
        format_penalties += 4
    if "\t\t\t\t" in resume_raw_text:
        format_penalties += 1
    if not any(b in resume_raw_text for b in ["•", "-", "*", "\n\n"]):
        format_penalties += 2
    format_score = max(3.0, 10.0 - format_penalties)
    score_formatting = round(format_score, 1)

    # 7. Section Completeness (5 max)
    sections_found = set(resume_parsed.get("sections_found", []))
    standard_sections = {"skills", "education", "experience", "projects"}
    present_count = len(standard_sections.intersection(sections_found))
    completeness_ratio = present_count / len(standard_sections)
    score_completeness = round(completeness_ratio * 100 * ATS_WEIGHTS["section_completeness"], 1)

    # Overall Score (Sum of components)
    overall_score = round(
        score_keyword + score_tech_skills + score_experience +
        score_education + score_projects + score_formatting + score_completeness,
        1
    )

    components = {
        "keyword_match": score_keyword,
        "technical_skill_match": score_tech_skills,
        "experience_match": score_experience,
        "education_match": score_education,
        "project_relevance": score_projects,
        "formatting": score_formatting,
        "section_completeness": score_completeness,
    }

    # Generate actionable explainability feedback
    recommendations = []
    if missing_skills:
        recommendations.append(f"Add direct evidence or project demonstrations for: {', '.join(missing_skills[:5])}")
    if related_matches:
        recommendations.append(f"Transferable experience found ({', '.join(related_matches[:3])}). Clarify if you have hands-on experience in target tools.")
    if score_formatting < 8.0:
        recommendations.append("Enhance bullet point readability and clear section headings for better ATS parser scanning.")
    if not resume_parsed.get("achievements"):
        recommendations.append("Quantify project impacts (e.g., 'improved throughput by 30%', 'reduced query latency').")

    return {
        "overall_score": overall_score,
        "scoring_version": "v2.0-deterministic",
        "components": components,
        "details": {
            "exact_matches": exact_matches,
            "related_matches": related_matches,
            "missing_skills": missing_skills,
            "matched_keywords_count": len(matched_keywords),
            "total_keywords_analyzed": len(jd_keywords),
        },
        "recommendations": recommendations,
    }
