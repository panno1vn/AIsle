# AIsle — Store Customer Simulation

## Team

- **Phan Trung Kiên**: Core simulation.
- **Lê Bảo Khang**: Sinh quần thể NPC bằng Genetic Algorithm.
- **Trần Đăng Khôi**: Trích xuất đặc trưng khách hàng từ video thực tế.
- **Phạm Tài Nguyên**: Thiết kế UI/UX.
- **Đặng Hải Đăng**: Thiết kế UI/UX.

## Tổng quan dự án

AIsle là hệ thống mô phỏng hành vi khách hàng trong cửa hàng tiện lợi. Dự án kết hợp dữ liệu quan sát từ video thực tế, ngữ cảnh cửa hàng, quần thể NPC sinh bằng Genetic Algorithm và cơ chế Utility AI lấy cảm hứng từ *The Sims*.

Hệ thống cho phép người quản lý thử nghiệm layout, vị trí kệ hàng, catalog và chính sách ưu đãi trong môi trường mô phỏng trước khi áp dụng vào cửa hàng thật.

## Đối tượng sử dụng

- Manager các chuỗi cửa hàng tiện lợi như Circle K, GS25 và 7-Eleven.
- Chủ cửa hàng muốn kiểm tra phương án bố trí và vận hành trước khi đầu tư triển khai.
- Nhóm phân tích hành vi khách hàng và hiệu quả kinh doanh.

## Bài toán cần giải quyết

Người quản lý thường không có đủ dữ liệu để biết phương án nào mang lại hiệu quả tốt nhất:

- Nên đặt từng nhóm sản phẩm ở kệ nào.
- Lối đi và vị trí checkout ảnh hưởng thế nào đến hành vi khách hàng.
- Ưu đãi hoặc chính sách bán hàng có làm tăng tỷ lệ mua hay không.
- Một thay đổi có thể cải thiện doanh thu nhưng làm giảm trải nghiệm và tỷ lệ quay lại hay không.

Việc thử trực tiếp trong cửa hàng thật tốn thời gian, chi phí và có rủi ro ảnh hưởng doanh thu. AIsle tạo một môi trường thử sai có thể quan sát, replay và so sánh.

## Mục tiêu

- Hỗ trợ tăng doanh thu và tỷ lệ chuyển đổi thành giao dịch.
- Tăng khả năng khách hàng quay lại cửa hàng.
- Thu hút khách hàng mới thông qua trải nghiệm mua sắm tốt hơn.
- Cho phép chạy nhiều kịch bản layout và chính sách với cùng một tập input có kiểm soát.
- Cung cấp bằng chứng từ trajectory, decision trace và kết quả giao dịch thay vì chỉ đưa ra một con số tổng hợp.

## Lý thuyết nền tảng sản phẩm: Peak–End Rule

Nhóm sử dụng **Peak–End Rule** làm một trong những lý thuyết nền tảng để xây dựng AIsle. Trải nghiệm của khách hàng không chỉ phụ thuộc vào giá trị trung bình trong toàn bộ hành trình. Ký ức về một trải nghiệm chịu ảnh hưởng lớn bởi thời điểm cảm xúc mạnh nhất và trạng thái ở cuối hành trình.

![Minh họa Peak–End Rule: ký ức về trải nghiệm chịu ảnh hưởng bởi đỉnh cảm xúc và điểm kết thúc](build/docs/pic.jpg)

Lý thuyết này được chuyển thành định hướng thiết kế sản phẩm như sau:

- Mỗi NPC có trajectory cảm xúc thay đổi trong suốt hành trình mua sắm.
- Tương tác tại shelf, sản phẩm hoặc ưu đãi có thể tạo ra điểm cảm xúc cao nhất hoặc thấp nhất.
- Checkout và thời điểm rời cửa hàng được xem là phần kết thúc của trải nghiệm.
- Một kịch bản không chỉ được đánh giá bằng doanh thu mà còn bằng peak valence, end valence và khả năng quay lại dự kiến.
- Replay và decision trace phải giúp nhóm xác định sự kiện nào tạo ra peak và điều gì dẫn đến trạng thái cuối.

Nhờ đó, AIsle có thể nghiên cứu đồng thời hiệu quả mua hàng và chất lượng trải nghiệm, thay vì chỉ tối đa hóa doanh thu ngắn hạn. Đây là cơ sở để nhóm phát triển tiếp các chỉ số cảm xúc, retention proxy và cơ chế so sánh kịch bản.

## Luồng hoạt động

```text
Video khách hàng thật ─┐
                       ├─> Trích xuất đặc trưng và gắn nhãn
Ngữ cảnh cửa hàng ─────┘
                                  │
                                  ▼
                     Sinh quần thể NPC bằng GA
                                  │
                                  ▼
               Chạy nhiều kịch bản layout/chính sách
                                  │
                                  ▼
             Quan sát, replay, so sánh và ra quyết định
```

Mỗi NPC có nhu cầu, cảm xúc, tốc độ, ý định mua và mức độ khám phá khác nhau. Shelf đóng vai trò smart object, quảng bá sản phẩm và giá trị mà nó có thể cung cấp. NPC tự chọn hành động dựa trên utility, khả năng tiếp cận và trạng thái hiện tại.

## Input

- Video khách hàng thực tế đã được xử lý offline.
- Layout gồm wall, shelf, entrance và checkout.
- Catalog sản phẩm và ánh xạ sản phẩm vào shelf.
- Cấu hình simulation, các hằng số Utility AI và random seed.
- Quần thể NPC sinh bằng GA hoặc danh sách NPC nhập tay để chạy test có kiểm soát.

## Output

- Doanh thu và số lượng giao dịch.
- Tỷ lệ chuyển đổi, main purchase và impulse purchase.
- Decision trace giải thích lựa chọn của từng NPC.
- Trajectory và replay chuyển động/trạng thái NPC.
- Dwell time theo shelf và dữ liệu phục vụ heatmap.
- Event phantom need, unreachable và stuck recovery.
- Lịch sử các lần chạy để so sánh kịch bản.

## Giá trị mang lại

AIsle không thay người quản lý tự động quyết định một layout “tối ưu”. Hệ thống cung cấp một phòng thí nghiệm mô phỏng để người quản lý kiểm tra giả thuyết, quan sát nguyên nhân dẫn đến kết quả và chọn phương án phù hợp với mục tiêu kinh doanh.

## Phạm vi hệ thống

- Xử lý video là pipeline offline, không phân tích camera theo thời gian thực.
- Simulator không tự động thay đổi layout cửa hàng thật.
- Kết quả phụ thuộc vào chất lượng input, giả định hành vi và các hằng số mô phỏng.
- Hệ thống tập trung vào mô phỏng, replay và đo lường; quyết định triển khai cuối cùng thuộc về người quản lý.
