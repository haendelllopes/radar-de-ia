import feedparser
import json
import os
import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ARXIV_FEEDS = [
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.CL"
]

BLOG_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://www.anthropic.com/news/rss"
]


def collect_feed_items(url, limit=30):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", "")
        })
    return items


def collect_all_sources():
    collected = []
    for feed in ARXIV_FEEDS + BLOG_FEEDS:
        collected.extend(collect_feed_items(feed))
    return collected


def load_prompt():
    with open("radar_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()


def call_llm(prompt, items):
    content = "\n\n".join(
        f"TÍTULO: {i['title']}\nRESUMO: {i['summary']}\nLINK: {i['link']}"
        for i in items
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def main():
    items = collect_all_sources()
    prompt = load_prompt()
    llm_output = call_llm(prompt, items)

    data = {
        "date": datetime.date.today().isoformat(),
        "content": llm_output
    }

    os.makedirs("data", exist_ok=True)
    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Radar gerado com sucesso.")


if __name__ == "__main__":
    main()
