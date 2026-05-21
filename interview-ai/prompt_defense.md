# Prompt Defense Document

## Module A — Interview Conductor

### Why this system prompt structure?

The core requirement is adaptive questioning — questions must genuinely 
respond to what the candidate said, not follow a fixed list.

The prompt enforces this with explicit IF/ELSE logic:
- WEAK answer → simpler follow-up on same topic, difficulty drops
- STRONG answer → harder probe of the specific thing they mentioned
- reasoning field must reference actual words from the previous answer

This forces the model to read the answer before writing a question.
Without this structure, the model defaults to a sequential question list.

### What I tried first and what broke

First attempt: Simple instruction "generate adaptive questions."
Problem: Model ignored previous answers and generated generic questions.

Fix: Added explicit keyword extraction step and made the reasoning field 
mandatory — requiring the model to cite the previous answer before 
generating the next question. This created accountability in the output 
that we can verify.

### ICP differentiation strategy

The prompt forks on two dimensions:
1. icp_type — controls tone, terminology, question domain
2. language — controls output language for ICP-B

ICP-B Hindi prompt specifically says "NOT translated English — write how 
a Hindi speaker actually talks." This prevents the most common failure: 
grammatically-correct-but-unnatural translated output.

---

## Module B — Interview Scorer

### Why transcript-grounded quotes?

Auto-fail condition: invented quotes.
The prompt explicitly says "exact substrings copied directly from the 
transcript answers" and explains what qualifies as auto-fail.

The validator.py then verifies this programmatically by checking if the 
quote is a substring of the actual transcript. If not — warning is raised.

### Why explicit gap_vs_bar math?

Common model behavior: softening negative scores (showing 0 instead of -20).
The prompt specifies: "gap_vs_bar = user_score - hiring_bar" with a 
concrete example (35 - 65 = -30) and explicitly says "NEVER show positive 
gap when user is clearly underperforming."

Giving a concrete formula + example prevents the model from interpreting 
the instruction creatively.

### What broke during testing

Hindi output quality: Initial outputs were translated English.
Fix: Added "NOT translated English. Natural Hindi phrasing." explicitly.
Also added "Write as a supportive manager speaking to a first-time job 
seeker" to anchor the register.

Score inflation: Model tended to give 70+ to mediocre answers.
Fix: Added explicit "weak answer signals" list to calibrate what counts 
as weak. This gave the model a concrete reference standard.
