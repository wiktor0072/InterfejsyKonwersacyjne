import subprocess
import tempfile
import os
from typing import Optional

try:
    from google.cloud import speech

    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    speech = None


class AudioService:
    def __init__(self, gcp_key_path: str = "gcp_key.json"):
        if not SPEECH_AVAILABLE:
            raise ImportError(
                "google-cloud-speech not installed. Run: uv pip install google-cloud-speech"
            )

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        key_path = os.path.join(base_dir, gcp_key_path)

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"GCP key file not found: {key_path}")

        self.speech_client = speech.SpeechClient.from_service_account_file(key_path)
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="pl-PL",
            enable_automatic_punctuation=True,
        )

    def transcode_webm_to_linear16(self, webm_data: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
            webm_file.write(webm_data)
            webm_path = webm_file.name

        wav_path = webm_path.replace(".webm", ".wav")

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    webm_path,
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-f",
                    "s16le",
                    wav_path,
                ],
                capture_output=True,
                check=True,
            )

            with open(wav_path, "rb") as wav_file:
                return wav_file.read()
        finally:
            if os.path.exists(webm_path):
                os.unlink(webm_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def transcribe(self, audio_data: bytes, is_webm: bool = True) -> Optional[str]:
        if is_webm:
            audio_data = self.transcode_webm_to_linear16(audio_data)

        audio = speech.RecognitionAudio(content=audio_data)
        response = self.speech_client.recognize(config=self.config, audio=audio)

        if response.results:
            return response.results[0].alternatives[0].transcript
        return None


audio_service: Optional[AudioService] = None


def get_audio_service() -> Optional[AudioService]:
    global audio_service
    if audio_service is None:
        try:
            audio_service = AudioService()
        except Exception:
            return None
    return audio_service
