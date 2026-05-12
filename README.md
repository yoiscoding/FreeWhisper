<div align="center">

# FreeWhisper

**Free, open-source push-to-talk dictation for macOS.**
Hold a key. Talk. Release. Your words appear at your cursor.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon-black?logo=apple)](https://github.com/yoiscoding/FreeWhisper)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?logo=python&logoColor=white)](https://www.python.org/)

</div>

> 100% local. Your voice never leaves your Mac. No subscriptions, no accounts, no API keys.

> 📖 **New here?** → [**INSTALL.md**](INSTALL.md) — step-by-step install guide, written for non-coders.

---

## What it is

A small menu-bar app that lets you dictate anywhere on your Mac. Hold **Right Option**, talk, release. Whatever you said gets typed at your cursor — in Notes, in your browser, in a code editor, anywhere.

It auto-detects language (English, Italian, Arabic, French, Spanish, German, and most others Whisper supports). It runs entirely on-device using Apple Silicon's neural engine via MLX-Whisper, so it's fast and private.

Built as a free, open-source alternative to paid dictation tools.

---

## Why FreeWhisper

|                              | FreeWhisper        | Built-in macOS dictation | Paid dictation apps |
| ---------------------------- | ------------------ | ------------------------ | ------------------- |
| Free, forever                | ✅                  | ✅                        | ❌ ($20–$80)         |
| Runs 100% local              | ✅                  | Partial                  | Varies              |
| Mixed-language support       | ✅ auto-detect      | ❌ one at a time          | Varies              |
| Customizable vocabulary      | ✅ glossary file    | ❌                        | Some                |
| Source code you can audit    | ✅ GPL v3           | ❌                        | ❌                   |
| Works offline                | ✅                  | Partial                  | Varies              |
| Custom hotkey                | ✅ (edit one line)  | Limited                  | Varies              |

---

## Requirements

- **Mac with Apple Silicon** (M1, M2, M3, M4 — any year)
- **macOS 13 Ventura or later** (tested on Tahoe / macOS 26)
- **Python 3.10+** (check with `python3 --version`)
- ~3 GB free disk space (1.5 GB for the Whisper model, 1 GB for dependencies)
- ~3 GB free RAM when running (works comfortably on 8 GB Macs)

Intel Macs are not supported — MLX requires Apple Silicon.

---

## Quick install (recommended)

One command. Open Terminal and run:

```bash
curl -fsSL https://raw.githubusercontent.com/yoiscoding/FreeWhisper/main/scripts/install.sh | bash
```

The installer will:
1. Verify your Mac is Apple Silicon
2. Create a virtual environment and install dependencies
3. Download the Whisper model (~1.5 GB, one-time)
4. Build a `FreeWhisper.app` launcher in your `/Applications` folder
5. Open System Settings to the right places for permissions

After install, double-click **FreeWhisper** in your Applications folder. Grant Microphone + Accessibility permissions when prompted, then test the hotkey.

---

## Manual install

If you'd rather see every step:

```bash
# 1. Clone
git clone https://github.com/yoiscoding/FreeWhisper.git
cd FreeWhisper

# 2. Set up an arm64 virtual environment
arch -arm64 python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Run it
python freewhisper.py
```

A 🎙️ icon appears in your menu bar. On first launch, it downloads the Whisper model (give it a minute or two).

---

## First-run permissions

macOS will prompt for two permissions. Both are one-time:

1. **Microphone** — granted via system popup when you first record.
2. **Accessibility** — required so FreeWhisper can detect your global hotkey and paste at your cursor.

To grant Accessibility:
- System Settings → Privacy & Security → Accessibility
- Toggle **FreeWhisper** (or **Terminal**, if you ran it manually) to ON

If the hotkey doesn't work, this is almost always the cause.

---

## Usage

1. Click into any text field (Notes, browser, code editor — anywhere).
2. **Hold Right Option**, speak, **release**.
3. Watch your words appear.

Menu bar icon tells you the state:
- 🎙️ — idle, ready
- 🔴 — recording
- ⏳ — transcribing

---

## Personalization: the glossary

FreeWhisper gets noticeably better at *your* vocabulary when you give it a short list of names, places, and jargon you use a lot.

Click the 🎙️ in your menu bar → **Edit glossary**. Add one term per line. Mix languages freely:

```
Mahmoud
Anthropic
TanStack
Cairo
Milano
gnocchi
```

The glossary is loaded into Whisper as context on every transcription. Keep it under ~800 characters for best effect.

---

## Change the hotkey

Open `freewhisper.py` and find:

```python
HOTKEY = keyboard.Key.alt_r  # Right Option
```

Common alternatives:
- `keyboard.Key.alt_l` — Left Option
- `keyboard.Key.f5` — F5
- `keyboard.Key.f13` — F13 (rare, often unused)
- `keyboard.KeyCode.from_char('§')` — Section key (top-left on most Mac keyboards)

Restart the app after editing.

---

## Where your data lives

Everything stays on your Mac, at `~/.freewhisper/`:

- `glossary.txt` — your editable vocab list
- `freewhisper.db` — SQLite log of every transcription
- `audio/` — raw wav recordings (delete anytime to reclaim space)

Click the 🎙️ → **Open data folder** to browse. Nothing is ever uploaded.

---

## Troubleshooting

<details>
<summary><strong>Hotkey does nothing</strong></summary>

Most common cause: Accessibility permission not granted. Open System Settings → Privacy & Security → Accessibility, and make sure FreeWhisper (or Terminal, if launched manually) is toggled on. You may need to fully quit and relaunch the app after toggling.
</details>

<details>
<summary><strong>First recording takes forever (30+ seconds of silence)</strong></summary>

The Whisper model (~1.5 GB) is downloading. One-time event. After this, transcription is near-instant for short clips, ~5 seconds for a minute of audio.
</details>

<details>
<summary><strong>"This process is not trusted" warning in Terminal</strong></summary>

Same as the hotkey issue — Accessibility permission missing. See above.
</details>

<details>
<summary><strong>App icon shows but transcription does nothing / text doesn't appear</strong></summary>

Two likely causes:
1. Microphone permission missing — System Settings → Privacy & Security → Microphone → enable FreeWhisper
2. The active window changed between recording and pasting. Click into the target text field *before* you start recording.
</details>

<details>
<summary><strong>"Incompatible architecture" error</strong></summary>

Your venv was built as x86_64 instead of arm64. Fix:
```bash
deactivate
rm -rf venv
arch -arm64 python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
</details>

<details>
<summary><strong>Memory pressure / Mac slows down while running</strong></summary>

FreeWhisper uses ~3 GB RAM. On 8 GB Macs with many apps open, close some browser tabs or quit heavy apps. There's no software fix for physical RAM.
</details>

<details>
<summary><strong>App doesn't auto-launch when I reboot my Mac</strong></summary>

System Settings → General → Login Items & Extensions → click **+** → select FreeWhisper from /Applications.
</details>

For anything else, [open an issue](https://github.com/yoiscoding/FreeWhisper/issues/new/choose).

---

## Roadmap

What might land in future versions, in rough order:

- [ ] First-run onboarding wizard (auto-grants permissions, no Terminal needed)
- [ ] Configurable hotkey from a UI (no code editing)
- [ ] Visual recording feedback (waveform / pulse)
- [ ] Transcription history viewer with search
- [ ] Edit-last-transcription shortcut (fix mistakes fast)
- [ ] Auto-launch toggle in the menu
- [ ] Linux port
- [ ] Windows port

Contributions toward any of these are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## How it works (under the hood)

```
┌─────────────────┐
│ Right Option    │  ← Global hotkey via pynput
│ pressed         │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Record audio    │  ← sounddevice, 16kHz mono float32
│ (in memory)     │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Right Option    │
│ released        │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Save .wav       │  ← Local log
│ Log to SQLite   │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ MLX-Whisper     │  ← Apple Silicon GPU, ~3 GB model
│ transcribe      │     auto-detects language
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Paste via       │  ← Save clipboard → set transcript
│ clipboard       │     → Cmd+V → restore clipboard
└─────────────────┘
```

---

## Contributing

Pull requests welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code style, and how to test changes.

Found a bug or have an idea? [Open an issue](https://github.com/yoiscoding/FreeWhisper/issues/new/choose).

---

## License

GPL v3. See [LICENSE](LICENSE) for the full text.

In short: you can use, modify, and distribute FreeWhisper freely — **but if you distribute it (modified or not), you must keep it open source under GPL v3**. You cannot take this code, rebrand it, and ship it as a closed-source paid product. That's the deal.

Copyright © 2026 Youssef Mohamed.

---

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) — the underlying speech recognition model
- [MLX](https://github.com/ml-explore/mlx) — Apple's framework for running models on Apple Silicon
- [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) — the MLX port
- [rumps](https://github.com/jaredks/rumps) — macOS menu bar app helper
- [pynput](https://github.com/moses-palmer/pynput) — global hotkey handling
