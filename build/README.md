# AIsle Live Simulation Studio — App + Web

Runtime chính đã chuyển sang JavaScript live simulation engine + Canvas 2D. Desktop mở bằng Microsoft Edge App Mode; web chạy cùng UI và cùng engine. Python/Tkinter được giữ lại dưới dạng legacy prototype, không còn là luồng chạy mặc định.

## Chạy desktop app

Yêu cầu Node.js 22+ và Microsoft Edge. Không cần cài npm package.

```powershell
cd build
.\run.ps1
```

Hoặc nhấp đúp `run.bat`.

`run.ps1` khởi động Node server nền rồi mở cửa sổ desktop không có browser chrome bằng Edge App Mode.

## Chạy bản web

Bản web dùng đúng `web/live-engine.js` của desktop app, không có simulation engine thứ hai:

```powershell
cd build
.\run_web.ps1
```

Hoặc nhấp đúp `run_web.bat`, sau đó mở `http://127.0.0.1:8765`.

## Phạm vi đã triển khai

- Layout Designer native canvas với 4 công cụ: tường, kệ, lối vào, quầy thu ngân; snap lưới 0,25 m, số đo và kéo-thả.
- Catalog dạng bảng, form thêm/sửa/xóa, import CSV, ánh xạ sản phẩm vào kệ.
- Sinh 150–200 NPC bằng crossover + bounded mutation từ 6 seed genome.
- Chế độ Manual NPC Input: nhập/dán CSV cho từng NPC gồm need, emotion, movement và target category; phù hợp chạy test có kiểm soát.
- Phân bổ `target_category`: 80% catalog, 10% thừa hưởng, 6% nhu cầu ma, 4% không có ý định mua.
- Spawn theo đường cong λ(t), utility chọn kệ, A* grid có làm mượt đường, biến đổi cảm xúc, mua chính và impulse cross-sell.
- Replay có tua/phát/tốc độ, heatmap dwell time, doanh thu tích lũy, phân bố nguồn nhu cầu.
- Tự lưu layout/catalog bằng JSON; purchase log và lịch sử bằng SQLite; so sánh 2 lần chạy; không chấm điểm hoặc đề xuất layout.
- Desktop và web cùng đọc/ghi `build/runtime` và cùng chạy `web/live-engine.js`.
- Một lần bấm `Run live` vừa bắt đầu physics tick vừa render NPC; không còn bước “tính xong rồi mới replay”.
- `Step`, `Pause`, `Reset`, deterministic seek và trail giúp kiểm tra quá trình dẫn tới kết quả.
- Chọn NPC để xem need, emotion, action state và utility breakdown.
- Parameter Lab cho nhập tay toàn bộ hệ số utility, purchase sigmoid, impulse, spawn, tick, pathfinding và collision.

## Ranh giới

Pipeline YOLOv8 → Homography → DeepFace là phần offline theo tài liệu và không nằm trong runtime simulator. Trajectory compact được lưu thành JSON trong `build/runtime`; SQLite lưu purchase log và lịch sử. Đây là lựa chọn để app chạy ngay bằng Python chuẩn, không cần PyArrow.

Python desktop cũ vẫn có thể chạy bằng `python desktop_app.py` để đối chiếu, nhưng không phải implementation chính.

## Kiểm thử

```powershell
python -m unittest discover -s tests -p "test_*.py"
node tests/live_engine.test.mjs
```
