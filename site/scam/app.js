function checkScamUI() {
  const raw = (document.getElementById("txt").value || "").toLowerCase();
  if (!raw.trim()) {
    alert("Nhập nội dung cần kiểm tra.");
    return;
  }
  const redFlags = [
    "chuyển tiền trước", "chuyển khoản trước", "nộp phạt", "phạt", "trúng thưởng",
    "mã otp", "otp", "mã xác thực", "cơ quan công an", "công an", "viện kiểm sát",
    "nhận thưởng", "hoàn tiền 100%", "lãi suất 0%", "vay không cần giấy tờ",
    "vay không cần thế chấp", "giải ngân 5 phút", "đóng phí trước", "đóng lệ phí trước",
    "khóa tài khoản", "tài khoản bị phong tỏa", "bí mật", "giữ kín", "không cho người thân biết",
  ];
  const yellowFlags = [
    "bit.ly", "t.co", "go.", "tinyurl", "rb.gy", "rebrand", "link rút gọn",
    "cmnd", "cccd", "mật khẩu", "gấp", "urgent", "khuyến mãi", "giảm sâu",
  ];
  let red = 0, yellow = 0;
  const hits = [];
  for (const f of redFlags) {
    if (raw.includes(f)) { red++; hits.push(f); }
  }
  for (const f of yellowFlags) {
    if (raw.includes(f)) { yellow++; }
  }

  const out = document.getElementById("scamOut");
  out.style.display = "block";
  let level, color, advice;
  if (red >= 2) {
    level = "CAO – RẤT CÓ THỂ LÀ LỪA ĐẢO";
    color = "red";
    advice = "Dừng ngay. TUYỆT ĐỐI không chuyển tiền, không cung cấp OTP/CMND. Liên hệ ngân hàng qua số chính thức hoặc báo cơ quan chức năng.";
  } else if (red === 1 || yellow >= 2) {
    level = "TRUNG BÌNH – CẦN CẨN TRỌNG";
    color = "yellow";
    advice = "Xác minh kỹ: gọi số chính thức của bên liên quan, đừng bấm link lạ, đừng chuyển tiền trước.";
  } else {
    level = "THẤP – ít dấu hiệu";
    color = "green";
    advice = "Vẫn giữ thói quen: không chia sẻ OTP, không chuyển tiền trước khi xác nhận.";
  }
  out.innerHTML =
    "Mức độ rủi ro: <b class='" + color + "'>" + level + "</b><br>" +
    "Số dấu hiệu đỏ phát hiện: <b>" + red + "</b>, dấu hiệu vàng: <b>" + yellow + "</b><br>" +
    (hits.length ? "Khớp: " + hits.join(", ") + "<br>" : "") +
    "<br><span class='" + color + "'>" + advice + "</span><br>" +
    "<span style='color:var(--muted)'>Tool heuristic, không thay thế tra cứu chính thức. Không lưu dữ liệu của bạn.</span>";
}
