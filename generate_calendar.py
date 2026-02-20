import os
import requests
from datetime import datetime
from urllib.parse import urlencode

# TMDB API key from environment variable
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/discover/movie"

def get_uk_releases(year, min_popularity=20, min_votes=50):
    """
    Fetch UK movie releases for a given year, filtering by popularity and vote count.
    Only movies with popularity >= min_popularity and votes >= min_votes are included.
    """
    movies = []
    params = {
        "api_key": API_KEY,
        "region": "GB",
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
            popularity = movie.get("popularity", 0)
            vote_count = movie.get("vote_count", 0)

            if release_date and popularity >= min_popularity and vote_count >= min_votes:
                movies.append((release_date, title))

        if data["page"] >= data["total_pages"]:
            break
        params["page"] += 1

    return movies

def build_ics(movies):
    """Generate ICS VEVENT strings from a list of (date, title) tuples"""
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
    # Fetch major UK 2026 releases
    releases = get_uk_releases(2026, min_popularity=20, min_votes=50)
    print(f"Generating ICS for {len(releases)} major releases...")

    calendar_body = build_ics(releases)
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UK Major Movie Releases 2026//EN
CALSCALE:GREGORIAN
{calendar_body}
END:VCALENDAR"""

    with open("uk-2026.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print("ICS file generated successfully.")

if __name__ == "__main__":
    main()
