import os
import requests
from datetime import datetime
from urllib.parse import urlencode

# Get your TMDB API key from environment variable
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/discover/movie"

def get_uk_releases(year):
    """Fetch UK movie releases from TMDB for a given year"""
    movies = []
    params = {
        "api_key": API_KEY,
        "region": "GB",      # UK region
        "language": "en-GB",
        "sort_by": "release_date.asc",
        "primary_release_year": year,
        "page": 1
    }

    while True:
        url = f"{BASE_URL}?{urlencode(params)}"
        resp = requests.get(url)
        data = resp.json()

        for movie in data.get("results", []):
            title = movie.get("title")
            release_date = movie.get("release_date")
            if release_date:
                movies.append((release_date, title))

        if data["page"] >= data["total_pages"]:
            break

        params["page"] += 1

    return movies

def build_ics(movies):
    """Generate ICS VEVENT strings from list of (date, title) tuples"""
    events = []
    for date_str, title in movies:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        uid = f"{dt.strftime('%Y%m%d')}-{title.replace(' ', '').replace(':','')}@ukmovies"
        events.append(
            f"""BEGIN:VEVENT
UID:{uid}
DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}
SUMMARY:{title} — UK Cinema Release
END:VEVENT
""")
    return "\n".join(events)

def main():
    releases = get_uk_releases(2026)
    calendar_body = build_ics(releases)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UK Movie Releases 2026//EN
CALSCALE:GREGORIAN
{calendar_body}
END:VCALENDAR"""

    with open("uk-2026.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
    print(f"ICS file generated with {len(releases)} movies.")

if __name__ == "__main__":
    main()
