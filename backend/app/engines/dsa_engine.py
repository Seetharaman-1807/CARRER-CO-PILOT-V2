import ast
import time
import sys
from typing import Dict, List, Any, Optional

# Curated high-yield problems across progressive topics
CURATED_DSA_PROBLEMS: List[Dict[str, Any]] = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "topic": "Hashing",
        "difficulty": "Easy",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    pass",
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
        ],
        "hints": [
            "A brute force approach checks all pairs in O(n^2). Can we do better with auxiliary space?",
            "Use a Hash Map (dictionary) to store previously seen numbers and their indices.",
            "For each number, check if (target - num) is already in the dictionary."
        ]
    },
    {
        "title": "Valid Palindrome",
        "slug": "valid-palindrome",
        "topic": "Two Pointers",
        "difficulty": "Easy",
        "description": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.\nGiven a string s, return True if it is a palindrome, or False otherwise.",
        "starter_code": "def is_palindrome(s: str) -> bool:\n    # Write your solution here\n    pass",
        "test_cases": [
            {"input": {"s": "A man, a plan, a canal: Panama"}, "expected": True},
            {"input": {"s": "race a car"}, "expected": False},
            {"input": {"s": " "}, "expected": True},
        ],
        "hints": [
            "Consider using two pointers: one starting from the beginning and one from the end.",
            "Advance pointers past non-alphanumeric characters using .isalnum().",
            "Compare lowercase characters at both pointer positions."
        ]
    },
    {
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "slug": "maximum-subarray",
        "topic": "Arrays",
        "difficulty": "Medium",
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "starter_code": "def max_sub_array(nums):\n    # Write your solution here\n    pass",
        "test_cases": [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [1]}, "expected": 1},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23},
        ],
        "hints": [
            "Think about whether a negative prefix sum helps you find a larger sum.",
            "Kadane's algorithm maintains the current subarray sum and resets it to 0 if it drops below 0.",
            "Keep track of the global maximum sum encountered so far."
        ]
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "topic": "Binary Search",
        "difficulty": "Easy",
        "description": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
        "starter_code": "def search(nums, target):\n    # Write your solution here\n    pass",
        "test_cases": [
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected": 4},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected": -1},
        ],
        "hints": [
            "Because the array is sorted, you can divide the search range in half each step.",
            "Calculate mid = (left + right) // 2.",
            "Adjust left = mid + 1 or right = mid - 1 based on comparison with target."
        ]
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "topic": "Sliding Window",
        "difficulty": "Medium",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "starter_code": "def length_of_longest_substring(s: str) -> int:\n    # Write your solution here\n    pass",
        "test_cases": [
            {"input": {"s": "abcabcbb"}, "expected": 3},
            {"input": {"s": "bbbbb"}, "expected": 1},
            {"input": {"s": "pwwkew"}, "expected": 3},
        ],
        "hints": [
            "Use a sliding window with two pointers representing the current valid substring.",
            "Store characters in a set or dictionary with their latest seen index.",
            "When a duplicate is encountered, advance the left pointer past the first occurrence."
        ]
    }
]


# Security sandbox checker using Python AST analysis
FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "socket", "requests", "shutil", "pathlib", "builtin"}
FORBIDDEN_FUNCTIONS = {"open", "exec", "eval", "compile", "__import__", "getattr", "globals", "locals"}


def inspect_code_safety(code_str: str) -> Optional[str]:
    """Inspects AST to ensure no dangerous operations or unauthorized system calls exist."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return f"Syntax Error: {e.msg} at line {e.lineno}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_IMPORTS:
                    return f"Security Policy Violation: Import of '{alias.name}' is prohibited."
        elif isinstance(node, ast.ImportFrom):
            if node.module in FORBIDDEN_IMPORTS:
                return f"Security Policy Violation: Import from '{node.module}' is prohibited."
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCTIONS:
                return f"Security Policy Violation: Invocation of '{node.func.id}()' is prohibited."

    return None


def execute_dsa_solution(code_str: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes student solution safely against test cases.
    Returns pass/fail status, runtime, test case details, and complexity estimation.
    """
    security_error = inspect_code_safety(code_str)
    if security_error:
        return {
            "passed": False,
            "total": len(test_cases),
            "passed_count": 0,
            "error": security_error,
            "runtime_ms": 0.0,
            "test_results": []
        }

    # Safe execution scope
    safe_globals: Dict[str, Any] = {
        "__builtins__": {
            "range": range, "len": len, "min": min, "max": max, "sum": sum,
            "enumerate": enumerate, "zip": zip, "sorted": sorted, "list": list,
            "dict": dict, "set": set, "tuple": tuple, "int": int, "float": float,
            "str": str, "bool": bool, "abs": abs, "print": lambda *args: None
        }
    }
    local_scope: Dict[str, Any] = {}

    start_time = time.perf_counter()
    try:
        exec(code_str, safe_globals, local_scope)
    except Exception as e:
        return {
            "passed": False,
            "total": len(test_cases),
            "passed_count": 0,
            "error": f"Execution Error: {type(e).__name__}: {str(e)}",
            "runtime_ms": 0.0,
            "test_results": []
        }

    # Find the callable function
    funcs = [v for k, v in local_scope.items() if callable(v) and not k.startswith("_")]
    if not funcs:
        return {
            "passed": False,
            "total": len(test_cases),
            "passed_count": 0,
            "error": "No callable function found in submission.",
            "runtime_ms": 0.0,
            "test_results": []
        }

    target_func = funcs[0]
    test_results = []
    passed_count = 0

    for idx, tc in enumerate(test_cases):
        inputs = tc["input"]
        expected = tc["expected"]
        try:
            actual = target_func(**inputs)
            # Handle list equality without order if needed, but strict comparison first
            is_match = (actual == expected)
            if is_match:
                passed_count += 1
            test_results.append({
                "test_index": idx + 1,
                "input": inputs,
                "expected": expected,
                "actual": actual,
                "passed": is_match
            })
        except Exception as e:
            test_results.append({
                "test_index": idx + 1,
                "input": inputs,
                "expected": expected,
                "actual": f"Error: {str(e)}",
                "passed": False
            })

    total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    all_passed = (passed_count == len(test_cases))

    return {
        "passed": all_passed,
        "total": len(test_cases),
        "passed_count": passed_count,
        "runtime_ms": total_time_ms,
        "error": None if all_passed else f"{len(test_cases) - passed_count} test cases failed",
        "test_results": test_results
    }
