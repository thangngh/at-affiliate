function num(s) {
  const n = String(s || "").replace(/[^0-9.]/g, "");
  const v = parseFloat(n);
  return isNaN(v) ? 0 : v;
}

function costUI() {
  const energy = num(document.getElementById("energy").value);
  const food = num(document.getElementById("food").value);
  if (energy <= 0 && food <= 0) { alert("Enter at least one bill amount."); return; }

  const E_RATE = 0.25; // illustrative war-driven energy inflation
  const F_RATE = 0.12; // illustrative war-driven food inflation

  const energyBase = energy / (1 + E_RATE);
  const foodBase = food / (1 + F_RATE);
  const extraEnergy = energy - energyBase;
  const extraFood = food - foodBase;
  const extraMonth = extraEnergy + extraFood;
  const extraYear = extraMonth * 12;

  const fmt = (v) => Math.round(v).toLocaleString("en-US") + "€";
  const out = document.getElementById("cOut");
  out.style.display = "block";
  out.innerHTML =
    "Assumed war-driven inflation: energy <b>+25%</b>, food <b>+12%</b><br><br>" +
    "Extra on energy: <b>" + fmt(extraEnergy) + "/mo</b><br>" +
    "Extra on food: <b>" + fmt(extraFood) + "/mo</b><br>" +
    "Total extra: <b>" + fmt(extraMonth) + "/mo</b> ≈ <b>" + fmt(extraYear) + "/year</b><br><br>" +
    "<span style='color:var(--muted)'>This is an estimate using average rates — your country & tariff differ. Use the tips above to cut it back.</span>";
}
