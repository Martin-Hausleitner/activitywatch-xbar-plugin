#!/usr/bin/python3
# -*- coding: utf-8 -*-
# <xbar.title>ActivityWatch Active Time</xbar.title>
# <xbar.version>v1.2</xbar.version>
# <xbar.desc>Shows today's and this week's active time from ActivityWatch</xbar.desc>
# <xbar.refreshInterval>60s</xbar.refreshInterval>

import json
import urllib.request
import os
from datetime import datetime, timedelta

HOSTNAME = "MHs-MacBook-Pro.local"
BASE_URL = "http://localhost:5600"
STATE_FILE = os.path.expanduser("~/.aw_xbar_icon_state")

def get_icon_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return f.read().strip() == "1"
        except:
            pass
    return False

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

def get_afk_status():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/0/buckets/aw-watcher-afk_{HOSTNAME}/events?limit=1")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            if data and len(data) > 0:
                return data[0].get("data", {}).get("status", "unknown")
    except:
        pass
    return "unknown"

def get_times():
    now = datetime.now().astimezone()
    
    # Check if current time is before 04:00 AM
    if now.hour < 4:
        now = now - timedelta(days=1)
    
    tz_offset_raw = now.strftime("%z")
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
    return f"{h:02d}:{m:02d}"

def fmt_hours(seconds):
    h = int(seconds // 3600)
    return f"{h}h"

try:
    today_secs, week_secs = get_times()
    show_icon = get_icon_state()
    
    icon_prefix = ""
    if show_icon:
        afk_status = get_afk_status()
        if afk_status == "not-afk":
            icon_prefix = "● " # Active
        elif afk_status == "afk":
            icon_prefix = "○ " # Inactive
        else:
            icon_prefix = "● " # Fallback
            
    now = datetime.now().astimezone()
    if now.hour < 4:
        now = now - timedelta(days=1)
        
    is_monday = (now.weekday() == 0)
    
    if is_monday:
        print(f"{icon_prefix}{fmt(today_secs)}")
    else:
        print(f"{icon_prefix}{fmt(today_secs)} / {fmt_hours(week_secs)}")
        
    print("---")
    print(f"Heute: {fmt(today_secs)}")
    print(f"Woche: {fmt(week_secs)}")
    print("---")
    
    toggle_val = "0" if show_icon else "1"
    toggle_text = "AFK Status-Icon ausblenden" if show_icon else "AFK Status-Icon (Kreis) einblenden"
    # Button to toggle icon
    print(f"{toggle_text} | bash='echo {toggle_val} > {STATE_FILE}' terminal=false refresh=true")
    
    print("ActivityWatch öffnen | href=http://localhost:5600")
    print("Aktualisieren | refresh=true")
except Exception as e:
    print("⚠️ Fehler")
    print("---")
    print("ActivityWatch nicht erreichbar oder interner Fehler")
    print(f"Details: {e}")
    print("Retry | refresh=true")
