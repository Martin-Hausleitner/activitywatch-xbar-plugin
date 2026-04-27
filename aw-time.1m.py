#!/usr/bin/python3
# -*- coding: utf-8 -*-
# <xbar.title>ActivityWatch Active Time</xbar.title>
# <xbar.version>v1.1</xbar.version>
# <xbar.desc>Shows today's and this week's active time from ActivityWatch</xbar.desc>
# <xbar.refreshInterval>60s</xbar.refreshInterval>

import json
import urllib.request
from datetime import datetime, timedelta

HOSTNAME = "MHs-MacBook-Pro.local"
BASE_URL = "http://localhost:5600"

def query_duration(start_str, end_str, tz_offset):
    start = f"{start_str}T04:00:00{tz_offset}"
    end   = f"{end_str}T03:59:59{tz_offset}"
    
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

def get_times():
    now = datetime.now().astimezone()
    
    # Check if current time is before 04:00 AM. If so, "today" in AW terms started yesterday.
    if now.hour < 4:
        now = now - timedelta(days=1)
    
    tz_offset_raw = now.strftime("%z")
    # Convert "+0200" to "+02:00"
    if tz_offset_raw:
        tz_offset = f"{tz_offset_raw[:3]}:{tz_offset_raw[3:]}"
    else:
        tz_offset = "+00:00"

    # Today
    today_str = now.strftime("%Y-%m-%d")
    next_day_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # This Week (Monday = 0)
    days_since_monday = now.weekday()
    monday = now - timedelta(days=days_since_monday)
    monday_str = monday.strftime("%Y-%m-%d")
    next_monday_str = (monday + timedelta(days=7)).strftime("%Y-%m-%d")
    
    today_secs = query_duration(today_str, next_day_str, tz_offset)
    week_secs = query_duration(monday_str, next_monday_str, tz_offset)
    
    return today_secs, week_secs

def fmt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h{m:02d}m"

def fmt_hours(seconds):
    h = int(seconds // 3600)
    return f"{h}h"

try:
    today_secs, week_secs = get_times()
    
    # Hide weekly hours if today is Monday (0)
    now = datetime.now().astimezone()
    if now.hour < 4:
        now = now - timedelta(days=1)
        
    is_monday = False # (now.weekday() == 0) - Temporarily disabled for testing
    
    if is_monday:
        print(f"{fmt(today_secs)} | size=12")
    else:
        print(f"{fmt(today_secs)} {fmt_hours(week_secs)} | size=12")
        
    print("---")
    print(f"Heute: {fmt(today_secs)}")
    print(f"Woche: {fmt(week_secs)}")
    print("---")
    print("ActivityWatch öffnen | href=http://localhost:5600")
    print("Aktualisieren | refresh=true")
except Exception as e:
    print("⚠️ Fehler")
    print("---")
    print("ActivityWatch nicht erreichbar oder interner Fehler")
    print(f"Details: {e}")
    print("Retry | refresh=true")
