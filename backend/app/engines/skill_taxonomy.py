from typing import Dict, List, Optional, Set, Tuple

CANONICAL_TAXONOMY: Dict[str, Dict] = {
    "Python": {
        "category": "Languages",
        "aliases": ["python", "python3", "py"],
        "related": ["Django", "FastAPI", "Flask", "Pandas", "NumPy"]
    },
    "JavaScript": {
        "category": "Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6"],
        "related": ["TypeScript", "React", "Node.js", "Express.js", "Next.js"]
    },
    "TypeScript": {
        "category": "Languages",
        "aliases": ["typescript", "ts"],
        "related": ["JavaScript", "React", "Node.js", "Angular", "Next.js"]
    },
    "Java": {
        "category": "Languages",
        "aliases": ["java", "jdk", "jvm"],
        "related": ["Spring", "Spring Boot", "Hibernate", "Kotlin"]
    },
    "C++": {
        "category": "Languages",
        "aliases": ["c++", "cpp"],
        "related": ["C", "Data Structures", "Algorithms", "Embedded Systems"]
    },
    "Go": {
        "category": "Languages",
        "aliases": ["go", "golang"],
        "related": ["Docker", "Kubernetes", "Microservices", "gRPC"]
    },
    "SQL": {
        "category": "Databases",
        "aliases": ["sql", "rdbms", "relational database"],
        "related": ["PostgreSQL", "MySQL", "SQLite"]
    },
    "PostgreSQL": {
        "category": "Databases",
        "aliases": ["postgres", "postgresql", "psql"],
        "related": ["SQL", "MySQL", "Redis", "Database Indexing"]
    },
    "MySQL": {
        "category": "Databases",
        "aliases": ["mysql", "mariadb"],
        "related": ["SQL", "PostgreSQL", "Redis"]
    },
    "MongoDB": {
        "category": "Databases",
        "aliases": ["mongo", "mongodb", "nosql"],
        "related": ["Mongoose", "NoSQL", "Document DB"]
    },
    "Redis": {
        "category": "Databases",
        "aliases": ["redis", "in-memory cache", "cache"],
        "related": ["Caching", "Message Queue", "PostgreSQL"]
    },
    "FastAPI": {
        "category": "Frameworks",
        "aliases": ["fastapi", "fast-api"],
        "related": ["Python", "Pydantic", "Starlette", "Django", "Flask", "REST API"]
    },
    "Django": {
        "category": "Frameworks",
        "aliases": ["django", "django rest framework", "drf"],
        "related": ["Python", "FastAPI", "Flask", "ORM", "REST API"]
    },
    "Flask": {
        "category": "Frameworks",
        "aliases": ["flask"],
        "related": ["Python", "FastAPI", "Django"]
    },
    "React": {
        "category": "Frameworks",
        "aliases": ["react", "react.js", "reactjs"],
        "related": ["JavaScript", "TypeScript", "Redux", "Next.js", "HTML", "CSS"]
    },
    "Next.js": {
        "category": "Frameworks",
        "aliases": ["next.js", "nextjs", "next"],
        "related": ["React", "TypeScript", "SSR", "Server Components"]
    },
    "Node.js": {
        "category": "Frameworks",
        "aliases": ["node", "node.js", "nodejs"],
        "related": ["Express.js", "JavaScript", "TypeScript", "NestJS"]
    },
    "Express.js": {
        "category": "Frameworks",
        "aliases": ["express", "express.js", "expressjs"],
        "related": ["Node.js", "REST API", "JavaScript"]
    },
    "Docker": {
        "category": "DevOps & Cloud",
        "aliases": ["docker", "container", "containers", "dockerfile", "containerization"],
        "related": ["Kubernetes", "CI/CD", "Linux", "Microservices"]
    },
    "Kubernetes": {
        "category": "DevOps & Cloud",
        "aliases": ["k8s", "kubernetes"],
        "related": ["Docker", "Cloud", "Microservices", "Helm"]
    },
    "AWS": {
        "category": "DevOps & Cloud",
        "aliases": ["aws", "amazon web services", "s3", "ec2", "lambda"],
        "related": ["Cloud", "Docker", "DevOps"]
    },
    "CI/CD": {
        "category": "DevOps & Cloud",
        "aliases": ["ci/cd", "ci-cd", "github actions", "gitlab ci", "jenkins"],
        "related": ["Docker", "Git", "DevOps"]
    },
    "Git": {
        "category": "Tools",
        "aliases": ["git", "github", "gitlab", "version control"],
        "related": ["CI/CD"]
    },
    "REST API": {
        "category": "Architecture",
        "aliases": ["rest", "restful", "rest api", "apis", "api design"],
        "related": ["FastAPI", "Django", "GraphQL", "Microservices", "HTTP"]
    },
    "System Design": {
        "category": "Architecture",
        "aliases": ["system design", "distributed systems", "high availability", "scalability", "load balancing"],
        "related": ["Microservices", "Caching", "Redis", "Database Indexing"]
    },
    "Microservices": {
        "category": "Architecture",
        "aliases": ["microservices", "microservice architecture", "event driven"],
        "related": ["System Design", "Docker", "Kubernetes", "REST API", "gRPC"]
    },
    "Data Structures & Algorithms": {
        "category": "DSA",
        "aliases": ["dsa", "data structures", "algorithms", "problem solving"],
        "related": ["Arrays", "Two Pointers", "Hashing", "Binary Search", "Dynamic Programming"]
    },
    "Arrays": {
        "category": "DSA",
        "aliases": ["arrays", "array manipulation"],
        "related": ["Two Pointers", "Sliding Window", "Data Structures & Algorithms"]
    },
    "Two Pointers": {
        "category": "DSA",
        "aliases": ["two pointer", "two pointers"],
        "related": ["Arrays", "Sliding Window"]
    },
    "Hashing": {
        "category": "DSA",
        "aliases": ["hash map", "hash table", "hashmap", "hashing", "dictionary"],
        "related": ["Arrays", "Data Structures & Algorithms"]
    },
    "Binary Search": {
        "category": "DSA",
        "aliases": ["binary search", "bsearch"],
        "related": ["Arrays", "Algorithms"]
    },
    "Dynamic Programming": {
        "category": "DSA",
        "aliases": ["dynamic programming", "dp", "memoization"],
        "related": ["Algorithms", "Recursion"]
    },
    "Linux": {
        "category": "Systems",
        "aliases": ["linux", "unix", "bash", "shell scripting"],
        "related": ["Docker", "DevOps"]
    },
    "Testing": {
        "category": "Quality",
        "aliases": ["pytest", "jest", "unit testing", "integration testing", "tdd", "testing"],
        "related": ["Python", "JavaScript", "CI/CD"]
    }
}


# Pre-build inverted alias lookup for fast normalized lookups
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, data in CANONICAL_TAXONOMY.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in data.get("aliases", []):
        ALIAS_TO_CANONICAL[alias.lower()] = canonical


def normalize_skill(skill_name: str) -> str:
    """Returns canonical skill name if recognized, or cleans and returns title-cased name."""
    clean = skill_name.strip()
    clean_lower = clean.lower()
    if clean_lower in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[clean_lower]
    return clean.title()


def get_skill_category(canonical_skill: str) -> str:
    if canonical_skill in CANONICAL_TAXONOMY:
        return CANONICAL_TAXONOMY[canonical_skill]["category"]
    return "General"


def are_skills_related(skill_a: str, skill_b: str) -> bool:
    """Checks if skill_a and skill_b belong to related technology clusters."""
    can_a = normalize_skill(skill_a)
    can_b = normalize_skill(skill_b)
    if can_a == can_b:
        return True
    data_a = CANONICAL_TAXONOMY.get(can_a)
    if data_a and can_b in data_a.get("related", []):
        return True
    data_b = CANONICAL_TAXONOMY.get(can_b)
    if data_b and can_a in data_b.get("related", []):
        return True
    # If same category, considered related/transferable
    cat_a = get_skill_category(can_a)
    cat_b = get_skill_category(can_b)
    if cat_a != "General" and cat_a == cat_b:
        return True
    return False
