#!/usr/bin/env bash
set -euo pipefail

# Run this from inside the extracted diodon-native folder:
#   chmod +x install.sh && ./install.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "== Diodon installer =="
echo "Project dir: $PROJECT_DIR"

echo ""
echo "-- Installing system dependencies (needs sudo) --"
echo "   python3-tk        : Tkinter GUI toolkit"
echo "   python3-venv       : virtual environments"
echo "   xclip              : reads highlighted (PRIMARY) text selection on X11"
echo "   wl-clipboard       : same, for Wayland sessions"
echo "   libnotify-bin      : desktop notifications (notify-send)"
echo "   gir1.2-ayatanaappindicator3-0.1 + gir1.2-gtk-3.0 : tray icon support"
sudo apt-get update -qq
sudo apt-get install -y \
    python3-tk python3-venv xclip wl-clipboard libnotify-bin \
    gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 \
    || sudo apt-get install -y gir1.2-appindicator3-0.1  # older Ubuntu versions use this package name instead

echo ""
echo "-- Setting up Python virtual environment --"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r "$PROJECT_DIR/requirements.txt" -q
deactivate

echo ""
echo "-- Installing the Ctrl+Y capture command --"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/diodon-capture-tasksheet" <<EOF
#!/usr/bin/env bash
"$VENV_DIR/bin/python" -m diodon.capture_cli
EOF
chmod +x "$BIN_DIR/diodon-capture-tasksheet"

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "NOTE: $HOME/.local/bin is not on your PATH. Add this to ~/.bashrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi

echo ""
echo "-- Setting up autostart (so Diodon launches automatically on login) --"
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_DIR/diodon.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Diodon
Comment=Clipboard + Tasksheet tray tool
Exec=$VENV_DIR/bin/python -m diodon.main
Path=$PROJECT_DIR
Icon=$PROJECT_DIR/assets/icon.png
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo ""
echo "================================================================"
echo " Install complete."
echo ""
echo " Diodon will start automatically next time you log in."
echo " To start it right now without logging out:"
echo "   $VENV_DIR/bin/python -m diodon.main &"
echo ""
echo " ONE MANUAL STEP LEFT (can't be scripted — it's a GNOME setting):"
echo " Set up the Ctrl+Y shortcut so selected text gets added to Tasksheet:"
echo "   1. Open Settings > Keyboard > View and Customize Shortcuts"
echo "   2. Scroll to Custom Shortcuts > click '+'"
echo "   3. Name: Diodon Capture"
echo "   4. Command: $BIN_DIR/diodon-capture-tasksheet"
echo "   5. Click the new shortcut row, press Ctrl+Y, confirm"
echo ""
echo " Clipboard capture (Ctrl+C) needs NO setup — it works automatically"
echo " once Diodon is running, since it just watches the system clipboard."
echo "================================================================"
