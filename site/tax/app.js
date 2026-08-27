function parseMoney(s) {
  if (!s) return 0;
  const n = String(s).replace(/[^0-9]/g, "");
  return n ? parseInt(n, 10) : 0;
}

function calcTaxUI() {
  const gross = parseMoney(document.getElementById("gross").value);
  const dep = parseInt(document.getElementById("dep").value || "0", 10);
  const other = parseMoney(document.getElementById("other").value);

  const personal = 11e6;
  const dependent = 4.4e6;
  const taxable = Math.max(0, gross - personal - dep * dependent - other);

  // progressive brackets (width, rate) on monthly taxable income
  const brackets = [
    [5e6, 0.05], [5e6, 0.10], [8e6, 0.15],
    [14e6, 0.20], [20e6, 0.25], [28e6, 0.30], [Infinity, 0.35],
  ];
  let remain = taxable, tax = 0;
  for (const [amt, rate] of brackets) {
    const portion = Math.min(remain, amt);
    if (portion <= 0) break;
    tax += portion * rate;
    remain -= portion;
    if (remain <= 0) break;
  }

  const fmt = (v) => Math.round(v).toLocaleString("vi-VN") + "₫";
  const out = document.getElementById("taxOut");
  out.style.display = "block";
  out.innerHTML =
    "Thu nhập chịu thuế: <b>" + fmt(taxable) + "</b><br>" +
    "Thuế TNCN phải nộp / tháng: <b>" + fmt(tax) + "</b><br>" +
    "Thực nhận / tháng: <b>" + fmt(gross - tax) + "</b><br>" +
    (tax > 0 ? "<span class='warn'>Nhắc: quyết toán thuế năm vào tháng 3 hàng năm.</span>"
             : "<span style='color:#86efac'>Thu nhập chưa tới mức chịu thuế.</span>");
}

function sumInvUI() {
  const raw = document.getElementById("inv").value.trim();
  if (!raw) return;
  let total = 0, count = 0, lines = [];
  raw.split("\n").forEach((ln) => {
    const parts = ln.split("|");
    const amt = parseMoney(parts[parts.length - 1]);
    if (amt > 0) {
      total += amt;
      count++;
      const name = parts.length > 1 ? parts[0].trim() : "Khoản " + (count);
      lines.push(name + ": " + amt.toLocaleString("vi-VN") + "₫");
    }
  });
  const out = document.getElementById("invOut");
  out.style.display = "block";
  out.innerHTML =
    "Số khoản: <b>" + count + "</b><br>" +
    "Tổng chi tiêu: <b>" + total.toLocaleString("vi-VN") + "₫</b><br>" +
    "<details><summary>Chi tiết</summary>" + lines.join("<br>") + "</details>" +
    (total > 20e6 ? "<br><span class='warn'>Chi tiêu cao – cân nhắc tiết kiệm hoặc mở thẻ tín dụng quản lý dòng tiền.</span>" : "");
}
