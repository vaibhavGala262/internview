# validator.py
"""
Schema validation and quote grounding checks.
Used by run_tests.py to validate all 10 test cases.
"""

CONDUCTOR_SCHEMA = {
    "next_question": str,
    "question_type": ["technical", "behavioral", "follow_up"],
    "difficulty_level": int,
    "reasoning": str
}

SCORER_SCHEMA = {
    "overall_score": int,
    "scores_per_axis": dict,
    "gap_vs_bar": dict,
    "weak_moment": dict,
    "strong_moment": dict,
    "next_action": str
}

SCORE_AXES = ["communication", "technical", "problem_solving", "behavioral", "delivery"]


def validate_conductor_output(output: dict) -> tuple[bool, list]:
    errors = []

    for field, expected_type in CONDUCTOR_SCHEMA.items():
        if field not in output:
            errors.append(f"MISSING FIELD: {field}")
            continue
        if isinstance(expected_type, list):
            if output[field] not in expected_type:
                errors.append(f"INVALID VALUE for {field}: {output[field]}")
        elif not isinstance(output[field], expected_type):
            errors.append(f"WRONG TYPE for {field}: expected {expected_type.__name__}")

    if "difficulty_level" in output:
        if not (1 <= output["difficulty_level"] <= 5):
            errors.append(f"difficulty_level out of range: {output['difficulty_level']}")

    return len(errors) == 0, errors


def validate_scorer_output(output: dict, transcript: list) -> tuple[bool, list]:
    errors = []

    for field in SCORER_SCHEMA:
        if field not in output:
            errors.append(f"MISSING FIELD: {field}")

    if "scores_per_axis" in output:
        for axis in SCORE_AXES:
            if axis not in output["scores_per_axis"]:
                errors.append(f"scores_per_axis missing axis: {axis}")

    if "gap_vs_bar" in output:
        for axis in SCORE_AXES:
            if axis not in output["gap_vs_bar"]:
                errors.append(f"gap_vs_bar missing axis: {axis}")

    if "overall_score" in output:
        if not (0 <= output["overall_score"] <= 100):
            errors.append(f"overall_score out of range: {output['overall_score']}")

    transcript_text = " ".join([qa["answer"] for qa in transcript])

    if "weak_moment" in output:
        if not output["weak_moment"].get("quote_verified", False):
            errors.append("QUOTE NOT VERIFIED: weak_moment quote not found in transcript")
        quote = output["weak_moment"].get("quote", "")
        if quote and quote not in transcript_text:
            errors.append(f"AUTO-FAIL: weak_moment quote not in transcript: '{quote[:60]}...'")

    if "strong_moment" in output:
        if not output["strong_moment"].get("quote_verified", False):
            errors.append("QUOTE NOT VERIFIED: strong_moment quote not found in transcript")
        quote = output["strong_moment"].get("quote", "")
        if quote and quote not in transcript_text:
            errors.append(f"AUTO-FAIL: strong_moment quote not in transcript: '{quote[:60]}...'")

    return len(errors) == 0, errors


def print_validation_report(case_name: str, conductor_results: list,
                             scorer_result: dict, transcript: list):
    print(f"\n{'='*50}")
    print(f"TEST CASE: {case_name}")
    print(f"{'='*50}")

    all_passed = True

    for i, result in enumerate(conductor_results):
        passed, errors = validate_conductor_output(result)
        status = "PASS" if passed else "FAIL"
        print(f"  Conductor Turn {i+1}: {status}")
        if errors:
            all_passed = False
            for e in errors:
                print(f"    ERROR: {e}")

    passed, errors = validate_scorer_output(scorer_result, transcript)
    status = "PASS" if passed else "FAIL"
    print(f"  Scorer: {status}")
    if errors:
        all_passed = False
        for e in errors:
            print(f"    ERROR: {e}")

    print(f"  Overall Score: {scorer_result.get('overall_score', 'N/A')}")
    print(f"  Result: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    return all_passed
