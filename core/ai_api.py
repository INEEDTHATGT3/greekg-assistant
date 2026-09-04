import requests


class APIBackend:
    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def clean_transcript(self, raw_text: str, system_prompt: str, strict_retry: bool = False) -> str:
        system = system_prompt
        if strict_retry:
            system += (
                "\n\nREMINDER: Your previous attempt broke the rules above by being "
                "conversational. Output ONLY the corrected transcript text -- no "
                "questions, no commentary, nothing conversational."
            )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"<transcript>{raw_text}</transcript>"},
        ]
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def test_connection(self) -> tuple[bool, str]:
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            base = self.api_url.rsplit("/", 1)[0] if "/chat/completions" in self.api_url else self.api_url
            resp = requests.get(base.replace("/chat/completions", "/models"), headers=headers, timeout=5)
            if resp.status_code == 200:
                return True, "Connected"
            return True, f"Endpoint reachable (status {resp.status_code})"
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach API endpoint"
        except Exception as e:
            return False, str(e)
