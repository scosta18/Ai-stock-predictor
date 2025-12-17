import times
import requests
from bs4 import BeautifulSoup

HEADESRS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}

def fetch_yahoo_news(symbol: str, limit: int = 20):
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    session = requests.Session()

    time.sleep(1.5)

    response = session.get(url, headers=HEADESRS, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"Yahoo blocked request: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    seen_titles = set()

    for item in soup.select("li.js-stream-content"):
        title_tag = item.find("h3")
        link_tag = item.find("a", href=True)
        source_tag = item.find("span")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        if title in seen_titles:
            continue

        seen_titles.add(title)

        link = link_tag["href"]
        if link.startswith("/"):
            link = "https://finance.yahoo.com" + link

        articles.append({
            "symbol": symbol,
            "title": title,
            "link": link,
            "source": source_tag.get_text(strip=True) if source_tag else "Yahooo Finance",
        })

        if len(articles) >= limit:
            break

    return articles