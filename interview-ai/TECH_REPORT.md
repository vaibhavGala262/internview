
## Project Overview
AI-powered mock interview pipeline with 3 modules: adaptive questioning, rubric-based scoring, and voice interaction.

---

## Technologies Used & Why

### Backend / AI
| Tech | Purpose | Why this one? |
|------|---------|---------------|
| **Python 3.13** | Runtime | — |
| **Gemini API** (`gemini-2.0-flash-lite`) | LLM for question generation & scoring | Free tier, fast, auto-fallback through 6 models on rate limit |
| **Anthropic Claude** (`claude-sonnet-4-20250514`) | Alternative LLM provider | Switchable via `.env` — `MODEL_PROVIDER=anthropic` |
| **Google Generative AI SDK** | Python client for Gemini | Official Google library |

### Voice (Module C — my implementation)
| Tech | Purpose | Why this one? |
|------|---------|---------------|
| **pyttsx3** | English TTS (text-to-speech) | Offline, no API key, uses Windows SAPI5 natively |
| **edge-tts** | Hindi TTS (text-to-speech) | Microsoft neural voices — free, natural-sounding, supports Hindi Devanagari natively |
| **pygame.mixer** | MP3 playback for edge-tts output | Reliable, maintained, works on Python 3.13 (playsound is broken) |
| **SpeechRecognition** (Google STT) | Speech-to-text transcription | Best free cloud STT; `language="en-IN"` / `"hi-IN"` for accent support |
| **PyAudio** | Raw audio capture from microphone | Needed for push-to-talk — records PCM chunks in real-time |
| **keyboard** library | Push-to-talk (spacebar hold) | Global hotkey detection — press spacebar to start, release to stop |

### Pipeline (existing modules I built on top of)
| Module | File | Function |
|--------|------|----------|
| Module A | `conductor.py` | Generates adaptive interview questions based on previous answer |
| Module B | `scorer.py` | Scores transcript on 5 axes with gap analysis |
| Model Client | `model_client.py` | Central API gateway (Gemini/Anthropic) with retry + fallback |
| Validator | `validator.py` | Schema validation + quote grounding checks |

---

## Scoring: Why You're Getting 30-40

The 30-33 range is **not a bug** — it's the scorer working correctly with the specific hiring bar set in the code. Here's why:

### The Hiring Bar (for SWE profile)
```
communication:    70
technical:        65
problem_solving:  70
behavioral:       65
delivery:         60
```

These are **thresholds for a hired candidate**, not a beginner. The scorer compares your scores against this bar and reports the gap. Scores of 30-40 mean the scorer honestly assessed your current level against professional hiring standards.

### What determines your score
The scorer (Module B) evaluates 5 axes each 0-100:
- **communication** — clarity, structure, easy to follow
- **technical** — accurate, deep, relevant technical knowledge
- **problem_solving** — logical thinking, concrete approaches
- **behavioral** — real examples, self-awareness
- **delivery** — confidence, conciseness, pacing

### How to improve scores
| What the scorer considers "strong" | What it considers "weak" |
|-----------------------------------|--------------------------|
| Specific examples with details | Vague ("I would just figure it out") |
| Correct terminology | No examples |
| Structured (situation → action → result) | Very short answers |
| Acknowledges trade-offs | Off-topic or hedging |

If you want higher scores, give **specific, structured answers** with real project examples. Generic answers will always score low because the scorer prompt explicitly flags them as weak.

---

## Key Technical Challenges Solved

1. **pyttsx3 engine reuse bug** — On Windows, reusing the same pyttsx3 engine for sequential TTS calls silently drops subsequent utterances. **Fix:** Create a fresh engine instance per `speak()` call via `_make_engine()`.

2. **Hindi TTS not supported** — Windows SAPI5 has no Hindi voice by default. **Fix:** Route Hindi text (detected via Devanagari Unicode range) to `edge-tts` with `hi-IN-SwaraNeural` neural voice.

3. **Silence detection unreliable** — `pause_threshold` approach hung forever with ambient noise. **Fix:** Replaced with push-to-talk — user holds spacebar to record, releases to stop. No silence detection needed.

4. **Audio playback library broken** — `playsound` is unmaintained and broken on Python 3.13. **Fix:** Switched to `pygame.mixer` for reliable MP3 playback.

---

## How Everything Connects

```
User selects profile (SWE English / CX Hindi)
        │
        ▼
  Module A (conductor.py) generates question
        │
        ▼
  My code speaks it via TTS (pyttsx3 / edge-tts)
        │
        ▼
  User holds SPACEBAR → speaks → releases
        │
        ▼
  PyAudio captures raw PCM → WAV buffer → Google STT
        │
        ▼
  Transcript saved, fed back to Module A for next question
        │
        ▼
  After 3 turns → Module B (scorer.py) evaluates
        │
        ▼
  Score report printed + spoken + saved to JSON
```
