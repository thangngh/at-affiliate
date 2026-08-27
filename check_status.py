import csv, sys, at_api

sys.stdout.reconfigure(encoding="utf-8")
tok, sd = at_api.load_token()

# top 20 ids from csv
ids = []
with open("output/top_campaigns.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        ids.append((row["rank"], row["name"], row["id"]))

# fetch all campaigns (any approval) and map id->approval
status = {}
for page in range(1, 8):
    res = at_api._request("GET", "/v1/campaigns", tok, params={"limit": 50, "page": page})
    if not isinstance(res, dict):
        break
    d = res.get("data", [])
    if isinstance(d, dict):
        d = d.get("data", [])
    if not d:
        break
    for c in d:
        status[str(c.get("id"))] = c.get("approval")
    if len(d) < 50:
        break

print("Approval status of top-20 you applied:")
for rank, name, cid in ids:
    st = status.get(cid, "NOT FOUND (chua apply hoac bi tu choi)")
    mark = "APPROVED" if str(st).lower() == "successful" else str(st)
    print("%2s. %-42s -> %s" % (rank, name[:42], mark))
