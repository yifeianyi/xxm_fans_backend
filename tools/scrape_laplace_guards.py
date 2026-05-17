#!/usr/bin/env python3
"""
Scrape all 大航海 (guards) user data from laplace.live for a given Bilibili UID.
Saves: avatar URL, user ID, username, fan badge level, guard type.

API: https://workers.vrp.moe/bilibili/live-guards/{uid}?p={page}

Guard Level mapping (laplace.live API):
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

API_BASE = "https://workers.vrp.moe/bilibili/live-guards"
REQUEST_DELAY = 0.3

def fetch_page(uid: int, page: int, timeout: int = 15) -> dict:
    """Fetch a single page of guard data."""
    url = f"{API_BASE}/{uid}?p={page}"
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API error: code={data.get('code')}, message={data.get('message')}")
    return data["data"]


def parse_guard(item: dict) -> dict:
    """Parse a single guard item into a flat dict."""
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


def scrape_all_guards(uid: int, output_dir: str = None) -> list[dict]:
    """Scrape all pages of guard data for a given UID."""
    if output_dir is None:
        output_dir = Path(__file__).parent

    # Fetch first page to get metadata
    print(f"Fetching page 1 for UID {uid}...")
    page1 = fetch_page(uid, 1)
    total = page1["info"]["num"]
    total_pages = page1["info"]["page"]
    print(f"Total guards: {total}, Total pages: {total_pages}")

    all_guards = []
    for item in page1["list"]:
        all_guards.append(parse_guard(item))

    # Fetch remaining pages
    for page in range(2, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}...", end=" ")
        try:
            data = fetch_page(uid, page)
            for item in data["list"]:
                all_guards.append(parse_guard(item))
            print(f"OK ({len(data['list'])} items)")
        except Exception as e:
            print(f"FAILED: {e}", file=sys.stderr)
        time.sleep(REQUEST_DELAY)

    return all_guards


def save_results(guards: list[dict], uid: int, output_dir: str):
    """Save results to JSON and print summary."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"laplace_guards_{uid}_{timestamp}.json")

    result = {
        "uid": uid,
        "scraped_at": datetime.now().isoformat(),
        "total": len(guards),
        "guards": guards,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(guards)} guards to {json_path}")

    # Summary stats
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
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 37754047
    output_dir = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).parent)

    print(f"Scraping guards for UID {uid}...")
    print(f"Output directory: {output_dir}")
    print()

    guards = scrape_all_guards(uid, output_dir)
    save_results(guards, uid, output_dir)

    return guards


if __name__ == "__main__":
    main()
