# main.py
"""
Entry point. Runs the full end-to-end pipeline for both ICP-A and ICP-B.
Shows the adaptive interview in action with 3 turns each.
"""

import json
import os
from conductor import run_conductor
from scorer import run_scorer

HIRING_BAR_A = {
    "communication": 70,
    "technical": 65,
    "problem_solving": 70,
    "behavioral": 65,
    "delivery": 60
}

HIRING_BAR_B = {
    "communication": 60,
    "technical": 40,
    "problem_solving": 55,
    "behavioral": 65,
    "delivery": 55
}


def run_pipeline(profile: dict, mock_answers: list, hiring_bar: dict, label: str):
    """
    Run the full interview pipeline:
    1. Module A x3 (adaptive questions)
    2. Module B (score full transcript)
    """
    print(f"\n{'='*60}")
    print(f"RUNNING PIPELINE: {label}")
    print(f"ICP: {profile['icp_type']} | Role: {profile['target_role']}")
    print(f"{'='*60}")

    transcript = []
    qa_pairs = []
    conductor_outputs = []

    for turn, mock_answer in enumerate(mock_answers, 1):
        print(f"\n--- TURN {turn} ---")

        output = run_conductor(
            icp_type=profile["icp_type"],
            target_role=profile["target_role"],
            round_type=profile["round_type"],
            company_tier=profile["company_tier"],
            language=profile["language"],
            previous_qa_pairs=qa_pairs
        )

        conductor_outputs.append(output)

        print(f"Q: {output['next_question']}")
        print(f"Type: {output['question_type']} | Difficulty: {output['difficulty_level']}/5")
        print(f"Reasoning: {output['reasoning']}")
        print(f"\nA (mock): {mock_answer}")

        qa_pairs.append({
            "question": output["next_question"],
            "answer_transcript": mock_answer
        })
        transcript.append({
            "question": output["next_question"],
            "answer": mock_answer
        })

    difficulty_progression = [output["difficulty_level"] for output in conductor_outputs]
    difficulty_reasonings = [output["reasoning"] for output in conductor_outputs]
    d1, d2, d3 = difficulty_progression
    reasoning_1, reasoning_2, reasoning_3 = difficulty_reasonings

    print("\n── ADAPTIVE DIFFICULTY TREND ──")
    print(f"Progression: {d1} → {d2} → {d3}")
    print(f"  Q1: {reasoning_1}")
    print(f"  Q2: {reasoning_2}")
    print(f"  Q3: {reasoning_3}")

    print(f"\n{'='*60}")
    print("RUNNING MODULE B — SCORER")
    print(f"{'='*60}")

    score_report = run_scorer(
        full_transcript=transcript,
        icp_type=profile["icp_type"],
        target_role=profile["target_role"],
        round_type=profile["round_type"],
        hiring_bar=hiring_bar
    )

    print(f"\nOverall Score: {score_report['overall_score']}/100")
    print("\nScores per axis:")
    for axis, score in score_report["scores_per_axis"].items():
        gap = score_report["gap_vs_bar"][axis]
        bar = hiring_bar[axis]
        print(f"  {axis}: {score}/100 (bar: {bar}, gap: {gap:+d})")

    print(f"\nWeak Moment ({score_report['weak_moment']['timestamp_approx']}):")
    print(f"  Quote: \"{score_report['weak_moment']['quote']}\"")
    print(f"  Why it hurt: {score_report['weak_moment']['why_it_hurt']}")

    print("\nStrong Moment:")
    print(f"  Quote: \"{score_report['strong_moment']['quote']}\"")
    print(f"  Why it helped: {score_report['strong_moment']['why_it_helped']}")

    print(f"\nNext Action: {score_report['next_action']}")

    return {
        "profile": profile,
        "conductor_outputs": conductor_outputs,
        "transcript": transcript,
        "difficulty_trend": {
            "progression": difficulty_progression,
            "reasonings": difficulty_reasonings
        },
        "score_report": score_report
    }


def run_comparison():
    profile = {
        "icp_type": "high_wage",
        "target_role": "Software Engineer",
        "round_type": "screening",
        "company_tier": "mid",
        "language": "en"
    }

    hiring_bar = {
        "communication": 70, "technical": 65,
        "problem_solving": 70, "behavioral": 65, "delivery": 60
    }

    strong_answers = [
        "I built a REST API using FastAPI with JWT authentication, "
        "deployed on AWS EC2 using Docker. Handled 10k requests per day. "
        "I used PostgreSQL with connection pooling and added Redis caching "
        "to reduce DB load by 40 percent.",

        "For the Docker setup I wrote a multi-stage Dockerfile to keep the "
        "image size under 200MB, used docker-compose for local dev with "
        "PostgreSQL and Redis services, and set up GitHub Actions to build "
        "and push to ECR on every merge to main.",

        "I handled a production incident where the API was returning 500 errors. "
        "I used CloudWatch logs to identify a connection pool exhaustion issue, "
        "increased the pool size, and added a circuit breaker pattern to prevent "
        "cascading failures. Downtime was under 8 minutes."
    ]

    weak_answers = [
        "I know Python and have made some projects. I built a website once.",

        "I don't know much about Docker. I've heard of it but never used it. "
        "I think it's like a virtual machine.",

        "I would just Google the error and try to fix it. "
        "I'm a fast learner so I think I'd figure it out."
    ]

    print("\n" + "="*60)
    print("STRONG vs WEAK CANDIDATE COMPARISON")
    print("Same profile, same hiring bar, different answers")
    print("="*60)

    # Run strong candidate (suppress turn-by-turn output)
    strong_result = run_pipeline(
        profile, strong_answers, hiring_bar, "STRONG CANDIDATE"
    )

    # Run weak candidate
    weak_result = run_pipeline(
        profile, weak_answers, hiring_bar, "WEAK CANDIDATE"
    )

    # Print comparison table
    axes = ["communication", "technical", "problem_solving", "behavioral", "delivery"]

    print("\n── SCORE COMPARISON ──")
    print(f"{'AXIS':<20} {'STRONG':>8} {'WEAK':>8} {'BAR':>8}")
    print("-" * 48)

    for axis in axes:
        strong_score = strong_result["score_report"]["scores_per_axis"][axis]
        weak_score = weak_result["score_report"]["scores_per_axis"][axis]
        bar = hiring_bar[axis]
        print(f"{axis:<20} {strong_score:>8} {weak_score:>8} {bar:>8}")

    strong_total = strong_result["score_report"]["overall_score"]
    weak_total = weak_result["score_report"]["overall_score"]

    print("-" * 48)
    print(f"{'OVERALL':<20} {strong_total:>8} {weak_total:>8}")
    print(f"\nDifference: {strong_total - weak_total} points apart")

    # Save comparison output
    import os, json
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/comparison.json", "w", encoding="utf-8") as f:
        json.dump({
            "strong": strong_result,
            "weak": weak_result,
            "score_gap": strong_total - weak_total
        }, f, ensure_ascii=False, indent=2)

    print("Comparison saved to outputs/comparison.json")


if __name__ == "__main__":

    profile_a = {
        "icp_type": "high_wage",
        "target_role": "Software Engineer",
        "round_type": "screening",
        "company_tier": "mid",
        "language": "en"
    }

    mock_answers_a = [
        "I've been working with Python for 2 years. I built a REST API "
        "using FastAPI with JWT authentication and deployed it on AWS EC2 "
        "using Docker containers. The API handled about 10k requests per day.",

        "I know about databases. I've used SQL before. I think I would just "
        "use whatever database the team uses.",

        "For the Docker deployment, I wrote a Dockerfile and used docker-compose "
        "to manage multiple services including PostgreSQL and Redis. I also set up "
        "a CI/CD pipeline using GitHub Actions to auto-deploy on merge to main."
    ]

    result_a = run_pipeline(profile_a, mock_answers_a, HIRING_BAR_A, "ICP-A SWE Screening")

    profile_b = {
        "icp_type": "low_wage",
        "target_role": "CX Associate",
        "round_type": "behavioral",
        "company_tier": "startup",
        "language": "hi"
    }

    mock_answers_b = [
        "मैंने पहले कभी office में काम नहीं किया है, लेकिन delivery के दौरान "
        "मैं हमेशा customers से अच्छे से बात करता था। एक बार एक customer बहुत "
        "गुस्से में था क्योंकि उसका package late था, मैंने उसे शांत करके "
        "problem solve की।",

        "Computer के बारे में ज़्यादा नहीं जानता। बस phone use करता हूं।",

        "मुझे नहीं पता office में क्या होता है। पर मैं मेहनत करता हूं और "
        "जल्दी सीखने की कोशिश करूंगा।"
    ]

    result_b = run_pipeline(profile_b, mock_answers_b, HIRING_BAR_B, "ICP-B CX Associate Behavioral")

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/main_run_a.json", "w", encoding="utf-8") as f:
        json.dump(result_a, f, ensure_ascii=False, indent=2)
    with open("outputs/main_run_b.json", "w", encoding="utf-8") as f:
        json.dump(result_b, f, ensure_ascii=False, indent=2)

    print("\n\nOutputs saved to outputs/main_run_a.json and outputs/main_run_b.json")

    print("\n\n")
    run_comparison()
