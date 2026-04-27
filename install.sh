#!/bin/bash
set -e

PLUGIN_DIR="$HOME/Library/Application Support/xbar/plugins"
SCRIPT_NAME="aw-time.1m.py"
SCRIPT_PATH="$(pwd)/$SCRIPT_NAME"

echo "Einrichten des ActivityWatch xbar Plugins..."

# Ensure xbar is installed
if ! ls -d /Applications/xbar.app >/dev/null 2>&1; then
    echo "xbar ist nicht installiert. Installiere xbar via Homebrew..."
    brew install --cask xbar
fi

# Ensure plugin directory exists
echo "Erstelle Plugin-Verzeichnis falls nötig: $PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

# Make script executable
chmod +x "$SCRIPT_PATH"

# Create symlink
TARGET_LINK="$PLUGIN_DIR/$SCRIPT_NAME"
if [ -L "$TARGET_LINK" ] || [ -e "$TARGET_LINK" ]; then
    echo "Entferne alten Link/Datei: $TARGET_LINK"
    rm "$TARGET_LINK"
fi

echo "Erstelle Symlink in xbar Plugin-Verzeichnis..."
ln -s "$SCRIPT_PATH" "$TARGET_LINK"

echo "Füge xbar zum macOS Autostart hinzu..."
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/xbar.app", hidden:false}' >/dev/null 2>&1 || echo "Autostart konnte nicht automatisch eingerichtet werden."

echo "Erfolgreich installiert!"
echo "Starte xbar neu..."
open /Applications/xbar.app || echo "Bitte xbar manuell starten."
