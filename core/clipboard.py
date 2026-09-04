import time
import pyperclip
import keyboard


def copy_text(text: str):
    pyperclip.copy(text)


def paste_text():
    time.sleep(0.1)
    keyboard.send("ctrl+v")


def get_clipboard() -> str:
    return pyperclip.paste()
