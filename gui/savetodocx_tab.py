import threading
import customtkinter as ctk

from gui.widgets import FeatureCard
from core.clipboard import get_clipboard
from core.docx_export import save_clipboard_to_docx
from core.notify import notify


class SaveToDocxTab(ctk.CTkFrame):
    def __init__(self, parent, on_status=None):
        super().__init__(parent, fg_color="transparent")
        self._on_status = on_status
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self._card = FeatureCard(self, title="Save to Word", on_action=self._save, button_text="Save Clipboard (F10)")
        self._card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)

        hint = ctk.CTkLabel(self, text="Copy text (Ctrl+C), then press F10 or click to append it to today's .docx file.",
                            text_color="gray", font=("", 11), wraplength=600)
        hint.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

    def _save(self):
        self._card.post_button_state("disabled")
        self._card.post_status("Saving...", "orange")
        if self._on_status:
            self._on_status("Saving to Word")
        threading.Thread(target=self._do_save, daemon=True).start()

    def _do_save(self):
        try:
            content = get_clipboard()
            if not content or not content.strip():
                self._card.post_status("Idle", "gray")
                self._card.post_log("Clipboard is empty — copy text first.")
                if self._on_status:
                    self._on_status("Idle")
                return

            success, msg = save_clipboard_to_docx(content)
            self._card.post_log(msg)
            self._card.post_status("Idle", "green" if success else "red")
            notify("GreekG — Saved", msg)
            if self._on_status:
                self._on_status("Idle")

        except Exception as e:
            self._card.post_status("Error", "red")
            self._card.post_log(f"Error: {e}")
        finally:
            self._card.post_button_state("normal")

    def trigger_save(self):
        self._save()
