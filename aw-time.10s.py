#!/usr/bin/python3
# -*- coding: utf-8 -*-
# <xbar.title>ActivityWatch Active Time</xbar.title>
# <xbar.version>v1.4</xbar.version>
# <xbar.desc>Shows active time, Cognitor launch, ActivityWatch controls, and weekly/monthly stats</xbar.desc>
# <xbar.refreshInterval>10s</xbar.refreshInterval>

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta

HOSTNAME = "MHs-MacBook-Pro.local"
BASE_URL = "http://localhost:5600"
STATE_FILE = os.path.expanduser("~/.aw_xbar_icon_state")
CACHE_FILE = os.path.expanduser("~/.aw_xbar_cache.json")
ACTIVITYWATCH_APP = "/Applications/ActivityWatch.app"
COGNITOR_LAUNCHER = os.path.expanduser(
    os.environ.get("COGNITOR_LAUNCHER", "~/Desktop/cognitor.command")
)
ACTIVITYWATCH_PROCESSES = [
    "aw-qt",
    "aw-server",
    "aw-server-rust",
    "aw-watcher-afk",
    "aw-watcher-window",
    "aw-watcher-window-macos",
    "aw-watcher-input",
    "aw-notify",
    "aw-sync",
]


def get_icon_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return f.read().strip() == "1"
        except OSError:
            pass
    return False


def set_icon_state(enabled):
    try:
        with open(STATE_FILE, "w") as f:
            f.write("1" if enabled else "0")
    except OSError:
        pass


def notify(message, title="ActivityWatch"):
    subprocess.run(
        ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def start_activitywatch():
    if not os.path.isdir(ACTIVITYWATCH_APP):
        notify("ActivityWatch wurde nicht gefunden.")
        return 1

    subprocess.run(["open", "-a", ACTIVITYWATCH_APP], check=False)
    notify("ActivityWatch wurde gestartet.")
    return 0


def stop_activitywatch():
    try:
        subprocess.run(
            ["osascript", "-e", 'tell application id "net.activitywatch.ActivityWatch" to quit'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        pass
    time.sleep(2)
    for process_name in ACTIVITYWATCH_PROCESSES:
        subprocess.run(
            ["pkill", "-x", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    time.sleep(1)
    for process_name in ACTIVITYWATCH_PROCESSES:
        subprocess.run(
            ["pkill", "-KILL", "-x", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    notify("ActivityWatch wurde gestoppt.")
    return 0


def start_cognitor():
    if not os.path.isfile(COGNITOR_LAUNCHER):
        notify("cognitor.command wurde nicht gefunden.", title="Cognitor")
        return 1

    env = os.environ.copy()
    env["COGNITOR_STOP_TAILSCALE"] = "0"
    subprocess.Popen(
        [COGNITOR_LAUNCHER],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        start_new_session=True,
    )
    notify("Cognitor wird ohne Tailscale gestartet.", title="Cognitor")
    return 0


def handle_action(argv):
    if len(argv) <= 1:
        return False

    action = argv[1]
    if action == "--toggle":
        set_icon_state(not get_icon_state())
        return True
    if action == "--start-aw":
        raise SystemExit(start_activitywatch())
    if action == "--stop-aw":
        raise SystemExit(stop_activitywatch())
    if action == "--start-cognitor":
        raise SystemExit(start_cognitor())
    return False


def query_duration(start_str, end_str, tz_offset):
    start = f"{start_str}T04:00:00{tz_offset}"
    end = f"{end_str}T03:59:59{tz_offset}"

    payload = {
        "timeperiods": [f"{start}/{end}"],
        "query": [
            f'window = query_bucket("aw-watcher-window_{HOSTNAME}");',
            f'afk = query_bucket("aw-watcher-afk_{HOSTNAME}");',
            'not_afk = filter_keyvals(afk, "status", ["not-afk"]);',
            'window = filter_period_intersect(window, not_afk);',
            'duration = sum_durations(window);',
            'RETURN = {"duration": duration};',
        ],
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/0/query/",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = json.loads(resp.read())

    if result and len(result) > 0 and "duration" in result[0]:
        return result[0]["duration"]
    return 0


def get_afk_status():
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/0/buckets/aw-watcher-afk_{HOSTNAME}/events?limit=1"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            if data and len(data) > 0:
                return data[0].get("data", {}).get("status", "unknown")
    except Exception:
        pass
    return "unknown"


def get_workday_now(now=None):
    now = now or datetime.now().astimezone()
    if now.hour < 4:
        now = now - timedelta(days=1)
    return now


def get_tz_offset(now):
    tz_offset_raw = now.strftime("%z")
    return f"{tz_offset_raw[:3]}:{tz_offset_raw[3:]}" if tz_offset_raw else "+00:00"


def get_times(now=None, duration_provider=query_duration):
    now = get_workday_now(now)
    tz_offset = get_tz_offset(now)

    today_str = now.strftime("%Y-%m-%d")
    next_day_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    days_since_monday = now.weekday()
    monday = now - timedelta(days=days_since_monday)
    monday_str = monday.strftime("%Y-%m-%d")
    next_monday_str = (monday + timedelta(days=7)).strftime("%Y-%m-%d")

    today_secs = duration_provider(today_str, next_day_str, tz_offset)
    week_secs = duration_provider(monday_str, next_monday_str, tz_offset)

    return today_secs, week_secs


def get_times_cached(show_icon):
    cache_ttl = 10 if show_icon else 120

    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                if time.time() - cache_data.get("timestamp", 0) < cache_ttl:
                    return cache_data.get("today_secs", 0), cache_data.get("week_secs", 0)
    except (OSError, json.JSONDecodeError):
        pass

    today_secs, week_secs = get_times()

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(
                {
                    "timestamp": time.time(),
                    "today_secs": today_secs,
                    "week_secs": week_secs,
                },
                f,
            )
    except OSError:
        pass

    return today_secs, week_secs


def fmt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}:{m:02d}"


def fmt_hours(seconds):
    h = int(seconds // 3600)
    return f"{h}h"


def activitywatch_running():
    for process_name in ACTIVITYWATCH_PROCESSES:
        result = subprocess.run(
            ["pgrep", "-x", process_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            return True
    return False


def week_bounds(now, weeks_ago):
    week_start = now - timedelta(days=now.weekday(), weeks=weeks_ago)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    return week_start, week_end


def build_stats(now, duration_provider=query_duration):
    now = get_workday_now(now)
    tz_offset = get_tz_offset(now)

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    tomorrow = now + timedelta(days=1)
    month_secs = duration_provider(
        month_start.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d"), tz_offset
    )
    elapsed_days = max(1, (tomorrow.date() - month_start.date()).days)

    stats = [
        ("Monatsgesamt:", month_secs),
        ("Monatsdurchschnitt/Tag:", month_secs / elapsed_days),
    ]

    for weeks_ago, label in [
        (0, "Diese Woche:"),
        (1, "Vorwoche:"),
        (2, "Vor 2 Wochen:"),
        (3, "Vor 3 Wochen:"),
    ]:
        start, end = week_bounds(now, weeks_ago)
        secs = duration_provider(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), tz_offset)
        stats.append((label, secs))

    last_four_weeks = [secs for _, secs in stats[2:]]
    if last_four_weeks:
        stats.append(("4-Wochen-Schnitt:", sum(last_four_weeks) / len(last_four_weeks)))

    return stats


def render_menu(
    show_icon,
    today_secs,
    week_secs,
    now=None,
    duration_provider=query_duration,
    activitywatch_running=None,
):
    now = get_workday_now(now)
    is_monday = now.weekday() == 0
    script_path = os.path.abspath(__file__)
    running = activitywatch_running if activitywatch_running is not None else globals()["activitywatch_running"]()

    icon_prefix = ""
    if show_icon and get_afk_status() == "afk":
        icon_prefix = "● "

    lines = []
    if is_monday:
        lines.append(f"{icon_prefix}{fmt(today_secs)}")
    else:
        lines.append(f"{icon_prefix}{fmt(today_secs)} / {fmt_hours(week_secs)}")

    lines.extend(
        [
            "---",
            f"Heute: {fmt(today_secs)}",
            f"Woche: {fmt(week_secs)}",
            "ActivityWatch: läuft" if running else "ActivityWatch: gestoppt",
            "---",
            f"⏹ ActivityWatch stoppen | bash='{script_path}' param1=--stop-aw terminal=false refresh=true",
            f"▶ ActivityWatch starten | bash='{script_path}' param1=--start-aw terminal=false refresh=true",
            f"🌐 Cognitor ohne Tailscale starten | bash='{script_path}' param1=--start-cognitor terminal=false refresh=false",
            "---",
            "📊 Statistiken",
        ]
    )

    stats = build_stats(now, duration_provider)
    for label, seconds in stats[:2]:
        lines.append(f"--{label} {fmt(seconds)}")

    lines.append("--Letzte Wochen")
    for label, seconds in stats[2:]:
        lines.append(f"--{label} {fmt(seconds)}")

    toggle_text = (
        "✅ AFK-Feature aktiv (Klicken zum Deaktivieren)"
        if show_icon
        else "❌ AFK-Feature inaktiv (Klicken zum Aktivieren)"
    )
    lines.extend(
        [
            "---",
            f"{toggle_text} | bash='{script_path}' param1=--toggle terminal=false refresh=true",
            "---",
            f"📊 Activity anzeigen | href={BASE_URL}/#/activity/{HOSTNAME}/view/",
            f"📈 Timeline anzeigen | href={BASE_URL}/#/timeline",
            f"⚙️ ActivityWatch Dashboard | href={BASE_URL}",
            "🔄 Aktualisieren | refresh=true",
        ]
    )
    return "\n".join(lines)


def main():
    if handle_action(sys.argv):
        return 0

    try:
        show_icon = get_icon_state()
        today_secs, week_secs = get_times_cached(show_icon)
        print(render_menu(show_icon, today_secs, week_secs))
    except Exception as e:
        print("⚠️ Fehler")
        print("---")
        print("ActivityWatch nicht erreichbar oder interner Fehler")
        print(f"Details: {e}")
        print("Retry | refresh=true")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
