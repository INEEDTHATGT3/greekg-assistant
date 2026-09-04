import requests


class OllamaBackend:
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    def clean_transcript(self, raw_text: str, system_prompt: str, strict_retry: bool = False) -> str:
        system = system_prompt
        if strict_retry:
            system += (
                "\n\nREMINDER: Your previous attempt broke the rules above by being "
                "conversational. Output ONLY the corrected transcript text -- no "
                "questions, no commentary, nothing conversational."
            )
        payload = {
            "model": self.model,
            "system": system,
            "prompt": f"<transcript>{raw_text}</transcript>",
            "stream": False,
            "options": {"temperature": 0.0},
        }
        resp = requests.post(self.url, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["response"].strip()

    def test_connection(self) -> tuple[bool, str]:
        try:
            resp = requests.get(self.url.replace("/api/generate", "/api/tags"), timeout=5)
            resp.raise_for_status()
            return True, "Connected"
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach Ollama. Is it running?"
        except Exception as e:
            return False, str(e)


CONVERSATIONAL_RED_FLAGS = (
    "could you", "can you clarify", "what would you like", "i'd be happy to",
    "sure!", "sure,", "here is", "here's the", "let me know", "happy to help",
)


def looks_conversational(text: str) -> bool:
    lower = text.lower().strip()
    if lower.endswith("?"):
        return True
    return any(flag in lower[:80] for flag in CONVERSATIONAL_RED_FLAGS)
