from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import sys
import os
import uuid
import asyncio
import traceback

_WEB_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJ_DIR = os.path.dirname(_WEB_DIR)
sys.path.append(_PROJ_DIR)
sys.path.append(_WEB_DIR)
from conductor import run_conductor
from scorer import run_scorer
from cheating import CheatingDetector
from tts import text_to_speech_file
from stt import transcribe_audio
from role_config import get_enriched_role, get_hiring_bar, get_role_config
from question_bank import QuestionBank

app = FastAPI(title="AI Interview Platform")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("web/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="web/static"), name="static")

sessions: dict = {}

_qbank = QuestionBank()


def _rag_target_role(session: dict) -> str:
    enriched = session["enriched_role"]
    context = _qbank.get_question_context(
        session["profile"]["role_key"], session["qa_pairs"]
    )
    if context:
        return enriched + "\n\n" + context
    return enriched


def _resolve_role(role_key: str, target_role: str) -> str:
    cfg = get_role_config(role_key)
    title = cfg["title"]
    context = cfg["context"]
    # Use the custom target_role if provided, else use context from config
    if target_role and target_role.lower() != title.lower():
        return f"{target_role} — focus: {context.split('— focus:')[1].strip() if '— focus:' in context else context}"
    return context


@app.get("/")
async def root():
    return FileResponse("web/static/index.html")


@app.post("/api/start")
async def start_interview(body: dict):
    try:
        session_id = uuid.uuid4().hex

        profile = {
            "icp_type": body["icp_type"],
            "role_key": body.get("role_key", "software_engineer"),
            "target_role": body["target_role"],
            "round_type": body.get("round_type", "screening"),
            "company_tier": body.get("company_tier", "mid"),
            "language": body["language"],
        }
        max_turns = body.get("max_turns", 3)
        enriched_role = _resolve_role(profile["role_key"], profile["target_role"])

        sessions[session_id] = {
            "profile": profile,
            "enriched_role": enriched_role,
            "qa_pairs": [],
            "transcript": [],
            "conductor_outputs": [],
            "current_question": None,
            "current_question_obj": None,
            "turn": 0,
            "max_turns": max_turns,
            "cheating_detector": CheatingDetector(),
            "hiring_bar": get_hiring_bar(profile["role_key"], profile["icp_type"]),
            "score_report": None,
        }

        opening = (
            "Hello! Welcome to your mock interview. We will go through 3 questions. Take your time."
            if profile["language"] == "en"
            else "Namaste! Mock interview mein swagat hai. Hum 3 sawaal karenge. Aaram se jawab dijiye."
        )

        audio_file = text_to_speech_file(opening, profile["language"])

        return {
            "session_id": session_id,
            "opening_text": opening,
            "opening_audio_url": f"/{audio_file}",
            "total_turns": max_turns,
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to start interview: {str(e)}"})


@app.post("/api/question/{session_id}")
async def get_next_question(session_id: str, body: dict = None):
    try:
        session = sessions.get(session_id)
        if not session:
            return JSONResponse(status_code=404, content={"error": "Session not found"})

        profile = session["profile"]

        output = run_conductor(
            icp_type=profile["icp_type"],
            target_role=_rag_target_role(session),
            round_type=profile["round_type"],
            company_tier=profile["company_tier"],
            language=profile["language"],
            previous_qa_pairs=session["qa_pairs"],
        )

        session["conductor_outputs"].append(output)
        session["current_question"] = output["next_question"]
        session["current_question_obj"] = output

        audio_file = text_to_speech_file(output["next_question"], profile["language"])

        return {
            "question": output["next_question"],
            "question_type": output["question_type"],
            "difficulty_level": output["difficulty_level"],
            "reasoning": output["reasoning"],
            "audio_url": f"/{audio_file}",
            "turn": session["turn"] + 1,
            "total_turns": session["max_turns"],
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to generate question: {str(e)}"})


@app.post("/api/answer/{session_id}")
async def submit_answer(session_id: str, audio: UploadFile = File(...)):
    try:
        session = sessions.get(session_id)
        if not session:
            return JSONResponse(status_code=404, content={"error": "Session not found"})

        audio_bytes = await audio.read()
        language = session["profile"]["language"]
        transcript = transcribe_audio(audio_bytes, language)

        qa_pair = {
            "question": session["current_question"],
            "answer_transcript": transcript,
        }
        session["qa_pairs"].append(qa_pair)
        session["transcript"].append({
            "question": session["current_question"],
            "answer": transcript,
        })
        session["turn"] += 1

        is_last_turn = session["turn"] >= session["max_turns"]
        next_question = None
        audio_url = None

        if not is_last_turn:
            output = run_conductor(
                icp_type=session["profile"]["icp_type"],
                target_role=_rag_target_role(session),
                round_type=session["profile"]["round_type"],
                company_tier=session["profile"]["company_tier"],
                language=session["profile"]["language"],
                previous_qa_pairs=session["qa_pairs"],
            )
            session["conductor_outputs"].append(output)
            session["current_question"] = output["next_question"]
            session["current_question_obj"] = output
            next_question = output["next_question"]
            audio_file = text_to_speech_file(output["next_question"], session["profile"]["language"])
            audio_url = f"/{audio_file}"

        return {
            "transcript": transcript,
            "turn": session["turn"],
            "total_turns": session["max_turns"],
            "is_last_turn": is_last_turn,
            "next_question": next_question,
            "next_audio_url": audio_url,
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to process answer: {str(e)}"})


@app.post("/api/score/{session_id}")
async def score_interview(session_id: str):
    try:
        session = sessions.get(session_id)
        if not session:
            return JSONResponse(status_code=404, content={"error": "Session not found"})

        score_report = run_scorer(
            full_transcript=session["transcript"],
            icp_type=session["profile"]["icp_type"],
            target_role=session["enriched_role"],
            round_type=session["profile"]["round_type"],
            hiring_bar=session["hiring_bar"],
        )

        session["score_report"] = score_report

        cheating_report = session["cheating_detector"].get_final_report()

        return {
            "score_report": score_report,
            "cheating_report": cheating_report,
            "hiring_bar": session["hiring_bar"],
            "transcript": session["transcript"],
            "profile": session["profile"],
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to score interview: {str(e)}"})


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = sessions.get(session_id)
    if not session:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return

    detector = session["cheating_detector"]

    try:
        while True:
            raw = await websocket.receive()
            if raw["type"] == "websocket.receive" and "bytes" in raw and raw["bytes"]:
                status = detector.analyze_frame(raw["bytes"])
                await websocket.send_json(status)
            elif raw["type"] == "websocket.receive" and "text" in raw and raw["text"]:
                try:
                    payload = json.loads(raw["text"])
                    status = detector.log_analysis(payload)
                    await websocket.send_json(status)
                except json.JSONDecodeError:
                    pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
