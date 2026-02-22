import requests
import calendar
from datetime import datetime
from ics import Calendar, Event

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_TMDB_API_KEY"
REGION = "GB"
LANGUAGE = "en-GB"
YEAR = 2026
TOP_N = 10  # <-- change this number if needed

BASE_URL = "https://api.themoviedb.org/3/discover/movie"

# -----------------------------
# Fetch all UK releases for a month
# -----------------------------
def get_uk_releases(year, month):
    all_movies = []

    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day}"

    params = {
        "api_key": API_KEY,
        "region": REGION,
        "language": LANGUAGE,
        "sort_by": "release_date.asc",
        "primary_release_date.gte": start_date,
        "primary_release_date.lte": end_date,
        "page": 1,
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    total_pages = data.get("total_pages", 1)

    for page in range(1, total_pages + 1):
        params["page"] = page
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        all_movies.extend(data.get("results", []))

    return all_movies


# -----------------------------
# Create ICS calendar
# -----------------------------
def create_calendar(year):
    cal = Calendar()

    for month in range(1, 13):
        print(f"Processing {calendar.month_name[month]}...")

        movies = get_uk_releases(year, month)

        # Sort by popularity (highest first)
        movies_sorted = sorted(
            movies,
            key=lambda x: x.get("popularity", 0),
            reverse=True
        )

        # Take top N
        top_movies = movies_sorted[:TOP_N]

        for movie in top_movies:
            release_date = movie.get("release_date")
            if not release_date:
                continue

            event = Event()
            event.name = movie["title"]
            event.begin = datetime.strptime(release_date, "%Y-%m-%d").date()
            event.make_all_day()

            overview = movie.get("overview", "")
            popularity = movie.get("popularity", 0)

            event.description = (
                f"Popularity: {popularity}\n\n"
                f"{overview}"
            )

            cal.events.add(event)

    with open(f"UK_Movies_{year}.ics", "w", encoding="utf-8") as f:
        f.writelines(cal)

    print("Calendar created successfully!")


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    create_calendar(YEAR)
