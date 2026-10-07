from app.engines.dsa_engine import (
    inspect_code_safety,
    execute_dsa_solution,
    CURATED_DSA_PROBLEMS,
)


def test_dsa_security_inspection_blocks_unsafe_code():
    unsafe_import = "import os\ndef two_sum(nums, target):\n    return [0, 1]"
    assert inspect_code_safety(unsafe_import) is not None
    assert "os" in inspect_code_safety(unsafe_import)

    unsafe_call = "def two_sum(nums, target):\n    open('/etc/passwd')\n    return [0, 1]"
    assert inspect_code_safety(unsafe_call) is not None
    assert "open" in inspect_code_safety(unsafe_call)


def test_dsa_execution_passing_solution():
    two_sum_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    problem = CURATED_DSA_PROBLEMS[0]  # Two Sum
    res = execute_dsa_solution(two_sum_code, problem["test_cases"])

    assert res["passed"] is True
    assert res["passed_count"] == len(problem["test_cases"])
    assert res["error"] is None
    assert res["runtime_ms"] > 0.0


def test_dsa_execution_failing_solution():
    broken_code = """
def two_sum(nums, target):
    return [0, 0]
"""
    problem = CURATED_DSA_PROBLEMS[0]  # Two Sum
    res = execute_dsa_solution(broken_code, problem["test_cases"])

    assert res["passed"] is False
    assert res["passed_count"] < len(problem["test_cases"])
