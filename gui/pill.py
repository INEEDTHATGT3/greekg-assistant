import customtkinter as ctk
from config.settings import get, set


class FloatingPill(ctk.CTkToplevel):
    """A small always-on-top, draggable pill that floats over the user's work.

    Collapsed by default: a slim status pill. Click to expand into a wider bar
    showing quick-action buttons and, when enabled, the last transcript + prompt.

    All public methods are safe to call from any thread: they marshal widget
    updates onto the Tk main thread via after(0, ...).
    """

    COLLAPSED_W = 190
    COLLAPSED_H = 44
    EXPANDED_W = 360
    EXPANDED_H = 220
    CORNER_MARGIN = 12
    SNAP_THRESHOLD = 60

    def __init__(self, on_dictate=None, on_launch=None, on_save=None, on_open=None):
        super().__init__()
        self.withdraw()
        self.overrideredirect(True)  # no window chrome -> small pill look
        self.attributes("-topmost", True)
        self.configure(fg_color=("gray80", "gray22"))

        self._on_dictate = on_dictate
        self._on_launch = on_launch
        self._on_save = on_save
        self._on_open = on_open

        self._expanded = False
        self._drag_offset = None
        self._status = "Idle"
        self._status_color = "gray"
        self._transcript = ""
        self._prompt = ""

        self._status_label = None
        self._frame = None
        self._build_ui()

        # corner-dock + opacity settings
        self._corner = get("general.pill_corner", "br")
        self._apply_opacity()

        x, y = self._load_position()
        self.geometry(f"{self.COLLAPSED_W}x{self.COLLAPSED_H}+{x}+{y}")
        self.deiconify()
        self._bind_drag(self._pill_bar)
        try:
            self._last_screen = (self.winfo_screenwidth(), self.winfo_screenheight())
        except Exception:
            self._last_screen = None
        self.bind("<Configure>", self._on_configure)

    def _apply_opacity(self):
        try:
            opacity = float(get("general.pill_opacity", 0.9))
            opacity = max(0.2, min(1.0, opacity))
            self.attributes("-alpha", opacity)
        except Exception:
            pass

    def set_corner(self, corner: str):
        """Re-dock the pill to one of the 4 screen corners (tl/tr/bl/br) or 'free'."""
        self._corner = corner
        set("general.pill_corner", corner)
        if corner and corner != "free":
            self._apply_opacity()
            self._snap_to_corner()

    def set_opacity(self, opacity: float):
        opacity = max(0.2, min(1.0, float(opacity)))
        set("general.pill_opacity", opacity)
        self._apply_opacity()

    def _snap_to_corner(self):
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            w = self.EXPANDED_W if self._expanded else self.COLLAPSED_W
            h = self.EXPANDED_H if self._expanded else self.COLLAPSED_H
            m = self.CORNER_MARGIN
            c = self._corner
            if c == "tl":
                x, y = m, m
            elif c == "tr":
                x, y = sw - w - m, m
            elif c == "bl":
                x, y = m, sh - h - m
            else:  # br default
                x, y = sw - w - m, sh - h - m
            self.geometry(f"+{int(x)}+{int(y)}")
            set("general.pill_x", int(x))
            set("general.pill_y", int(y))
        except Exception:
            pass

    def _on_configure(self, _event=None):
        # Re-dock only when the screen/display size actually changes (resolution
        # switch, monitor plug), not on ordinary resizes/moves — the latter would
        # fight the user/drag and disturb teardown.
        if not (self._corner and self._corner != "free"):
            return
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
        except Exception:
            return
        last = getattr(self, "_last_screen", None)
        if last == (sw, sh):
            return
        self._last_screen = (sw, sh)
        self._snap_to_corner()

    # ---- UI construction -------------------------------------------------
    def _build_ui(self):
        self._pill_bar = ctk.CTkFrame(self, corner_radius=22, fg_color=self.cget("fg_color"))
        self._pill_bar.pack(fill="both", expand=True, padx=2, pady=2)

        self._status_dot = ctk.CTkLabel(self._pill_bar, text="●", text_color=self._status_color,
                                        width=16, font=("", 12))
        self._status_dot.pack(side="left", padx=(12, 2))

        self._status_label = ctk.CTkLabel(self._pill_bar, text="Idle", font=("", 12))
        self._status_label.pack(side="left", padx=(0, 8))

        self._expand_hint = ctk.CTkLabel(self._pill_bar, text="▾", text_color="gray", font=("", 12))
        self._expand_hint.pack(side="right", padx=(0, 10))

        self._pill_bar.bind("<Button-1>", self._on_click)
        self._status_dot.bind("<Button-1>", self._on_click)
        self._status_label.bind("<Button-1>", self._on_click)

    def _build_expanded(self):
        self._expanded_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=self.cget("fg_color"))
        self._expanded_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self._expanded_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self._expanded_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="GreekG", font=("", 12, "bold")).grid(row=0, column=0, sticky="w")
        self._collapse_btn = ctk.CTkButton(header, text="▴", width=24, height=22, command=self.collapse)
        self._collapse_btn.grid(row=0, column=1, sticky="e")

        self._live_status = ctk.CTkLabel(self._expanded_frame, text=self._status, text_color=self._status_color,
                                         font=("", 12), anchor="w")
        self._live_status.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 2))

        self._live_text = ctk.CTkTextbox(self._expanded_frame, height=90, state="disabled",
                                         font=("Consolas", 11), wrap="word")
        self._live_text.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 6))

        btn_row = ctk.CTkFrame(self._expanded_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        btn_row.grid_columnconfigure(tuple(range(4)), weight=1)
        ctk.CTkButton(btn_row, text="Dictate", height=30, command=lambda: self._call(self._on_dictate)).grid(
            row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(btn_row, text="Launch", height=30, command=lambda: self._call(self._on_launch)).grid(
            row=0, column=1, padx=2, sticky="ew")
        ctk.CTkButton(btn_row, text="Save", height=30, command=lambda: self._call(self._on_save)).grid(
            row=0, column=2, padx=2, sticky="ew")
        ctk.CTkButton(btn_row, text="Open", height=30, command=lambda: self._call(self._on_open)).grid(
            row=0, column=3, padx=2, sticky="ew")

        self._bind_drag(self._expanded_frame)

    # ---- public API (thread-safe) ---------------------------------------
    def _post(self, fn):
        try:
            self.after(0, fn)
        except Exception:
            pass

    def set_status(self, text: str, color="gray"):
        self._post(lambda: self._apply_status(text, color))

    def set_transcript(self, text: str):
        self._post(lambda: self._apply_transcript(text))

    def set_prompt(self, text: str):
        self._post(lambda: self._apply_prompt(text))

    def toggle(self):
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def show(self):
        self._post(self.deiconify)

    def hide(self):
        self._post(self.withdraw)

    # ---- internal --------------------------------------------------------
    def _apply_status(self, text, color):
        self._status = text
        self._status_color = color
        if self._status_label is not None:
            self._status_label.configure(text=text)
        if self._status_dot is not None:
            self._status_dot.configure(text_color=color)
        if getattr(self, "_live_status", None) is not None:
            self._live_status.configure(text=text, text_color=color)

    def _apply_transcript(self, text):
        self._transcript = text
        if self._expanded and getattr(self, "_live_text", None) is not None:
            self._update_live_text()

    def _apply_prompt(self, text):
        self._prompt = text
        if self._expanded and getattr(self, "_live_text", None) is not None:
            self._update_live_text()

    def _update_live_text(self):
        if not get("general.live_preview", True):
            return
        parts = []
        if self._transcript:
            parts.append(f"[Spoken]\n{self._transcript}")
        if self._prompt:
            parts.append(f"\n[Prompt]\n{self._prompt}")
        text = "\n".join(parts) if parts else self._status
        self._live_text.configure(state="normal")
        self._live_text.delete("1.0", "end")
        self._live_text.insert("1.0", text)
        self._live_text.configure(state="disabled")

    def expand(self):
        self._post(self._do_expand)

    def collapse(self):
        self._post(self._do_collapse)

    def _do_expand(self):
        if self._expanded:
            return
        self._expanded = True
        self._pill_bar.pack_forget()
        if getattr(self, "_expanded_frame", None) is None:
            self._build_expanded()
        else:
            self._expanded_frame.pack(fill="both", expand=True, padx=4, pady=4)
        x, y = self._current_xy()
        self.geometry(f"{self.EXPANDED_W}x{self.EXPANDED_H}+{x}+{y}")
        self._apply_status(self._status, self._status_color)
        self._update_live_text()
        if self._corner and self._corner != "free":
            self._snap_to_corner()

    def _do_collapse(self):
        if not self._expanded:
            return
        self._expanded = False
        if getattr(self, "_expanded_frame", None) is not None:
            self._expanded_frame.pack_forget()
        self._pill_bar.pack(fill="both", expand=True, padx=2, pady=2)
        x, y = self._current_xy()
        self.geometry(f"{self.COLLAPSED_W}x{self.COLLAPSED_H}+{x}+{y}")
        if self._corner and self._corner != "free":
            self._snap_to_corner()

    def _current_xy(self):
        try:
            x = self.winfo_x()
            y = self.winfo_y()
            return x, y
        except Exception:
            return 0, 0

    def _load_position(self):
        from config.settings import get as g
        x = g("general.pill_x")
        y = g("general.pill_y")
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            if x is None:
                x = sw - self.COLLAPSED_W - 40
            if y is None:
                y = sh - self.COLLAPSED_H - 120
            x = max(0, min(int(x), sw - 10))
            y = max(0, min(int(y), sh - 10))
        except Exception:
            x = x if x is not None else 100
            y = y if y is not None else 100
        return int(x), int(y)

    def _save_position(self):
        try:
            set("general.pill_x", self.winfo_x())
            set("general.pill_y", self.winfo_y())
        except Exception:
            pass

    def _on_click(self, _event=None):
        if not self._expanded:
            self.expand()
        # clicking the collapsed pill expands; clicking expanded header collapses via button

    def _bind_drag(self, widget):
        for w in (widget,) if isinstance(widget, (list, tuple)) else self._drag_targets(widget):
            w.bind("<ButtonPress-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_move)
            w.bind("<ButtonRelease-1>", self._on_drag_end)

    def _drag_targets(self, widget):
        return [widget]

    def _on_drag_start(self, event):
        try:
            self._drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())
        except Exception:
            self._drag_offset = (0, 0)

    def _on_drag_move(self, event):
        if self._drag_offset is None:
            return
        try:
            self.geometry(f"+{event.x_root - self._drag_offset[0]}+{event.y_root - self._drag_offset[1]}")
        except Exception:
            pass

    def _on_drag_end(self, _event=None):
        self._drag_offset = None
        nearest = self._nearest_corner()
        if nearest:
            self._corner = nearest
            set("general.pill_corner", nearest)
            self._snap_to_corner()
        else:
            if self._corner and self._corner != "free":
                self._corner = "free"
                set("general.pill_corner", "free")
            self._save_position()

    def _nearest_corner(self):
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = self.winfo_x()
            y = self.winfo_y()
            w = self.EXPANDED_W if self._expanded else self.COLLAPSED_W
            h = self.EXPANDED_H if self._expanded else self.COLLAPSED_H
            # pill's own 4 corners
            pill_corners = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
            screen_corners = {
                "tl": (0, 0),
                "tr": (sw, 0),
                "bl": (0, sh),
                "br": (sw, sh),
            }
            best, best_d = None, None
            for name, (sx, sy) in screen_corners.items():
                # minimum distance from any pill corner to this screen corner
                d = min(((px - sx) ** 2 + (py - sy) ** 2) ** 0.5 for px, py in pill_corners)
                if best_d is None or d < best_d:
                    best_d, best = d, name
            if best_d is not None and best_d <= self.SNAP_THRESHOLD:
                return best
        except Exception:
            pass
        return None

    def _call(self, fn):
        if fn:
            try:
                fn()
            except Exception:
                pass
