import json
import os
import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MONTH = datetime.date.today().strftime("%Y-%m")
BASE_PATH = f"docs/tools/{MONTH}.json"
CURRENT_PATH = "docs/tools/current.json"
LIMIT = 30


# Carrega ferramentas existentes do mês
existing = []
if os.path.exists(BASE_PATH):
    with open(BASE_PATH, encoding="utf-8") as f:
        existing = json.load(f).get("tools", [])

# Se já bateu o limite, apenas replica para current.json
if len(existing) >= LIMIT:
    payload = {"month": MONTH, "tools": existing}
    os.makedirs("docs/tools", exist_ok=True)
    with open(CURRENT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    exit()


# Carrega prompt
with open("tools_prompt.txt", encoding="utf-8") as f:
    prompt = f.read()


# Chamada ao modelo (JSON forçado)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt}
    ],
    temperature=0.3,
    response_format={"type": "json_object"}
)

parsed = json.loads(response.choices[0].message.content)
new_tools = parsed.get("tools", [])


# Deduplicação e incremento
names = {t["name"].lower() for t in existing}

for tool in new_tools:
    if tool["name"].lower() not in names and len(existing) < LIMIT:
        existing.append(tool)
        names.add(tool["name"].lower())


# Salva arquivos
payload = {"month": MONTH, "tools": existing}

os.makedirs("docs/tools", exist_ok=True)

with open(BASE_PATH, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

with open(CURRENT_PATH, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print("Ferramentas atualizadas com sucesso.")
