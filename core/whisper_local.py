import os


class LocalWhisperSTT:
    def __init__(self, model_size="small", device="auto"):
        self.model_size = model_size
        self._device_hint = device
        self._model = None
        self._active_device = None

    def _load(self):
        if self._model is not None:
            return
        from faster_whisper import WhisperModel

        if self._device_hint == "auto":
            try:
                self._model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
                self._active_device = "cuda"
                return
            except Exception:
                pass

        try:
            self._model = WhisperModel(self.model_size, device=self._device_hint, compute_type="float16")
            self._active_device = self._device_hint
        except Exception:
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            self._active_device = "cpu"

    @property
    def device(self):
        self._load()
        return self._active_device

    def transcribe(self, wav_path: str) -> str:
        self._load()
        try:
            segments, _ = self._model.transcribe(wav_path, language="en")
            return " ".join(seg.text.strip() for seg in segments).strip()
        except Exception as e:
            if self._active_device == "cuda":
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self._active_device = "cpu"
                segments, _ = self._model.transcribe(wav_path, language="en")
                return " ".join(seg.text.strip() for seg in segments).strip()
            raise
