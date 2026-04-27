# Skill: ActivityWatch xbar Plugin Installieren

**Name:** Install ActivityWatch xbar Plugin
**Description:** Installiert die ActivityWatch Menüleisten-Erweiterung auf einem macOS System. Die Erweiterung zeigt die exakte "Time Active" aus ActivityWatch in der macOS Menüleiste an, indem sie `xbar` installiert und das Plugin-Repository clont.

## Instruktionen für den Agenten

Wenn der User dich bittet, das ActivityWatch Menüleisten-Plugin auf seinem Mac zu installieren, führe exakt die folgenden Schritte nacheinander aus:

### 1. Repository klonen und einrichten
Führe diesen Befehl aus, um das offizielle Repository in den Scratch-Ordner des Users herunterzuladen:
```bash
git clone https://github.com/Martin-Hausleitner/activitywatch-xbar-plugin.git ~/Desktop/activitywatch-xbar-plugin || echo "Bereits vorhanden"
cd ~/Desktop/activitywatch-xbar-plugin
```

### 2. Hostname vollautomatisch ermitteln & patchen (CRITICAL)
Das Plugin benötigt den exakten Hostnamen des PCs/Macs, um die richtigen Daten aus ActivityWatch zu ziehen und die dynamischen Activity-Links (`#/activity/.../view/`) im Dropdown-Menü korrekt zu generieren.

**Als KI-Agent musst du den Hostnamen zwingend automatisch ermitteln und in die Python-Datei eintragen:**
1. Frage die lokalen Buckets ab, um den echten Namen des Window-Watchers zu finden:
```bash
curl -s http://localhost:5600/api/0/buckets | grep -o 'aw-watcher-window_[^"]*' | head -n 1
```
2. Extrahiere den Hostnamen (alles nach `aw-watcher-window_`).
3. Ersetze die Variable `HOSTNAME = "..."` in der Datei `aw-time.10s.py` mit dem gefundenen Hostnamen.

### 3. Setup-Skript ausführen (inkl. Autostart)
Das beiliegende Setup-Skript erledigt die Installation von `xbar`, erstellt das Plugin-Verzeichnis, setzt den Symlink und **trägt Xbar fest in den macOS-Autostart ein**, sodass die Leiste bei jedem Neustart sofort funktioniert.
```bash
chmod +x install.sh
./install.sh
```

*(Hinweis: Der Befehl `./install.sh` erfordert eventuell User-Approval, da xbar über Homebrew installiert wird und via AppleScript in den Autostart eingetragen wird. Warte den Abschluss der Installation ab.)*

### 4. xbar starten
Falls das Skript `xbar` nicht automatisch starten konnte, starte es manuell:
```bash
open /Applications/xbar.app
```

### 5. Dem User die Funktionen & Einstellungen erklären
Teile dem User nach Abschluss der Installation folgendes mit:
1. "Das Plugin wurde erfolgreich installiert und **xbar startet ab sofort automatisch beim Systemstart** (Autostart)."
2. "xbar wurde heruntergeladen und gestartet. Möglicherweise öffnet macOS einen Sicherheitsdialog ('xbar ist eine aus dem Internet geladene App...'). Bitte bestätige diesen mit 'Öffnen'."
3. "Du siehst nun eine extrem kompakte Zeit in deiner Menüleiste (z.B. `6:12 / 6h`). **Smarte Logik:** An einem Montag wird nur die heutige Zeit (`6:12`) angezeigt, da die Woche frisch beginnt."
4. "Im Dropdown-Menü findest du **dynamische Schnellzugriffs-Buttons** (Activity, Timeline, Dashboard), die direkt auf diesen PC/Mac zugeschnitten sind."
5. "Du hast im Menü außerdem einen **AFK-Button ('AFK Status-Icon einblenden')**:"
   - **Eingeschaltet:** Das Skript aktualisiert sich live **alle 10 Sekunden**. Bist du am PC aktiv, verschwindet das Icon. Bist du abwesend (AFK), erscheint ein Punkt (`●`).
   - **Ausgeschaltet (Standard):** Das Skript arbeitet extrem ressourcenschonend mit Cache und aktualisiert sich nur **alle 2 Minuten**. Es wird nie ein AFK-Punkt angezeigt.
   *(Diese Einstellung wird fest gespeichert und greift auch nach einem Neustart).*
