import os
import sys
import time
import tempfile
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf

try:
    import importlib.metadata

    def _find_nvidia_dll_dir(dist_name: str):
        try:
            dist = importlib.metadata.distribution(dist_name)
        except importlib.metadata.PackageNotFoundError:
            return None
        for f in (dist.files or []):
            if str(f).lower().endswith(".dll"):
                return str(dist.locate_file(f).parent)
        return None

    def _register_cuda_dll_dirs():
        if os.name != "nt":
            return
        for dist_name in ("nvidia-cuda-runtime-cu12", "nvidia-cublas-cu12", "nvidia-cudnn-cu12"):
            dll_dir = _find_nvidia_dll_dir(dist_name)
            if dll_dir:
                os.add_dll_directory(dll_dir)

    _register_cuda_dll_dirs()
except Exception:
    pass


SAMPLE_RATE = 16000
CHUNK_SAMPLES = 1280


def pick_input_device():
    try:
        hostapis = sd.query_hostapis()
        wasapi_idx = next((i for i, h in enumerate(hostapis) if "wasapi" in h["name"].lower()), None)
        if wasapi_idx is None:
            return None
        devices = sd.query_devices()
        for idx, d in enumerate(devices):
            if d["hostapi"] == wasapi_idx and d["max_input_channels"] > 0:
                return idx
    except Exception:
        pass
    return None


class AudioStream:
    def __init__(self):
        self.is_recording = False
        self.current_mode = None
        self.current_triggered_by = None
        self.audio_frames = []
        self.record_start_time = None
        self.speech_confirmed = False
        self.last_voice_time = None
        self._last_toggle_time = {}
        self._callbacks = {}
        self._stream = None
        self._input_device = pick_input_device()

    def on(self, event: str, callback):
        self._callbacks.setdefault(event, []).append(callback)

    def _emit(self, event: str, *args, **kwargs):
        for cb in self._callbacks.get(event, []):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass

    def open(self):
        extra_settings = None
        if self._input_device is not None:
            try:
                hostapi_name = sd.query_hostapis(sd.query_devices(self._input_device)["hostapi"])["name"]
                if "wasapi" in hostapi_name.lower():
                    extra_settings = sd.WasapiSettings(auto_convert=True)
            except Exception:
                pass

        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                blocksize=CHUNK_SAMPLES, device=self._input_device,
                extra_settings=extra_settings, callback=self._audio_callback,
            )
            self._stream.start()
        except sd.PortAudioError:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                blocksize=CHUNK_SAMPLES, device=None, callback=self._audio_callback,
            )
            self._stream.start()

    def close(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        self._emit("audio_chunk", indata, frames, time_info, status)

    def beep(self, freq=880, dur_ms=120):
        try:
            import winsound
            winsound.Beep(freq, dur_ms)
        except Exception:
            pass

    def save_frames_to_wav(self, frames, path):
        audio = np.concatenate(frames, axis=0).flatten()
        sf.write(path, audio, SAMPLE_RATE)

    def create_temp_wav(self, frames):
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self.save_frames_to_wav(frames, tmp.name)
        return tmp.name
