# scorer.py
import json
from model_client import call_model
from prompts import SCORER_SYSTEM_PROMPT


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _quote_exists_in_transcript(quote: str, full_transcript: list) -> bool:
    if not quote:
        return False
    return any(quote in qa.get("answer", "") for qa in full_transcript)


def run_scorer(
    full_transcript: list,
    icp_type: str,
    target_role: str,
    round_type: str,
    hiring_bar: dict
) -> dict:
    """
    Module B: Score a full interview transcript.

    Args:
        full_transcript: list of {"question": str, "answer": str}
        icp_type: "high_wage" or "low_wage"
        target_role: e.g. "Software Engineer"
        round_type: "screening" | "technical" | "behavioral"
        hiring_bar: dict with keys: communication, technical,
                    problem_solving, behavioral, delivery (each 0-100)

    Returns:
        dict with overall_score, scores_per_axis, gap_vs_bar,
        weak_moment, strong_moment, next_action
    """
    user_message = f"""
Evaluation Context:
- icp_type: {icp_type}
- target_role: {target_role}
- round_type: {round_type}
- hiring_bar: {json.dumps(hiring_bar)}

Full Interview Transcript:
{json.dumps(full_transcript, ensure_ascii=False, indent=2)}

Generate the evaluation report now.
"""

    raw = call_model(SCORER_SYSTEM_PROMPT, user_message).strip()
    try:
        result = _parse_json_response(raw)
    except json.JSONDecodeError:
        retry_message = (
            f"{user_message}\n\n"
            f"The previous response was not valid JSON:\n{raw}\n\n"
            "Return the same evaluation as raw valid JSON only. No markdown."
        )
        result = _parse_json_response(call_model(SCORER_SYSTEM_PROMPT, retry_message))

    if "weak_moment" in result and isinstance(result["weak_moment"], dict):
        weak_quote = result["weak_moment"].get("quote", "")
        result["weak_moment"]["quote_verified"] = _quote_exists_in_transcript(
            weak_quote, full_transcript
        )

    if "strong_moment" in result and isinstance(result["strong_moment"], dict):
        strong_quote = result["strong_moment"].get("quote", "")
        result["strong_moment"]["quote_verified"] = _quote_exists_in_transcript(
            strong_quote, full_transcript
        )

    required = ["overall_score", "scores_per_axis", "gap_vs_bar",
                "weak_moment", "strong_moment", "next_action"]
    for field in required:
        if field not in result:
            raise ValueError(f"Module B missing field: {field}")

    axes = ["communication", "technical", "problem_solving", "behavioral", "delivery"]
    for axis in axes:
        if axis not in result["scores_per_axis"]:
            raise ValueError(f"scores_per_axis missing: {axis}")
        if axis not in result["gap_vs_bar"]:
            raise ValueError(f"gap_vs_bar missing: {axis}")

    transcript_text = " ".join([qa["answer"] for qa in full_transcript])
    weak_quote = result["weak_moment"].get("quote", "")
    strong_quote = result["strong_moment"].get("quote", "")

    if weak_quote and weak_quote not in transcript_text:
        print("WARNING: weak_moment quote not found in transcript verbatim.")

    if strong_quote and strong_quote not in transcript_text:
        print("WARNING: strong_moment quote not found in transcript verbatim.")

    return result
