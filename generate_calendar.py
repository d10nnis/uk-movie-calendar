import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.filmdates.co.uk/films/year/2026/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

events = []

# Each release is inside an <li> under the release list
for item in soup.select("li.film"):
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

    uid = f"{date_str}-{title.replace(' ', '').replace(':','')}@ukmovies"

    event = f"""BEGIN:VEVENT
UID:{uid}
DTSTART;VALUE=DATE:{date_str}
SUMMARY:{title} - UK Cinema Release
END:VEVENT
"""
    events.append(event)

calendar = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UK Movie Releases 2026//EN
CALSCALE:GREGORIAN
{''.join(events)}
END:VCALENDAR
"""

with open("uk-2026.ics", "w", encoding="utf-8") as f:
    f.write(calendar)
