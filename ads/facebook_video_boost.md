# Chạy Facebook Ads 100k cho video affiliate (All-in Facebook)

Mục tiêu: dùng 100k mua traffic đủ để chốt **1 đơn hoa hồng cao** (FPT Software: 1.400.000–1.750.000₫/người vào làm → 1 đơn đã vượt 1M).

## 1. Chọn offer & video
- **Khuyên dùng: FPT SOFTWARE EMBEDDED** (tuyển dụng IT) — Facebook dễ duyệt, hoa hồng 1.75M.
  - Video: `videos/FPT_SOFTWARE_EMBEDDED.mp4`
  - Link đích: **https://shorten.asia/JhMmRqbU**
- ⚠️ Tima (vay ô tô, 2.3M) hoa hồng cao nhất nhưng sản phẩm **vay/tín dụng** thường bị FB hạn chế (cần xác minh tài chính). Chỉ dùng `videos/Tima.mp4` nếu tài khoản BM của bạn đã được phê duyệt mảng này.

## 2. Tạo chiến dịch (Facebook Ads Manager / BM)
1. Mục tiêu: **Lưu lượng truy cập (Traffic)** hoặc **Tương tác (Engagement)**.
2. Định dạng: Video (tải `FPT_SOFTWARE_EMBEDDED.mp4`).
3. Đường link đích (Website): dán `https://shorten.asia/JhMmRqbU` (link đăng ký có mã affiliate của bạn).
4. Trình chiếu: để link hiển thị rõ trong mô tả + comment mở khóa link.

## 3. Targeting (đưa chuẩn để không phí click)
- Vị trí: chỉ Facebook Feed (tắt Audience Network/Instagram để tiết kiệm).
- Độ tuổi: **22–40**.
- Vị trí: Việt Nam.
- Sở thích / hành vi: `việc làm`, `tuyển dụng`, `career`, `FPT`, `lập trình`, `IT`, `thực tập`, `sinh viên CNTT`.
- Loại trừ: từ khóa không liên quan (game, crypto…).
- Không dùng tệp quá rộng (dễ đốt tiền vô ích).

## 4. Ngân sách (All-in 100k)
- Đặt **50.000₫/ngày × 2 ngày = 100.000₫** (tổng chiến dịch 100k).
- Giá thầu: chọn **CPC** (trả theo click), để tự động tối ưu trong 50k/ngày.
- Cách an toàn hơn (nếu muốn học trước): chạy thử **30k/2 ngày**, xem video nào/creative nào ra click rẻ nhất, rồi dồn 70k vào biến thể thắng.

## 5. Lưu ý chính sách (quan trọng)
- **Không** hứa thu nhập, không "cam kết", "kiếm tiền triệu", "đảm bảo" → FB sẽ từ chối/ khóa.
- Nội dung video hiện tại chỉ nêu factual ("nhận hoa hồng đến X₫", "miễn phí tham gia") → hợp lệ.
- Tracking: xem đơn thực tế tại Accesstrade dashboard → mục **Transactions**.

## 6. Dòng tiền
- Hoa hồng Accesstrade thanh toán ngày **18 hàng tháng** (sau khi đơn được duyệt).
- Nếu 100k ra 0 đơn: coi như chi phí học; quay lại làm organic (video + SEO web) miễn phí để tăng cơ hội lần sau.

## 7. Sinh thêm video
- Lệnh: `python at_api.py videos --top 3` (top 3 theo hoa hồng) hoặc `--id <campaign_id>` cho 1 campaign.
- Lưu ý: giọng đọc dùng edge-tts (Microsoft), thỉnh thoại mạng kẹt vài chục giây — script đã có timeout/retry.
