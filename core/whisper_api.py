import requests


class APIWhisperSTT:
    def __init__(self, api_url: str, api_key: str, model: str = "whisper-1"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def transcribe(self, wav_path: str) -> str:
        with open(wav_path, "rb") as f:
            files = {"file": (wav_path, f, "audio/wav")}
            data = {"model": self.model, "language": "en"}
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            resp = requests.post(self.api_url, files=files, data=data, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.json().get("text", "").strip()
