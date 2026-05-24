# Interview AI — Mock Interview Platform

AI-powered mock interview system with **adaptive questioning**, **rubric-based scoring**, **voice interview mode**, and a full **web application** with real-time cheating detection.

---

## Features

### 🧠 Adaptive Questioning (Module A)
Questions adapt dynamically to each answer — weak answer → simpler follow-up, strong answer → deeper probe. Powered by Gemini or Anthropic, with role-specific context from a **curated question bank (RAG)**.

### 📊 Rubric-Based Scoring (Module B)
Scores across 5 axes (communication, technical, problem_solving, behavioral, delivery), each 0–100, with `gap_vs_bar` analysis against role-specific hiring thresholds.

### 🎤 Voice Interview (Module C)
Push-to-talk voice interview via terminal — TTS speaks questions, hold SPACEBAR to answer, STT transcribes, full pipeline scores you.

### 🌐 Web Application
Full browser-based interview experience with:
- **Role selector** — 13 roles across Technical and CX categories with auto-configured ICP, language, round type, and company tier
- **Question Bank RAG** — ChromaDB vector store with 130 curated questions; top-3 semantically similar questions retrieved per turn to ground LLM generation
- **Real-time cheating detection** — MediaPipe Tasks Vision (478-point face mesh, iris landmarks for gaze), tab switch monitoring, background motion detection, audio ambient energy analysis, phone/object near-face detection
- **WebSocket** live analysis stream with integrity score, alert logging, and final integrity report
- **gTTS** text-to-speech (English & Hindi), **Google SpeechRecognition** STT
- **Role-specific hiring bars** — different thresholds per role and ICP type

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

### 1. Prerequisites

- Python 3.11+
- An **Anthropic** or **Gemini** API key

### 2. Setup

```powershell
cd interview-ai
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install chromadb
```

Create `.env` in `interview-ai/`:

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

### 🖥️ Option A: Web Application (Recommended)

```powershell
.\venv\Scripts\Activate.ps1
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

### ⌨️ Option B: Terminal Voice Interview

```powershell
pip install pyttsx3 SpeechRecognition pyaudio keyboard
.\venv\Scripts\Activate.ps1
py voice_interview.py
```

> **Windows pyaudio workaround:**
> ```powershell
> pip install pipwin
> pipwin install pyaudio
> ```

Select a profile → hear questions via TTS → **hold SPACEBAR** to answer → release to stop → get scored.

### 📄 Option C: Text Pipeline

```powershell
.\venv\Scripts\Activate.ps1
py main.py
```

Runs ICP-A (SWE screening) + ICP-B (CX behavioral) + strong vs weak comparison. Outputs saved to `outputs/`.

### 🧪 Run All 10 Test Cases

```powershell
.\venv\Scripts\Activate.ps1
py run_tests.py
```

---

## Cheating Detection Details

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

## Model Providers

| Provider | `MODEL_PROVIDER` | Model |
|----------|-------------------|-------|
| Gemini | `gemini` | `gemini-2.0-flash-lite` (auto-fallback chain on rate limit) |
| Anthropic | `anthropic` | `claude-sonnet-4-20250514` |

Set matching `*_API_KEY` in `.env`. No API key needed for TTS/STT.

---

## RAG — Question Bank

The ChromaDB vector store (`web/question_bank.py`) is seeded with **130 curated questions** across all 13 roles. On each turn, the last Q&A pair is embedded with `all-MiniLM-L6-v2` and the top-3 semantically closest questions are injected into the LLM prompt as reference material.

Questions are tagged by type (technical/behavioral), difficulty (1–5), and skill tags. The LLM adapts them dynamically based on the candidate's previous answers.

---

## Architecture

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

## License

MIT
