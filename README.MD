## Team: BlackBox AI

- **Phan Trung Kiên** — Core simulation.
- **Lê Bảo Khang** — Genetic Algorithm và NPC population.
- **Trần Đăng Khôi** — Trích xuất đặc trưng từ video thực tế.
- **Phạm Tài Nguyên** — UI/UX.
- **Đặng Hải Đăng** — UI/UX.

# AIsle — Store Customer Simulation

AIsle là hệ thống mô phỏng hành vi khách hàng trong cửa hàng tiện lợi. Dự án kết hợp dữ liệu quan sát từ video thực tế, ngữ cảnh cửa hàng, quần thể NPC sinh bằng Genetic Algorithm và Utility AI lấy cảm hứng từ *The Sims*.

Manager có thể thử nghiệm layout, vị trí kệ hàng, catalog và chính sách bán hàng trong môi trường mô phỏng trước khi áp dụng vào cửa hàng thật. Hệ thống tập trung vào khả năng quan sát, replay và giải thích nguyên nhân dẫn đến kết quả; không tự động tuyên bố một layout là “tối ưu”.

## Lý thuyết nền tảng sản phẩm

Nhóm sử dụng **Peak–End Rule** làm một trong những lý thuyết nền tảng để thiết kế AIsle. Ký ức của khách hàng về một trải nghiệm chịu ảnh hưởng lớn bởi thời điểm cảm xúc mạnh nhất và trạng thái ở cuối hành trình.

![Peak–End Rule — lý thuyết nền tảng cho mô hình trải nghiệm khách hàng của AIsle](build/docs/pic.jpg)

Trong simulator:

- Mỗi NPC có trajectory cảm xúc trong suốt hành trình mua sắm.
- Tương tác tại shelf, sản phẩm hoặc ưu đãi có thể tạo peak valence.
- Checkout và thời điểm rời cửa hàng tạo thành trạng thái kết thúc.
- Replay và decision trace giúp xác định sự kiện tạo peak và nguyên nhân dẫn tới end state.
- Kịch bản có thể được nghiên cứu đồng thời theo doanh thu, trải nghiệm và retention proxy.

## Đối tượng sử dụng

- Manager các chuỗi cửa hàng tiện lợi như Circle K, GS25 và 7-Eleven.
- Chủ cửa hàng muốn kiểm tra phương án bố trí trước khi đầu tư triển khai.
- Nhóm phân tích hành vi khách hàng và hiệu quả kinh doanh.

### Chân dung người dùng chính

Người dùng trọng tâm của AIsle là quản lý hoặc chủ cửa hàng chịu trách nhiệm về layout, danh mục hàng hóa, ưu đãi và hiệu quả kinh doanh. Họ cần thử nhiều phương án với chi phí thấp, đồng thời phải nhìn thấy đường đi và quyết định của NPC để hiểu vì sao một kịch bản tạo ra kết quả cụ thể.

Các nhu cầu chính gồm:

- So sánh layout và chính sách trước khi áp dụng tại cửa hàng thật.
- Quan sát live simulation, replay, heatmap và decision trace thay vì chỉ nhận KPI cuối.
- Nhập thủ công hằng số, chỉ số và NPC cho các ca kiểm thử có kiểm soát.
- Đánh giá doanh thu cùng trải nghiệm khách hàng và khả năng quay lại.

Xem tài liệu [chân dung người dùng và kịch bản sử dụng](build/docs/personal.md) để biết đầy đủ mục tiêu, pain points, job-to-be-done và tiêu chí thành công của sản phẩm.

## Bài toán

Việc thử trực tiếp một layout hoặc chính sách mới trong cửa hàng thật tốn thời gian, chi phí và có thể ảnh hưởng doanh thu. AIsle cung cấp một phòng thí nghiệm mô phỏng để trả lời các câu hỏi:

- Nên đặt từng nhóm sản phẩm ở đâu?
- Wall, lối đi, entrance và checkout ảnh hưởng thế nào đến luồng khách?
- Ưu đãi có làm tăng tỷ lệ mua hoặc impulse purchase không?
- Một phương án tăng doanh thu có làm giảm trải nghiệm cuối hành trình không?
- NPC chọn shelf vì nhu cầu, cảm xúc hay chi phí di chuyển?

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
              Utility AI + A* + hard collision rules
                                  │
                                  ▼
               Chạy nhiều layout/chính sách thử nghiệm
                                  │
                                  ▼
          Live view, replay, history và decision trace
```

Shelf là smart object quảng bá category, sản phẩm và valence. NPC chấm utility theo attenuated need-delta, mức khám phá, cảm xúc và chi phí đường đi bậc hai. Lựa chọn trong top-K sử dụng weighted random có seed, giúp hành vi có biến thiên nhưng vẫn replay được.

## Tính năng chính

- Canvas editor cho wall, shelf, entrance và checkout.
- Wall có thể di chuyển, thay đổi đầu mút hoặc nhập tọa độ trực tiếp.
- Sinh 150–200 NPC bằng GA hoặc nhập NPC thủ công bằng CSV.
- Poisson spawn theo đường cong lưu lượng có seed.
- Utility AI, cảm xúc, main purchase và impulse purchase.
- A* pathfinding không xuyên wall/shelf, có stuck recovery và abandon target.
- Event `phantom-need`, `unreachable`, `replan` và decision trace.
- Run, Pause, Reset, Single Step, timeline và nhiều tốc độ chạy.
- Live KPI: doanh thu, conversion, purchases và nhu cầu ngoài catalog.
- Export chuẩn `aisle.sim-result.v1`.
- Trajectory replay đầy đủ cho từng NPC.
- History API để lưu, liệt kê và đọc lại simulation run.

## Chạy ứng dụng

### Yêu cầu

- Windows.
- Node.js 22 trở lên.
- Không cần cài npm package.

### Khởi động

Nhấp đúp:

```text
build\run.bat
```

Launcher sẽ khởi động backend tại `http://127.0.0.1:8765` và mở web bằng trình duyệt mặc định.

## Cấu trúc chính

```text
build/
├── run.bat
├── backend/
│   ├── server.mjs
│   ├── routes/api-router.mjs
│   └── storage/project-store.mjs
├── web/
│   ├── index.html
│   ├── app.js
│   ├── live-engine.js
│   ├── layout-validation.js
│   └── sim-result.js
├── runtime/
├── tests/
└── docs/
```

- `web/live-engine.js`: simulation core độc lập với DOM.
- `web/app.js`: editor, Canvas renderer và live controls.
- `web/sim-result.js`: schema dùng chung cho export/history.
- `backend/routes`: quy tắc HTTP API.
- `backend/storage`: lưu project và history.
- `runtime`: layout, catalog và dữ liệu sinh ra khi chạy.

## Input và output

### Input

- Video khách hàng đã được xử lý offline.
- Layout gồm wall, shelf, entrance và checkout.
- Catalog và ánh xạ sản phẩm vào shelf.
- Random seed và các hằng số simulation.
- Quần thể NPC từ GA hoặc dữ liệu nhập tay.

### Output

- Doanh thu, conversion và số giao dịch.
- Main purchase và impulse purchase.
- Dwell time theo shelf.
- Decision trace và utility breakdown.
- Trajectory cảm xúc/chuyển động để replay.
- Lịch sử các lần chạy để so sánh kịch bản.

## API chính

- `GET /health`
- `GET /api/project`
- `POST /api/project`
- `GET /api/history`
- `POST /api/history`
- `GET /api/history/:id`

## Kiểm thử

Từ thư mục `build`:

```powershell
node tests/live_engine.test.mjs
node tests/pathfinding_rules.test.mjs
node tests/emotion_need_dynamics.test.mjs
node tests/utility_attenuation.test.mjs
node tests/weighted_random_choice.test.mjs
node tests/phantom_need.test.mjs
node tests/spawn_curve.test.mjs
node tests/layout_validation.test.mjs
node tests/population_generation.test.mjs
node tests/sim_result_history.test.mjs
node tests/benchmark.mjs
```

Benchmark hiện tại với 200 NPC × 3.600 ticks, bao gồm trajectory capture, thấp hơn một giây trên máy phát triển.

## Phạm vi và giới hạn

- Video được xử lý offline, không phân tích camera theo thời gian thực.
- Các kết quả phụ thuộc vào chất lượng input và giả định hành vi.
- Một số hằng số hiện là design constants, chưa phải số đo được hiệu chỉnh từ cửa hàng thật.
- Simulator không tự thay đổi cửa hàng thật và không thay manager ra quyết định cuối cùng.

## Tài liệu

- [Project overview](Project.md)
- [Product brief](build/docs/plan.md)
- [Chân dung người dùng](build/docs/personal.md)
- [Kiến trúc simulator](build/docs/ARCHITECTURE.md)
- [Kế hoạch triển khai](build/docs/PLAN_CODEX.md)
- [Hướng dẫn riêng cho build](build/README.md)
