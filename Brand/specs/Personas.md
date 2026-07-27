# Personas — AIsle

> **Lưu ý quan trọng:** đây là persona của **người dùng sản phẩm AIsle** (theo đúng phương pháp Product Design), tức là ai sẽ mở dashboard lên và thao tác — **khác** với "archetype khách hàng ảo" (Khách vội, Khách dạo...) đã định nghĩa trong tài liệu đặc tả kỹ thuật (`ke-hoach-poc-mo-phong-khach-hang.md`, mục 2.5). Archetype đó mô tả NPC *bên trong* mô phỏng; personas dưới đây mô tả người *sử dụng* công cụ.

---

## Persona 1 — Người dùng chính (Primary)

### Chị Hồng — Quản lý cửa hàng tiện lợi độc lập

| | |
|---|---|
| **Tuổi** | 34 |
| **Vai trò** | Quản lý 1 cửa hàng tiện lợi (không thuộc chuỗi lớn) |
| **Kinh nghiệm** | 6 năm nhân viên bán lẻ → 3 năm quản lý |
| **Mức độ rành công nghệ** | Trung bình — dùng thành thạo điện thoại, Excel cơ bản, ngại phần mềm nhiều bước |
| **Thiết bị chính** | Laptop cá nhân ở văn phòng sau cửa hàng, thỉnh thoảng dùng điện thoại |

**Câu nói đại diện:**
> "Tôi không cần AI làm hộ tôi quyết định — tôi chỉ cần biết trước, nếu đổi thế này, có tệ hơn không."

**Bối cảnh:** Chị Hồng chịu trách nhiệm toàn bộ vận hành cửa hàng: đặt hàng, xếp lịch nhân viên, và cả cách bày biện kệ hàng. Chị có trực giác tốt sau nhiều năm quan sát khách, nhưng mỗi lần muốn thử cách bày mới, chị phải tự bỏ tiền túi thời gian dời kệ, rồi chờ vài tuần mới biết đúng hay sai — mà không có cách nào so sánh khách quan với cách cũ.

**Mục tiêu (Goals):**
- Tăng doanh thu mà không phải đánh cược bằng tiền và công sức thật
- Có con số cụ thể để tự tin hơn khi thử cách bày hàng mới
- Nếu cần xin ngân sách cải tạo từ chủ, có căn cứ để thuyết phục

**Nỗi đau (Pain points):**
- Không có ngân sách thuê tư vấn thiết kế cửa hàng
- Đổi layout thật tốn công, khó thử nhiều phương án cùng lúc
- Không biết "thái độ phục vụ" của nhân viên ảnh hưởng doanh thu bao nhiêu — chỉ cảm tính
- Sợ phần mềm phức tạp, từng bỏ dở một app quản lý kho vì giao diện rối

**AIsle giúp gì:**
- Thử layout trên máy trước, không tốn công dời kệ thật
- Giao diện thao tác bằng cách vẽ/click, không cần biết lập trình
- Xem trực tiếp số liệu và replay để tự đánh giá — công cụ không áp đặt kết luận, chị vẫn là người quyết định cuối cùng

**Một ngày dùng AIsle (kịch bản):** Chị Hồng mở dashboard, vẽ lại cách bày kệ nước ngọt gần quầy thu ngân (ý tưởng chị đã nghĩ từ lâu nhưng chưa dám thử thật). Nhập catalog 15 sản phẩm chính. Bấm chạy mô phỏng, xem replay khách hàng ảo di chuyển, thấy doanh thu mô phỏng tăng nhẹ so với cách bày hiện tại. Chị lưu lại kết quả này để so sánh thêm với 1-2 phương án khác trước khi quyết định dời kệ thật.

---

## Persona 2 — Người dùng thứ cấp / Stakeholder (Secondary)

### Anh Đức — Area Manager, chuỗi 6 cửa hàng tiện lợi

| | |
|---|---|
| **Tuổi** | 41 |
| **Vai trò** | Quản lý vùng, phụ trách 6 cửa hàng trong một chuỗi nhỏ |
| **Kinh nghiệm** | 10 năm trong ngành bán lẻ, từng làm quản lý cửa hàng trước khi lên vùng |
| **Mức độ rành công nghệ** | Khá — quen thuộc với dashboard báo cáo, Google Sheets, họp online |
| **Thiết bị chính** | Laptop công ty, di chuyển thường xuyên giữa các cửa hàng |

**Câu nói đại diện:**
> "Tôi cần thấy con số trước khi duyệt ngân sách cải tạo cho cả 6 cửa hàng, chứ không thể chỉ nghe một quản lý nói 'chắc sẽ ổn hơn'."

**Bối cảnh:** Anh Đức quản lý 6 cửa hàng, mỗi quản lý cửa hàng lại có cách bày biện khác nhau dựa trên cảm tính riêng. Anh muốn chuẩn hoá cách bày hàng cho toàn chuỗi nhưng không có cách nào so sánh khách quan giữa các đề xuất trước khi đầu tư cải tạo hàng loạt.

**Mục tiêu (Goals):**
- So sánh nhiều phương án layout một cách khách quan trước khi duyệt ngân sách
- Tìm ra công thức layout chung có thể áp dụng cho nhiều chi nhánh
- Giảm rủi ro khi quyết định đầu tư cải tạo cho nhiều cửa hàng cùng lúc

**Nỗi đau (Pain points):**
- Mỗi quản lý cửa hàng đề xuất một kiểu, không có cách xếp hạng khách quan
- Thử nghiệm thật ở nhiều chi nhánh cùng lúc quá tốn kém
- Báo cáo hiện tại từ các cửa hàng thiếu tính nhất quán để so sánh

**AIsle giúp gì:**
- Màn Lịch sử cho phép lưu và so sánh nhiều lần chạy cạnh nhau bằng số liệu
- Có thể mô phỏng layout đề xuất từ nhiều quản lý khác nhau trên cùng một chuẩn đánh giá
- Không đưa ra xếp hạng "tốt/xấu" tự động — anh Đức vẫn giữ vai trò người ra quyết định cuối cùng, đúng với vị trí quản lý của mình

---

## Ghi chú cho việc dùng Personas này khi thiết kế UI

- Vì cả hai persona đều **không rành kỹ thuật sâu**, dashboard cần ưu tiên: thao tác bằng click/vẽ, không yêu cầu hiểu code hoặc JSON; số liệu hiển thị trực quan (biểu đồ, replay) hơn là bảng số thô.
- Cả hai đều **không muốn hệ thống "quyết định thay"** — đây là lý do nguyên tắc "công cụ đánh giá, không phải công cụ tối ưu tự động" (đã chốt trong đặc tả kỹ thuật, mục 0.1) khớp đúng với insight từ personas, không phải một giới hạn kỹ thuật đơn thuần.
- Chị Hồng là đối tượng chính cho toàn bộ 5 màn hình; anh Đức là lý do màn **Lịch sử & So sánh** (Màn 5) quan trọng, dù nó không phải màn hình được ưu tiên nhất về mặt kỹ thuật.
