import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://www.filmdates.co.uk/films/year/2026/"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

events = []

# Find all rows in the releases table
for row in soup.select("table tbody tr"):
    date_cell = row.select_one("td")
    title_link = row.select_one("a")

    if not date_cell or not title_link:
        continue

    date_text = date_cell.text.strip()
    title = title_link.text.strip()

    # Parse UK date format: e.g., 30 Jan 2026
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
