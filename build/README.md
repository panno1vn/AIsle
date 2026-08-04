# AIsle Store Simulator

Ứng dụng mô phỏng cửa hàng chạy bằng JavaScript live engine và Canvas 2D. Không cần cài npm package.

## Chạy web

Yêu cầu Node.js 22+. Nhấp đúp duy nhất:

```text
run.bat
```

Launcher khởi động backend ở `http://127.0.0.1:8765` và mở trình duyệt mặc định. Nếu backend đã chạy, launcher chỉ mở lại trang web.

## Bố cục thư mục

```text
build/
├── run.bat                    # launcher duy nhất
├── backend/
│   ├── server.mjs             # HTTP host và static pages
│   ├── routes/api-router.mjs  # quy tắc endpoint API
│   └── storage/project-store.mjs
├── web/
│   ├── index.html             # page hiện tại; có thể thêm page mới tại đây
│   ├── app.js                 # editor và Canvas UI
│   ├── live-engine.js         # simulation core, không phụ thuộc DOM
│   ├── project-defaults.js
│   ├── styles.css
│   └── overrides.css
├── runtime/                   # layout/catalog và output khi chạy
├── tests/                     # Node tests
└── docs/ARCHITECTURE.md
```

Backend tách router khỏi storage. Khi thêm page, đặt HTML/JS/CSS trong `web`; khi thêm API, khai báo route trong `backend/routes/api-router.mjs` và nghiệp vụ lưu trữ trong `backend/storage`.

## Quy tắc NPC

- Shelf quảng bá category, valence và sản phẩm; NPC chấm utility theo nhu cầu, khám phá, cảm xúc và chi phí đường đi.
- Chỉ shelf có access point mà A* thực sự đi tới được mới được đưa vào quyết định.
- Wall và shelf là hard obstacle. Không có fallback đường thẳng xuyên vật cản.
- Mỗi bước di chuyển và crowd separation đều kiểm tra segment walkable.
- NPC bị kẹt sẽ tìm đường lại; quá số lần cho phép thì bỏ shelf và quay về entrance.
- Nếu mọi shelf đều không tới được, NPC ghi event `unreachable` và rời cửa hàng.

Các hằng số `stuckTimeout`, `maxReplans`, kích thước grid, obstacle margin và utility có thể chỉnh trong Parameter Lab.

## Test

```powershell
node tests/live_engine.test.mjs
node tests/pathfinding_rules.test.mjs
```
