from gtts import gTTS
import os
import uuid


def text_to_speech_file(text: str, language: str = "en") -> str:
    """
    Convert text to speech and save as mp3.
    Returns the file path relative to web/.
    language: "en" for English, "hi" for Hindi
    """
    lang_code = "hi" if language == "hi" else "en"
    filename = f"static/audio_{uuid.uuid4().hex[:8]}.mp3"
    os.makedirs("web/static", exist_ok=True)
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(f"web/{filename}")
    return filename
