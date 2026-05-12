#!/bin/bash
# ============================================================
# FreeWhisper installer for macOS
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/yoiscoding/FreeWhisper/main/scripts/install.sh | bash
#
# Or, after cloning:
#   bash scripts/install.sh
# ============================================================

set -e

# ---- Pretty output helpers ----
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

info()    { printf "${BOLD}==>${NC} %s\n" "$1"; }
success() { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}⚠${NC}  %s\n" "$1"; }
fail()    { printf "${RED}✗${NC} %s\n" "$1"; exit 1; }

# ---- Banner ----
cat <<'BANNER'

  ╔═══════════════════════════════════════╗
  ║         FreeWhisper Installer         ║
  ║   free open-source voice dictation    ║
  ╚═══════════════════════════════════════╝

BANNER

# ============================================================
# 1. Sanity checks
# ============================================================

info "Checking your Mac..."

# Apple Silicon?
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
  fail "FreeWhisper requires Apple Silicon (M1/M2/M3/M4). Your Mac is: $ARCH"
fi
success "Apple Silicon detected"

# macOS version?
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)
if [ "$MACOS_MAJOR" -lt 13 ]; then
  warn "macOS 13+ recommended (you have $MACOS_VERSION). Continuing anyway."
else
  success "macOS $MACOS_VERSION"
fi

# Python 3.10+?
if ! command -v python3 &>/dev/null; then
  fail "Python 3 not found. Install it from https://www.python.org/downloads/ or with: brew install python"
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  fail "Python 3.10+ required. You have $PY_VERSION. Install a newer Python from python.org."
fi
success "Python $PY_VERSION"

# Verify Python is arm64 (could be x86_64 under Rosetta)
PY_ARCH=$(python3 -c 'import platform; print(platform.machine())')
if [ "$PY_ARCH" != "arm64" ]; then
  fail "Your Python is running as $PY_ARCH (Intel emulation). Install arm64 Python from python.org or with: brew install python"
fi
success "Python is native arm64"

# ============================================================
# 2. Disk space check
# ============================================================

FREE_GB=$(df -g "$HOME" | awk 'NR==2 {print $4}')
if [ "$FREE_GB" -lt 4 ]; then
  fail "Need at least 4 GB free disk space. You have ${FREE_GB} GB."
fi
success "Disk space OK (${FREE_GB} GB free)"

# ============================================================
# 3. Locate project source
# ============================================================

# If installer is being run from a cloned repo, use that.
# Otherwise, clone fresh.
if [ -f "freewhisper.py" ] && [ -f "requirements.txt" ]; then
  PROJECT_DIR="$(pwd)"
  info "Using current directory: $PROJECT_DIR"
else
  INSTALL_DIR="$HOME/.freewhisper-app"
  if [ -d "$INSTALL_DIR" ]; then
    info "Updating existing install at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull --quiet || warn "Could not git pull — using existing files"
  else
    info "Cloning FreeWhisper to $INSTALL_DIR"
    if ! command -v git &>/dev/null; then
      fail "git not found. Install with: xcode-select --install"
    fi
    git clone --quiet https://github.com/yoiscoding/FreeWhisper.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
  fi
  PROJECT_DIR="$INSTALL_DIR"
fi

# ============================================================
# 4. Virtual environment + deps
# ============================================================

info "Setting up Python virtual environment..."

if [ -d "venv" ]; then
  warn "Existing venv found — removing and rebuilding cleanly"
  rm -rf venv
fi

arch -arm64 python3 -m venv venv
source venv/bin/activate
success "Virtual environment created"

info "Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
success "Dependencies installed"

# Verify imports
info "Verifying installation..."
python -c "import mlx_whisper, sounddevice, pynput, pyperclip, rumps" \
  || fail "Verification failed — please open an issue with the error above"
success "All imports OK"

# ============================================================
# 5. Build the .app launcher
# ============================================================

info "Building FreeWhisper.app launcher..."

APP_PATH="/Applications/FreeWhisper.app"

if [ -d "$APP_PATH" ]; then
  warn "Existing FreeWhisper.app found — replacing"
  sudo rm -rf "$APP_PATH"
fi

sudo mkdir -p "$APP_PATH/Contents/MacOS"

sudo tee "$APP_PATH/Contents/Info.plist" > /dev/null <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>FreeWhisper</string>
  <key>CFBundleDisplayName</key><string>FreeWhisper</string>
  <key>CFBundleIdentifier</key><string>org.freewhisper.app</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>FreeWhisper</string>
  <key>LSUIElement</key><true/>
  <key>NSMicrophoneUsageDescription</key><string>FreeWhisper needs microphone access to transcribe your voice.</string>
  <key>NSAppleEventsUsageDescription</key><string>FreeWhisper uses Apple Events to paste transcribed text at your cursor.</string>
</dict>
</plist>
PLIST

sudo tee "$APP_PATH/Contents/MacOS/FreeWhisper" > /dev/null <<SH
#!/bin/bash
# FreeWhisper launcher — forces arm64 and uses absolute paths
# so it works when launched from Finder (no inherited PATH).
exec /usr/bin/arch -arm64 "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/freewhisper.py" >> /tmp/freewhisper.log 2>&1
SH

sudo chmod +x "$APP_PATH/Contents/MacOS/FreeWhisper"

# Ad-hoc sign so macOS Gatekeeper accepts it
sudo codesign --force --deep --sign - --entitlements /dev/null "$APP_PATH" 2>/dev/null || true
sudo xattr -cr "$APP_PATH" 2>/dev/null || true

success "FreeWhisper.app installed at $APP_PATH"

# ============================================================
# 6. Permission prep
# ============================================================

info "Opening System Settings for permissions..."

# Clear any stale permission state
tccutil reset Microphone org.freewhisper.app 2>/dev/null || true
tccutil reset Accessibility org.freewhisper.app 2>/dev/null || true

# Wait a beat, then open the right settings panel
sleep 1
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || true

# ============================================================
# 7. Done
# ============================================================

cat <<DONE

${GREEN}${BOLD}✓ Installation complete!${NC}

  ${BOLD}What's next:${NC}

  1. System Settings should be open to ${BOLD}Privacy & Security → Accessibility${NC}.
     - Click ${BOLD}+${NC}, navigate to ${BOLD}/Applications${NC}, add ${BOLD}FreeWhisper${NC}.
     - Toggle it ${BOLD}ON${NC} (enter password / Touch ID).

  2. Double-click ${BOLD}FreeWhisper${NC} in your Applications folder.
     - First launch downloads the Whisper model (~1.5 GB, one-time).
     - When macOS asks for ${BOLD}Microphone${NC} access → click Allow.

  3. Wait ~60 seconds for the ${BOLD}🎙️${NC} to appear in your menu bar.

  4. Open Notes, hold ${BOLD}Right Option${NC}, talk, release — your words appear.

  ${BOLD}Need help?${NC}
  → README:  https://github.com/yoiscoding/FreeWhisper#readme
  → Issues:  https://github.com/yoiscoding/FreeWhisper/issues

DONE
