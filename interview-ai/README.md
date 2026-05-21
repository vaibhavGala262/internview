# Interview AI — Mock Interview Pipeline

AI-powered mock interview system with adaptive questioning (Module A) 
and rubric-based scoring (Module B).

## Setup (under 2 minutes)

1. Clone and enter the repo
2. Install dependencies:
   pip install -r requirements.txt
3. Choose a model provider and set the matching API key:
   export MODEL_PROVIDER=anthropic
   export ANTHROPIC_API_KEY=your_key_here

   Or:
   export MODEL_PROVIDER=gemini
   export GEMINI_API_KEY=your_key_here
4. Run the full pipeline:
   python main.py

## Run all 10 test cases
   python run_tests.py

Outputs saved to outputs/ directory.

## Project Structure
- conductor.py    — Module A: Adaptive interview conductor
- scorer.py       — Module B: Transcript-grounded scorer
- prompts.py      — All system prompts
- validator.py    — Schema + quote validation
- main.py         — End-to-end pipeline runner
- run_tests.py    — Test harness for all 10 cases
- test_cases/     — 10 JSON test inputs (5 ICP-A, 5 ICP-B)
- outputs/        — Generated test outputs (auto-created)

## Model Used
Set `MODEL_PROVIDER=anthropic` for `claude-sonnet-4-20250514` via Anthropic API.
Set `MODEL_PROVIDER=gemini` for `gemini-2.0-flash-lite` via Google Gemini API.
