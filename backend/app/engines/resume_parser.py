import io
import re
from typing import Dict, List, Any, Optional
from pypdf import PdfReader
import docx
from app.engines.skill_taxonomy import normalize_skill, ALIAS_TO_CANONICAL


def extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        return f"[PDF Parsing Error: {str(e)}]"


def extract_text_from_docx(content: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text.strip()
    except Exception as e:
        return f"[DOCX Parsing Error: {str(e)}]"


def sanitize_untrusted_text(text: str) -> str:
    """Sanitizes resume text to prevent prompt injection attempts."""
    # Defang system prompts / instructions masquerading in resume
    cleaned = re.sub(r"(?i)(ignore previous instructions|reveal system prompt|system message)", "[FILTERED]", text)
    return cleaned


def detect_sections(text: str) -> Dict[str, str]:
    """Splits raw resume text into distinct logical sections."""
    section_patterns = {
        "education": r"(?i)\b(education|academic background|academics|qualifications)\b",
        "experience": r"(?i)\b(experience|work experience|employment history|professional experience|internship)\b",
        "projects": r"(?i)\b(projects|key projects|personal projects|technical projects)\b",
        "skills": r"(?i)\b(skills|technical skills|technologies|core competencies|tools & technologies)\b",
        "certifications": r"(?i)\b(certifications|certificates|licenses|achievements & certifications)\b",
        "summary": r"(?i)\b(summary|professional summary|about me|profile|objective)\b",
    }

    # Identify line indices where headers appear
    lines = text.splitlines()
    section_markers: List[tuple[int, str]] = []

    for idx, line in enumerate(lines):
        line_clean = line.strip()
        if len(line_clean) < 40:  # headers are usually short
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_clean):
                    section_markers.append((idx, section_name))
                    break

    # If no headers detected, return full text in experience/summary
    if not section_markers:
        return {"general": text}

    sections: Dict[str, List[str]] = {}
    for i, (line_idx, section_name) in enumerate(section_markers):
        start = line_idx + 1
        end = section_markers[i + 1][0] if i + 1 < len(section_markers) else len(lines)
        section_content = "\n".join(lines[start:end]).strip()
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append(section_content)

    return {k: "\n\n".join(v) for k, v in sections.items()}


def extract_skills_with_evidence(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extracts skills from text with exact supporting evidence and confidence."""
    extracted: Dict[str, Dict[str, Any]] = {}

    # Check each section
    for section_name, section_text in sections.items():
        lines = section_text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Look for alias matches
            lower_line = line_str.lower()
            for alias, canonical in ALIAS_TO_CANONICAL.items():
                # Word boundary match
                pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
                if re.search(pattern, lower_line):
                    # Higher confidence if found in Skills or Projects section
                    confidence = 0.95 if section_name in ("skills", "projects") else 0.85
                    
                    if canonical not in extracted:
                        extracted[canonical] = {
                            "skill": canonical,
                            "canonical": canonical,
                            "evidence": line_str[:250],
                            "source_section": section_name.capitalize(),
                            "confidence": confidence,
                        }
                    else:
                        # If existing evidence was general, update with specific project evidence
                        if section_name == "projects" and extracted[canonical]["source_section"] != "Projects":
                            extracted[canonical]["evidence"] = line_str[:250]
                            extracted[canonical]["source_section"] = "Projects"
                            extracted[canonical]["confidence"] = 0.95

    return list(extracted.values())


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    
    first_few_lines = [l.strip() for l in text.splitlines()[:5] if l.strip()]
    candidate_name = first_few_lines[0] if first_few_lines else "Candidate"
    
    return {
        "name": candidate_name[:60],
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def extract_measurable_achievements(text: str) -> List[str]:
    """Finds bullet points containing quantifiable metrics (%, numbers, scale)."""
    achievements = []
    lines = text.splitlines()
    metric_pattern = re.compile(r"(\b\d+%\b|\b\d+x\b|\b\$\d+|\b\d+\+?\s*(users|requests|ms|seconds|million|thousand|k|reduction|increase|improved))", re.I)

    for line in lines:
        cleaned = line.strip()
        if (cleaned.startswith(("-", "•", "*")) or len(cleaned) > 20) and metric_pattern.search(cleaned):
            achievements.append(cleaned)
            if len(achievements) >= 8:
                break
    return achievements


def parse_resume_content(raw_text: str) -> Dict[str, Any]:
    """Complete parsing pipeline returning structured, evidence-backed candidate data."""
    sanitized = sanitize_untrusted_text(raw_text)
    sections = detect_sections(sanitized)
    skills = extract_skills_with_evidence(sanitized, sections)
    contact = extract_contact_info(sanitized)
    achievements = extract_measurable_achievements(sanitized)

    # Basic structured sections
    education_entries = [e.strip() for e in sections.get("education", "").split("\n\n") if e.strip()]
    project_entries = [p.strip() for p in sections.get("projects", "").split("\n\n") if p.strip()]
    experience_entries = [x.strip() for x in sections.get("experience", "").split("\n\n") if x.strip()]

    return {
        "contact": contact,
        "summary": sections.get("summary", ""),
        "education": education_entries,
        "experience": experience_entries,
        "projects": project_entries,
        "skills": skills,
        "certifications": [c.strip() for c in sections.get("certifications", "").split("\n\n") if c.strip()],
        "achievements": achievements,
        "sections_found": list(sections.keys()),
    }
