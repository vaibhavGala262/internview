# conductor.py
import json
from model_client import call_model
from prompts import CONDUCTOR_SYSTEM_PROMPT


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _normalize_question_type(result: dict, round_type: str, previous_qa_pairs: list) -> None:
    allowed = ["technical", "behavioral", "follow_up"]
    if result.get("question_type") in allowed:
        return

    if previous_qa_pairs:
        result["question_type"] = "follow_up"
    elif round_type == "technical":
        result["question_type"] = "technical"
    else:
        result["question_type"] = "behavioral"


def run_conductor(
    icp_type: str,
    target_role: str,
    round_type: str,
    company_tier: str,
    language: str,
    previous_qa_pairs: list
) -> dict:
    """
    Module A: Generate the next adaptive interview question.

    Args:
        icp_type: "high_wage" or "low_wage"
        target_role: e.g. "Software Engineer" or "CX Associate"
        round_type: "screening" | "technical" | "behavioral"
        company_tier: "startup" | "mid" | "enterprise"
        language: "en" | "hi"
        previous_qa_pairs: list of {"question": str, "answer_transcript": str}

    Returns:
        dict with next_question, question_type, difficulty_level, reasoning
    """
    user_message = f"""
Candidate Profile:
- icp_type: {icp_type}
- target_role: {target_role}
- round_type: {round_type}
- company_tier: {company_tier}
- language: {language}

Previous Q&A Pairs:
{json.dumps(previous_qa_pairs, ensure_ascii=False, indent=2)}

Generate the next interview question now.
"""

    raw = call_model(CONDUCTOR_SYSTEM_PROMPT, user_message).strip()
    try:
        result = _parse_json_response(raw)
    except json.JSONDecodeError:
        retry_message = (
            f"{user_message}\n\n"
            f"The previous response was not valid JSON:\n{raw}\n\n"
            "Return the same answer as raw valid JSON only. No markdown."
        )
        result = _parse_json_response(call_model(CONDUCTOR_SYSTEM_PROMPT, retry_message))

    _normalize_question_type(result, round_type, previous_qa_pairs)

    required = ["next_question", "question_type", "difficulty_level", "reasoning"]
    for field in required:
        if field not in result:
            raise ValueError(f"Module A missing field: {field}")

    assert isinstance(result["difficulty_level"], int), "difficulty_level must be int"
    assert result["question_type"] in ["technical", "behavioral", "follow_up"], \
        f"Invalid question_type: {result['question_type']}"
    assert 1 <= result["difficulty_level"] <= 5, \
        f"difficulty_level out of range: {result['difficulty_level']}"

    return result
