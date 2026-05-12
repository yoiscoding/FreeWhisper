#!/usr/bin/env python3
"""
FreeWhisper — Free, open-source push-to-talk dictation for macOS.

Hold a hotkey, talk, release. Whatever you said gets typed at your cursor.
Auto-detects language. Runs 100% locally — your voice never leaves your Mac.

Project home: https://github.com/yoiscoding/FreeWhisper
License: GPL v3 (see LICENSE file)
"""

import sys
import time
import wave
import sqlite3
import threading
import subprocess
from pathlib import Path
from datetime import datetime

import numpy as np
import sounddevice as sd
import pyperclip
import rumps
from pynput import keyboard
import mlx_whisper


# ============================================================
# Configuration
# ============================================================

APP_NAME = "FreeWhisper"
HOME = Path.home()
APP_DIR = HOME / ".freewhisper"
APP_DIR.mkdir(exist_ok=True)

GLOSSARY_PATH = APP_DIR / "glossary.txt"
DB_PATH = APP_DIR / "freewhisper.db"
AUDIO_DIR = APP_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# whisper-large-v3-turbo via MLX — fits comfortably on 8GB Apple Silicon,
# and is the only Whisper variant that handles non-English languages well.
MODEL_REPO = "mlx-community/whisper-large-v3-turbo"

# Audio config — 16kHz mono is Whisper's native format.
SAMPLE_RATE = 16_000
CHANNELS = 1

# Hotkey: hold Right Option to record.
# To change, swap to keyboard.Key.f5, keyboard.Key.alt_l, etc.
HOTKEY = keyboard.Key.alt_r

# Ignore recordings shorter than this (filters Option+letter accent typing).
MIN_RECORDING_SECONDS = 0.4

# Whisper's initial_prompt soft limit (~224 tokens).
MAX_GLOSSARY_CHARS = 800


# ============================================================
# Glossary (lightweight personalization)
# ============================================================

def ensure_glossary():
    """Create a starter glossary file on first run."""
    if GLOSSARY_PATH.exists():
        return
    GLOSSARY_PATH.write_text(
        "# FreeWhisper glossary\n"
        "# Add names, places, jargon, project terms — one per line.\n"
        "# Mix languages freely. These are injected as Whisper context\n"
        "# to improve accuracy on YOUR vocabulary.\n"
        "# Lines starting with # are ignored.\n"
        "# Keep total under ~800 characters for best effect.\n"
        "\n"
        "# Example entries (delete and replace with your own):\n"
        "# Anthropic\n"
        "# FreeWhisper\n"
        "# macOS\n"
    )


def load_glossary() -> str:
    """Return the glossary as a comma-separated string for Whisper's initial_prompt."""
    if not GLOSSARY_PATH.exists():
        return ""
    items = []
    for raw in GLOSSARY_PATH.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            items.append(line)
    if not items:
        return ""
    prompt = ", ".join(items)
    if len(prompt) > MAX_GLOSSARY_CHARS:
        prompt = prompt[:MAX_GLOSSARY_CHARS]
    return prompt


# ============================================================
# Local SQLite log (for history / future improvements)
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            language TEXT,
            duration_seconds REAL,
            audio_path TEXT,
            transcript TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_transcription(language, duration, audio_path, transcript):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO transcriptions "
            "(timestamp, language, duration_seconds, audio_path, transcript) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                datetime.now().isoformat(timespec="seconds"),
                language,
                duration,
                str(audio_path),
                transcript,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[FreeWhisper] DB log failed: {e}", file=sys.stderr)


# ============================================================
# Audio recording
# ============================================================

class Recorder:
    """Captures microphone audio while the hotkey is held."""

    def __init__(self):
        self.frames = []
        self.stream = None
        self.start_time = None
        self._lock = threading.Lock()

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            self.frames.append(indata.copy())

    def start(self):
        with self._lock:
            self.frames = []
        self.start_time = time.time()
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()

    def stop(self):
        if self.stream is None:
            return None, 0.0
        try:
            self.stream.stop()
            self.stream.close()
        finally:
            self.stream = None
        duration = time.time() - self.start_time
        with self._lock:
            if not self.frames:
                return None, duration
            audio = np.concatenate(self.frames, axis=0).flatten()
        return audio, duration


def save_wav(audio: np.ndarray, path: Path):
    """Save mono float32 audio as 16-bit PCM wav."""
    pcm = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


# ============================================================
# Paste at cursor (via clipboard)
# ============================================================

def paste_text(text: str):
    """
    Set clipboard to text, simulate Cmd+V, restore previous clipboard.

    Pasting (vs simulating keystrokes) is critical for RTL languages like Arabic
    and Hebrew — simulated typing breaks in many apps, but paste is bulletproof.
    """
    if not text:
        return
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    pyperclip.copy(text)
    time.sleep(0.05)

    kc = keyboard.Controller()
    with kc.pressed(keyboard.Key.cmd):
        kc.press("v")
        kc.release("v")

    time.sleep(0.2)
    try:
        pyperclip.copy(original)
    except Exception:
        pass


# ============================================================
# Menu bar app
# ============================================================

class FreeWhisperApp(rumps.App):
    ICON_IDLE = "🎙️"
    ICON_RECORDING = "🔴"
    ICON_TRANSCRIBING = "⏳"

    def __init__(self):
        super().__init__(APP_NAME, title=self.ICON_IDLE, quit_button=None)
        self.recorder = Recorder()
        self.is_recording = False
        self.is_transcribing = False
        self.menu = [
            rumps.MenuItem("Edit glossary", callback=self.open_glossary),
            rumps.MenuItem("Open data folder", callback=self.open_data_folder),
            rumps.MenuItem("View history", callback=self.open_history),
            None,
            rumps.MenuItem("About FreeWhisper", callback=self.open_about),
            rumps.MenuItem("Quit FreeWhisper", callback=rumps.quit_application),
        ]

        # Global hotkey listener — runs in its own thread.
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
        )
        self.listener.daemon = True
        self.listener.start()

        # Warm up the model in the background so first transcription is fast.
        threading.Thread(target=self._warmup, daemon=True).start()

    def _warmup(self):
        try:
            silence = np.zeros(int(SAMPLE_RATE * 0.5), dtype=np.float32)
            mlx_whisper.transcribe(silence, path_or_hf_repo=MODEL_REPO)
        except Exception as e:
            print(f"[FreeWhisper] Warmup failed (will retry on first use): {e}", file=sys.stderr)

    def set_icon(self, icon):
        self.title = icon

    def on_press(self, key):
        if key != HOTKEY:
            return
        if self.is_recording or self.is_transcribing:
            return
        self.is_recording = True
        self.set_icon(self.ICON_RECORDING)
        try:
            self.recorder.start()
        except Exception as e:
            self.is_recording = False
            self.set_icon(self.ICON_IDLE)
            print(f"[FreeWhisper] Recording failed: {e}", file=sys.stderr)

    def on_release(self, key):
        if key != HOTKEY:
            return
        if not self.is_recording:
            return
        self.is_recording = False
        audio, duration = self.recorder.stop()
        if audio is None or duration < MIN_RECORDING_SECONDS:
            self.set_icon(self.ICON_IDLE)
            return
        self.is_transcribing = True
        self.set_icon(self.ICON_TRANSCRIBING)
        threading.Thread(
            target=self._transcribe,
            args=(audio, duration),
            daemon=True,
        ).start()

    def _transcribe(self, audio, duration):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = AUDIO_DIR / f"{timestamp}.wav"
            save_wav(audio, audio_path)

            kwargs = {"path_or_hf_repo": MODEL_REPO}
            glossary = load_glossary()
            if glossary:
                kwargs["initial_prompt"] = glossary

            result = mlx_whisper.transcribe(audio, **kwargs)
            text = (result.get("text") or "").strip()
            language = result.get("language", "")

            if text:
                log_transcription(language, duration, audio_path, text)
                paste_text(text)
        except Exception as e:
            print(f"[FreeWhisper] Transcription failed: {e}", file=sys.stderr)
        finally:
            self.is_transcribing = False
            self.set_icon(self.ICON_IDLE)

    def open_glossary(self, _):
        subprocess.Popen(["open", "-t", str(GLOSSARY_PATH)])

    def open_data_folder(self, _):
        subprocess.Popen(["open", str(APP_DIR)])

    def open_history(self, _):
        # Quick history dump as a temp text file — simple, no extra UI.
        out = APP_DIR / "recent-history.txt"
        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT timestamp, language, transcript FROM transcriptions "
                "ORDER BY id DESC LIMIT 100"
            ).fetchall()
            conn.close()
            with out.open("w") as f:
                f.write("FreeWhisper — last 100 transcriptions\n")
                f.write("=" * 60 + "\n\n")
                for ts, lang, txt in rows:
                    f.write(f"[{ts}] ({lang})\n{txt}\n\n")
            subprocess.Popen(["open", "-t", str(out)])
        except Exception as e:
            rumps.alert(f"Could not open history: {e}")

    def open_about(self, _):
        rumps.alert(
            title="FreeWhisper",
            message=(
                "Free, open-source push-to-talk dictation for macOS.\n\n"
                "Hold Right Option to record. Release to transcribe.\n\n"
                "github.com/yoiscoding/FreeWhisper\n"
                "Licensed under GPL v3."
            ),
        )


def main():
    init_db()
    ensure_glossary()
    FreeWhisperApp().run()


if __name__ == "__main__":
    main()
