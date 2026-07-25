# AIsle — Digital Twin cho Cửa hàng Tiện lợi

> Mô phỏng cửa hàng tiện lợi bằng AI agent (khách hàng + nhân viên) để thử layout và thái độ phục vụ tối ưu doanh thu trước khi áp dụng ngoài đời thật.

---

## 👥 Thành viên nhóm

| Tên · Email · Student ID · Vai trò |
|---|
| Phan Trung Kiên · n23dcat038@student.ptithcm.edu.vn · N23DCAT038 · Team Lead |
| Đàng Hải Đăng · n24dece007@student.ptithcm.edu.vn · N24DECE007 · AI / Simulation |
| Trần Đăng Khôi · n23dcat036@student.ptithcm.edu.vn · N23DCAT036 · UI/UX & Backend / WebApp |

> Bảng này đã được điền theo thông tin bạn gửi. Nếu muốn đổi lại cách chia vai trò cho sát thực tế hơn, mình có thể chỉnh tiếp trong lần sau.

---

## 🧭 Tổng quan project

AIsle dựng một **môi trường ảo mô phỏng cửa hàng tiện lợi**, trong đó AI đóng vai:

- **Khách hàng** — persona đa dạng (ngân sách, mục đích ghé mua, tính cách), ra quyết định di chuyển và mua hàng trong cửa hàng ảo.
- **Nhân viên** — các chiến lược thái độ phục vụ khác nhau, ảnh hưởng đến quyết định mua của khách.

Mục tiêu là chạy hàng loạt mô phỏng với nhiều **layout gian hàng** và **kiểu phục vụ** khác nhau, rồi so sánh doanh thu / tỷ lệ chuyển đổi để tìm ra cấu hình tối ưu trước khi thử ngoài đời thật.

📄 Bản trình bày sponsor nằm ở [Brand/pitch/index.html](Brand/pitch/index.html).

---

## 🗂️ Cấu trúc repo

```
AIsle/
├── Learn/
│   ├── AI-Basic/
│   ├── UI-UX/
│   ├── Backend/
│   └── Data/
│
├── Brand/
│   ├── identity/
│   ├── pitch/
│   └── specs/
│
└── WebApp/
    ├── frontend/
    ├── backend/
    └── docs/
```

### Learn/
Chia theo 4 mảng thật của project: AI-Basic cho prompt/agent, UI-UX cho dashboard, Backend cho simulation engine, và Data cho metrics / kết quả mô phỏng.

### Brand/
Tách thành `identity/` cho logo / màu / brand guideline, `pitch/` cho bản trình bày sponsor, và `specs/` cho đặc tả kỹ thuật.

### WebApp/
Build xuyên suốt trong `frontend/`, `backend/`, `docs/` thay vì tách riêng theo tuần.

---

## 📅 Nhật ký commit theo tuần

> Commit đều mỗi tuần. Repo là bằng chứng tiến độ, không phải nơi để dồn việc cuối kỳ.

| Tuần | Mốc cần đạt | Trạng thái |
|---|---|---|
| 1 | Dựng store layout (grid) + agent khách hàng đơn giản | ⬜ |
| 2 | Cơ chế mô phỏng hàng loạt + tham số layout / thái độ | ⬜ |
| 3 | So sánh nhiều layout + dashboard trực quan | ⬜ |
| 4 | Hoàn thiện demo + tài liệu pitch cho sponsor | ⬜ |

Cập nhật cột **Trạng thái** theo tuần: ⬜ chưa làm, 🟨 đang làm, ✅ xong.

---

## 🚀 Bắt đầu

```bash
git clone <repo-url>
cd AIsle
```

Sau đó bắt đầu lần lượt từ `WebApp/backend/` và `WebApp/frontend/`, còn `Brand/pitch/` dùng để giữ nội dung trình bày cho sponsor.

---

## 📌 Ghi chú

- Mỗi thành viên nên có ít nhất 1 commit / tuần trong `Learn/` thuộc mảng của mình.
- `Brand/pitch/` cần đi cùng tiến độ thật của `WebApp/`.
- Kết quả trong `Data/` phải ghi rõ là dữ liệu mô phỏng, chưa phải dữ liệu thực tế.