# Interview AI - Mock Interview Pipeline

AI-powered mock interview system with adaptive questioning (Module A) and rubric-based scoring (Module B).

## Setup (under 2 minutes)

1. Clone and enter the repo:
   ```powershell
   git clone https://github.com/vaibhavGala262/internview.git
   cd internview\interview-ai
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Choose a model provider and set the matching API key in `interview-ai/.env`:
   ```txt
   MODEL_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   ```

   Or use Anthropic:
   ```txt
   MODEL_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_key_here
   ```

4. Run the full pipeline:
   ```powershell
   py main.py
   ```

## Run all 10 test cases

From `interview-ai/`:

```powershell
py run_tests.py
```

Outputs are saved to `interview-ai/outputs/`.

## Project Structure

- `interview-ai/conductor.py` - Module A: Adaptive interview conductor
- `interview-ai/scorer.py` - Module B: Transcript-grounded scorer
- `interview-ai/model_client.py` - Central Anthropic/Gemini model client
- `interview-ai/prompts.py` - All system prompts
- `interview-ai/validator.py` - Schema, quote, and validation checks
- `interview-ai/main.py` - End-to-end pipeline runner and comparison demo
- `interview-ai/run_tests.py` - Test harness for all 10 cases
- `interview-ai/test_cases/` - 10 JSON test inputs
- `interview-ai/outputs/` - Generated output JSON files
- `interview-ai/prompt_defense.md` - Prompt defense document

## Features

- Adaptive interview question generation
- Rubric-based scoring report
- High-wage English and low-wage Hindi ICP behavior
- Gemini and Anthropic provider switching through `MODEL_PROVIDER`
- Quote verification with `quote_verified`
- Difficulty trend logging
- Strong vs weak candidate comparison
- 10/10 test cases verified

## Model Used

Set `MODEL_PROVIDER=gemini` for Gemini API support.
Set `MODEL_PROVIDER=anthropic` for `claude-sonnet-4-20250514` via Anthropic API.
