# Voice Interview Module — Documentation

## File Created
**`voice_interview.py`** — New file added to `interview-ai/`. Zero existing files were modified.

---

## What It Does

Adds a **voice-based interview experience** on top of the existing pipeline (Module A: Conductor + Module B: Scorer). Instead of typed answers, the candidate:

1. Hears questions spoken aloud via **TTS** (Text-To-Speech)
2. Answers by speaking into a microphone
3. Gets scored automatically by the existing scorer
4. Receives the score report both printed and spoken

---

## Components Implemented

### 1. TTS Engine (`_make_engine` + `speak`)
- Uses `pyttsx3` (offline TTS, no API key needed)
- Female voice, rate 155 wpm, full volume
- **Key decision**: Fresh engine created per `speak()` call to avoid a Windows pyttsx3 bug

### 2. Adaptive STT (`listen`)
- Uses `speech_recognition` with Google STT
- `pause_threshold=2.0` — waits 2 seconds of silence to decide candidate finished
- `phrase_time_limit=30` — safety cutoff so it never hangs forever
- `language="en-IN"` — better Indian English accent recognition
- `dynamic_energy_threshold=True` — auto-adjusts to room noise
- **Visual spinner** (`show_listening_indicator`) — animated recording indicator in a daemon thread

### 3. ICP Selector (`select_icp`)
- Menu: 1 = Software Engineer (English, high-wage), 2 = CX Associate (Hindi, low-wage)
- Sets profile, role, round type, company tier, and language

### 4. Opening Messages (`get_opening_message`)
- English welcome for high-wage ICP
- Hindi welcome for low-wage ICP ("Namaste! Aapka mock interview mein swagat hai...")

### 5. Main Interview Loop (`run_voice_interview`)
- 3 turns: generate question via `run_conductor()` → speak it → listen for voice answer → log transcript
- After each answer: press Enter to continue (user controls pacing)
- After turn 3: runs `run_scorer()` → prints full score report → speaks summary
- Saves everything to `outputs/voice_interview_result.json`

### 6. README Update
- Added "Voice Interview Mode" section with setup instructions and Windows pyaudio workaround

---

## Problems Faced & Resolutions

### Problem 1: Hard phrase_time_limit cutting off long answers
**Symptom**: With `phrase_time_limit=60`, the recorder cut off candidates mid-sentence.
**Fix**: Changed to adaptive listening with `phrase_time_limit=None` (natural pause detection via `pause_threshold=2.0`). Later added `phrase_time_limit=30` as a safety net.

### Problem 2: Recording indicator never stops (spinner hangs)
**Symptom**: With `phrase_time_limit=None` + ambient noise, `listen()` never detected silence, the spinner kept spinning forever, and `stop_flag.set()` was never reached.
**Root cause**: `recognizer.listen()` blocks until `pause_threshold` seconds of silence. If room noise keeps energy above speech level, silence is never detected.
**Fix**: 
- Added `phrase_time_limit=30` as a hard safety cutoff
- Moved `stop_flag.set()` into a `finally` block so it runs even on exceptions

### Problem 3: Only first question spoken; subsequent questions only printed
**Symptom**: Q1 spoken via TTS correctly, Q2 and Q3 were printed but silent.
**Root cause**: `pyttsx3` on Windows has a known bug where reusing the same engine instance for sequential `speak()` calls causes later calls to silently fail. The engine state becomes corrupted.
**Initial attempted fix**: Restructured the loop to pre-fetch the next question and combine it with the acknowledgment. This failed because the user expected to hear the question at the start of each turn, not embedded in an acknowledgment.
**Final fix**: Changed `speak()` to create a **fresh pyttsx3 engine** on every single call (`_make_engine()` inside `speak()` instead of reusing a shared engine). This eliminated the state corruption entirely.

### Problem 4: Unnatural "Thank you" between turns
**Symptom**: AI saying "Thank you" after every answer felt robotic and impractical.
**Fix**: Replaced spoken acknowledgment with `input("Press Enter when you're ready for the next question...")` — user controls pacing.

### Problem 5: STT not understanding Indian English accents
**Symptom**: Google STT with default `"en-US"` had poor accuracy on Indian accents.
**Fix**: Changed to `recognize_google(audio, language="en-IN")`.

---

## Files Touched

| File | Action |
|------|--------|
| `voice_interview.py` | **Created** — 314 lines, all 5 components |
| `README.md` | **Modified** — Added Voice Interview Mode section |

No existing Python files were modified.
