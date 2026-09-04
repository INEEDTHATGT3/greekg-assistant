import customtkinter as ctk
from config.settings import get, set, save_settings, set_auto_start


class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent, on_settings_changed=None, on_pill_config=None):
        super().__init__(parent, fg_color="transparent")
        self._on_settings_changed = on_settings_changed
        self._on_pill_config = on_pill_config
        self._build_ui()

    def _on_corner_change(self, label):
        for c, l in getattr(self._corner_menu, "_corner_map", []):
            if l == label:
                set("general.pill_corner", c)
                if self._on_pill_config:
                    self._on_pill_config("corner", c)
                save_settings()
                return
        self.save_settings()

    def _on_opacity_change(self, value):
        val = float(value)
        try:
            self._opacity_label.configure(text=f"{val*100:.0f}%")
        except Exception:
            pass
        set("general.pill_opacity", val)
        if self._on_pill_config:
            self._on_pill_config("opacity", val)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)

        row = 0

        # ── AI Backend ──
        ctk.CTkLabel(scroll, text="AI Backend (Grammar Cleanup)", font=("", 16, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1

        self._ai_backend_var = ctk.StringVar(value=get("ai.backend", "ollama"))
        ai_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ai_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        ai_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ai_frame, text="Backend:").grid(row=0, column=0, padx=(0, 10))
        ctk.CTkSegmentedButton(ai_frame, values=["ollama", "api"], variable=self._ai_backend_var,
                               command=self._on_ai_backend_change).grid(row=0, column=1, sticky="ew")
        row += 1

        self._ai_ollama_frame = ctk.CTkFrame(scroll)
        self._ai_ollama_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._ai_ollama_frame.grid_columnconfigure(1, weight=1)
        self._build_ollama_fields(self._ai_ollama_frame)
        row += 1

        self._ai_api_frame = ctk.CTkFrame(scroll)
        self._ai_api_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._ai_api_frame.grid_columnconfigure(1, weight=1)
        self._build_ai_api_fields(self._ai_api_frame)
        row += 1

        # ── Whisper Backend ──
        ctk.CTkLabel(scroll, text="Speech-to-Text (Whisper)", font=("", 16, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
        row += 1

        self._whisper_backend_var = ctk.StringVar(value=get("whisper.backend", "local"))
        ws_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ws_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        ws_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ws_frame, text="Backend:").grid(row=0, column=0, padx=(0, 10))
        ctk.CTkSegmentedButton(ws_frame, values=["local", "api"], variable=self._whisper_backend_var,
                               command=self._on_whisper_backend_change).grid(row=0, column=1, sticky="ew")
        row += 1

        self._whisper_local_frame = ctk.CTkFrame(scroll)
        self._whisper_local_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._whisper_local_frame.grid_columnconfigure(1, weight=1)
        self._build_whisper_local_fields(self._whisper_local_frame)
        row += 1

        self._whisper_api_frame = ctk.CTkFrame(scroll)
        self._whisper_api_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._whisper_api_frame.grid_columnconfigure(1, weight=1)
        self._build_whisper_api_fields(self._whisper_api_frame)
        row += 1

        # ── Hotkeys ──
        ctk.CTkLabel(scroll, text="Hotkeys", font=("", 16, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
        row += 1

        hk_frame = ctk.CTkFrame(scroll)
        hk_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        hk_frame.grid_columnconfigure(1, weight=1)
        self._hotkey_entries = {}
        for i, (name, label) in enumerate([("dictate", "Dictate (F9)"), ("launch", "Launch (F8)"), ("save_docx", "Save Word (F10)")]):
            ctk.CTkLabel(hk_frame, text=f"{label}:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(hk_frame)
            entry.insert(0, get(f"hotkeys.{name}", ""))
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self._hotkey_entries[name] = entry

        # Open GreekG (click-to-capture)
        ctk.CTkLabel(hk_frame, text="Open GreekG:").grid(row=len(self._hotkey_entries), column=0, padx=10, pady=5, sticky="w")
        self._toggle_capture_btn = ctk.CTkButton(
            hk_frame,
            text=get("hotkeys.toggle_ui", "ctrl+shift+g"),
            width=60,
            height=28,
            command=self._start_capture_toggle,
        )
        self._toggle_capture_btn.grid(row=len(self._hotkey_entries), column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(hk_frame, text="Click field, then press the key combo",
                     text_color="gray", font=("", 10)).grid(row=len(self._hotkey_entries) + 1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")
        row += 1

        # ── Features ──
        ctk.CTkLabel(scroll, text="Features", font=("", 16, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
        row += 1

        feat_frame = ctk.CTkFrame(scroll)
        feat_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._feature_toggles = {}
        for i, (key, label) in enumerate([
            ("dictate_enabled", "Dictate & Paste"),
            ("launch_enabled", "Voice App Launch"),
            ("save_docx_enabled", "Save to Word"),
            ("wake_word_enabled", "Wake Word Detection"),
        ]):
            var = ctk.BooleanVar(value=get(f"features.{key}", True))
            ctk.CTkSwitch(feat_frame, text=label, variable=var).grid(row=i, column=0, padx=15, pady=5, sticky="w")
            self._feature_toggles[key] = var
        row += 1

        # ── General ──
        ctk.CTkLabel(scroll, text="General", font=("", 16, "bold")).grid(row=row, column=0, sticky="w", padx=10, pady=(15, 5))
        row += 1

        gen_frame = ctk.CTkFrame(scroll)
        gen_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self._tray_var = ctk.BooleanVar(value=get("general.minimize_to_tray", True))
        ctk.CTkSwitch(gen_frame, text="Minimize to system tray", variable=self._tray_var).grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self._autostart_var = ctk.BooleanVar(value=get("general.auto_start_windows", False))
        ctk.CTkSwitch(gen_frame, text="Auto-start with Windows", variable=self._autostart_var).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self._notify_var = ctk.BooleanVar(value=get("general.notify_enabled", False))
        ctk.CTkSwitch(gen_frame, text="Audible feedback on events", variable=self._notify_var).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkLabel(gen_frame, text="(beep + log; desktop toasts disabled for stability)",
                     text_color="gray", font=("", 10)).grid(row=3, column=0, padx=15, pady=(0, 5), sticky="w")
        self._live_preview_var = ctk.BooleanVar(value=get("general.live_preview", True))
        ctk.CTkSwitch(gen_frame, text="Show transcript in floating pill", variable=self._live_preview_var).grid(row=4, column=0, padx=15, pady=5, sticky="w")
        row += 1

        # ── Floating pill frame ──
        pill_frame = ctk.CTkFrame(scroll)
        pill_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        pill_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pill_frame, text="Floating pill corner:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._corner_var = ctk.StringVar(value=get("general.pill_corner", "br"))
        corner_map = [("br", "Bottom-right"), ("bl", "Bottom-left"), ("tr", "Top-right"), ("tl", "Top-left"), ("free", "Free (drag)")]
        self._corner_menu = ctk.CTkOptionMenu(pill_frame, values=[c[1] for c in corner_map],
                                              command=self._on_corner_change)
        self._corner_menu._corner_map = corner_map
        for c, label in corner_map:
            if c == get("general.pill_corner", "br"):
                self._corner_menu.set(label)
        self._corner_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(pill_frame, text="Pill opacity:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._opacity_var = ctk.DoubleVar(value=float(get("general.pill_opacity", 0.9)))
        self._opacity_slider = ctk.CTkSlider(pill_frame, from_=0.3, to=1.0, number_of_steps=7,
                                             variable=self._opacity_var, command=self._on_opacity_change)
        self._opacity_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self._opacity_label = ctk.CTkLabel(pill_frame, text=f"{self._opacity_var.get()*100:.0f}%", width=40)
        self._opacity_label.grid(row=1, column=2, padx=10, pady=5, sticky="e")
        row += 1

        # ── Save Button ──
        ctk.CTkButton(scroll, text="Save Settings", command=self._save, height=40, font=("", 14, "bold")).grid(row=row, column=0, padx=10, pady=(20, 10), sticky="ew")
        row += 1

        self._on_ai_backend_change(self._ai_backend_var.get())
        self._on_whisper_backend_change(self._whisper_backend_var.get())

    def _build_ollama_fields(self, parent):
        ctk.CTkLabel(parent, text="URL:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._ollama_url = ctk.CTkEntry(parent)
        self._ollama_url.insert(0, get("ai.ollama_url", "http://localhost:11434/api/generate"))
        self._ollama_url.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="Model:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._ollama_model = ctk.CTkEntry(parent)
        self._ollama_model.insert(0, get("ai.ollama_model", "llama3.2"))
        self._ollama_model.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    def _build_ai_api_fields(self, parent):
        ctk.CTkLabel(parent, text="Endpoint URL:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._ai_api_url = ctk.CTkEntry(parent)
        self._ai_api_url.insert(0, get("ai.api_url", ""))
        self._ai_api_url.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="API Key:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._ai_api_key = ctk.CTkEntry(parent, show="*")
        self._ai_api_key.insert(0, get("ai.api_key", ""))
        self._ai_api_key.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="Model:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self._ai_api_model = ctk.CTkEntry(parent)
        self._ai_api_model.insert(0, get("ai.api_model", ""))
        self._ai_api_model.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def _build_whisper_local_fields(self, parent):
        ctk.CTkLabel(parent, text="Model Size:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._whisper_model_size = ctk.CTkSegmentedButton(parent, values=["tiny", "base", "small", "medium"],
                                                          variable=ctk.StringVar(value=get("whisper.local_model_size", "small")))
        self._whisper_model_size.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="Device:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._whisper_device = ctk.CTkSegmentedButton(parent, values=["auto", "cuda", "cpu"],
                                                      variable=ctk.StringVar(value=get("whisper.local_device", "auto")))
        self._whisper_device.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    def _build_whisper_api_fields(self, parent):
        ctk.CTkLabel(parent, text="Endpoint URL:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._whisper_api_url = ctk.CTkEntry(parent)
        self._whisper_api_url.insert(0, get("whisper.api_url", ""))
        self._whisper_api_url.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="API Key:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._whisper_api_key = ctk.CTkEntry(parent, show="*")
        self._whisper_api_key.insert(0, get("whisper.api_key", ""))
        self._whisper_api_key.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent, text="Model:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self._whisper_api_model = ctk.CTkEntry(parent)
        self._whisper_api_model.insert(0, get("whisper.api_model", "whisper-large-v3"))
        self._whisper_api_model.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def _on_ai_backend_change(self, value):
        if value == "ollama":
            self._ai_ollama_frame.grid()
            self._ai_api_frame.grid_remove()
        else:
            self._ai_ollama_frame.grid_remove()
            self._ai_api_frame.grid()

    def _on_whisper_backend_change(self, value):
        if value == "local":
            self._whisper_local_frame.grid()
            self._whisper_api_frame.grid_remove()
        else:
            self._whisper_local_frame.grid_remove()
            self._whisper_api_frame.grid()

    def _save(self):
        set("ai.backend", self._ai_backend_var.get())
        set("ai.ollama_url", self._ollama_url.get())
        set("ai.ollama_model", self._ollama_model.get())
        set("ai.api_url", self._ai_api_url.get())
        set("ai.api_key", self._ai_api_key.get())
        set("ai.api_model", self._ai_api_model.get())

        set("whisper.backend", self._whisper_backend_var.get())
        set("whisper.local_model_size", self._whisper_model_size.get())
        set("whisper.local_device", self._whisper_device.get())
        set("whisper.api_url", self._whisper_api_url.get())
        set("whisper.api_key", self._whisper_api_key.get())
        set("whisper.api_model", self._whisper_api_model.get())

        for name, entry in self._hotkey_entries.items():
            set(f"hotkeys.{name}", entry.get())

        for key, var in self._feature_toggles.items():
            set(f"features.{key}", var.get())

        set("general.minimize_to_tray", self._tray_var.get())
        set("general.live_preview", self._live_preview_var.get())
        set("general.pill_opacity", float(self._opacity_var.get()))
        for c, l in getattr(self._corner_menu, "_corner_map", []):
            if l == self._corner_menu.get():
                set("general.pill_corner", c)
                break

        notify_enabled = self._notify_var.get()
        set("general.notify_enabled", notify_enabled)
        from core import notify
        notify.configure(notify_enabled)

        autostart = self._autostart_var.get()
        set_auto_start(autostart)

        save_settings()
        if self._on_settings_changed:
            self._on_settings_changed()

    # ---- click-to-capture hotkey for "Open GreekG" ----
    def _start_capture_toggle(self):
        try:
            import keyboard
        except Exception:
            return
        if getattr(self, "_capturing", False):
            return
        self._capturing = True
        self._toggle_capture_btn.configure(text="Press combo...")
        self._capture_hook = keyboard.hook(self._on_capture_key)

    def _on_capture_key(self, event):
        if not getattr(self, "_capturing", False):
            return
        if event.event_type != "down":
            return
        try:
            import keyboard
            combo = [keyboard.get_hotkey_name(k) for k in (event.name or "").replace("-", " ").split()]
            hotkey_str = "+".join(combo)
            # wait for key release state; if a single key, keep listening till combo settles
            if not combo:
                return
            if self._validate_toggle_hotkey(hotkey_str):
                set("hotkeys.toggle_ui", hotkey_str)
                self.after(0, lambda: self._toggle_capture_btn.configure(text=hotkey_str))
            else:
                self.after(0, lambda: self._toggle_capture_btn.configure(text="Invalid/conflict"))
        finally:
            self.after(0, self._stop_capture_toggle)

    def _stop_capture_toggle(self):
        if not getattr(self, "_capturing", False):
            return
        self._capturing = False
        try:
            import keyboard
            keyboard.unhook(getattr(self, "_capture_hook", None))
        except Exception:
            pass
        self._capture_hook = None

    def _validate_toggle_hotkey(self, hotkey_str: str) -> bool:
        if not hotkey_str:
            return False
        low = hotkey_str.lower()
        if low in ("f9", "f8", "f10"):
            return False
        if low == get("hotkeys.toggle_ui", "").lower():
            return True
        # reject if it equals any other configured hotkey
        for k in ("dictate", "launch", "save_docx"):
            if low == get(f"hotkeys.{k}", "").lower():
                return False
        return True
