"""
Problem Statement:
Modern routines require checking time, weather, news, and personal tasks across multiple places,
which causes context switching and wasted attention.

This script consolidates a minimal daily brief—local time, an Open‑Meteo weather snapshot,
top Hacker News headlines, and a few items from tasks.txt—into a single, fast terminal command.

It avoids heavy dashboards and API keys by using public JSON endpoints and a tiny ~/.dailyrc config
to keep setup simple and portability high.
"""
"""
daily.py — A daily dashboard CLI:
- Local time and weekday
- Weather (Open-Meteo, no key needed)
- Top Hacker News headlines
- Local tasks from tasks.txt

Setup:
  1) Create a config file at ~/.dailyrc with:
        [location]
        latitude = 28.6139
        longitude = 77.2090
        timezone = Asia/Kolkata

     Tip: Use https://www.latlong.net to find coordinates and choose an IANA timezone like Asia/Kolkata.

  2) (Optional) Create a tasks file at ~/tasks.txt, one task per line.

Run:
  python daily.py
"""
from __future__ import annotations
import os
import sys
import json
import textwrap
from datetime import datetime
from pathlib import Path
import configparser
import urllib.request
import urllib.parse

# ---------- Utilities ----------
def human_time_now(tz_name: str | None) -> str:
    # Uses OS local time if tz_name missing; otherwise tries zoneinfo
    try:
        if tz_name:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(tz_name))
        else:
            now = datetime.now()
    except Exception:
        now = datetime.now()
    return now.strftime("%A, %d %b %Y • %I:%M %p")

def fetch_json(url: str, timeout: int = 10) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "daily-cli/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        return json.loads(data.decode("utf-8"))

def read_lines_safe(path: Path, limit: int | None = None) -> list[str]:
    if not path.exists():
        return []
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                lines.append(line)
            if limit is not None and i + 1 >= limit:
                break
    return lines

def wrap(s: str, width: int = 80) -> str:
    return "\n".join(textwrap.wrap(s, width=width))

# ---------- Config ----------
def load_config() -> dict:
    cfg_path = Path(os.path.expanduser("~/.dailyrc"))
    parser = configparser.ConfigParser()
    if cfg_path.exists():
        parser.read(cfg_path, encoding="utf-8")
    loc = parser["location"] if "location" in parser else {}
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    tz = loc.get("timezone")
    d = {}
    if lat and lon:
        try:
            d["latitude"] = float(lat)
            d["longitude"] = float(lon)
        except ValueError:
            pass
    if tz:
        d["timezone"] = tz
    return d

# ---------- Weather (Open-Meteo) ----------
def get_weather(lat: float, lon: float, tz_name: str | None) -> dict | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability",
        "current_weather": "true",
        "timezone": tz_name or "auto",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    try:
        return fetch_json(url)
    except Exception:
        return None

def summarize_weather(data: dict) -> str:
    # Current temperature
    current = data.get("current_weather", {})
    temp = current.get("temperature")
    wind = current.get("windspeed")
    # Next hours precipitation probability (take next 6 if available)
    hourly = data.get("hourly", {})
    probs = hourly.get("precipitation_probability") or []
    if isinstance(probs, list) and probs:
        next_probs = [p for p in probs[:6] if isinstance(p, (int, float))]
        if next_probs:
            max_prob = max(next_probs)
        else:
            max_prob = None
    else:
        max_prob = None
    parts = []
    if isinstance(temp, (int, float)):
        parts.append(f"{temp:.0f}°C now")
    if isinstance(wind, (int, float)):
        parts.append(f"wind {wind:.0f} km/h")
    if isinstance(max_prob, (int, float)):
        parts.append(f"precip ≤ {max_prob:.0f}% next hrs")
    return " • ".join(parts) if parts else "Weather unavailable"

# ---------- Hacker News ----------
def get_hn_top(limit: int = 5) -> list[str]:
    try:
        top_ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")[:limit]
        titles = []
        for tid in top_ids:
            item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{tid}.json")
            title = item.get("title") or "Untitled"
            titles.append(title)
        return titles
    except Exception:
        return []

# ---------- Tasks ----------
def get_tasks(limit: int = 5) -> list[str]:
    tasks_path = Path(os.path.expanduser("~/tasks.txt"))
    return read_lines_safe(tasks_path, limit=limit)

# ---------- Main render ----------
def main() -> int:
    cfg = load_config()
    tz_name = cfg.get("timezone")
    header = human_time_now(tz_name)
    print("=" * 80)
    print(f"Daily • {header}")
    print("=" * 80)
    # Weather
    print("\nWeather")
    print("-" * 80)
    if "latitude" in cfg and "longitude" in cfg:
        w = get_weather(cfg["latitude"], cfg["longitude"], tz_name)
        print(summarize_weather(w) if w else "Weather unavailable")
    else:
        print("Set latitude/longitude in ~/.dailyrc for weather")
    # News
    print("\nHeadlines")
    print("-" * 80)
    for i, title in enumerate(get_hn_top(5), 1):
        print(f"{i}. {wrap(title, 70)}")
    # Tasks
    print("\nTasks")
    print("-" * 80)
    tasks = get_tasks(5)
    if tasks:
        for i, t in enumerate(tasks, 1):
            print(f"[ ] {t}")
    else:
        print("Add tasks to ~/tasks.txt (one per line)")
    print("\nTip: Edit ~/.dailyrc and ~/tasks.txt to personalize this dashboard.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
