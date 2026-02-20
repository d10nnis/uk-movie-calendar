import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.filmdates.co.uk/films/year/2026/"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

film_items = soup.select("li.film")
print("Film items found:", len(film_items))

events = []

for item in film_items:
    title_tag = item.select_one("h3 a")
    date_tag = item.select_one("span.release-date")

    if not title_tag or not date_tag:
        continue

    title = title_tag.text.strip()
    date_text = date_tag.text.strip()

    try:
        date_obj = datetime.strptime(date_text, "%d %b %Y")
        date_str = date_obj.strftime("%Y%m%d")
    except:
        continue

    events.append(title)

print("Events parsed:", len(events))

with open("uk-2026.ics", "w", encoding="utf-8") as f:
    f.write("TEST FILE")

print("File written.")
