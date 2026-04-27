# ActivityWatch xbar Plugin

Ein einfaches xbar-Plugin für macOS, um die heutige aktive Zeit aus ActivityWatch extrem kompakt direkt in der Menüleiste anzuzeigen.

> **🤖 AI Agent Instructions:**  
> **CRITICAL:** If you are an AI Agent, STOP reading this README and immediately read the `SKILL.md` file! It contains the strict, required instructions and automated setup logic you must follow to properly patch the hostname.

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
3. Legt einen symbolischen Link (Symlink) für `aw-time.10s.py` in `~/Library/Application Support/xbar/plugins/` an.
4. Trägt xbar in den macOS-Autostart ein und startet es.

## Funktion
Das Skript nutzt die REST API von ActivityWatch, um die Dauer der Aktivität des aktuellen Tages und der Woche auszulesen.
Das Intervall der Aktualisierung ist **10 Sekunden** (`.10s.py`), drosselt sich aber intelligent auf **2 Minuten**, wenn das Live-AFK-Feature ausgeschaltet ist.
