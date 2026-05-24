import speech_recognition as sr
import io


def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """
    Transcribe audio bytes to text.
    language: "en" for en-IN, "hi" for hi-IN
    """
    recognizer = sr.Recognizer()
    lang_code = "hi-IN" if language == "hi" else "en-IN"

    audio_file = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        raise Exception(f"STT service error: {e}")
