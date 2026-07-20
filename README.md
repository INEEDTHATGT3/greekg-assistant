# GreekG Assistant

A hotkey-driven, offline voice assistant for Windows — think a lightweight, local "Jarvis"
that turns speech into cleaned-up text, launches apps by voice, and logs AI responses to a
daily Word document. Everything runs on-device (Whisper + a local LLM); no cloud APIs.

Built to cut the friction out of everyday desktop work: dictate a prompt straight into
whatever window is focused, open apps without touching the mouse, and keep a timestamped
record of AI answers.

## Features

| Hotkey | Mode | What it does |
|---|---|---|
| **F9** | Dictate | Record → Whisper STT → local LLM grammar cleanup → paste into the focused window |
| **F8** | App launch | Record → STT → fuzzy-match the spoken app name → launch it |
| **F10** | Save to Word | Read the clipboard and append it, timestamped, into today's `.docx` |
| *"Hey Jarvis"* | Wake word | Hands-free Dictate mode; auto-stops after ~1.5 s of silence |

## Tech

Python · faster-whisper (GPU-accelerated speech-to-text) · Ollama / llama3.2 (grammar
cleanup) · openWakeWord (wake-word detection) · global hotkeys · python-docx · sounddevice

## Prerequisites

- Windows 10/11 (global hotkeys + app launching)
- Python 3.10+
- [Ollama](https://ollama.com) running locally: `ollama pull llama3.2`
- NVIDIA GPU recommended for real-time Whisper (CUDA runtime pulled via requirements)

## Setup

```bash
pip install -r requirements.txt
cp apps_config.example.json apps_config.json   # then edit paths for your machine
python greekg_assistant.py                     # run terminal as Administrator for global hotkeys
```

First run downloads openWakeWord's pretrained models (one-time, needs internet). If that
fails, the wake word is simply disabled — F9/F8/F10 still work.

## Notes

- `apps_config.json` is machine-specific and gitignored; edit the example template.
- Saved AI responses go to `Documents\GreekG_Exports\GreekG_<date>.docx`.
