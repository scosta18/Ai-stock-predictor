import requests
from bs4 import BeautifulSoup

def get_yahoo_news(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
    }

    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        print("Yahoo blocked the request or there's an error.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    news_list = []
    # Yahoo news article links typically start with /news/
    for a_tag in soup.select("a[href^='/news/']"):
        title = a_tag.get_text(strip=True)
        relative_link = a_tag['href']
        full_url = f"https://finance.yahoo.com{relative_link}"
        if title and full_url not in [n['url'] for n in news_list]:  # Avoid duplicates
            news_list.append({'title': title, 'url': full_url})

    return news_list

# Test
if __name__ == "__main__":
    ticker = input("Enter stock ticker symbol (e.g., TSLA): ").upper()
    news = get_yahoo_news(ticker)

    if news:
        for item in news:
            print(item['title'])
            print(item['url'])
            print("----")
    else:
        print("No news found. Yahoo may have changed the structure or blocked access.")
