# AIsle — Product Brief

## Thành viên

- **Phan Trung Kiên** — Core simulation.
- **Lê Bảo Khang** — Genetic Algorithm và NPC population.
- **Trần Đăng Khôi** — Trích xuất đặc trưng từ video thực tế.
- **Phạm Tài Nguyên** — Thiết kế UI/UX.
- **Đặng Hải Đăng** — Thiết kế UI/UX.

## Who

- Manager các chuỗi cửa hàng tiện lợi như Circle K, GS25 và 7-Eleven.
- Chủ cửa hàng và nhóm phân tích hành vi khách hàng.

## Goal

- Tăng doanh thu và tỷ lệ mua hàng.
- Tăng tỷ lệ khách hàng quay lại.
- Thu hút khách hàng mới thông qua trải nghiệm mua sắm tốt hơn.

## Pain point

Người quản lý chưa có cách an toàn và có thể đo lường để biết phương án sắp xếp kệ hàng, hàng hóa, ưu đãi và chính sách nào phù hợp nhất. Thử trực tiếp trong cửa hàng thật tốn thời gian, chi phí và có thể ảnh hưởng doanh thu.

## Giải pháp

AIsle mô phỏng nhiều phương án bố trí và chính sách trước khi triển khai thực tế. Manager có thể quan sát NPC, xem replay, đọc decision trace và so sánh kết quả giữa các lần chạy.

```text
Video khách hàng thật ─┐
                       ├─> Trích xuất đặc trưng và gắn nhãn
Ngữ cảnh cửa hàng ─────┘
                                  │
                                  ▼
                     Sinh quần thể NPC bằng GA
                                  │
                                  ▼
                 Thử sai nhiều layout/chính sách
                                  │
                                  ▼
            Đo lường, replay, so sánh và ra quyết định
```

## Lý thuyết sản phẩm

Peak–End Rule là một trong các lý thuyết nền tảng của nhóm: ký ức về trải nghiệm chịu ảnh hưởng lớn bởi thời điểm cảm xúc mạnh nhất và trạng thái ở cuối hành trình. Simulator vì vậy cần theo dõi không chỉ doanh thu mà cả trajectory cảm xúc, peak valence và end valence.
