# ActivityWatch xbar Plugin

Ein einfaches xbar-Plugin für macOS, um die heutige aktive Zeit aus ActivityWatch direkt in der Menüleiste anzuzeigen.

## Voraussetzungen
* ActivityWatch muss lokal auf Port 5600 laufen.
* xbar (wird bei der Installation automatisch via Homebrew installiert, falls noch nicht vorhanden).

## Installation

Einfach das Installationsskript ausführen:

```bash
./install.sh
```

Dies führt folgende Schritte durch:
1. Prüft, ob `xbar` installiert ist (installiert es andernfalls über `brew`).
2. Erstellt das Plugin-Verzeichnis für xbar (falls noch nicht vorhanden).
3. Legt einen symbolischen Link (Symlink) für `aw-time.1m.py` in `~/Library/Application Support/xbar/plugins/` an.
4. Startet/Aktualisiert xbar.

## Funktion
Das Skript nutzt die REST API von ActivityWatch, um die Dauer der Aktivität ("not-afk" Events) des aktuellen Tages aus dem passenden Bucket (`aw-watcher-afk_*`) auszulesen.

Das Intervall der Aktualisierung ist über den Dateinamen auf **1 Minute** (`.1m.py`) festgelegt.
