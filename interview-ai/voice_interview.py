# voice_interview.py
"""
Voice-based interview experience built on top of the existing pipeline.
Uses TTS (pyttsx3) to speak questions and STT (speech_recognition) to capture answers.
"""

import json
import os
import time

import pyttsx3
import speech_recognition as sr

from conductor import run_conductor
from scorer import run_scorer


# ── COMPONENT 1: TTS Engine Setup ──────────────────────────────────────────

def _make_engine():
    eng = pyttsx3.init()
    eng.setProperty('rate', 155)
    eng.setProperty('volume', 1.0)
    voices = eng.getProperty('voices')
    eng.setProperty('voice', voices[min(1, len(voices) - 1)].id)
    return eng


def speak(text):
    """Create a fresh engine per call to avoid pyttsx3 reuse bugs on Windows."""
    print(f"\n\U0001f399 INTERVIEWER: {text}\n")
    engine = _make_engine()
    engine.say(text)
    engine.runAndWait()


# ── COMPONENT 2: STT Functions ─────────────────────────────────────────────

def show_listening_indicator():
    import threading
    import sys

    stop_flag = threading.Event()

    def animate():
        chars = ["\u2be2", "\u2bfd", "\u2beb", "\u2baa", "\u2bbf", "\u2bdf", "\u2baf", "\u2bb7"]
        i = 0
        while not stop_flag.is_set():
            sys.stdout.write(f"\r  \U0001f3a4 Recording {chars[i % len(chars)]} ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r  \u2705 Got it!          \n")
        sys.stdout.flush()

    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()
    return stop_flag


def listen():
    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 2500
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 2.0
    recognizer.non_speaking_duration = 1.5
    recognizer.phrase_threshold = 0.3

    with sr.Microphone() as source:
        print("\U0001f3a4 Listening... (speak freely, pause when done)")
        print("   [Recording will stop 2 seconds after you stop speaking]\n")

        recognizer.adjust_for_ambient_noise(source, duration=1.5)

        stop_flag = None
        try:
            stop_flag = show_listening_indicator()

            # phrase_time_limit=30 acts as safety net if silence is never detected
            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=30
            )

            print("\u23f3 Processing your answer...")
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"\u2705 Captured: {text}\n")
            return text

        except sr.WaitTimeoutError:
            print("\u23f1 No speech detected in 8 seconds.")
            return None
        except sr.UnknownValueError:
            print("\u2753 Could not understand. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"\u274c STT error: {e}")
            return None
        finally:
            if stop_flag is not None:
                stop_flag.set()
                time.sleep(0.15)  # let animation thread print its final frame


# ── COMPONENT 3: ICP Selector ──────────────────────────────────────────────

def select_icp():
    print("\n" + "=" * 50)
    print("  INTERVIEW AI \u2014 VOICE MODE")
    print("=" * 50)
    print("\nSelect your profile:")
    print("  1 \u2192 Software Engineer (English)")
    print("  2 \u2192 CX Associate / Office Role (Hindi)")
    print()

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return {
                "icp_type": "high_wage",
                "target_role": "Software Engineer",
                "round_type": "screening",
                "company_tier": "mid",
                "language": "en"
            }
        elif choice == "2":
            return {
                "icp_type": "low_wage",
                "target_role": "CX Associate",
                "round_type": "behavioral",
                "company_tier": "startup",
                "language": "hi"
            }
        else:
            print("Please enter 1 or 2.")


# ── COMPONENT 4: Opening Message per ICP ───────────────────────────────────

def get_opening_message(icp_type):
    if icp_type == "high_wage":
        return (
            "Hello! Welcome to your mock interview. "
            "I am your AI interviewer today. "
            "We will go through 3 questions. "
            "Take your time and answer clearly. "
            "Let us begin."
        )
    else:
        return (
            "Namaste! Aapka mock interview mein swagat hai. "
            "Main aapka AI interviewer hoon. "
            "Hum 3 sawaal karenge. "
            "Aaram se jawab dijiye. "
            "Chaliye shuru karte hain."
        )


# ── COMPONENT 5: Main Voice Interview Loop ─────────────────────────────────

def run_voice_interview():
    profile = select_icp()

    hiring_bar = {
        "communication": 70, "technical": 65,
        "problem_solving": 70, "behavioral": 65, "delivery": 60
    } if profile["icp_type"] == "high_wage" else {
        "communication": 60, "technical": 40,
        "problem_solving": 55, "behavioral": 65, "delivery": 55
    }

    opening = get_opening_message(profile["icp_type"])
    speak( opening)
    time.sleep(1)

    transcript = []
    qa_pairs = []
    conductor_outputs = []
    TURNS = 3

    for turn in range(1, TURNS + 1):
        print(f"\n{'\u2500' * 40}")
        print(f"TURN {turn} of {TURNS}")
        print(f"{'\u2500' * 40}")

        output = run_conductor(
            icp_type=profile["icp_type"],
            target_role=profile["target_role"],
            round_type=profile["round_type"],
            company_tier=profile["company_tier"],
            language=profile["language"],
            previous_qa_pairs=qa_pairs
        )
        conductor_outputs.append(output)

        question = output["next_question"]
        difficulty = output["difficulty_level"]
        reasoning = output["reasoning"]

        print(f"[Difficulty: {difficulty}/5]")
        print(f"[Reasoning: {reasoning}]")

        speak( question)
        time.sleep(0.5)

        answer = None
        attempts = 0
        while answer is None and attempts < 3:
            attempts += 1
            if attempts == 1:
                prompt = (
                    "Take your time. I will wait until you finish speaking."
                    if profile["language"] == "en"
                    else "Aaram se boliye. Main tab tak sununga jab tak aap bolte rahenge."
                )
                speak( prompt)
            answer = listen()
            if answer is None and attempts < 3:
                retry_msg = (
                    "I did not catch that. Please speak clearly and "
                    "pause for 2 seconds when you are done."
                    if profile["language"] == "en"
                    else "Samajh nahi aaya. Thoda clearly boliye aur "
                         "khatam hone par 2 second ruko."
                )
                speak( retry_msg)

        if answer is None:
            answer = "No response provided."

        qa_pairs.append({
            "question": question,
            "answer_transcript": answer
        })
        transcript.append({
            "question": question,
            "answer": answer
        })

        if turn < TURNS:
            input("\nPress Enter when you're ready for the next question...")

    closing = (
        "Thank you for completing the interview. Analyzing your responses now."
        if profile["language"] == "en"
        else "Interview complete. Ab main aapke jawaabon ka analysis kar raha hoon."
    )
    speak( closing)

    print(f"\n{'=' * 50}")
    print("SCORING YOUR INTERVIEW...")
    print(f"{'=' * 50}")

    score_report = run_scorer(
        full_transcript=transcript,
        icp_type=profile["icp_type"],
        target_role=profile["target_role"],
        round_type=profile["round_type"],
        hiring_bar=hiring_bar
    )

    print(f"\n{'=' * 50}")
    print("INTERVIEW SCORE REPORT")
    print(f"{'=' * 50}")
    print(f"Overall Score: {score_report['overall_score']}/100")
    print(f"\nScores per axis:")
    axes = ["communication", "technical", "problem_solving", "behavioral", "delivery"]
    for axis in axes:
        score = score_report["scores_per_axis"][axis]
        gap = score_report["gap_vs_bar"][axis]
        bar = hiring_bar[axis]
        print(f"  {axis:<20} {score}/100  (bar: {bar}, gap: {gap:+d})")

    print(f"\nStrong Moment:")
    print(f"  \"{score_report['strong_moment']['quote']}\"")
    print(f"  \u2192 {score_report['strong_moment']['why_it_helped']}")

    print(f"\nWeak Moment:")
    print(f"  \"{score_report['weak_moment']['quote']}\"")
    print(f"  \u2192 {score_report['weak_moment']['why_it_hurt']}")

    print(f"\nNext Action: {score_report['next_action']}")

    summary = (
        f"Your overall score is {score_report['overall_score']} out of 100. "
        f"Your strongest area was communication. "
        f"Your recommended next action is: {score_report['next_action']}"
        if profile["language"] == "en"
        else
        f"Aapka overall score hai {score_report['overall_score']} out of 100. "
        f"Aapka sabse accha area tha communication. "
        f"Aapki agli practice: {score_report['next_action']}"
    )
    speak( summary)

    os.makedirs("outputs", exist_ok=True)
    output_data = {
        "profile": profile,
        "conductor_outputs": conductor_outputs,
        "transcript": transcript,
        "score_report": score_report
    }
    with open("outputs/voice_interview_result.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("\nFull result saved to outputs/voice_interview_result.json")
    return output_data


if __name__ == "__main__":
    run_voice_interview()
