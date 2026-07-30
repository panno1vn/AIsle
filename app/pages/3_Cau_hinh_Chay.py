"""
Màn 3 — Cấu hình & Chạy (mục 5.5).

NÂNG CẤP so với bản trước: giờ dùng engine/simulation.py + population/generate.py
thật, chạy với quần thể đầy đủ (mặc định 200 NPC) — không còn là bản rút gọn
3 NPC mẫu nữa. Kết quả được lưu vào data/runs/ để Màn 4 và Màn 5 đọc.

Vẫn còn đơn giản hoá thật (ghi rõ, không giấu): λ(t) từ video chưa làm (Phần D,
không trên đường găng) — dùng đường cong mặc định hình sin.
"""
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.models import load_catalog, load_layout  # noqa: E402
from engine.simulation import duong_cong_mac_dinh, run_simulation, save_run  # noqa: E402
from population.generate import generate_population  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Cấu hình & Chạy", layout="wide")
apply_theme()
st.title("3 — Cấu hình & Chạy mô phỏng")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

# --- λ(t) ---
st.subheader("Spawn rate λ(t)")
nguon_lambda = st.radio(
    "Nguồn λ(t)", ["Đường cong mặc định (hình sin giờ cao điểm)", "Tải video mẫu (đang xây — Phần D)"],
    horizontal=True,
)
if nguon_lambda.startswith("Tải video"):
    st.file_uploader("Video mẫu", type=["mp4"], disabled=True)
    st.info("Trích λ(t) từ video chưa làm (Phần D, không trên đường găng). Dùng đường cong mặc định bên dưới.")

so_phut = st.slider("Thời lượng mô phỏng (phút)", 5, 60, 15)
curve = duong_cong_mac_dinh(so_phut)
st.line_chart(pd.DataFrame(curve).set_index("minute"))

st.divider()

# --- Quần thể NPC ---
st.subheader("Quần thể NPC")
so_npc = st.number_input("Số lượng NPC", min_value=10, max_value=1000, value=200, step=10)

if st.button("🧬 Sinh thử quần thể NPC (xem trước phân bố)"):
    catalog_hien_tai = st.session_state.get("catalog") or load_catalog(f"{DATA_DIR}/catalog_mau.json")
    if not catalog_hien_tai:
        st.error("Chưa có catalog. Sang Màn 2 nhập sản phẩm trước.")
    else:
        preview_pop = generate_population(int(so_npc), catalog_hien_tai)
        phan_bo = pd.Series(
            [n.genome.need.target_category_origin for n in preview_pop]
        ).value_counts(normalize=True).rename("tỷ lệ")
        st.caption("Tỷ lệ nguồn gốc target_category trong quần thể vừa sinh thử (kỳ vọng ≈ 80/10/6/4, xem mục 3.3):")
        st.dataframe((phan_bo * 100).round(1).astype(str) + " %")

st.divider()

# --- Chạy mô phỏng thật ---
st.subheader("Chạy mô phỏng")
st.caption(f"Sẽ chạy engine đầy đủ với {int(so_npc)} NPC, {so_phut} phút mô phỏng — dùng population/generate.py + engine/simulation.py thật.")

if st.button("▶ Chạy mô phỏng cho layout này", type="primary"):
    layout = st.session_state.get("layout_json") or load_layout(f"{DATA_DIR}/layout_mau.json")
    catalog = st.session_state.get("catalog") or load_catalog(f"{DATA_DIR}/catalog_mau.json")

    if not catalog:
        st.error("Chưa có catalog. Sang Màn 2 nhập sản phẩm trước.")
    elif "Entrance" not in layout.get("zones", {}):
        st.error("Layout chưa có zone 'Entrance'. Sang Màn 1 vẽ và đặt tên zone Entrance trước.")
    else:
        with st.spinner(f"Đang mô phỏng {int(so_npc)} NPC..."):
            result = run_simulation(layout, catalog, so_phut=so_phut, so_npc=int(so_npc), curve=curve)
            run_path = save_run(result, out_dir=os.path.join(DATA_DIR, "runs"))

        st.session_state.last_run = result
        st.session_state.last_run_path = run_path

        c1, c2, c3 = st.columns(3)
        c1.metric("Doanh thu", f"{result['tong_doanh_thu']:,} đ")
        c2.metric("Tỷ lệ mua", f"{result['ty_le_mua']:.0%}")
        c3.metric("Số khách", result["so_khach"])

        st.dataframe(pd.DataFrame(result["purchase_log"]), width='stretch')
        st.success(f"Đã lưu kết quả: `{run_path}`. Sang Màn 4 để xem replay, hoặc Màn 5 để so sánh với lần chạy khác.")
