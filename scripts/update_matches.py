import requests
import json
from datetime import datetime, timedelta

API_KEY = "API_FOOTBALL_KEY"
OUTPUT_FILE = "home.json"

HEADERS = {
    "x-apisports-key": API_KEY
}

LEAGUES = {
    39: "Premier League",
    140: "LaLiga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    307: "Botola Pro",
    233: "Egyptian Premier League",
    278: "Saudi Pro League",
    202: "Tunisian Ligue 1",
    186: "Algerian Ligue 1"
}

VIDEO_URL = "https://raw.githubusercontent.com/ringy9/AymaneTV/refs/heads/main/beim.mp4"
THUMBNAIL = "https://i.postimg.cc/Gtnx9YdF/Whats-App-Image-2026-04-15-at-00-10-19.jpg"

def get_fixtures(date):
    all_matches = []

    for league_id, league_name in LEAGUES.items():
        url = "https://v3.football.api-sports.io/fixtures"
        params = {
            "date": date,
            "league": league_id,
            "season": 2025
        }

        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=20)
            data = r.json()

            for item in data.get("response", []):
                fixture = item["fixture"]
                teams = item["teams"]
                league = item["league"]

                all_matches.append({
                    "leagueId": league_id,
                    "leagueName": league.get("name", league_name),
                    "homeTeam": teams["home"]["name"],
                    "awayTeam": teams["away"]["name"],
                    "homeLogo": teams["home"].get("logo", ""),
                    "awayLogo": teams["away"].get("logo", ""),
                    "time": fixture.get("date", ""),
                    "thumbnail": league.get("logo", THUMBNAIL),
                    "isLive": False,
                    "streamTitle": f"ملخص {teams['home']['name']} vs {teams['away']['name']}",
                    "streamUrl": VIDEO_URL,
                    "streamType": "mp4"
                })

        except Exception as e:
            print(f"Error league {league_id}: {e}")

    return all_matches


today = datetime.now()
dates = [
    today.strftime("%Y-%m-%d"),
    (today + timedelta(days=1)).strftime("%Y-%m-%d")
]

matches = []

for d in dates:
    matches.extend(get_fixtures(d))

for index, match in enumerate(matches, start=1):
    match["id"] = index

leagues = []
seen = set()

for match in matches:
    if match["leagueId"] not in seen:
        seen.add(match["leagueId"])
        leagues.append({
            "id": match["leagueId"],
            "name": match["leagueName"],
            "image": match["thumbnail"] or THUMBNAIL
        })

home_json = {
    "matchDetailsSection": {
        "title": "أهم مباريات اليوم والغد",
        "image": THUMBNAIL,
        "text": "تابع أهم مباريات اليوم والغد من الدوريات الأوروبية والعربية، مع جدول محدث وأخبار رياضية."
    },
    "news": [],
    "leagues": leagues,
    "matches": matches,
    "highlights": []
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(home_json, f, ensure_ascii=False, indent=2)

print(f"Updated {OUTPUT_FILE} with {len(matches)} matches")
