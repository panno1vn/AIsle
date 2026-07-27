# AIsle v2 — Kiến trúc Oxyte

Khung xương thật cho Tuần 1, theo `ke-hoach-poc-mo-phong-khach-hang.md` +
`AIsle_ke_hoach_thuc_thi.md`. Đã thay hoàn toàn bản AIsle rule-based cũ.

## Đã có (chạy được ngay)

- `engine/models.py` — Genome/NPC/loaders (mục 2.3)
- `engine/geometry.py` — zone polygon, centroid, khoảng cách (dùng Shapely)
- `engine/behavior.py` — utility chọn zone + emotion update (mục 2.4)
- `engine/purchase.py` — công thức xác suất mua, đã sửa theo A3, có 2 ca test
- `data/*_mau.json` — 3 schema mẫu giả (layout, genome, catalog, trajectory)
- `app/pages/1_Layout_Designer.py` — vẽ zone polygon bằng streamlit-drawable-canvas
- `app/pages/4_Ket_qua_Replay.py` — replay + biểu đồ bằng Plotly, đọc trajectory mẫu
- `tests/test_engine_basics.py` — 5 test cơ bản, đã chạy pass

## Chưa có (việc tiếp theo, xem lịch Tuần 1-2 trong AIsle_ke_hoach_thuc_thi.md)

- `engine/spawn.py` — λ(t) + Poisson spawn (đã có pseudocode ở mục 10 bản đặc tả)
- `population/generate.py` — sinh 150-200 NPC bằng crossover+mutation (Tuần 2)
- `engine/simulation.py` — vòng lặp tick chính, nối tất cả lại (Tuần 3)
- Màn 2 (Catalog Manager), Màn 3 (Cấu hình & Chạy), Màn 5 (Lịch sử)

## Cài đặt & chạy

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Chạy test:
```bash
pytest tests/ -v
```

Kiểm tra công thức mua hàng (2 ca mẫu):
```bash
python -m engine.purchase
```

Chạy dashboard:
```bash
streamlit run app/Home.py
```

## Lưu ý kỹ thuật quan trọng

**Định dạng dữ liệu polygon từ `streamlit-drawable-canvas`:** đã xác nhận qua mã nguồn/PR của thư viện polygon
trả về dạng `path`: `[['M', x, y], ['L', x, y], ..., ['z']]`, không phải `points`.
Hàm `_extract_polygon_points_meters()` trong `1_Layout_Designer.py` đã xử lý đúng
định dạng này, có cộng offset `left/top` và nhân `scaleX/scaleY`. Nếu bản thư viện
bạn cài trả về khác (có thể đổi giữa các phiên bản), dùng nút "🔧 Debug" trong
sidebar Màn 1 để xem `json_data` thật và chỉnh lại hàm cho khớp.

**Tất cả code trong `engine/` không phụ thuộc Streamlit** — có thể unit test độc
lập, và tái sử dụng được nếu sau này đổi sang FastAPI/frontend khác.
