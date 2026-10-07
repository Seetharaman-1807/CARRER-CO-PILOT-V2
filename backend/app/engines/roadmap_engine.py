from typing import Dict, List, Any
from app.engines.skill_taxonomy import normalize_skill


def generate_adaptive_roadmap(
    role_name: str,
    top_gaps: List[Dict[str, Any]],
    candidate_skills: List[Dict[str, Any]],
    available_hours: int = 10
) -> Dict[str, Any]:
    """
    Constructs a personalized multi-week learning plan and actionable roadmap tasks.
    Adapts based on current high-priority gaps.
    """
    tasks_to_create = []

    # Priority 1: Address High and Medium priority skill gaps
    gap_skills = [g.get("canonical_skill", g.get("skill")) for g in top_gaps[:4]]
    
    # If no gaps provided, focus on foundational role pillars
    if not gap_skills:
        if "Backend" in role_name:
            gap_skills = ["FastAPI", "PostgreSQL", "Docker", "System Design"]
        else:
            gap_skills = ["Data Structures & Algorithms", "SQL", "Docker", "System Design"]

    # Generate Weekly plan
    weekly_plan = [
        {
            "week": 1,
            "focus": f"Core Foundations: {gap_skills[0]} & DSA Patterns",
            "goals": [f"Deep dive into {gap_skills[0]} fundamentals", "Solve 5 array & hashing problems"]
        },
        {
            "week": 2,
            "focus": f"Architecture & Persistence: {gap_skills[1] if len(gap_skills) > 1 else 'SQL & APIs'}",
            "goals": ["Build a CRUD microservice with indexing", "Conduct mock technical interview"]
        },
        {
            "week": 3,
            "focus": f"DevOps & Containerization: {gap_skills[2] if len(gap_skills) > 2 else 'Docker & CI/CD'}",
            "goals": ["Containerize multi-container app", "Setup automated test pipelines"]
        },
        {
            "week": 4,
            "focus": "Comprehensive Interview Readiness & System Design",
            "goals": ["End-to-end full system architecture interview", "Final resume tailoring for target roles"]
        }
    ]

    # Generate specific roadmap tasks
    for idx, skill in enumerate(gap_skills):
        priority = "High" if idx < 2 else "Medium"
        tasks_to_create.append({
            "skill_name": skill,
            "title": f"Master {skill} Core Principles & Practical Implementation",
            "description": f"Study official documentation, implement a working prototype, and document architecture decisions for {skill}.",
            "priority": priority,
            "estimated_minutes": 60,
            "completion_criteria": f"Write an implementation snippet and test case demonstrating hands-on proficiency in {skill}."
        })

    # Always include a DSA practice milestone
    tasks_to_create.append({
        "skill_name": "Data Structures & Algorithms",
        "title": "Complete 2 Two-Pointer & Hashing DSA Challenges",
        "description": "Solve algorithm challenges with optimal O(n) time and O(n) space complexity without using hints.",
        "priority": "High",
        "estimated_minutes": 45,
        "completion_criteria": "Pass all visible and edge-case unit tests in the DSA practice console."
    })

    # Always include a Mock Interview milestone
    tasks_to_create.append({
        "skill_name": "REST API",
        "title": "Complete Live Technical Mock Interview Round",
        "description": "Participate in a simulated technical interview covering distributed architectures and backend reliability.",
        "priority": "Medium",
        "estimated_minutes": 30,
        "completion_criteria": "Achieve an overall rubric score of 7.0/10 or higher across technical accuracy and clarity."
    })

    return {
        "title": f"Targeted {role_name} Career Acceleration Roadmap",
        "goal": f"Reach 85+ Career Readiness for {role_name} within 4 weeks at {available_hours} hrs/week.",
        "weekly_plan": weekly_plan,
        "tasks": tasks_to_create
    }


def generate_daily_plan(tasks: List[Dict[str, Any]], top_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates 3 to 5 high-impact actionable items for 'What should I do today?'.
    """
    daily = []
    
    # 1. DSA task
    daily.append({
        "task": "Solve 1 Hashing or Two-Pointer DSA Problem",
        "reason": "Reinforces algorithmic problem-solving speed and space-time optimization.",
        "skill": "Data Structures & Algorithms",
        "estimated_time": "25 mins",
        "priority": "High",
        "completion_criteria": "Submit working Python code passing 100% of test cases."
    })

    # 2. Top Gap Skill study
    gap_skill = top_gaps[0].get("canonical_skill", "System Design") if top_gaps else "System Design"
    daily.append({
        "task": f"Complete hands-on exercise for {gap_skill}",
        "reason": f"Identified as your highest priority gap for your target role.",
        "skill": gap_skill,
        "estimated_time": "35 mins",
        "priority": "High",
        "completion_criteria": f"Implement a mini service or configuration using {gap_skill}."
    })

    # 3. Resume / Project improvement
    daily.append({
        "task": "Review Project Metrics in Resume V1",
        "reason": "Measurable metrics (throughput, latency, users) boost ATS and recruiter engagement by 40%.",
        "skill": "Resume Optimization",
        "estimated_time": "20 mins",
        "priority": "Medium",
        "completion_criteria": "Add at least 2 quantifiable achievements to your project descriptions."
    })

    # 4. Mock interview quick check
    daily.append({
        "task": "Conduct a 15-minute Mock Interview Session",
        "reason": "Validates ability to clearly articulate design trade-offs under timed conditions.",
        "skill": "Technical Communication",
        "estimated_time": "15 mins",
        "priority": "Medium",
        "completion_criteria": "Complete at least 2 technical questions with structured explanations."
    })

    return daily
