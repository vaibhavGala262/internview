# Interview AI — Mock Interview Pipeline

AI-powered mock interview system with **adaptive questioning** (Module A), **rubric-based scoring** (Module B), **voice interview mode** (Module C), and a **web application** with RAG question bank + real-time cheating detection.

---

## Features

### Core Pipeline
| Feature | Description |
|---------|-------------|
| **Adaptive Questioning** | Questions dynamically adjust based on candidate's previous answer — weak answer leads to simpler follow-up, strong answer leads to deeper probe |
| **Rubric-Based Scoring** | Scores 5 axes (communication, technical, problem_solving, behavioral, delivery) each 0–100 with `gap_vs_bar` analysis against a hiring threshold |
| **Two ICP Profiles** | High-wage (English, technical, SWE) and Low-wage (Hindi, conversational, CX Associate) with completely different tone, question domains, and language |
| **Company Tier Awareness** | Startup (scrappy/practical), Mid (balanced), Enterprise (formal/process-oriented) |
| **Round Type Awareness** | Screening (background/fit), Technical (deep knowledge), Behavioral (situational/soft skills) |
| **Quote Verification** | All weak/strong moment quotes verified as exact substrings of the transcript — `quote_verified` flag set programmatically |
| **Difficulty Trend Logging** | Tracks `difficulty_level` progression across turns (e.g. 2 → 3 → 1) with per-turn reasoning |
| **Strong vs Weak Comparison** | `main.py` runs both a strong and weak candidate through the same profile and compares scores side by side |
| **Multi-Provider** | Switch between Gemini (with automatic fallback chain) and Anthropic via `MODEL_PROVIDER` env var |
| **10/10 Test Cases** | All test cases pass schema validation, difficulty range checks, and quote grounding verification |

### Voice Interview Mode
| Feature | Description |
|---------|-------------|
| **Text-to-Speech** | Questions spoken aloud via `pyttsx3` (offline TTS, no API key) — female voice, 155 wpm |
| **Push-to-Talk** | Hold SPACEBAR to record, release to stop — no silence detection issues, no accidental cutoffs |
| **Speech-to-Text** | Google STT with `en-IN` accent support; processes audio from push-to-talk WAV buffer |
| **Live Visual Feedback** | Dots printed per audio chunk while recording so you know it's capturing |
| **ICP-Specific Prompts** | English prompts for SWE; Hindi prompts for CX Associate |
| **User-Controlled Pacing** | Press Enter between turns; push-to-talk for answers |
| **Spoken Score Summary** | After 3 turns, the full score report is both printed and spoken aloud |
| **Auto-Save** | Full transcript + score report saved to `outputs/voice_interview_result.json` |

### Web Application
| Feature | Description |
|---------|-------------|
| **Role Selector** | 13 roles across Technical and CX categories with auto-configured ICP, language, round type, and company tier |
| **Question Bank RAG** | ChromaDB vector store with 130 curated questions; top-3 semantically similar questions retrieved per turn to ground LLM generation |
| **Real-Time Cheating Detection** | MediaPipe Tasks Vision (478-point face mesh, iris landmarks for gaze), tab switch monitoring, background motion detection, audio ambient energy analysis, phone/object near-face detection |
| **WebSocket Live Stream** | Analysis sent every 800ms, backend computes integrity score and returns live status + alerts |
| **gTTS + Google STT** | Text-to-speech (English & Hindi) and speech-to-text via browser recording |
| **Role-Specific Hiring Bars** | Different thresholds per role and ICP type |
| **Integrity Report** | Final alert breakdown, risk level, and integrity score in results dashboard |

---

## Project Structure

```
interview-ai/
├── web/                              # Web application
│   ├── app.py                        # FastAPI backend (REST + WebSocket)
│   ├── question_bank.py              # ChromaDB vector store with 130 curated Qs
│   ├── role_config.py                # 13 role definitions, skills, hiring bars
│   ├── cheating.py                   # Cheating alert recorder & analyzer
│   ├── tts.py                        # gTTS text-to-speech wrapper
│   ├── stt.py                        # Google SpeechRecognition wrapper
│   └── static/
│       └── index.html                # Single-page frontend (no build step)
├── conductor.py                      # Module A: Adaptive interview conductor
├── scorer.py                         # Module B: Transcript-grounded scorer
├── voice_interview.py                # Module C: Terminal voice interview
├── model_client.py                   # Central Anthropic/Gemini model client
├── prompts.py                        # All system prompts
├── validator.py                      # Schema, quote, and validation checks
├── main.py                           # End-to-end pipeline + comparison demo
├── run_tests.py                      # Test harness for all 10 cases
├── test_cases/                       # 10 JSON test inputs (5 ICP-A, 5 ICP-B)
├── outputs/                          # Generated output JSON files
├── .env                              # API keys and config (not committed)
└── requirements.txt                  # Python dependencies
```

---

## Quick Start

### Setup

```powershell
cd interview-ai
pip install -r requirements.txt
```

Set API key in `.env`:
```txt
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

Or for Anthropic:
```txt
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

---

## Usage

### 1. CLI — Text Pipeline

```powershell
py main.py
```

Runs ICP-A (SWE screening) + ICP-B (CX behavioral) + strong vs weak comparison. Outputs saved to `outputs/`.

### 2. CLI — Voice Interview

```powershell
pip install pyttsx3 SpeechRecognition pyaudio keyboard
py voice_interview.py
```

> **Windows pyaudio workaround:**
> ```powershell
> pip install pipwin
> pipwin install pyaudio
> ```

Select profile → hear questions via TTS → hold SPACEBAR to answer → release when done → get scored.

### 3. Web Application

```powershell
pip install chromadb uvicorn
uvicorn web.app:app --reload --port 8000
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser.

1. Select a **Category** → **Role** (fields auto-configure)
2. Choose question count (1–5), round type, company tier
3. Click **Start Interview**
4. Grant camera & microphone access
5. Hear the opening greeting, then **Record** your answers
6. After all questions, view your **score report**, **strong/weak moments**, and **integrity report**

**Cheating detection** runs automatically:
- Face visible? Gaze centered? → live status in top-left
- Tab switches, background motion, unusual audio, phone near face → logged with severity
- Final integrity score in the results dashboard

### Run All 10 Test Cases

```powershell
py run_tests.py
```
Validates schema, quote grounding, and difficulty ranges. Filter with `$env:TEST_FILTER="icp_a"`.

---

## How Modules Work Together

```
                    ┌─────────────┐
                    │  .env /     │
                    │  model_     │
                    │  client.py  │
                    └──────┬──────┘
                           ▼
             ┌─────────────┴─────────────┐
             │         prompts.py         │
             │  (system prompts for both  │
             │   conductor & scorer)      │
             └─────────────┬─────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
     ┌────────────────┐       ┌────────────────┐
     │ conductor.py   │       │  scorer.py     │
     │ (Module A)     │       │  (Module B)    │
     │                │       │                │
     │ Takes: ICP,    │       │ Takes: full    │
     │ role, round,   │       │ transcript,    │
     │ tier, lang,    │       │ ICP, bar       │
     │ prev Q&A       │       │                │
     │                │       │ Returns:       │
     │ Returns: next_ │       │ overall_score, │
     │ question,      │       │ scores_per_    │
     │ question_type, │       │ axis, gap_vs_  │
     │ difficulty,    │       │ bar, weak/     │
     │ reasoning      │       │ strong moments │
     └───────┬────────┘       └───────┬────────┘
             │                        │
             └───────────┬────────────┘
                         ▼
                ┌──────────────────┐
                │  validator.py    │
                │  Schema check    │
                │  Quote verify    │
                └──────┬───────────┘
                       ▼
                ┌──────────────────┐
                │   outputs/       │
                │   JSON results   │
                └──────────────────┘

     ┌──────────────────────────────────────┐
     │         voice_interview.py           │
     │  (Module C — wraps A + B with TTS   │
     │   and STT for spoken interaction)   │
     └──────────────────────────────────────┘
```

---

## Web Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  Browser    │◄──►│  FastAPI Backend │◄──►│  LLM (Gemini/     │
│  (index.html│    │  (app.py)        │    │  Anthropic)        │
│  + MediaPipe│    │                  │    │                    │
│  JS)        │    │  ┌────────────┐  │    │  conductor.py     │
│             │    │  │ WebSocket  │  │    │  scorer.py         │
│ WebSocket   │    │  │ + cheating │  │    └────────────────────┘
│ (analysis)  │    │  │ detector   │  │
│             │    │  └────────────┘  │    ┌────────────────────┐
│ REST        │    │  ┌────────────┐  │    │  ChromaDB          │
│ (start/     │◄──►│  │ Question   │◄─┼────┤  (130 questions)   │
│  question/  │    │  │ Bank RAG   │  │    └────────────────────┘
│  answer/    │    │  └────────────┘  │
│  score)     │    └──────────────────┘
└─────────────┘
```

---

## Model Providers

| Provider | `MODEL_PROVIDER` | Model |
|----------|-------------------|-------|
| Gemini | `gemini` | `gemini-2.0-flash-lite` (auto-fallback through 6 models on rate limit) |
| Anthropic | `anthropic` | `claude-sonnet-4-20250514` |

Set matching `*_API_KEY` in `.env`. No API key needed for TTS/STT in voice/web mode.

---

## RAG — Question Bank

The ChromaDB vector store (`web/question_bank.py`) is seeded with **130 curated questions** across all 13 roles. On each turn, the last Q&A pair is embedded with `all-MiniLM-L6-v2` and the top-3 semantically closest questions are injected into the LLM prompt as reference material.

Questions are tagged by type (technical/behavioral), difficulty (1–5), and skill tags. The LLM adapts them dynamically based on the candidate's previous answers.

---

## Cheating Detection

| Feature | Method | Runs On |
|---------|--------|---------|
| **Face detection** | MediaPipe FaceLandmarker (478-point mesh) | Browser (CDN) |
| **Gaze estimation** | Iris landmarks 468/473 position vs eye corners | Browser (CDN) |
| **Tab switch** | `visibilitychange` + `blur` events with dedup | Browser (native) |
| **Background motion** | Frame differencing at 160×120, pixel diff threshold | Browser (Canvas) |
| **Audio analysis** | Web Audio API AnalyserNode, sustained energy monitoring | Browser (native) |
| **Phone near face** | Pixel stddev below chin region, threshold > 50 | Browser (Canvas) |
| **Alert management** | 25s warmup, dedup per alert type, cascade to integrity score | Backend (Python) |

Frontend sends JSON analysis every 800ms over WebSocket. Backend computes integrity score (`max(0, 100 - alerts×5)`) and returns live status + new alerts.

---

## License

MIT
