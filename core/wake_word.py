import time
import numpy as np


class WakeWordDetector:
    def __init__(self, model_name="hey_jarvis", threshold=0.5, cooldown=3.0):
        self.model_name = model_name
        self.threshold = threshold
        self.cooldown = cooldown
        self._model = None
        self._last_trigger = 0.0
        self.enabled = False

    def load(self):
        try:
            from openwakeword.model import Model as OWWModel
            self._model = OWWModel(wakeword_models=[self.model_name])
            self.enabled = True
        except Exception:
            self._model = None
            self.enabled = False

    def predict(self, audio_int16: np.ndarray) -> float:
        if not self.enabled or self._model is None:
            return 0.0
        predictions = self._model.predict(audio_int16)
        return predictions.get(self.model_name, 0.0)

    def should_trigger(self, score: float) -> bool:
        now = time.time()
        if score > self.threshold and (now - self._last_trigger) > self.cooldown:
            self._last_trigger = now
            return True
        return False
