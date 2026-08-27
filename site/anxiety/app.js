function anxietyUI() {
  const names = ["q1", "q2", "q2b", "q3", "q4"];
  let score = 0, answered = 0;
  for (const n of names) {
    const sel = document.querySelector('input[name="' + n + '"]:checked');
    if (sel) { score += parseInt(sel.value, 10); answered++; }
  }
  if (answered < names.length) { alert("Please answer all 5 questions."); return; }
  const out = document.getElementById("aOut");
  out.style.display = "block";
  let level, color, tips;
  if (score <= 4) {
    level = "You're doing okay";
    color = "green";
    tips = "Keep a healthy balance: set one news check per day, not constant.";
  } else if (score <= 9) {
    level = "Mild news stress";
    color = "yellow";
    tips = "Pick 1 reliable source, mute war keywords, and protect sleep (no news 1h before bed).";
  } else {
    level = "High war-news anxiety";
    color = "red";
    tips = "Limit to ONE checked update/day, take real action locally (donate/vounteer verified orgs), talk to friends or a helpline. You are not helpless.";
  }
  out.innerHTML = "Score: <b>" + score + "/13</b> — <b class='" + color + "'>" + level + "</b><br><br>" + tips +
    "<br><br><span style='color:var(--muted)'>Not medical advice. Free tool by thangnh.</span>";
}
