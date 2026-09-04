import os
import sys

_base = os.path.dirname(os.path.abspath(__file__))
if _base not in sys.path:
    sys.path.insert(0, _base)

from config.settings import load_settings, get


def main():
    settings = load_settings()

    minimize_to_tray = get("general.minimize_to_tray", True)

    from gui.app import create_app
    app = create_app()

    tray = None
    if minimize_to_tray:
        try:
            from gui.tray import TrayIcon
            tray = TrayIcon(app)
            tray.start()
            # window starts VISIBLE; the X button hides to tray to keep it quick-access
            app._close_to_tray = True
        except Exception:
            pass

    try:
        app.mainloop()
    finally:
        if tray:
            tray.stop()


if __name__ == "__main__":
    main()
