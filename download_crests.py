"""
download_crests.py

Downloads team crest PNGs from FotMob's CDN, one time, into a local folder
ready to commit/push to your scouting-photos GitHub repo (or a new dedicated
repo - your call).

The input CSV (team_crests_list.csv) was already generated from your real
players_final.json - it has all 1,662 distinct teams in your dataset. You
don't need to run extract_team_crests.py yourself; just put this CSV next
to this script and run it.

Resume-safe: re-running skips crests already downloaded.

Usage (PowerShell):
    python download_crests.py

Edit CRESTS_DIR below to point at wherever you want the output folder
(e.g. inside your scouting-photos repo clone).
"""

import csv
import time
from pathlib import Path
import urllib.request
import urllib.error

INPUT_CSV = Path("team_crests_list.csv")
CRESTS_DIR = Path(r"C:\Users\matth\OneDrive\Documents\GitHub\scouting-photos\crests")
FOTMOB_CREST_BASE = "https://images.fotmob.com/image_resources/logo/teamlogo/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_one(team_id: str) -> bool:
    out_path = CRESTS_DIR / f"{team_id}.png"
    if out_path.exists():
        return True  # already downloaded, resume-safe skip

    url = f"{FOTMOB_CREST_BASE}{team_id}.png"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        return True
    except urllib.error.HTTPError as e:
        print(f"  [{team_id}] HTTP error {e.code}")
        return False
    except Exception as e:
        print(f"  [{team_id}] failed: {e}")
        return False

def main():
    if not INPUT_CSV.exists():
        print(f"Could not find {INPUT_CSV} - run extract_team_crests.py first.")
        return

    CRESTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} teams to process.")
    print(f"Saving to: {CRESTS_DIR}")

    ok_count = 0
    fail_count = 0
    skip_count = 0

    for i, row in enumerate(rows, 1):
        tid = row["teamFotmobId"]
        name = row["team_name"]
        out_path = CRESTS_DIR / f"{tid}.png"

        if out_path.exists():
            skip_count += 1
            continue

        success = download_one(tid)
        if success:
            ok_count += 1
            print(f"[{i}/{len(rows)}] OK   {tid}  {name}")
        else:
            fail_count += 1
            print(f"[{i}/{len(rows)}] FAIL {tid}  {name}")

        time.sleep(0.15)  # gentle rate limit, avoid hammering fotmob's CDN

    print()
    print(f"Done. Downloaded: {ok_count}, Already had: {skip_count}, Failed: {fail_count}")
    print(f"Next step: commit & push the '{CRESTS_DIR.name}' folder to GitHub,")
    print("then update CREST_BASE in PlayerScoutingCard.js to point at the raw GitHub URL.")

if __name__ == "__main__":
    main()
