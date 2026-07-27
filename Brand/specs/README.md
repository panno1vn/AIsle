# Bài nộp — Product Design & Frontend (Module 2)

Đáp ứng 3 yêu cầu giảng viên: hoàn thiện Personas, vẽ Information System, vẽ Information Architecture.

## Nội dung

| File | Nội dung |
|---|---|
| `Personas.md` | 2 persona hoàn thiện: Chị Hồng (quản lý cửa hàng độc lập, người dùng chính) và anh Đức (Area Manager, người dùng thứ cấp) |
| `Information_System.svg` | Sơ đồ hệ thống cấp cao: actor (Manager), thành phần (Dashboard, Simulation Engine, NPC Population Generator, Data Store), luồng dữ liệu, và vị trí của "Đối tác Camera/Video" như nguồn dữ liệu ngoài, tuỳ chọn |
| `Information_Architecture.svg` | Cấu trúc 5 màn hình dashboard, dữ liệu dùng chung giữa các màn, đánh dấu màn nào đã có UI chạy được |

## Về bonus UI

Nhóm đã có **UI chạy được thật** cho 2/5 màn hình (đánh dấu ✓ trong sơ đồ IA):
- Màn 1 — Layout Designer (vẽ zone polygon bằng `streamlit-drawable-canvas`)
- Màn 4 — Kết quả & Replay (biểu đồ + replay NPC bằng Plotly animation)

Cả hai đã chạy thử với dữ liệu mẫu và pass unit test. Nếu muốn ăn trọn phần bonus, ưu tiên làm nốt Màn 2 (Catalog Manager) và Màn 3 (Cấu hình & Chạy) trước — cả hai chỉ là form Streamlit thuần, không cần thư viện canvas phức tạp như Màn 1/4, nên làm nhanh hơn nhiều.

## Lưu ý khi nộp

- **Timestamp GitHub (last commit) = thời gian nộp bài chính thức** — commit và push các file này *trước* deadline, đừng để sát giờ mới push vì mạng/CI có thể trễ.
- Gợi ý vị trí đặt trong repo (khớp cấu trúc `README.md` gốc của dự án): `Brand/specs/` — vì đây là tài liệu đặc tả/kiến trúc, không phải code hay pitch deck. Nếu repo hiện tại của nhóm có cấu trúc khác, điều chỉnh đường dẫn cho phù hợp, không bắt buộc đúng y hệt.
- Cả 2 file `.svg` mở trực tiếp được trên GitHub (không cần tải phần mềm gì thêm) — kiểm tra lại 1 lần trên chính trang GitHub sau khi push, vì đôi khi trình duyệt hiển thị khác với xem local.
