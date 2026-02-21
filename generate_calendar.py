import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode

API_KEY = os.getenv("TMDB_API_KEY")
DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
DETAILS_URL = "https://api.themoviedb.org/3/movie"

# -------------------------------------------------
# Fetch monthly UK releases
# -------------------------------------------------
def get_uk_releases(year, month):
    movies = []

    params = {
        "api_key": API_KEY,
        "region": "GB",
        "language": "en-GB",
        "sort_by": "release_date.asc",
        "primary_release_date.gte": f"{year}-{month:02d}-01",
        "primary_release_date.lte": f"{year}-{month:02d}-31",
        "page": 1
    }

    while True:
        url = f"{DISCOVER_URL}?{urlencode(params)}"
        response = requests.get(url)
        data = response.json()

        for movie in data.get("results", []):
            if movie.get("release_date"):
                movies.append((
                    movie["release_date"],
                    movie["title"],
                    movie["popularity"],
                    movie["overview"],
                    movie["id"],
                    movie["vote_average"]
                ))

        if data["page"] >= data["total_pages"]:
            break

        params["page"] += 1

    return movies


# -------------------------------------------------
# Fetch runtime, genres & trailer
# -------------------------------------------------
def get_movie_details(movie_id):
    url = f"{DETAILS_URL}/{movie_id}?api_key={API_KEY}&language=en-GB&append_to_response=videos"
    response = requests.get(url)
    data = response.json()

    runtime = data.get("runtime", 0)

    genres_list = data.get("genres", [])
    genres = ", ".join(g["name"] for g in genres_list)

    # Find YouTube trailer
    trailer_url = ""
    videos = data.get("videos", {}).get("results", [])
    for video in videos:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break

    return runtime, genres, trailer_url


# -------------------------------------------------
# Select Top 5 by popularity
# -------------------------------------------------
def select_top_releases(monthly_movies, top_n=5):
    sorted_movies = sorted(monthly_movies, key=lambda x: x[2], reverse=True)
    return sorted_movies[:top_n]


# -------------------------------------------------
# Escape ICS special characters
# -------------------------------------------------
def escape_text(text):
    if not text:
        return ""
    return text.replace("\\", "\\\\") \
               .replace(";", "\\;") \
               .replace(",", "\\,") \
               .replace("\n", "\\n")


# -------------------------------------------------
# Build ICS
# -------------------------------------------------
def build_ics(movies):
    events = []

    for release_date, title, _, overview, movie_id, rating in movies:
        try:
            dt = datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            continue

        runtime, genres, trailer_url = get_movie_details(movie_id)

        uid = f"{dt.strftime('%Y%m%d')}-{movie_id}@ukmovies"

        description = (
            f"Runtime: {runtime} minutes\n"
            f"Rating: {rating}\n"
            f"Genres: {genres}\n\n"
            f"{overview}\n\n"
            f"Trailer: {trailer_url}"
        )

        events.append(
            "BEGIN:VEVENT\n"
            f"UID:{uid}\n"
            f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}\n"
            f"SUMMARY:{escape_text(title)}\n"
            f"DESCRIPTION:{escape_text(description)}\n"
            "END:VEVENT\n"
        )

    return "\n".join(events)


# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    today = datetime.now()
    all_releases = []

    for i in range(12):
        month_date = today + relativedelta(months=i)
        year = month_date.year
        month = month_date.month

        monthly_movies = get_uk_releases(year, month)
        top_releases = select_top_releases(monthly_movies, top_n=5)

        print(f"{year}-{month:02d}: {len(top_releases)} top releases")

        all_releases.extend(top_releases)

    all_releases.sort(key=lambda x: x[0])

    calendar_body = build_ics(all_releases)

    ics_content = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//UK Top Movie Releases Rolling 12 Months//EN\n"
        "CALSCALE:GREGORIAN\n"
        f"{calendar_body}"
        "END:VCALENDAR"
    )

    with open("uk-next12months.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"ICS file generated with {len(all_releases)} releases.")


if __name__ == "__main__":
    main()
