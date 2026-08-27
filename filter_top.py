import at_api, sys, csv, os, re

sys.stdout.reconfigure(encoding="utf-8")
tok, sd = at_api.load_token()


def parse_com(s):
    if not s:
        return 0, ""
    raw = str(s).strip()
    # all numeric tokens (allow . or , as thousands separators)
    tokens = re.findall(r"\d[\d.,]*", raw)
    best = 0
    for t in tokens:
        if "," in t and "." in t:
            t = t.replace(",", "")
        elif "." in t:
            t = t.replace(".", "")
        elif "," in t:
            t = t.replace(",", "")
        try:
            best = max(best, int(t))
        except ValueError:
            pass
    return best, raw


allc = []
for page in range(1, 8):
    res = at_api._request("GET", "/v1/campaigns", tok, params={"limit": 50, "page": page})
    if not isinstance(res, dict):
        break
    d = res.get("data", [])
    if isinstance(d, dict):
        d = d.get("data", [])
    if not d:
        break
    allc += d
    if len(d) < 50:
        break

unreg = [c for c in allc if str(c.get("approval")) not in ("successful", "Successful")]
scored = []
for c in unreg:
    val, raw = parse_com(c.get("max_com"))
    scored.append((val, raw, c))
scored.sort(key=lambda x: -x[0])
top = scored[:20]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "top_campaigns.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["rank", "name", "merchant", "max_com", "category", "id", "url"])
    for i, (val, raw, c) in enumerate(top, 1):
        w.writerow([i, c.get("name"), c.get("merchant"), raw, c.get("category"), c.get("id"), c.get("url")])

print("Top 20 campaigns by max commission:")
for i, (val, raw, c) in enumerate(top, 1):
    name = str(c.get("name"))[:45]
    print(f"{i:2}. {val:>10} | {name:45} | {c.get('merchant')}")
print()
print("Saved ->", out)
