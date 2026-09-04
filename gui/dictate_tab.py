import os
import time
import threading
import tempfile
import customtkinter as ctk
import numpy as np
import soundfile as sf

from gui.widgets import FeatureCard
from config.settings import get
from core.audio import SAMPLE_RATE
from core.ai_ollama import looks_conversational
from core.notify import notify


class DictateTab(ctk.CTkFrame):
    def __init__(self, parent, audio_stream, on_status=None, on_result=None):
        super().__init__(parent, fg_color="transparent")
        self._audio = audio_stream
        self._on_status = on_status
        self._on_result = on_result
        self._is_recording = False
        self._frames = []
        self._record_start = 0.0
        self._debounce_last = 0.0

        self._whisper = None
        self._ai_backend = None
        self._load_backends()

        self._build_ui()
        self._audio.on("audio_chunk", self._on_audio_chunk)

    def _load_backends(self):
        backend = get("ai.backend", "ollama")
        if backend == "ollama":
            from core.ai_ollama import OllamaBackend
            self._ai_backend = OllamaBackend(get("ai.ollama_url"), get("ai.ollama_model"))
        else:
            from core.ai_api import APIBackend
            self._ai_backend = APIBackend(get("ai.api_url"), get("ai.api_key"), get("ai.api_model"))

        stt = get("whisper.backend", "local")
        if stt == "local":
            from core.whisper_local import LocalWhisperSTT
            self._whisper = LocalWhisperSTT(get("whisper.local_model_size"), get("whisper.local_device"))
        else:
            from core.whisper_api import APIWhisperSTT
            self._whisper = APIWhisperSTT(get("whisper.api_url"), get("whisper.api_key"), get("whisper.api_model"))

    def reload_backends(self):
        self._load_backends()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self._card = FeatureCard(self, title="Dictate & Paste", on_action=self._toggle_recording, button_text="Start Recording (F9)")
        self._card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)

        hint = ctk.CTkLabel(self, text="Press F9 or click to start/stop. Speak, then stop — cleaned text is pasted into the focused window.",
                            text_color="gray", font=("", 11), wraplength=600)
        hint.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

    def _on_audio_chunk(self, indata, frames, time_info, status):
        if self._is_recording:
            self._frames.append(indata.copy())

    def _toggle_recording(self):
        now = time.time()
        if now - self._debounce_last < 0.4:
            return
        self._debounce_last = now

        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_and_process()

    def _start_recording(self):
        if self._audio.is_recording:
            self._card.post_log("Already recording in another mode.")
            return
        self._is_recording = True
        self._audio.is_recording = True
        self._audio.current_mode = "dictate"
        self._frames = []
        self._record_start = time.time()
        self._card.post_status("Recording...", "red")
        self._card.post_button_text("Stop Recording (F9)")
        self._card.post_log("Recording started...")
        if self._on_status:
            self._on_status("Recording (Dictate)")
        self._audio.beep(880, 120)

        max_sec = get("general.max_record_seconds", 90)
        threading.Thread(target=self._watchdog, args=(max_sec,), daemon=True).start()

    def _watchdog(self, max_sec):
        time.sleep(max_sec)
        if self._is_recording:
            self._card.post_log(f"Auto-stopped after {max_sec}s limit.")
            self._stop_and_process()

    def _stop_and_process(self):
        if not self._is_recording:
            return
        self._is_recording = False
        self._audio.is_recording = False
        self._audio.current_mode = None
        self._audio.beep(440, 120)

        duration = time.time() - self._record_start
        self._card.post_status("Processing...", "orange")
        self._card.post_button_text("Start Recording (F9)")
        if self._on_status:
            self._on_status("Processing (Dictate)")

        if duration < get("general.min_record_seconds", 0.4):
            self._card.post_status("Idle", "gray")
            self._card.post_log("Recording too short, ignored.")
            if self._on_status:
                self._on_status("Idle")
            return

        frames = self._frames.copy()
        threading.Thread(target=self._process, args=(frames,), daemon=True).start()

    def _process(self, frames):
        try:
            wav_path = self._audio.create_temp_wav(frames)
            self._card.post_log("Transcribing...")
            raw_text = self._whisper.transcribe(wav_path)
            try:
                os.remove(wav_path)
            except OSError:
                pass

            if not raw_text:
                self._card.post_status("Idle", "gray")
                self._card.post_log("No speech detected.")
                if self._on_status:
                    self._on_status("Idle")
                return

            if self._on_result:
                try:
                    self._on_result(raw_text, None)
                except Exception:
                    pass
            self._card.post_log(f"Raw: {raw_text}")
            self._card.post_log("Cleaning up via AI...")
            system_prompt = get("ai.system_prompt", "")
            cleaned = self._ai_backend.clean_transcript(raw_text, system_prompt)

            if looks_conversational(cleaned):
                self._card.post_log("AI broke character, retrying...")
                retry = self._ai_backend.clean_transcript(raw_text, system_prompt, strict_retry=True)
                if not looks_conversational(retry):
                    cleaned = retry
                else:
                    cleaned = raw_text[0].upper() + raw_text[1:] if raw_text else raw_text
                    self._card.post_log("Using raw transcript fallback.")

            self._card.post_log(f"Cleaned: {cleaned}")
            if self._on_result:
                try:
                    self._on_result(raw_text, cleaned)
                except Exception:
                    pass
            self._card.post_log("Pasting...")
            from core.clipboard import copy_text, paste_text
            copy_text(cleaned)
            paste_text()

            self._card.post_status("Idle", "gray")
            self._card.post_log("Done — pasted into focused window.")
            notify("GreekG — Pasted", cleaned[:120])
            if self._on_status:
                self._on_status("Idle")

        except Exception as e:
            self._card.post_status("Error", "red")
            self._card.post_log(f"Error: {e}")
            notify("GreekG — Error", str(e)[:150])
            if self._on_status:
                self._on_status("Error")
