function parseMoney(s) {
  if (!s) return 0;
  const n = String(s).replace(/[^0-9]/g, "");
  return n ? parseInt(n, 10) : 0;
}

function calcLoanUI() {
  const amt = parseMoney(document.getElementById("amt").value);
  const rate = parseFloat((document.getElementById("rate").value || "0").replace(",", "."));
  const months = parseInt(document.getElementById("months").value || "0", 10);

  if (amt <= 0 || !(rate >= 0) || months <= 0) {
    alert("Nhập số tiền, lãi %/tháng và kỳ hạn hợp lệ.");
    return;
  }
  const interest = amt * (rate / 100) * months;
  const total = amt + interest;
  const monthlyPay = total / months;
  const yearly = rate * 12;
  const blackInterest = amt * 0.10 * months;

  const fmt = (v) => Math.round(v).toLocaleString("vi-VN") + "₫";
  const out = document.getElementById("loanOut");
  out.style.display = "block";
  let warn = "";
  if (rate >= 3) {
    warn = "<br><span class='red'>⚠ Lãi " + rate + "%/tháng (~" + (rate * 12).toFixed(0) + "%/năm) – có dấu hiệu tín dụng đen. Cân nhắc kênh hợp pháp bên dưới.</span>";
  } else {
    warn = "<br><span class='green'>Lãi ở mức hợp lý (&lt;3%/tháng).</span>";
  }
  out.innerHTML =
    "Tổng lãi phải trả: <b>" + fmt(interest) + "</b><br>" +
    "Tổng gốc + lãi: <b>" + fmt(total) + "</b><br>" +
    "Trả mỗi tháng (" + months + " tháng): <b>" + fmt(monthlyPay) + "</b><br>" +
    "Lãi suất năm quy đổi: <b>" + yearly.toFixed(1) + "%</b><br>" +
    "So sánh nếu vay tín dụng đen 10%/tháng: lãi <b>" + fmt(blackInterest) + "</b> (" + (blackInterest / Math.max(interest, 1)).toFixed(1) + " lần)<br>" +
    warn;
}
