import os
import requests
from datetime import datetime
from urllib.parse import urlencode

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/discover/movie"

def get_uk_releases(year, month=None, min_popularity=20, min_votes=50):
    """
    Fetch UK movie releases from TMDB for a given year (and optional month),
    filtering by popularity and vote count.
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

    if month:
        # Filter to the specific month
        params["primary_release_date.gte"] = f"{year}-{month:02d}-01"
        params["primary_release_date.lte"] = f"{year}-{month:02d}-31"

    while True:
        url = f"{BASE_URL}?{urlencode(params)}"
        resp = requests.get(url)
        data = resp.json()

        for movie in data.get("results", []):
            title = movie.get("title")
            release_date = movie.get("release_date")
            popularity = movie.get("popularity", 0)
            vote_count = movie.get("vote_count", 0)

            # Keep only “major” releases
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
    all_releases = []

    # Fetch month by month to cover all 12 months
    for month in range(1, 13):
        monthly_releases = get_uk_releases(2026, month=month, min_popularity=20, min_votes=50)
        print(f"Month {month:02d}: {len(monthly_releases)} major releases")
        all_releases.extend(monthly_releases)

    # Sort by release date
    all_releases.sort(key=lambda x: x[0])

    calendar_body = build_ics(all_releases)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UK Major Movie Releases 2026//EN
CALSCALE:GREGORIAN
{calendar_body}
END:VCALENDAR"""

    with open("uk-2026.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"ICS file generated with {len(all_releases)} major releases.")

if __name__ == "__main__":
    main()
