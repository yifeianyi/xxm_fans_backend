#!/usr/bin/env python3
"""
Scrape all 大航海 (guards) user data from Bilibili official API.
Saves: avatar URL, user ID, username, fan badge level, guard type, days.

API: https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList

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

GUARD_LEVEL_MAP = {
    1: "总督",
    2: "提督",
    3: "舰长",
}

API_URL = "https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList"
PAGE_SIZE = 29
REQUEST_DELAY = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://live.bilibili.com",
}


def fetch_page(room_id: int, ruid: int, page: int, timeout: int = 15) -> dict:
    params = {"roomid": room_id, "ruid": ruid, "page": page, "page_size": PAGE_SIZE}
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=timeout)
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

    print(f"Fetching page 1 for room_id={room_id}, ruid={ruid}...")
    page1 = fetch_page(room_id, ruid, 1)
    total = page1["info"]["num"]
    total_pages = page1["info"]["page"]
    print(f"Total guards: {total}, Total pages: {total_pages}")

    all_guards = [parse_guard(item) for item in page1["list"]]

    for page in range(2, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}...", end=" ")
        try:
            data = fetch_page(room_id, ruid, page)
            items = [parse_guard(item) for item in data["list"]]
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
        room_id = 8777  # default for 咻咻满
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
