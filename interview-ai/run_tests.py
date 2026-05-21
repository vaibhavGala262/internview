# run_tests.py
"""
Runs all 10 test cases from test_cases/ directory.
Validates schema and quote grounding for each.
Saves outputs to outputs/ directory.
Prints pass/fail summary.
"""

import json
import os
from conductor import run_conductor
from scorer import run_scorer
from validator import print_validation_report

HIRING_BAR_A = {
    "communication": 70, "technical": 65,
    "problem_solving": 70, "behavioral": 65, "delivery": 60
}
HIRING_BAR_B = {
    "communication": 60, "technical": 40,
    "problem_solving": 55, "behavioral": 65, "delivery": 55
}

os.makedirs("outputs", exist_ok=True)

test_files = sorted([f for f in os.listdir("test_cases") if f.endswith(".json")])
test_filter = os.getenv("TEST_FILTER", "").strip()
if test_filter:
    test_files = [f for f in test_files if test_filter in f]

results_summary = []

for test_file in test_files:
    with open(f"test_cases/{test_file}", "r", encoding="utf-8") as f:
        case = json.load(f)

    profile = case["profile"]
    mock_answers = case["mock_answers"]
    hiring_bar = HIRING_BAR_A if profile["icp_type"] == "high_wage" else HIRING_BAR_B

    transcript = []
    qa_pairs = []
    conductor_outputs = []

    for answer in mock_answers:
        output = run_conductor(
            icp_type=profile["icp_type"],
            target_role=profile["target_role"],
            round_type=profile["round_type"],
            company_tier=profile["company_tier"],
            language=profile["language"],
            previous_qa_pairs=qa_pairs
        )
        conductor_outputs.append(output)
        qa_pairs.append({
            "question": output["next_question"],
            "answer_transcript": answer
        })
        transcript.append({
            "question": output["next_question"],
            "answer": answer
        })

    score_report = run_scorer(
        full_transcript=transcript,
        icp_type=profile["icp_type"],
        target_role=profile["target_role"],
        round_type=profile["round_type"],
        hiring_bar=hiring_bar
    )

    passed = print_validation_report(
        test_file, conductor_outputs, score_report, transcript
    )
    results_summary.append({"case": test_file, "passed": passed})

    output_data = {
        "case": test_file,
        "profile": profile,
        "conductor_outputs": conductor_outputs,
        "transcript": transcript,
        "score_report": score_report
    }
    out_name = test_file.replace(".json", "_output.json")
    with open(f"outputs/{out_name}", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print("FINAL TEST SUMMARY")
print(f"{'='*60}")
passed_count = sum(1 for r in results_summary if r["passed"])
print(f"Passed: {passed_count}/{len(results_summary)}")
for r in results_summary:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"  {status} - {r['case']}")
