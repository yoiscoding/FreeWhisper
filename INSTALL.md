<div align="center">

# How to install FreeWhisper

**Total time: 5 minutes**
**Skill needed: copy and paste**

</div>

---

## Before you start — check 3 things

You'll know in 30 seconds whether your Mac can run FreeWhisper.

### 1. Do you have an Apple Silicon Mac?

Click the  in the top-left of your screen → **About This Mac**. Look at "Chip":

✅ **M1, M2, M3, or M4** → you're good
❌ **Intel** → FreeWhisper won't work on your Mac (sorry, this is a hardware limitation)

### 2. Do you have macOS 13 or newer?

Same window → "macOS":

✅ **Ventura (13), Sonoma (14), Sequoia (15), Tahoe (26)** → you're good
⚠️ **Older** → it might work but isn't tested. Try anyway.

### 3. Do you have ~4 GB free disk space?

Apple menu → About This Mac → More Info → Storage. You need at least 4 GB free.

---

## The install — one command

**Step 1.** Open the **Terminal** app.

> 💡 Don't know where Terminal is? Press `Cmd + Space`, type `terminal`, hit Enter.

**Step 2.** Copy this whole line, paste it into Terminal, and press Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/yoiscoding/FreeWhisper/main/scripts/install.sh | bash
```

**Step 3.** Wait 3-5 minutes. The installer will:

- Check your Mac is compatible ✓
- Install Python dependencies ✓
- Download the Whisper model (~1.5 GB) ✓
- Build the FreeWhisper app icon ✓
- Open the System Settings page for permissions ✓

You'll see colorful progress text the whole time. Don't close Terminal until you see **"Installation complete!"**

---

## Granting permissions

macOS requires two permissions before FreeWhisper can work. **This is normal and one-time only.**

### Permission 1: Accessibility (so the hotkey works)

The installer opens System Settings automatically when it finishes. You should see:

> **System Settings → Privacy & Security → Accessibility**

Do this:

1. Click the **+** button at the bottom of the list
2. In the file picker, navigate to **Applications**
3. Select **FreeWhisper**
4. Click **Open**
5. Toggle the switch next to **FreeWhisper** to **ON** (it turns blue)
6. Enter your Mac password or Touch ID when asked

### Permission 2: Microphone (so it can hear you)

You'll get this prompt automatically the first time you record. Just click **Allow**.

If you want to set it up now: System Settings → Privacy & Security → **Microphone** → enable FreeWhisper there too.

---

## Launching FreeWhisper

**Open Finder → Applications → double-click FreeWhisper.**

- 🎙️ icon should appear in your **menu bar** (top-right of your screen, near the clock) within 30-60 seconds
- The very first launch takes longer because the app warms up the model — give it a minute

**If you don't see 🎙️ after a minute**, see Troubleshooting below.

---

## Your first transcription

1. Open the **Notes** app (or any app with a text field — browser, Messages, anything)
2. Click into the text area so your cursor is blinking there
3. **Hold down the Right Option key** (the Option key to the right of your spacebar)
4. Speak naturally: *"Hello, this is my first FreeWhisper transcription"*
5. **Release** the Right Option key
6. Wait 2-3 seconds

✨ Your words appear at the cursor.

> 🌍 **Speak in any language.** FreeWhisper auto-detects English, Italian, Arabic, French, Spanish, German, Mandarin, Hindi, and most others Whisper supports.

---

## Watching what's happening

The menu bar icon tells you the state:

| Icon | Means |
|------|-------|
| 🎙️ | Idle, ready, listening for hotkey |
| 🔴 | Recording your voice right now |
| ⏳ | Transcribing (usually 1-3 seconds) |

---

## Making FreeWhisper smarter at YOUR words

FreeWhisper learns nothing on its own — but you can give it a "glossary" of words it tends to mispronounce.

1. Click 🎙️ in your menu bar
2. Click **Edit glossary**
3. A text file opens. Add words you use a lot — names, places, jargon. **One per line:**

```
Mahmoud
Cairo
Anthropic
gnocchi
useState
```

4. Save the file (Cmd+S). Done. Next transcription uses your words as context.

> 💡 Mix languages freely — Arabic names, Italian words, English jargon, all in the same file.

---

## Make it launch automatically when you boot your Mac

**System Settings → General → Login Items & Extensions → click +**

Pick **FreeWhisper** from Applications. Done. From now on, 🎙️ shows up automatically every time you start your Mac.

---

## Troubleshooting

### 🔴 The hotkey does nothing

**99% of the time:** Accessibility permission isn't granted. Go back to the "Granting permissions" section above.

After granting, **fully quit FreeWhisper** (click 🎙️ → Quit) and relaunch it from Applications. Permission only applies to a fresh launch.

### 🔴 No 🎙️ appears after launching

**First launch only:** the app is downloading the model (~1.5 GB). Give it 3-5 minutes. Check your internet connection.

**Subsequent launches:** look at `/tmp/freewhisper.log` for the error. Open Terminal and run:

```bash
cat /tmp/freewhisper.log | tail -30
```

Copy that into a [new issue](https://github.com/yoiscoding/FreeWhisper/issues/new/choose) and we'll figure it out.

### 🔴 macOS says "FreeWhisper can't be opened because it's from an unidentified developer"

Normal — happens with all open-source apps. **Right-click** FreeWhisper in Applications → **Open** → click **Open** in the dialog. Just for the first launch.

### 🔴 "Incompatible architecture" error

Your Python is running as Intel (x86_64) instead of Apple Silicon (arm64). Fix:

```bash
# Install arm64 Python
brew install python

# Or download from python.org and pick the universal2 installer
```

Then re-run the installer.

### 🔴 Mac slows down while FreeWhisper is running

FreeWhisper uses ~3 GB RAM. On 8 GB Macs, that can squeeze things. Close some browser tabs or quit heavy apps.

### 🔴 Something else

[Open an issue](https://github.com/yoiscoding/FreeWhisper/issues/new/choose). Include your macOS version, Mac chip, and the contents of `/tmp/freewhisper.log`.

---

## Uninstalling

If you ever want to remove FreeWhisper completely, paste this into Terminal:

```bash
# Quit any running instance
killall FreeWhisper Python python3 2>/dev/null

# Remove the app and the install
sudo rm -rf /Applications/FreeWhisper.app
rm -rf ~/.freewhisper-app

# Optional: also remove your transcription history and recordings
rm -rf ~/.freewhisper

echo "FreeWhisper uninstalled."
```

---

<div align="center">

**Need help?** [Open an issue](https://github.com/yoiscoding/FreeWhisper/issues/new/choose) or check the [main README](README.md).

**Like FreeWhisper?** Give it a ⭐ on [GitHub](https://github.com/yoiscoding/FreeWhisper).

</div>
