(function () {
  var LIMIT = 3;
  try {
    var key = "pw_" + location.pathname;
    var n = parseInt(localStorage.getItem(key) || "0", 10) + 1;
    localStorage.setItem(key, n);
    if (n <= LIMIT) return;
    var el = document.createElement("div");
    el.style.cssText = "position:fixed;inset:0;background:rgba(8,12,25,.93);color:#e2e8f0;display:flex;align-items:center;justify-content:center;z-index:9999;padding:20px;text-align:center";
    el.innerHTML = '<div style="max-width:440px"><h2 style="color:#facc15">Bạn đã dùng hết lượt miễn phí</h2><p>Mỗi công cụ miễn phí 3 lượt / trình duyệt. Trở thành hội viên để dùng không giới hạn + nhận bí kíp độc quyền (thoát nợ, kiếm tiền affiliate).</p><p style="margin-top:14px"><a href="/members/" style="color:#facc15;font-weight:700">Xem gói hội viên &rarr;</a></p></div>';
    document.body.appendChild(el);
  } catch (e) {}
})();
