import sys
import threading

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None


def _create_icon_image(size=64):
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, size - 4, size - 4], fill=(50, 120, 200, 255))
        draw.text((size // 2 - 8, size // 2 - 10), "GG", fill="white")
        return img
    except Exception:
        return None


class TrayIcon:
    def __init__(self, app=None):
        self._app = app
        self._icon = None
        self._running = False

    def start(self):
        if pystray is None:
            return
        icon_image = _create_icon_image()
        if icon_image is None:
            return

        menu = pystray.Menu(
            pystray.MenuItem("Show", self._on_show, default=True),
            pystray.MenuItem("Dictate (F9)", self._on_dictate),
            pystray.MenuItem("Launch App (F8)", self._on_launch),
            pystray.MenuItem("Save to Word (F10)", self._on_save),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

        self._icon = pystray.Icon("GreekG", icon_image, "GreekG Assistant", menu)
        self._running = True
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        self._running = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _on_show(self, icon=None, item=None):
        if self._app:
            self._app.after(0, self._app.deiconify)

    def _on_dictate(self, icon=None, item=None):
        if self._app:
            self._app.after(0, self._app._dictate_tab._toggle_recording)

    def _on_launch(self, icon=None, item=None):
        if self._app:
            self._app.after(0, self._app._launch_tab._toggle_recording)

    def _on_save(self, icon=None, item=None):
        if self._app:
            self._app.after(0, self._app._save_tab.trigger_save)

    def _on_quit(self, icon=None, item=None):
        if self._app:
            self._app.after(0, self._app.quit_app)
        self.stop()
