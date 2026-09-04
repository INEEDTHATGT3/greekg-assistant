import sys
import threading
import customtkinter as ctk

from config.settings import load_settings, get
from core.audio import AudioStream
from core import notify
from gui.pill import FloatingPill
from gui.dictate_tab import DictateTab
from gui.launch_tab import LaunchTab
from gui.savetodocx_tab import SaveToDocxTab
from gui.settings_tab import SettingsTab


class GreekGApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        load_settings()
        notify.configure(get("general.notify_enabled", False))
        self._setup_window()
        self._audio = AudioStream()
        self._audio.open()
        self._build_ui()
        self._build_pill()
        self._register_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_window(self):
        self.title("GreekG Assistant")
        self.geometry("720x680")
        self.minsize(600, 550)
        try:
            self.after(201, lambda: self.iconbitmap(default=""))
        except Exception:
            pass
        ctk.set_appearance_mode(get("general.theme", "dark"))
        ctk.set_default_color_theme("blue")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._status_var = ctk.StringVar(value="Idle")
        status_bar = ctk.CTkFrame(self, height=30, fg_color=("gray85", "gray20"))
        status_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        status_bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(status_bar, text="Status:", font=("", 12, "bold")).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(status_bar, textvariable=self._status_var, font=("", 12), text_color=("gray20", "gray70")).grid(row=0, column=1, sticky="w", padx=5)

        self._close_to_tray = False

        self._tabview = ctk.CTkTabview(self)
        self._tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self._tab_dictate = self._tabview.add("Dictate")
        self._tab_launch = self._tabview.add("App Launch")
        self._tab_save = self._tabview.add("Save to Word")
        self._tab_settings = self._tabview.add("Settings")

        self._dictate_tab = DictateTab(self._tab_dictate, self._audio, on_status=self._update_status, on_result=self._on_dictate_result)
        self._dictate_tab.pack(fill="both", expand=True, padx=5, pady=5)

        self._launch_tab = LaunchTab(self._tab_launch, self._audio, on_status=self._update_status)
        self._launch_tab.pack(fill="both", expand=True, padx=5, pady=5)

        self._save_tab = SaveToDocxTab(self._tab_save, on_status=self._update_status)
        self._save_tab.pack(fill="both", expand=True, padx=5, pady=5)

        self._settings_tab = SettingsTab(self._tab_settings, on_settings_changed=self._on_settings_changed, on_pill_config=self._on_pill_config)
        self._settings_tab.pack(fill="both", expand=True, padx=5, pady=5)

    def _update_status(self, text: str):
        self.after(0, lambda: self._status_var.set(text))
        if self._pill is not None:
            color = self._status_color(text)
            self._pill.set_status(text, color)

    @staticmethod
    def _status_color(text: str) -> str:
        t = text.lower()
        if "record" in t or "listen" in t:
            return "red"
        if "process" in t or "sav" in t:
            return "orange"
        if "error" in t or "fail" in t:
            return "red"
        if "pasted" in t or "down" in t or "saved" in t:
            return "green"
        return "gray"

    def _build_pill(self):
        self._pill = FloatingPill(
            on_dictate=self._dictate_tab._toggle_recording,
            on_launch=self._launch_tab._toggle_recording,
            on_save=self._save_tab.trigger_save,
            on_open=self._show_main_window,
        )

    def _on_dictate_result(self, raw, cleaned):
        if raw:
            self._pill.set_transcript(raw)
        if cleaned:
            self._pill.set_prompt(cleaned)

    def _on_pill_config(self, kind, value):
        if self._pill is None:
            return
        if kind == "corner":
            self._pill.set_corner(value)
        elif kind == "opacity":
            self._pill.set_opacity(value)

    def _show_main_window(self):
        self.deiconify()
        self.lift()
        self.after(0, lambda: self._status_var.set("Idle"))

    def toggle_pill(self):
        if self._pill is not None:
            self._pill.toggle()
            self._show_main_window()

    def _on_settings_changed(self):
        self._dictate_tab.reload_backends()
        self._launch_tab.reload_backends()

    def _register_hotkeys(self):
        import keyboard

        def debounce_wrap(fn):
            last = [0.0]
            def wrapped():
                import time
                now = time.time()
                if now - last[0] < 0.4:
                    return
                last[0] = now
                fn()
            return wrapped

        hk_dictate = get("hotkeys.dictate", "f9")
        hk_launch = get("hotkeys.launch", "f8")
        hk_save = get("hotkeys.save_docx", "f10")
        hk_toggle = get("hotkeys.toggle_ui", "ctrl+shift+g")

        keyboard.add_hotkey(hk_dictate, debounce_wrap(lambda: self.after(0, self._dictate_tab._toggle_recording)))
        keyboard.add_hotkey(hk_launch, debounce_wrap(lambda: self.after(0, self._launch_tab._toggle_recording)))
        keyboard.add_hotkey(hk_save, debounce_wrap(lambda: self.after(0, self._save_tab.trigger_save)))
        keyboard.add_hotkey(hk_toggle, debounce_wrap(lambda: self.after(0, self.toggle_pill)))

    def _on_close(self):
        if getattr(self, "_close_to_tray", False):
            self.withdraw()
        else:
            self.quit_app()

    def quit_app(self):
        if getattr(self, "_pill", None) is not None:
            try:
                self._pill.destroy()
            except Exception:
                pass
        self._audio.close()
        self.destroy()


def create_app():
    return GreekGApp()
