import json, sys, glob

sys.stdout.reconfigure(encoding="utf-8")
files = sorted(glob.glob("output/links_all_*.json"))
if not files:
    print("no links file")
    sys.exit()
items = json.load(open(files[-1], encoding="utf-8"))
print("Total links:", len(items))
for it in items:
    lk = it.get("link", "")
    tag = "OK" if lk.startswith("http") else "ERR"
    name = str(it.get("name", ""))[:42]
    print("[%s] %s -> %s" % (tag, name, lk))
