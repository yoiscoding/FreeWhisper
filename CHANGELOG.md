# Changelog

All notable changes to FreeWhisper will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-05-12

Initial public release.

### Added
- Push-to-talk dictation with Right Option hotkey
- MLX-Whisper transcription (large-v3-turbo model) for Apple Silicon
- Auto language detection (English, Italian, Arabic, French, Spanish, and more)
- Menu bar app with status icon (🎙️ idle, 🔴 recording, ⏳ transcribing)
- Personal glossary file injected into Whisper as context
- Local SQLite log of every transcription
- Audio recordings saved to `~/.freewhisper/audio/`
- One-command installer that handles arm64 venv, app bundle, and permissions
- `View history` menu item to inspect recent transcriptions

### Known limitations
- Apple Silicon only (MLX requirement)
- Single hotkey, hard-coded (planned: configurable in 0.2)
- No GUI for editing glossary (use the menu item to open the file)
