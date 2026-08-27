"""Accesstrade Publisher API client.

Reads the API token from a local .env file (never hardcode it, never paste it
in chat). Token is obtained at https://pub2.accesstrade.vn/profile/api_key

Usage:
  python at_api.py campaigns [--keyword "tài chính"] [--limit 20]
  python at_api.py link --campaign_id ID --url "https://shop.url/product"
  python at_api.py transactions [--limit 20]
  python at_api.py build --niche finance
"""

import argparse
import csv
import json
import os
import urllib.request
import urllib.error
import urllib.parse
import unicodedata
import sys
from datetime import datetime


def _normalize(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

API_BASE = "https://api.accesstrade.vn"


def load_token():
    """Load AT_TOKEN from .env in the script directory (or CWD)."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), ".env")
    token = ""
    short_domain = ""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == "AT_TOKEN":
                    token = val
                elif key == "AT_SHORT_DOMAIN":
                    short_domain = val
    if not token or token == "PASTE_YOUR_TOKEN_HERE":
        raise SystemExit(
            "ERROR: AT_TOKEN not set. Copy .env.example to .env and paste your "
            "token from https://pub2.accesstrade.vn/profile/api_key"
        )
    return token, short_domain


def _request(method, path, token, body=None, params=None):
    url = API_BASE + path
    if params:
        q = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        url += "?" + q
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Token " + token)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        raise SystemExit(f"HTTP {e.code} on {method} {url}: {detail}")


def get_campaigns(token, approval="successful", limit=50, page=1):
    params = {"limit": min(int(limit), 50), "page": page, "approval": approval}
    return _request("GET", "/v1/campaigns", token, params=params)


def create_link(token, campaign_id, urls, short_domain=None, utm=None):
    body = {"campaign_id": campaign_id, "urls": urls}
    if short_domain:
        body["short_domain"] = short_domain
    if utm:
        body.update(utm)
    return _request("POST", "/v1/product_link/create", token, body=body)


def get_transactions(token, limit=20):
    params = {"limit": limit}
    return _request("GET", "/v1/transactions", token, params=params)


# --- Niche configuration: tài chính/làm giàu, mẹ & bé, thời trang ---
NICHE_KEYWORDS = {
    "finance": ["tài chính", "vay", "thẻ", "đầu tư", "chứng khoán", "bảo hiểm", "tích điểm"],
    "mother_baby": ["mẹ", "bé", "em bé", "sữa", "tã", "bỉm", "đồ chơi", "mẹ và bé"],
    "fashion": ["thời trang", "quần áo", "giày", "túi", "trang sức", "mỹ phẩm", "lam dep"],
}

# Content draft templates per niche. {link} is replaced with the affiliate link.
CONTENT_TEMPLATES = {
    "finance": (
        "## [Tên bài] - Cẩm nang {name}\n\n"
        "Bạn đang tìm hiểu về {name} từ {merchant}? Dưới đây là những điều cần biết "
        "trước khi đăng ký, cùng ưu/nhược điểm thực tế.\n\n"
        "- Điều kiện: ...\n- Lợi ích: ...\n- Lưu ý phí/ kỳ hạn: ...\n\n"
        "👉 Tìm hiểu & đăng ký tại đây: {link}\n"
    ),
    "mother_baby": (
        "## Review [Sản phẩm] - {name}\n\n"
        "Là mẹ bỉm, mình chọn {name} của {merchant} vì ... (trải nghiệm thật).\n\n"
        "- Phù hợp: ...\n- Ưu điểm: ...\n- Lưu ý: ...\n\n"
        "🛒 Xem chi tiết & đặt mua: {link}\n"
    ),
    "fashion": (
        "## Gợi ý phong cách - {name}\n\n"
        "{name} từ {merchant} đang được săn đón nhờ ...\n\n"
        "- Phối đồ: ...\n- Size/ giá: ...\n- Tips chọn: ...\n\n"
        "🛍️ Mua ngay tại đây: {link}\n"
    ),
}

# Short blurb per niche, shown as card description on the site.
NICHE_BLURB = {
    "finance": "Cơ hội tài chính, thẻ, đầu tư và hoàn tiền hấp dẫn.",
    "mother_baby": "Đồ dùng mẹ & bé chính hãng, giá tốt mỗi ngày.",
    "fashion": "Thời trang, mỹ phẩm và phụ kiện theo xu hướng.",
}


def build_niche(token, short_domain, niche, limit=50, max_pages=6):
    keys = [_normalize(k) for k in NICHE_KEYWORDS.get(niche, [niche])]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    seen = set()
    rows = []
    for page in range(1, max_pages + 1):
        try:
            res = get_campaigns(token, limit=limit, page=page)
        except SystemExit as e:
            print(f"  [skip '{niche}'] {e}")
            return None
        if not isinstance(res, dict):
            break
        data = res.get("data", [])
        if isinstance(data, dict):
            data = data.get("data", [])
        if not data:
            break
        for c in data:
            hay = _normalize(" ".join(str(c.get(f, "")) for f in
                                     ["name", "description", "category", "sub_category", "merchant"]))
            if not any(k in hay for k in keys):
                continue
            cid = c.get("id") or c.get("campaign_id")
            if cid in seen:
                continue
            seen.add(cid)
            rows.append({
                "niche": niche,
                "campaign_id": cid,
                "name": c.get("name") or c.get("title"),
                "merchant": c.get("merchant"),
                "category": c.get("category"),
                "sub_category": c.get("sub_category"),
                "commission": c.get("default_commission") or c.get("commission"),
                "status": c.get("status"),
                "url": c.get("url"),
            })
        if len(data) < limit:
            break
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(out_dir, f"campaigns_{niche}_{ts}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["niche", "campaign_id", "name", "merchant", "category", "sub_category", "commission", "status", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {len(rows)} campaigns -> {csv_path}")
    return csv_path


def _latest_csv(niche):
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    files = [f for f in os.listdir(out_dir) if f.startswith(f"campaigns_{niche}_") and f.endswith(".csv")] if os.path.isdir(out_dir) else []
    return os.path.join(out_dir, sorted(files)[-1]) if files else None


def generate_content(token, short_domain, niche):
    csv_path = _latest_csv(niche)
    if not csv_path:
        raise SystemExit(f"No campaign CSV for '{niche}'. Run: python at_api.py build --niche {niche}")
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    template = CONTENT_TEMPLATES.get(niche, CONTENT_TEMPLATES["finance"])
    out_dir = os.path.dirname(csv_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(out_dir, f"content_{niche}_{ts}.md")
    json_path = os.path.join(out_dir, f"links_{niche}_{ts}.json")
    items = []
    count = 0
    with open(md_path, "w", encoding="utf-8") as out:
        for r in rows:
            cid = r.get("campaign_id")
            url = r.get("url")
            link = ""
            if cid and url:
                try:
                    res = create_link(token, cid, url, short_domain or None, None)
                    sl = res.get("data", {}).get("success_link", [{}])
                    link = sl[0].get("short_link") or sl[0].get("aff_link") or ""
                except SystemExit as e:
                    link = f"(link err: {e})"
            text = template.format(
                name=r.get("name", ""),
                merchant=r.get("merchant", ""),
                commission=r.get("commission", ""),
                link=link,
            )
            out.write(text + "\n---\n\n")
            items.append({
                "name": r.get("name", ""),
                "merchant": r.get("merchant", ""),
                "commission": r.get("commission", ""),
                "link": link,
            })
            count += 1
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(items, jf, ensure_ascii=False, indent=2)
    print(f"Generated {count} drafts -> {md_path}")
    print(f"Links JSON          -> {json_path}")


def build_site():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.isdir(out_dir):
        raise SystemExit("No output dir. Run build + gen first.")
    latest = {}
    for fn in os.listdir(out_dir):
        if not fn.startswith("links_") or not fn.endswith(".json"):
            continue
        niche = fn[len("links_"):-len(".json")].split("_")[0]
        if niche not in latest or fn > latest[niche]:
            latest[niche] = fn
    grouped = {}
    for niche, fn in latest.items():
        with open(os.path.join(out_dir, fn), encoding="utf-8") as f:
            grouped[niche] = json.load(f)
    if not grouped:
        raise SystemExit("No link JSONs found. Run gen first.")
    # de-duplicate products that matched multiple niches (keep first occurrence)
    seen_links = set()
    cards = []
    for niche, items in grouped.items():
        for it in items:
            if not it.get("link") or it["link"].startswith("(link"):
                continue
            if it["link"] in seen_links:
                continue
            seen_links.add(it["link"])
            cards.append(
                f'      <div class="card">\n'
                f'        <div class="tag">{niche}</div>\n'
                f'        <h3>{it.get("name","")}</h3>\n'
                f'        <p class="merch">{it.get("merchant","")}</p>\n'
                f'        <p class="desc">{NICHE_BLURB.get(niche,"")}</p>\n'
                f'        <a class="btn" href="{it.get("link","")}" target="_blank" rel="nofollow">Xem &amp; nhận ưu đãi</a>\n'
                f'      </div>'
            )
    total = len(cards)
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deal &amp; Affiliate Hub - Tài chính, Mẹ &amp; Bé, Thời trang</title>
<meta name="description" content="Tổng hợp ưu đãi affiliate từ Accesstrade: tài chính, mẹ và bé, thời trang. Link deal chính chủ, cập nhật mỗi ngày.">
<meta property="og:title" content="Deal &amp; Affiliate Hub">
<meta property="og:description" content="Tổng hợp ưu đãi affiliate từ Accesstrade: tài chính, mẹ và bé, thời trang.">
<meta property="og:type" content="website">
<style>
  body {{ font-family: system-ui, Segoe UI, Roboto, Arial; margin:0; background:#f6f7fb; color:#1a1a2e; }}
  header {{ background:#5b2be0; color:#fff; padding:28px 16px; text-align:center; }}
  header h1 {{ margin:0; font-size:24px; }}
  .intro {{ max-width:960px; margin:0 auto; padding:18px 20px 0; color:#444; font-size:15px; }}
  .wrap {{ max-width:960px; margin:0 auto; padding:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:14px; }}
  .card {{ background:#fff; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,.06); display:flex; flex-direction:column; gap:8px; }}
  .tag {{ align-self:flex-start; background:#eef; color:#5b2be0; font-size:12px; padding:2px 8px; border-radius:999px; text-transform:capitalize; }}
  .card h3 {{ margin:0; font-size:16px; }}
  .merch {{ margin:0; color:#777; font-size:13px; }}
  .desc {{ margin:0; color:#555; font-size:13px; line-height:1.4; }}
  .btn {{ margin-top:auto; text-align:center; background:#5b2be0; color:#fff; text-decoration:none; padding:9px 12px; border-radius:8px; font-size:14px; }}
  footer {{ text-align:center; color:#999; padding:20px; font-size:13px; }}
</style>
</head>
<body>
<header><h1>Deal &amp; Affiliate Hub</h1><p>{total} ưu đãi đang chờ bạn</p></header>
<p class="intro">Chúng tôi tổng hợp các chương trình affiliate uy tín từ Accesstrade (Tiki, giới thiệu bạn, và nhiều thương hiệu khác). Nhấn vào từng ưu đãi để xem chi tiết và nhận quyền lợi từ trang chủ chính chủ.</p>
<div class="wrap"><div class="grid">
{chr(10).join(cards)}
</div></div>
<footer>Affiliate tự động qua Accesstrade · Vui lòng review kỹ trước khi đăng</footer>
</body>
</html>
"""
    site_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
    os.makedirs(site_dir, exist_ok=True)
    site_path = os.path.join(site_dir, "index.html")
    with open(site_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built site with {total} cards -> {site_path}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="Accesstrade Publisher API client")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("campaigns")
    pc.add_argument("--keyword")
    pc.add_argument("--category")
    pc.add_argument("--limit", type=int, default=50)

    pl = sub.add_parser("link")
    pl.add_argument("--campaign_id", required=True)
    pl.add_argument("--url", required=True, help="Product/page URL to wrap")
    pl.add_argument("--utm_source")
    pl.add_argument("--utm_campaign")

    pt = sub.add_parser("transactions")
    pt.add_argument("--limit", type=int, default=20)

    pb = sub.add_parser("build")
    pb.add_argument("--niche", required=True, choices=list(NICHE_KEYWORDS.keys()) + ["all"])
    pb.add_argument("--limit", type=int, default=50)

    pg = sub.add_parser("gen")
    pg.add_argument("--niche", required=True, choices=list(NICHE_KEYWORDS.keys()))

    ps = sub.add_parser("site")

    args = p.parse_args()
    token, short_domain = load_token()

    if args.cmd == "campaigns":
        res = get_campaigns(token, limit=args.limit)
        data = res.get("data", [])
        if isinstance(data, dict):
            data = data.get("data", [])
        if args.keyword or args.category:
            keys = [_normalize(args.keyword)] if args.keyword else []
            cat = _normalize(args.category) if args.category else None
            data = [c for c in data if
                    (any(k in _normalize(str(c.get("name", ""))) for k in keys) if keys else True)
                    and (cat in _normalize(str(c.get("category", ""))) if cat else True)]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.cmd == "link":
        utm = {}
        if args.utm_source:
            utm["utm_source"] = args.utm_source
        if args.utm_campaign:
            utm["utm_campaign"] = args.utm_campaign
        res = create_link(token, args.campaign_id, args.url, short_domain or None, utm or None)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "transactions":
        res = get_transactions(token, limit=args.limit)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "build":
        niches = list(NICHE_KEYWORDS.keys()) if args.niche == "all" else [args.niche]
        for n in niches:
            print(f"== Building niche: {n} ==")
            build_niche(token, short_domain, n, args.limit)
    elif args.cmd == "gen":
        generate_content(token, short_domain, args.niche)
    elif args.cmd == "site":
        build_site()


if __name__ == "__main__":
    main()
