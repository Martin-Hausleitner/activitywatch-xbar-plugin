#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <xbar.title>ActivityWatch Active Time</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.desc>Shows today's active time from ActivityWatch</xbar.desc>
# <xbar.refreshInterval>60s</xbar.refreshInterval>

import json
import urllib.request
from datetime import datetime

HOSTNAME = "MHs-MacBook-Pro.local"
BASE_URL = "http://localhost:5600"

def get_active_seconds():
    now = datetime.now().astimezone()
    today = now.strftime("%Y-%m-%d")
    
    tz_offset_raw = now.strftime("%z")
    # Convert "+0200" to "+02:00"
    if tz_offset_raw:
        tz_offset = f"{tz_offset_raw[:3]}:{tz_offset_raw[3:]}"
    else:
        tz_offset = "+00:00"

    start = f"{today}T00:00:00{tz_offset}"
    end   = f"{today}T23:59:59{tz_offset}"

    payload = {
        "timeperiods": [f"{start}/{end}"],
        "query": [
            f'afk = query_bucket("aw-watcher-afk_{HOSTNAME}");',
            'not_afk = filter_keyvals(afk, "status", ["not-afk"]);',
            'duration = sum_durations(not_afk);',
            'RETURN = {"duration": duration};',
        ],
    }

    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        f"{BASE_URL}/api/0/query/",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        result = json.loads(resp.read())
    
    if result and len(result) > 0 and "duration" in result[0]:
        return result[0]["duration"]
    return 0

def fmt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"

try:
    secs = get_active_seconds()
    print(f"⏱ {fmt(secs)}")
    print("---")
    print(f"Heute aktiv: {fmt(secs)}")
    print("ActivityWatch öffnen | href=http://localhost:5600")
    print("Aktualisieren | refresh=true")
except Exception as e:
    print("⏱ –")
    print("---")
    print("ActivityWatch nicht erreichbar")
    print(f"Fehler: {e}")
    print("Retry | refresh=true")
