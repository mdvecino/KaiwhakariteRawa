from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup, Tag

router = APIRouter()

@router.get("/maori-news")
def get_maori_news():
    url = "https://www.teaonews.co.nz/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    news_items = []

    for article in soup.select("article"):
        title_tag = article.find("h2")
        link_tag = article.find("a", href=True)
        summary_tag = article.find("p")
        if title_tag and isinstance(link_tag, Tag):
            news_items.append({
                "title": title_tag.get_text(strip=True),
                "url": link_tag.get("href"),
                "summary": summary_tag.get_text(strip=True) if summary_tag else ""
            })
        if len(news_items) >= 5:
            break

    return {"news": news_items} 