import feedparser, json, os, datetime, openai

openai.api_key = os.getenv("OPENAI_API_KEY")

ARXIV_FEEDS = [
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.CL"
]

BLOG_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://www.anthropic.com/news/rss"
]

def collect(url, limit=30):
    feed = feedparser.parse(url)
    return [{
        "title": e.get("title", ""),
        "summary": e.get("summary", ""),
        "link": e.get("link", "")
    } for e in feed.entries[:limit]]

items = []
for f in ARXIV_FEEDS + BLOG_FEEDS:
    items.extend(collect(f))

prompt = open("radar_prompt.txt", encoding="utf-8").read()

content = "\n\n".join(
    f"TÍTULO: {i['title']}\nRESUMO: {i['summary']}\nLINK: {i['link']}"
    for i in items
)

resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": content}
    ],
    temperature=0.3
)

data = {
    "date": datetime.date.today().isoformat(),
    "content": resp.choices[0].message.content
}

os.makedirs("data", exist_ok=True)
json.dump(data, open("data/today.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

