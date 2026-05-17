#!/usr/bin/env python3
"""
Scrape all 大航海 (guards) user data from Bilibili official API.
Uses v1 API for page 1 (includes top3 expired governors), v2 for subsequent pages.
Saves: avatar URL, user ID, username, fan badge level, guard type, days.

API:
  v1: https://api.live.bilibili.com/xlive/app-room/v1/guardTab/topList
  v2: https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList

Guard Level mapping (Bilibili API):
  1 = 总督 (Governor)
  2 = 提督 (Admiral)
  3 = 舰长 (Captain)
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

GUARD_LEVEL_MAP = {1: "总督", 2: "提督", 3: "舰长"}

API_V1 = "https://api.live.bilibili.com/xlive/app-room/v1/guardTab/topList"
API_V2 = "https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList"
PAGE_SIZE = 29
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://live.bilibili.com",
}


def _load_cookie():
    """Try to load Bilibili cookie from Django DB."""
    try:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xxm_fans_home.settings")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        django.setup()
        from moments.services.cookie_service import CookieService
        cookie = CookieService.get_cookie("bilibili")
        if cookie:
            return cookie
    except Exception:
        pass
    return ""


def _fetch(api_url: str, params: dict, timeout: int = 15) -> dict:
    resp = requests.get(api_url, params=params, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API error: code={data.get('code')}, message={data.get('message')}")
    return data["data"]


def parse_guard(item: dict) -> dict:
    medal = item.get("medal_info", {})
    return {
        "uid": item["uid"],
        "username": item["username"],
        "face": item["face"],
        "guard_level": item["guard_level"],
        "guard_type": GUARD_LEVEL_MAP.get(item["guard_level"], f"未知({item['guard_level']})"),
        "medal_name": medal.get("medal_name", ""),
        "medal_level": medal.get("medal_level", 0),
        "accompany": item.get("accompany", 0),
    }


def scrape_all_guards(room_id: int, ruid: int, output_dir: str = None) -> list[dict]:
    if output_dir is None:
        output_dir = Path(__file__).parent

    # Load cookie for authenticated API access
    cookie = _load_cookie()
    if cookie:
        HEADERS["Cookie"] = cookie
        print("Using authenticated cookie")

    # Page 1: use v1 to get top3 (expired governors), v2 for full list with medal_info
    print(f"Fetching page 1 for room_id={room_id}, ruid={ruid}...")
    page1_v1 = _fetch(API_V1, {"roomid": room_id, "ruid": ruid, "page": 1, "page_size": PAGE_SIZE})
    page1_v2 = _fetch(API_V2, {"roomid": room_id, "ruid": ruid, "page": 1, "page_size": PAGE_SIZE})
    total = page1_v2["info"]["num"]
    total_pages = page1_v2["info"]["page"]
    print(f"Total guards: {total}, Total pages: {total_pages}")

    seen_uids = set()
    all_guards = []

    # Process top3 from v1 (expired governors not in v2 list)
    for item in page1_v1.get("top3", []):
        if item["uid"] not in seen_uids:
            seen_uids.add(item["uid"])
            all_guards.append(parse_guard(item))

    # Process v2 list (has medal_info + accompany)
    for item in page1_v2.get("list", []):
        if item["uid"] not in seen_uids:
            seen_uids.add(item["uid"])
            all_guards.append(parse_guard(item))

    # Remaining pages: v2 API
    for page in range(2, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}...", end=" ")
        try:
            data = _fetch(API_V2, {"roomid": room_id, "ruid": ruid, "page": page, "page_size": PAGE_SIZE})
            items = []
            for item in data["list"]:
                if item["uid"] not in seen_uids:
                    seen_uids.add(item["uid"])
                    items.append(parse_guard(item))
            all_guards.extend(items)
            print(f"OK ({len(items)} items)")
        except Exception as e:
            print(f"FAILED: {e}", file=sys.stderr)
        time.sleep(REQUEST_DELAY)

    return all_guards


def save_results(guards: list[dict], ruid: int, output_dir: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"laplace_guards_{ruid}_{timestamp}.json")

    result = {
        "ruid": ruid,
        "scraped_at": datetime.now().isoformat(),
        "total": len(guards),
        "guards": guards,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(guards)} guards to {json_path}")

    guard_types = {}
    for g in guards:
        gt = g["guard_type"]
        guard_types[gt] = guard_types.get(gt, 0) + 1

    print("\n--- Summary ---")
    print(f"Total: {len(guards)} guards")
    for gt, count in sorted(guard_types.items()):
        print(f"  {gt}: {count}")
    max_medal = max(guards, key=lambda g: g["medal_level"])
    print(f"Highest fan badge: Lv.{max_medal['medal_level']} ({max_medal['username']})")


def main():
    if len(sys.argv) >= 3:
        room_id = int(sys.argv[1])
        ruid = int(sys.argv[2])
    elif len(sys.argv) >= 2:
        ruid = int(sys.argv[1])
        room_id = 8777
    else:
        room_id = 8777
        ruid = 37754047

    output_dir = sys.argv[-1] if len(sys.argv) >= 4 and os.path.isdir(sys.argv[-1]) else str(Path(__file__).parent)

    print(f"Scraping guards: room_id={room_id}, ruid={ruid}")
    print(f"Output directory: {output_dir}")
    print()

    guards = scrape_all_guards(room_id, ruid, output_dir)
    save_results(guards, ruid, output_dir)
    return guards


if __name__ == "__main__":
    main()
