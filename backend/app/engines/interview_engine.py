import re
from typing import Dict, List, Any, Optional

ROLE_QUESTION_BANKS = {
    "Backend Developer": [
        {
            "id": "be-q1",
            "category": "technical",
            "focus_skill": "REST API",
            "question": "How do you handle idempotency in RESTful APIs, especially for POST and PATCH operations?",
            "keywords": ["idempotent", "token", "header", "database", "uuid", "retry", "state"]
        },
        {
            "id": "be-q2",
            "category": "technical",
            "focus_skill": "PostgreSQL",
            "question": "Explain the difference between clustered and non-clustered indexes, and how indexing affects write vs read latency.",
            "keywords": ["b-tree", "disk", "write overhead", "lookup", "query", "scan", "leaf nodes"]
        },
        {
            "id": "be-q3",
            "category": "technical",
            "focus_skill": "System Design",
            "question": "How would you design a distributed rate limiter that handles 100,000 requests per second across multiple API gateway nodes?",
            "keywords": ["token bucket", "leaky bucket", "redis", "sliding window", "distributed", "concurrency"]
        },
        {
            "id": "be-q4",
            "category": "behavioral",
            "focus_skill": "Problem Solving",
            "question": "Describe a production incident or bug you diagnosed under high pressure. How did you identify the root cause and prevent recurrence?",
            "keywords": ["logs", "monitoring", "root cause", "postmortem", "rollback", "alert"]
        }
    ],
    "Software Engineer": [
        {
            "id": "se-q1",
            "category": "technical",
            "focus_skill": "Data Structures & Algorithms",
            "question": "When would you choose a Hash Table over a Balanced Binary Search Tree (like an AVL or Red-Black tree)?",
            "keywords": ["o(1)", "o(log n)", "collision", "ordering", "range query", "worst case"]
        },
        {
            "id": "se-q2",
            "category": "technical",
            "focus_skill": "Docker",
            "question": "What is the difference between a container and a virtual machine, and how do multi-stage Docker builds reduce attack surfaces and image size?",
            "keywords": ["kernel", "hypervisor", "namespace", "cgroups", "layers", "build stage", "minimal"]
        },
        {
            "id": "se-q3",
            "category": "behavioral",
            "focus_skill": "Team Collaboration",
            "question": "Tell me about a time you strongly disagreed with a peer's technical architecture decision. How did you resolve the conflict?",
            "keywords": ["trade-offs", "data", "benchmark", "discussion", "consensus", "compromise"]
        }
    ]
}


def get_interview_questions_for_role(role_name: str, session_type: str = "technical") -> List[Dict[str, Any]]:
    # Find matching bank or fallback to Software Engineer
    bank = ROLE_QUESTION_BANKS.get(role_name, ROLE_QUESTION_BANKS["Software Engineer"])
    if session_type == "behavioral":
        filtered = [q for q in bank if q["category"] == "behavioral"]
        if filtered:
            return filtered
    return bank


def evaluate_interview_response(
    question_data: Dict[str, Any],
    user_response: str
) -> Dict[str, Any]:
    """
    Evaluates interview response using rubric criteria:
    - Technical Accuracy (1-10)
    - Clarity & Structure (1-10)
    - Technical Depth (1-10)
    - Overall Score (1-10)
    Generates actionable feedback and skill evidence.
    """
    response_clean = user_response.strip()
    words = len(response_clean.split())
    keywords = question_data.get("keywords", [])
    matched_keywords = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", response_clean, re.I)]
    
    # 1. Depth & Length rubric
    if words < 20:
        depth_score = 3.0
        clarity_score = 4.0
    elif words < 50:
        depth_score = 5.5
        clarity_score = 6.5
    elif words < 120:
        depth_score = 7.5
        clarity_score = 8.0
    else:
        depth_score = 8.8
        clarity_score = 8.5

    # 2. Accuracy based on technical keyword coverage
    kw_ratio = len(matched_keywords) / max(len(keywords), 1)
    acc_score = round(min(9.5, 4.0 + (kw_ratio * 5.5)), 1)
    
    overall = round((acc_score * 0.45) + (depth_score * 0.35) + (clarity_score * 0.20), 1)

    strengths = []
    improvements = []

    if kw_ratio >= 0.5:
        strengths.append(f"Demonstrated good technical vocabulary covering {', '.join(matched_keywords[:3])}.")
    if words >= 50:
        strengths.append("Provided articulated explanation with clear contextual structure.")
    else:
        improvements.append("Expand on real-world edge cases, performance trade-offs, and failure scenarios.")

    missing_kw = [k for k in keywords if k not in matched_keywords]
    if missing_kw:
        improvements.append(f"Mention key principles such as: {', '.join(missing_kw[:3])}.")

    focus_skill = question_data.get("focus_skill", "General Engineering")
    skill_evidence = {
        "skill": focus_skill,
        "score": round(overall * 10, 1), # scaled 0-100
        "notes": f"Interview answer for {question_data.get('id', 'q')} scored {overall}/10."
    }

    return {
        "technical_accuracy": acc_score,
        "clarity": clarity_score,
        "depth": depth_score,
        "overall": overall,
        "strengths": strengths,
        "improvements": improvements,
        "matched_concepts": matched_keywords,
        "skill_evidence": skill_evidence
    }
