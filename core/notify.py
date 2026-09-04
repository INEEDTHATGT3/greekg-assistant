import os
import sys

# Desktop toast notifications via win11toast are NOT safe to use from a thread
# that coexists with Tkinter's mainloop: win11toast.toast() calls asyncio.run()
# / get_running_loop(), which races _tkinter and hard-crashes the process (the
# app "closes on its own"). To avoid this, notifications are:
#   - written to a log file (always, non-fatal), and
#   - optionally surfaced as Windows toast ONLY when explicitly enabled in
#     settings AND the win11toast dependency is available.
# By default the GUI app shows status in-window, so toasts are disabled.
_TOAST_ENABLED = False

_LOG_DIR = os.path.join(os.path.expanduser("~"), ".greekg")


def configure(toast_enabled: bool = False):
    global _TOAST_ENABLED
    _TOAST_ENABLED = bool(toast_enabled)


def notify(title: str, message: str):
    _log(title, message)
    if not _TOAST_ENABLED:
        return
    _toast(title, message)


def _log(title: str, message: str):
    try:
        import datetime
        os.makedirs(_LOG_DIR, exist_ok=True)
        line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {title}: {message}\n"
        with open(os.path.join(_LOG_DIR, "notifications.log"), "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def _toast(title: str, message: str):
    # Uses a synchronous, SIG-free approach. If win11toast's threaded asyncio
    # proves unsafe here, this is a no-op and must simply stay disabled.
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONINFORMATION)
    except Exception:
        pass
