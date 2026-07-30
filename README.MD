# AIsle — Store Simulator (kiến trúc Oxyte)

Công cụ **đánh giá** layout cửa hàng tiện lợi bằng mô phỏng NPC. Không tự tối ưu, không xếp hạng tự động — Manager tự đọc số liệu và quyết định.

---

## Trạng thái: 5/5 màn hình đã chạy được

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| `engine/models.py` | ✅ | Genome/NPC dataclass + loaders |
| `engine/geometry.py` | ✅ | Zone polygon (Shapely) |
| `engine/behavior.py` | ✅ | Utility chọn zone + emotion update |
| `engine/purchase.py` | ✅ | `P = sigmoid(a·need + b·valence + c)`, khớp 2 ca mẫu A3 |
| `engine/simulation.py` | ✅ | Vòng lặp đầy đủ + spawn Poisson + lưu/đọc run |
| `population/generate.py` | ✅ | Crossover + mutation, tỷ lệ 80/10/6/4 |
| Màn 1 — Layout Designer | ✅ | Vẽ polygon (streamlit-drawable-canvas) |
| Màn 2 — Catalog Manager | ✅ | Bảng inline-edit + form + import CSV |
| Màn 3 — Cấu hình & Chạy | ✅ | Chạy engine thật, 200 NPC, lưu ra `data/runs/` |
| Màn 4 — Kết quả & Replay | ✅ | Plotly animation, đọc kết quả thật |
| Màn 5 — Lịch sử | ✅ | So sánh nhiều lần chạy |

**Kiểm thử:** 16/16 pytest pass · 6/6 trang chạy sạch qua `streamlit.testing.v1.AppTest`

---

## Cài đặt & chạy

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

pytest tests/ -v                  # chạy test
python -m engine.purchase          # kiểm tra 2 ca mẫu công thức mua hàng
streamlit run app/Home.py          # chạy dashboard
```

Luồng dùng thử: Màn 1 vẽ zone (nhớ có zone tên `Entrance`) → Màn 2 nhập sản phẩm → Màn 3 bấm Chạy → Màn 4 xem replay → Màn 5 so sánh nhiều lần chạy.

Nếu chưa vẽ layout riêng, Màn 3 tự dùng `data/layout_mau.json` + `data/catalog_mau.json` nên vẫn chạy được ngay.

---

## Giới hạn đã biết (ghi vào báo cáo, mục 9 đặc tả)

**Tham số do nhóm chọn, không phải số đo thật:**
- Hằng số `a=3.0, b=1.5, c=-2.0` trong công thức xác suất mua (`engine/purchase.py`)
- Tỷ lệ `target_category_origin` 80/10/6/4 (`population/generate.py`)
- 5 gen gốc mẫu `GEN_GOC_MAC_DINH` — gán tay, thay cho trích xuất từ video thật
- Hàm `zone_base_valence()` trong `engine/behavior.py` — heuristic tự bổ sung, đặc tả gốc không có công thức này

**Đơn giản hoá có chủ đích trong `engine/simulation.py`:**
- Mỗi NPC ghé 1–3 zone rồi quyết định mua, không mô phỏng từng bước đi chi tiết — đủ cho replay và số liệu, tránh dựng full physics-step cho PoC

**Chưa làm (Phần D, không nằm trên đường găng):**
- Trích λ(t) từ video → đang dùng đường cong sin mặc định
- Trích gen gốc từ video qua homography + FER → đang dùng gen gán tay
- NPC không tiến hoá qua nhiều thế hệ

---

## Bug đã bắt được khi tự test (giữ lại để tham khảo)

1. **`generate_population(gen_goc=[])` không báo lỗi** — dùng `gen_goc or GEN_GOC_MAC_DINH` khiến list rỗng bị coi như "không truyền". Sửa: kiểm tra `is None` tường minh.
2. **`save_run()` ghi đè file** — timestamp chỉ chính xác tới giây, mà engine chạy 200 NPC chỉ mất ~0.08s, nên 2 lần chạy liên tiếp trùng tên file. Sửa: thêm suffix ngẫu nhiên. Đã có test `test_luu_nhieu_run_lien_tiep_khong_ghi_de` để không tái diễn.

## Lưu ý khi chạy test

`AppTest.from_file("pages/5_Lich_su.py")` sẽ báo `KeyError: 'url_pathname'` ở `st.page_link`/`st.switch_page` **khi `data/runs/` rỗng**. Đây **không phải bug**: `PagesManager` của Streamlit định vị thư mục `pages/` theo `main_script_path`, nên khi test cô lập 1 trang con, nó tìm nhầm `pages/pages/`. Chạy thật qua `streamlit run app/Home.py` không gặp lỗi này.
