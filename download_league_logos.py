"""
download_league_logos.py

Downloads league logo PNGs from FotMob's CDN, one time, into a local folder
ready to commit/push to your scouting-photos GitHub repo - same pattern as
download_crests.py.

NOTE: league_logos_list.csv covers ~53 leagues reconstructed from past
sessions, not your full 158+ league list. Leagues not in this CSV just
won't have a logo in the scouting card (clean fallback, no broken image).
If you want more added later, just say which leagues and I can extend it.

Resume-safe: re-running skips logos already downloaded.

Usage (PowerShell), run from inside your scouting-photos folder:
    python download_league_logos.py
"""

import csv
import time
from pathlib import Path
import urllib.request
import urllib.error

INPUT_CSV = Path("league_logos_list.csv")
LOGOS_DIR = Path("league_logos")  # created as a sibling to photos/ and crests/
FOTMOB_LOGO_BASE = "https://images.fotmob.com/image_resources/logo/leaguelogo/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_one(logo_id: str) -> bool:
    out_path = LOGOS_DIR / f"{logo_id}.png"
    if out_path.exists():
        return True

    url = f"{FOTMOB_LOGO_BASE}{logo_id}.png"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        return True
    except urllib.error.HTTPError as e:
        print(f"  [{logo_id}] HTTP error {e.code}")
        return False
    except Exception as e:
        print(f"  [{logo_id}] failed: {e}")
        return False

def main():
    if not INPUT_CSV.exists():
        print(f"Could not find {INPUT_CSV} - put it in this same folder.")
        return

    LOGOS_DIR.mkdir(parents=True, exist_ok=True)

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # dedupe by logo ID (some leagues share an ID, e.g. duplicate entries in the source data)
    seen = {}
    for row in rows:
        seen[row["leagueLogoId"]] = row["league_name"]

    print(f"Found {len(seen)} distinct league logos to process.")
    print(f"Saving to: {LOGOS_DIR.resolve()}")

    ok_count = 0
    fail_count = 0
    skip_count = 0

    for i, (logo_id, name) in enumerate(seen.items(), 1):
        out_path = LOGOS_DIR / f"{logo_id}.png"
        if out_path.exists():
            skip_count += 1
            continue

        success = download_one(logo_id)
        if success:
            ok_count += 1
            print(f"[{i}/{len(seen)}] OK   {logo_id}  {name}")
        else:
            fail_count += 1
            print(f"[{i}/{len(seen)}] FAIL {logo_id}  {name}")

        time.sleep(0.15)

    print()
    print(f"Done. Downloaded: {ok_count}, Already had: {skip_count}, Failed: {fail_count}")
    print(f"Next step: commit & push the '{LOGOS_DIR}' folder to GitHub,")
    print("then I'll update LEAGUE_LOGOS in PlayerScoutingCard.js to point at the raw GitHub URLs.")

if __name__ == "__main__":
    main()
