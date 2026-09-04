import customtkinter as ctk


class StatusLog(ctk.CTkTextbox):
    def __init__(self, parent, height=150):
        super().__init__(parent, height=height, state="disabled", font=("Consolas", 12))
        self._max_lines = 200

    def log(self, text: str):
        self.configure(state="normal")
        self.insert("end", text + "\n")
        lines = int(self.index("end-1c").split(".")[0])
        if lines > self._max_lines:
            self.delete("1.0", f"{lines - self._max_lines}.0")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class FeatureCard(ctk.CTkFrame):
    def __init__(self, parent, title: str, on_action=None, button_text="Start"):
        super().__init__(parent, border_width=1, border_color=("gray70", "gray30"))
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)

        self._title = ctk.CTkLabel(header, text=title, font=("", 15, "bold"))
        self._title.grid(row=0, column=0, sticky="w")

        self._status = ctk.CTkLabel(header, text="Idle", text_color="gray")
        self._status.grid(row=0, column=1, sticky="e")

        self._action_btn = ctk.CTkButton(self, text=button_text, command=on_action, height=35, font=("", 13))
        self._action_btn.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        self._log = StatusLog(self, height=100)
        self._log.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def set_status(self, text: str, color="gray"):
        self._status.configure(text=text, text_color=color)

    def log(self, text: str):
        self._log.log(text)

    def clear_log(self):
        self._log.clear()

    def set_button_state(self, state: str):
        self._action_btn.configure(state=state)

    def set_button_text(self, text: str):
        self._action_btn.configure(text=text)

    def _post(self, fn):
        try:
            self.after(0, fn)
        except Exception:
            pass

    def post_status(self, text: str, color="gray"):
        self._post(lambda: self.set_status(text, color))

    def post_log(self, text: str):
        self._post(lambda: self.log(text))

    def post_button_text(self, text: str):
        self._post(lambda: self.set_button_text(text))

    def post_button_state(self, state: str):
        self._post(lambda: self.set_button_state(state))
