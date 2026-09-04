import os
import time
import threading
import customtkinter as ctk

from gui.widgets import FeatureCard
from config.settings import get, load_apps_config


class LaunchTab(ctk.CTkFrame):
    def __init__(self, parent, audio_stream, on_status=None):
        super().__init__(parent, fg_color="transparent")
        self._audio = audio_stream
        self._on_status = on_status
        self._is_recording = False
        self._frames = []
        self._record_start = 0.0
        self._debounce_last = 0.0
        self._whisper = None
        self._apps = load_apps_config()
        self._load_whisper()

        self._build_ui()
        self._audio.on("audio_chunk", self._on_audio_chunk)

    def _load_whisper(self):
        stt = get("whisper.backend", "local")
        if stt == "local":
            from core.whisper_local import LocalWhisperSTT
            self._whisper = LocalWhisperSTT(get("whisper.local_model_size"), get("whisper.local_device"))
        else:
            from core.whisper_api import APIWhisperSTT
            self._whisper = APIWhisperSTT(get("whisper.api_url"), get("whisper.api_key"), get("whisper.api_model"))

    def reload_backends(self):
        self._load_whisper()
        self._apps = load_apps_config()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self._card = FeatureCard(self, title="Voice App Launch", on_action=self._toggle_recording, button_text="Start Recording (F8)")
        self._card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)

        apps_text = ", ".join(self._apps.keys()) if self._apps else "None configured (edit apps_config.json)"
        hint = ctk.CTkLabel(self, text=f"Press F8 or click. Say an app name (e.g. 'open highlight'). Apps: {apps_text}",
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
        self._audio.current_mode = "launch"
        self._frames = []
        self._record_start = time.time()
        self._card.post_status("Recording...", "red")
        self._card.post_button_text("Stop Recording (F8)")
        self._card.post_log("Recording started...")
        if self._on_status:
            self._on_status("Recording (Launch)")
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
        self._card.post_button_text("Start Recording (F8)")
        if self._on_status:
            self._on_status("Processing (Launch)")

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

            self._card.post_log(f'Heard: "{raw_text}"')

            from core.app_launcher import AppLauncher
            launcher = AppLauncher(self._apps)
            success, msg = launcher.find_and_launch(raw_text)
            self._card.post_log(msg)
            self._card.post_status("Idle", "green" if success else "red")
            if self._on_status:
                self._on_status("Idle")

        except Exception as e:
            self._card.post_status("Error", "red")
            self._card.post_log(f"Error: {e}")
            if self._on_status:
                self._on_status("Error")
