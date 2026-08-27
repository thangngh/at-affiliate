function checkDonationUI() {
  const raw = (document.getElementById("dtxt").value || "").toLowerCase();
  if (!raw.trim()) { alert("Enter the appeal text, URL or org name to check."); return; }
  const red = [
    "gift card", "amazon card", "steam card", "crypto only", "bitcoin", "usdt",
    "western union", "moneygram", "100% to victim", "no overhead", "double your donation",
    "match your donation", "act now", "urgent", "telegram only", "whatsapp only", "dm to donate",
    "dm me", "copy of red cross", "like red cross", "just created", "new charity",
    "no charity number", "no registration", "personal paypal", "send to my wallet",
  ];
  const yellow = [
    "bit.ly", "tinyurl", "t.co", "go.", "rb.gy", "unknown org", "only facebook",
    "only instagram", "no website", "gofundme", "new account", "looks official",
  ];
  let r = 0, y = 0; const hits = [];
  for (const f of red) if (raw.includes(f)) { r++; hits.push(f); }
  for (const f of yellow) if (raw.includes(f)) y++;
  const out = document.getElementById("dOut");
  out.style.display = "block";
  let level, color, advice;
  if (r >= 2) {
    level = "HIGH RISK — likely a scam";
    color = "red";
    advice = "Do NOT send money. Real charities never ask for gift cards, crypto, Western Union, or DMs. Donate only on the official domain (see section 2).";
  } else if (r === 1 || y >= 2) {
    level = "MEDIUM — verify carefully";
    color = "yellow";
    advice = "Check the official registry, confirm the exact domain, and never pay via personal PayPal / gift cards. Prefer the verified orgs in section 2.";
  } else {
    level = "LOW — few red flags";
    color = "green";
    advice = "Still donate only on the organisation's official website. Bookmark it; don't click links from messages.";
  }
  out.innerHTML =
    "Risk: <b class='" + color + "'>" + level + "</b><br>" +
    "Red flags: <b>" + r + "</b>, yellow flags: <b>" + y + "</b><br>" +
    (hits.length ? "Matched: " + hits.join(", ") + "<br>" : "") +
    "<br><span class='" + color + "'>" + advice + "</span><br>" +
    "<span style='color:var(--muted)'>Heuristic only — not official verification. We are not affiliated with any charity.</span>";
}
