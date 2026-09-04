# GreekG Assistant

A **GUI-driven** voice assistant for Windows — think a lightweight "Jarvis" that turns
speech into cleaned-up text, launches apps by voice, and logs AI responses to a daily Word
document. It has a modern dark-theme GUI with a system tray icon, and works with **either**
an on-device AI (Ollama) **or** any OpenAI-compatible API (Groq, Together, OpenRouter,
OpenAI, etc.) — so you can use free models and minimize local processing.

## Features

| Hotkey | Mode | What it does |
|---|---|---|
| **F9** | Dictate | Record → Whisper STT → AI grammar cleanup → paste into the focused window |
| **F8** | App launch | Record → STT → fuzzy-match the spoken app name → launch it |
| **F10** | Save to Word | Read the clipboard and append it, timestamped, into today's `.docx` |
| **Ctrl+Shift+G** | Open GreekG | Toggle the floating pill + surface the main window (no focus steal) |
| *"Hey Jarvis"* | Wake word | Hands-free Dictate mode; auto-stops after ~1.5 s of silence |

All features can be enabled/disabled independently in the **Settings** tab.

## GUI

- **4 tabs**: Dictate & Paste · App Launch · Save to Word · Settings
- **System tray icon** with quick actions (right-click for menu, click to show/hide window)
- **Status bar** showing real-time state (Idle / Recording / Processing)
- **Floating utility pill** — a small always-on-top pill that starts collapsed, expands on
  click to show quick-action buttons (Dictate / Launch / Save / Open) plus, when enabled,
  the last spoken transcript and cleaned prompt. Draggable; its position is remembered.
- Configurable hotkeys (including **click-to-capture** for the Open GreekG combo), AI
  backend, Whisper backend, and wake word settings
- Optional **auto-start with Windows**

## Floating pill

- Collapsed: a slim pill showing live status (Idle / Listening / Processing).
- Click to expand; **Ctrl+Shift+G** (configurable) toggles it and surfaces the window
  without stealing focus.
- **Docks to any of the 4 screen corners** (bottom-right by default, changeable in
  Settings → Floating pill corner). Drag it near a corner to snap it there, or drag it
  freely to detach.
- **Transparency** is adjustable (Settings → Pill opacity), from 30% to fully opaque.
- The expanded view shows the latest spoken transcript and converted prompt when the
  **"Show transcript in floating pill"** setting is enabled (default on). This reuses the
  same transcript the Dictate flow already produces — it adds **zero** extra Whisper/AI
  processing.

## AI Backends (pick one in Settings)

| Backend | How it works | Use case |
|---|---|---|
| **Ollama** | Local HTTP, fully offline | No API key, private, runs entirely on your machine |
| **API** | Any OpenAI-compatible endpoint | Use free models (Groq, Together, etc.), removes local LLM load |

Works with any OpenAI-compatible chat endpoint — provide URL + key + model name.

## Whisper Backends (pick one in Settings)

| Backend | How it works | Use case |
|---|---|---|
| **Local** | faster-whisper on GPU/CPU | Fully offline, no API key |
| **API** | Groq/OpenAI audio transcription | Minimal local processing, faster on weak machines |

## Setup (development)

```bash
pip install -r requirements.txt
cp apps_config.example.json apps_config.json   # then edit paths for your machine
python main.py                                 # run terminal as Administrator for global hotkeys
```

First run downloads openWakeWord's pretrained models (one-time, needs internet). If that
fails, the wake word is simply disabled — F9/F8/F10 still work.

## Building a distributable bundle (for other PCs)

```bash
# install build deps once
pip install -r requirements-build.txt

# one-click build -> dist\GreekG Assistant\
build.bat
```

The output lands in `dist\GreekG Assistant\`. Zip that folder and send it to another PC —
users just extract and double-click `GreekG Assistant.exe`. No Python install needed.

## Project structure

```
main.py               # Entry point (GUI + tray)
core/                 # Engine modules (audio, STT backends, AI backends, etc.)
gui/                  # CustomTkinter UI (tabs, pill, tray, widgets)
config/               # settings.py + default_config.json
resources/icon.ico    # App icon
build.bat, build.spec # PyInstaller bundling
```

## Notes

- Settings are stored in `~/.greekg/settings.json` on each machine.
- `apps_config.json` is machine-specific and gitignored; edit the example template.
- Saved AI responses go to `Documents\GreekG_Exports\GreekG_<date>.docx`.
- The original single-file version is preserved as `greekg_assistant.py` for reference.
