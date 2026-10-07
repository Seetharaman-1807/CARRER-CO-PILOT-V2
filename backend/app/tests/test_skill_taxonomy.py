from app.engines.skill_taxonomy import (
    normalize_skill,
    get_skill_category,
    are_skills_related,
)


def test_skill_aliases_normalization():
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("postgresql") == "PostgreSQL"
    assert normalize_skill("fastapi") == "FastAPI"
    assert normalize_skill("fast-api") == "FastAPI"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("js") == "JavaScript"


def test_skill_categories():
    assert get_skill_category("Python") == "Languages"
    assert get_skill_category("PostgreSQL") == "Databases"
    assert get_skill_category("FastAPI") == "Frameworks"
    assert get_skill_category("Docker") == "DevOps & Cloud"
    assert get_skill_category("Binary Search") == "DSA"


def test_related_skills_detection():
    # Django and FastAPI are related backend frameworks
    assert are_skills_related("FastAPI", "Django") is True
    # PostgreSQL and MySQL are relational databases
    assert are_skills_related("PostgreSQL", "MySQL") is True
    # Python and Docker are in different categories, not direct relations
    assert are_skills_related("Python", "Docker") is False
