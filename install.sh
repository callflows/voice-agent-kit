#!/usr/bin/env bash
# Installiert das Skillpack fuer Claude Code.
#
#   ./install.sh          → ~/.claude/skills/voice-agent-kit  (global, alle Projekte)
#   ./install.sh --here   → .claude/skills/voice-agent-kit    (nur dieses Projekt)
#
# Fuer Claude Desktop kein Script noetig: voice-agent-kit.zip hochladen
# (Einstellungen → Capabilities → Skills).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "--here" ]; then
  # Projektweit: relativ zum Verzeichnis, aus dem aufgerufen wurde.
  TARGET="$PWD/.claude/skills/voice-agent-kit"
else
  TARGET="$HOME/.claude/skills/voice-agent-kit"
fi

if [ -e "$TARGET" ]; then
  read -r -p "$TARGET existiert bereits. Ueberschreiben? [j/N] " a
  [ "$a" = "j" ] || [ "$a" = "J" ] || { echo "Abgebrochen."; exit 0; }
  rm -rf "$TARGET"
fi

mkdir -p "$(dirname "$TARGET")"
cp -R "$SRC/skills" "$TARGET"
find "$TARGET" -name ".DS_Store" -delete 2>/dev/null || true

echo "Installiert: $TARGET"
echo ""
echo "Naechster Schritt — API-Key setzen:"
echo "  export ELEVENLABS_API_KEY=\"dein-key\""
echo ""
echo "Dann in Claude Code:  \"bau mir einen Voice Agent\""
