"""
Kisan Sathi — AMPIS price scraper
Runs daily via GitHub Actions. Pulls Min/Max/Average prices for the six
tracked crops across six markets from ampis.gov.np and writes the results
into data.json (same file the web app reads from).

Free to run forever: GitHub Actions' free tier covers this easily (one run/day,
a few seconds each).
"""

import re
import json
import time
from datetime import date

import requests
import nepali_datetime

BASE_URL = "https://ampis.gov.np/market-price-comparison"

# --- Confirmed market IDs (from AMPIS's own filter dropdown) ---
MARKETS = {
    "dhalkebar": "7",
    "lalbandi": "15",
    "kalimati": "23",
    "pokhara": "10",
    "kohalpur": "12",
    "butwal": "11",
}

# --- Confirmed commodity IDs for the six tracked crops ---
# (Terai/local variants chosen where available, matching Madhesh Pradesh relevance)
CROPS = {
    "tomato": "409",    # गोलभेंडा ठुलो (नेपाली)
    "potato": "378",    # आलु रातो (मुढे)
    "onion": "1694656",  # प्याज सुकेको (नेपाली)
    "cauli": "398",     # काउली (तराई)
    "cabbage": "401",   # बन्दा (तराई)
    "chili": "1694671",  # खुर्सानी हरियो (लाम्चो)
}

# --- BS (Bikram Sambat) year -> AMPIS's internal entity-reference ID ---
# IMPORTANT: these IDs are NOT predictable/sequential — AMPIS assigns a new
# one whenever a new BS year is added to their system. When the year rolls
# over (mid-April, Gregorian) and this map doesn't have the new year, the
# scraper will log a warning and skip the run rather than fail silently.
# To fix: repeat the manual devtools inspection from before, for one query
# in the new year, and add the ID here.
YEAR_ID_MAP = {
    2080: "16",
    2081: "446538",
    2082: "894719",
    2083: "1614822",
}

# --- BS month number -> AMPIS's internal entity-reference ID (fixed, stable) ---
MONTH_ID_MAP = {
    1: "33", 2: "34", 3: "35", 4: "36", 5: "37", 6: "38",
    7: "39", 8: "40", 9: "41", 10: "42", 11: "43", 12: "44",
}

BS_MONTH_NAMES = {
    1: "बैशाख", 2: "जेठ", 3: "असार", 4: "साउन", 5: "भदौ", 6: "असोज",
    7: "कार्तिक", 8: "मंसिर", 9: "पुष", 10: "माघ", 11: "फागुन", 12: "चैत",
}

CATEGORY_ID = "2"  # तरकारी — confirmed working for all six crops in testing


def get_bs_today():
    bs = nepali_datetime.date.today()
    return bs.year, bs.month, bs.day


def fetch_price(market_id, year_id, month_id, day, commodity_id, session):
    """Returns the rounded average price, or None if no data was found."""
    params = {
        "uid_entityreference_filter": market_id,
        "field_market_rate_year_target_id_entityreference_filter": year_id,
        "field_commodity_category_target_id_entityreference_filter": CATEGORY_ID,
        "field_market_rate_month_target_id": month_id,
        "field_market_rate_commodity_target_id_entityreference_filter": commodity_id,
        "field_market_rate_day_target_id": day,
    }
    try:
        resp = session.get(BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  request failed: {e}")
        return None

    row_match = re.search(r"<tbody>\s*<tr>(.*?)</tr>\s*</tbody>", resp.text, re.S)
    if not row_match:
        return None

    cells = re.findall(r"<td[^>]*>(.*?)</td>", row_match.group(1), re.S)
    cells = [re.sub(r"\s+", " ", c).strip() for c in cells]
    # Expected columns: market, month, day, commodity, unit, min, max, avg
    if len(cells) < 8:
        return None
    try:
        return round(float(cells[7]))
    except (ValueError, IndexError):
        return None


def main():
    year, month, day = get_bs_today()

    if year not in YEAR_ID_MAP:
        print(
            f"WARNING: BS year {year} has no known AMPIS year ID yet. "
            f"Skipping this run — see the comment above YEAR_ID_MAP for how to fix."
        )
        return

    year_id = YEAR_ID_MAP[year]
    month_id = MONTH_ID_MAP[month]
    date_bs_label = f"{BS_MONTH_NAMES[month]} {day}, {year}"

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (KisanSathi price sync; contact via GitHub repo)"})

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    missing = []
    updated = 0

    for crop_key, commodity_id in CROPS.items():
        if crop_key not in data["crops"]:
            continue
        for market_key, market_id in MARKETS.items():
            price = fetch_price(market_id, year_id, month_id, day, commodity_id, session)
            if price is None:
                missing.append(f"{crop_key}/{market_key}")
            else:
                data["crops"][crop_key]["prices"][market_key] = price
                updated += 1
            time.sleep(1)  # polite delay between requests

    data["date_bs"] = date_bs_label
    data["note"] = "AMPIS बाट स्वचालित रूपमा अद्यावधिक गरिएको दैनिक डाटा।"

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Done. Updated {updated} price points for {date_bs_label}.")
    if missing:
        print(f"Could not fetch (kept previous value): {', '.join(missing)}")


if __name__ == "__main__":
    main()
