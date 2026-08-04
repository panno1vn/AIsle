# Chân dung người dùng AIsle

## Người dùng chính

**Quản lý hoặc chủ cửa hàng tiện lợi** tại các chuỗi như Circle K, GS25, 7-Eleven hoặc cửa hàng bán lẻ có mô hình tương tự.

Họ chịu trách nhiệm về bố trí không gian, danh mục hàng hóa, chương trình ưu đãi và hiệu quả kinh doanh, nhưng thường không có công cụ an toàn để kiểm tra một phương án mới trước khi triển khai tại cửa hàng thật.

## Mục tiêu

- Tăng doanh thu và tỷ lệ khách thực hiện mua hàng.
- Cải thiện tỷ lệ khách quay lại và thu hút khách hàng mới.
- Tìm vị trí phù hợp cho từng nhóm sản phẩm, quầy thanh toán và lối đi.
- Đánh giá tác động của ưu đãi, catalog và chính sách bán hàng.
- So sánh nhiều kịch bản với chi phí và rủi ro thấp hơn thử nghiệm trực tiếp.

## Pain points

- Không biết cách bố trí kệ hàng nào phù hợp với hành vi di chuyển thực tế của khách.
- Khó xác định một thay đổi doanh thu đến từ layout, sản phẩm, ưu đãi hay ngẫu nhiên.
- Thử nghiệm tại cửa hàng thật tốn thời gian, chi phí và có thể làm gián đoạn hoạt động.
- Báo cáo kết quả đơn thuần không cho biết NPC đã di chuyển và ra quyết định như thế nào.
- Một phương án tăng doanh thu có thể đồng thời làm giảm trải nghiệm hoặc ý định quay lại.

## Job to be done

> Khi cần thay đổi layout hoặc chính sách bán hàng, người quản lý muốn thử nghiệm trên một quần thể khách hàng mô phỏng có hành vi giải thích được, để có thể so sánh các phương án trước khi đầu tư triển khai thực tế.

## Kịch bản sử dụng chính

1. Nhập layout, catalog, các hằng số mô phỏng và dữ liệu hành vi đã trích xuất từ video thực tế.
2. Dùng Genetic Algorithm để sinh quần thể NPC hoặc tự nhập NPC cho một ca kiểm thử cụ thể.
3. Chạy mô phỏng và quan sát trực tiếp đường đi, tương tác với shelf, trạng thái cảm xúc và quyết định mua hàng.
4. Xem replay, heatmap, KPI và decision trace để kiểm tra nguyên nhân dẫn đến kết quả.
5. Thay đổi layout hoặc chính sách, chạy lại với seed kiểm soát và so sánh các kịch bản.
6. Chọn phương án phù hợp để thử nghiệm có kiểm soát tại cửa hàng thật.

```text
Video thực tế ─┐
               ├─> Trích xuất đặc trưng ─> Sinh/gắn nhãn NPC ─┐
Ngữ cảnh ──────┘                                               │
                                                               ▼
Layout + chính sách ────────────────────────────────> Mô phỏng thử–sai
                                                               │
                                                               ▼
                                              Replay + giải thích + KPI
                                                               │
                                                               ▼
                                             So sánh và chọn phương án
```

## Tiêu chí thành công

- Người dùng nhìn thấy toàn bộ quá trình tạo ra KPI, không chỉ kết quả cuối.
- NPC không đi xuyên vật cản và có cách xử lý khi mục tiêu không thể tiếp cận.
- Cùng input và random seed phải tái hiện được cùng một lần chạy.
- Các hằng số, chỉ số và NPC kiểm thử có thể nhập hoặc điều chỉnh thủ công.
- Kết quả giữa các kịch bản có thể lưu, replay, xuất và so sánh.
- Hệ thống phân biệt dữ liệu quan sát, giả định mô hình và kết quả mô phỏng.

## Nhu cầu sản phẩm suy ra từ persona

- Trình chỉnh sửa trực quan cho wall, shelf, entrance và checkout.
- Live simulation với Run, Pause, Step, Reset, timeline và điều chỉnh tốc độ.
- Manual NPC input bên cạnh quần thể sinh bằng Genetic Algorithm.
- Pathfinding, collision rules, stuck recovery và abandon target.
- Replay trajectory, heatmap, decision trace và history cho từng lần chạy.
- Tham số có mô tả, đơn vị, miền giá trị và giá trị mặc định rõ ràng.
- Export dữ liệu chuẩn để kiểm tra hoặc phân tích độc lập.

## Giới hạn và nguyên tắc sử dụng

- AIsle là công cụ kiểm tra giả thuyết, không tự tuyên bố một phương án là “tối ưu”.
- Kết quả phụ thuộc vào chất lượng dữ liệu đầu vào và các giả định hành vi.
- Mô phỏng không thay thế thử nghiệm có kiểm soát tại cửa hàng thật.
- Doanh thu cần được đánh giá cùng trải nghiệm khách hàng và retention proxy.
