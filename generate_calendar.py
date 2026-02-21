import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode

API_KEY = os.getenv("TMDB_API_KEY")
DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
DETAILS_URL = "https://api.themoviedb.org/3/movie"

def escape_text(text):
    """Escape special ICS characters"""
    if not text:
        return ""
    return text.replace("\\", "\\\\") \
               .replace(";", "\\;") \
               .replace(",", "\\,") \
               .replace("\n", "\\n")

def get_movie_details(movie_id):
    """Fetch runtime, genres and rating from TMDB movie details endpoint"""
    url = f"{DETAILS_URL}/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-GB"
    }
    response = requests.get(url, params=params)
    data = response.json()

    runtime = data.get("runtime")
    rating = data.get("vote_average")
    genres = ", ".join([g["name"] for g in data.get("genres", [])])

    return runtime, rating, genres

def get_uk_releases(year, month):
    movies = []
    params = {
        "api_key": API_KEY,
        "region": "GB",
        "language": "en-GB",
        "sort_by": "release_date.asc",
        "primary_release_year": year,
        "primary_release_date.gte": f"{year}-{month:02d}-01",
        "primary_release_date.lte": f"{year}-{month:02d}-31",
        "page": 1
    }

    while True:
        url = f"{DISCOVER_URL}?{urlencode(params)}"
        resp = requests.get(url)
        data = resp.json()

        for movie in data.get("results", []):
            if movie.get("release_date"):
                movies.append((
                    movie["release_date"],
                    movie["title"],
                    movie["popularity"],
                    movie["overview"],
                    movie["id"]
                ))

        if data["page"] >= data["total_pages"]:
            break
        params["page"] += 1

    return movies

def select_top_releases(monthly_movies, top_n=5):
    return sorted(monthly_movies, key=lambda x: x[2], reverse=True)[:top_n]

def build_ics(movies):
    events = []

    for release_date, title, _, overview, movie_id in movies:
        try:
            dt = datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            continue

        runtime, rating, genres = get_movie_details(movie_id)

        description = (
            f"Runtime: {runtime} minutes\n"
            f"Rating: {rating}\n"
            f"Genres: {genres}\n\n"
