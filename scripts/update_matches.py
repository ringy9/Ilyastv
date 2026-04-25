import os
import json
import requests
from datetime import datetime, timedelta, timezone

API_KEY = os.getenv("API_FOOTBALL_KEY")

OUTPUT_FILE = "home.json"

VIDEO_URL = "https://raw.githubusercontent.com/ringy9/AymaneTV/refs/heads/main/beim.mp4"
THUMBNAIL = "https://i.postimg.cc/Gtnx9YdF/Whats-App-Image-2026-04-15-at-00-10-19.jpg"

LEAGUES = {
    39: "Premier League",
    140: "LaLiga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    307: "Botola Pro",
    186: "Algerian Ligue 1",
    202: "Tunisian Ligue 1",
    233: "Egyptian Premier League",
    278: "Saudi Pro League"
}

HEADERS = {
    "x-apisports-key": API_KEY or ""
}


def safe_get(value, default=""):
    if value is None:
        return default
    return value


def format_time(raw_date):
    try:
        dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        return dt.strftime("%a %d %b - %H:%M")
    except Exception:
        return raw_date


def get_fixtures(date_value):
    all_matches = []

    if not API_KEY:
        print("ERROR: API_FOOTBALL_KEY is missing from GitHub Secrets")
        return all_matches

    print(f"Fetching fixtures for date: {date_value}")

    for league_id, default_league_name in LEAGUES.items():
        url = "https://v3.football.api-sports.io/fixtures"

        params = {
            "date": date_value,
            "league": league_id,
            "season": 2024
        }

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=25
            )

            print(f"League {league_id} status:", response.status_code)

            if response.status_code != 200:
                print("Response error:", response.text[:300])
                continue

            data = response.json()

            errors = data.get("errors")
            if errors:
                print(f"API errors for league {league_id}:", errors)

            fixtures = data.get("response", [])
            print(f"League {league_id} matches found:", len(fixtures))

            for item in fixtures:
                fixture = item.get("fixture", {})
                league = item.get("league", {})
                teams = item.get("teams", {})

                home = teams.get("home", {})
                away = teams.get("away", {})

                home_name = safe_get(home.get("name"), "Home Team")
                away_name = safe_get(away.get("name"), "Away Team")

                league_name = safe_get(
                    league.get("name"),
                    default_league_name
                )

                league_logo = safe_get(league.get("logo"), THUMBNAIL)

                match = {
                    "leagueId": league_id,
                    "leagueName": league_name,
                    "homeTeam": home_name,
                    "awayTeam": away_name,
                    "homeLogo": safe_get(home.get("logo")),
                    "awayLogo": safe_get(away.get("logo")),
                    "time": format_time(safe_get(fixture.get("date"))),
                    "thumbnail": league_logo if league_logo else THUMBNAIL,
                    "isLive": False,
                    "streamTitle": f"ملخص {home_name} vs {away_name}",
                    "streamUrl": VIDEO_URL,
                    "streamType": "mp4"
                }

                all_matches.append(match)

        except Exception as e:
            print(f"Error fetching league {league_id}: {e}")

    return all_matches


def build_leagues(matches):
    leagues = []
    seen = set()

    for match in matches:
        league_id = match.get("leagueId")

        if league_id in seen:
            continue

        seen.add(league_id)

        leagues.append({
            "id": league_id,
            "name": match.get("leagueName", ""),
            "image": match.get("thumbnail", THUMBNAIL) or THUMBNAIL
        })

    return leagues


def build_news(matches):
    news = []

    for index, match in enumerate(matches[:6], start=1):
        home = match.get("homeTeam", "")
        away = match.get("awayTeam", "")
        league = match.get("leagueName", "")

        news.append({
            "id": index,
            "title": f"مواجهة مرتقبة بين {home} و {away}",
            "cover": match.get("thumbnail", THUMBNAIL) or THUMBNAIL,
            "content": f"تتجه الأنظار إلى مباراة {home} ضد {away} ضمن منافسات {league}. مواجهة مهمة ينتظرها عشاق كرة القدم لمعرفة تفاصيلها ونتيجتها.",
            "timeAgo": f"{index} hour ago"
        })

    return news


def main():
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)

    dates = [
        today.strftime("%Y-%m-%d"),
        tomorrow.strftime("%Y-%m-%d")
    ]

    print("Dates:", dates)

    matches = []

    for date_value in dates:
        matches.extend(get_fixtures(date_value))

    for index, match in enumerate(matches, start=1):
        match["id"] = index

    leagues = build_leagues(matches)
    news = build_news(matches)

    home_json = {
        "matchDetailsSection": {
            "title": "أهم مباريات اليوم والغد",
            "image": THUMBNAIL,
            "text": "تابع أهم مباريات اليوم والغد من الدوريات الأوروبية والعربية، مع جدول محدث وأخبار رياضية."
        },
        "news": news,
        "leagues": leagues,
        "matches": matches,
        "highlights": []
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(home_json, file, ensure_ascii=False, indent=2)

    print(f"Done. Total matches: {len(matches)}")
    print(f"Updated file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
