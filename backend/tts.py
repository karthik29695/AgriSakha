import io
import logging
from typing import Optional

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from gtts import gTTS
import speech_recognition as sr

log = logging.getLogger("agrisakha-tts")


# ==================== TEXT TO SPEECH ====================
async def text_to_speech(text: str, lang: str = "en") -> StreamingResponse:
    """
    Convert text to speech in the given language.
    Returns an audio/mpeg stream.
    """

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="audio/mpeg")

    except Exception as e:
        log.error(f"TTS failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate speech."
        )


# ==================== SPEECH TO TEXT ====================
async def speech_to_text(
    audio_file: UploadFile,
    lang: Optional[str] = "en-IN"
) -> dict:
    """
    Convert voice input to text.
    Accepts WAV or MP3 audio files.
    """

    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Only audio files are allowed."
        )

    recognizer = sr.Recognizer()

    try:
        audio_bytes = await audio_file.read()
        audio_stream = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_stream) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(
            audio,
            language=lang
        )

        return {
            "text": text,
            "language": lang
        }

    except sr.UnknownValueError:
        raise HTTPException(
            status_code=400,
            detail="Could not understand the audio."
        )

    except sr.RequestError as e:
        log.error(f"Speech recognition service error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Speech recognition service unavailable."
        )

    except Exception as e:
        log.error(f"Speech to text failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process audio."
        )
