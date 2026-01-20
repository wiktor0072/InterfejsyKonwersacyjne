import sys
import os
from typing import Optional
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts.elevenlabs_tts import ElevenLabsTTS, ELEVENLABS_AVAILABLE


class TTSService:
    def __init__(self, voice_name: str = "Brian", model_id: str = "eleven_flash_v2_5"):
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                "elevenlabs package not installed. Run: uv pip install elevenlabs"
            )

        self.tts = ElevenLabsTTS(model_id=model_id)
        try:
            self.tts.select_voice(voice_name)
        except ValueError:
            print(f"[TTS] Voice '{voice_name}' not found, using default")

    def generate_audio(self, text: str) -> bytes:
        return self.tts.generate(text)

    def generate_audio_base64(self, text: str) -> str:
        audio_bytes = self.generate_audio(text)
        return base64.b64encode(audio_bytes).decode("utf-8")


tts_service: Optional[TTSService] = None


def get_tts_service() -> Optional[TTSService]:
    global tts_service
    if tts_service is None:
        try:
            tts_service = TTSService()
        except Exception as e:
            print(f"[TTS] Service unavailable: {e}")
            return None
    return tts_service
