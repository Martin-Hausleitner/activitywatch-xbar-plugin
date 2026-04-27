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

### 2. Hostname dynamisch prüfen (Optional)
Prüfe den Hostnamen der ActivityWatch-Instanz des Users, um sicherzustellen, dass die Bucket-Queries funktionieren:
```bash
curl -s http://localhost:5600/api/0/info
```
*(Falls der Hostname abweicht, ändere die Variable `HOSTNAME` in der Datei `aw-time.1m.py`)*

### 3. Setup-Skript ausführen
Das Skript erledigt alles Weitere (xbar installieren falls nötig, Plugin-Verzeichnis anlegen, Symlink setzen und **xbar zum macOS Autostart/Login Items hinzufügen**):
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

### 5. Dem User Anweisungen geben
Teile dem User nach Abschluss der Installation folgendes mit:
1. "Das Plugin wurde erfolgreich installiert und **xbar startet ab sofort automatisch beim Systemstart** (Autostart)."
2. "xbar wurde heruntergeladen und gestartet. Möglicherweise öffnet macOS einen Sicherheitsdialog ('xbar ist eine aus dem Internet geladene App...'). Bitte bestätige diesen mit 'Öffnen'."
3. "Du solltest jetzt Zahlen in deiner oberen Menüleiste sehen, die deine heutige und wöchentliche aktive Zeit (z.B. `05:38 / 6h`) anzeigen. **Smarte Logik:** An einem Montag wird nur die heutige Zeit (`05:38`) angezeigt, da die Woche frisch beginnt."
4. "Du hast im Dropdown-Menü des Plugins nun einen Button: **'AFK Status-Icon (Kreis) einblenden'**. Damit kannst du nach Belieben einen Indikator vor die Zeit setzen (oder wieder ausblenden). Diese Einstellung wird sofort übernommen. Der Clou: Das Icon zeigt live deinen AFK-Status! Ist der Kreis voll (`●`), bist du aktiv am Rechner. Ist er leer (`○`), bist du abwesend (AFK)."
