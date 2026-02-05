import json, os, datetime, openai

openai.api_key = os.getenv("OPENAI_API_KEY")

MONTH = datetime.date.today().strftime("%Y-%m")
BASE_PATH = f"data/tools/{MONTH}.json"
CURRENT_PATH = "data/tools/current.json"
LIMIT = 30

existing = []
if os.path.exists(BASE_PATH):
    existing = json.load(open(BASE_PATH, encoding="utf-8")).get("tools", [])

if len(existing) >= LIMIT:
    json.dump({"month": MONTH, "tools": existing},
              open(CURRENT_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    exit()

prompt = open("tools_prompt.txt", encoding="utf-8").read()

resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": prompt}],
    temperature=0.3
)

new_tools = json.loads(resp.choices[0].message.content).get("tools", [])

names = {t["name"].lower() for t in existing}
for tool in new_tools:
    if tool["name"].lower() not in names and len(existing) < LIMIT:
        existing.append(tool)

os.makedirs("data/tools", exist_ok=True)
payload = {"month": MONTH, "tools": existing}

json.dump(payload, open(BASE_PATH, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
json.dump(payload, open(CURRENT_PATH, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

