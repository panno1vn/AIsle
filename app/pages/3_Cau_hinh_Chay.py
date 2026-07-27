"""
Màn 3 — Cấu hình & Chạy (mục 5.5).

QUAN TRỌNG — phạm vi trung thực: population/generate.py (sinh 150-200 NPC
bằng crossover+mutation) và engine/simulation.py (vòng lặp tick đầy đủ) là
việc của Tuần 2-3, CHƯA làm. Màn này dùng engine/behavior.py + engine/purchase.py
đã có sẵn để chạy 1 lượt rút gọn trên quần thể MẪU (3 NPC từ genome_mau.json)
— là demo thật, không phải hàng giả, nhưng chưa phải bản đầy đủ ~200 NPC.
"""
import math
import random
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.behavior import choose_next_zone
from engine.models import load_catalog, load_layout, load_npcs
from engine.purchase import xac_suat_mua_chinh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Cấu hình & Chạy", layout="wide")
apply_theme()
st.title("3 — Cấu hình & Chạy mô phỏng")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

# --- λ(t): video mẫu (chưa làm, Phần D) hoặc đường cong mặc định ---
st.subheader("Spawn rate λ(t)")
nguon_lambda = st.radio(
    "Nguồn λ(t)", ["Đường cong mặc định (hình sin giờ cao điểm)", "Tải video mẫu (đang xây — Phần D)"],
    horizontal=True,
)

if nguon_lambda.startswith("Tải video"):
    st.file_uploader("Video mẫu", type=["mp4"], disabled=True)
    st.info("Trích λ(t) từ video chưa làm (nằm ở Phần D, không trên đường găng). Dùng đường cong mặc định bên dưới thay thế.")

so_phut = st.slider("Thời lượng mô phỏng (phút)", 5, 60, 15)
curve = [{"minute": m, "rate": round(4 + 3 * math.sin(m / 3), 1)} for m in range(so_phut)]
st.line_chart(pd.DataFrame(curve).set_index("minute"))

st.divider()

# --- Cấu hình quần thể NPC ---
st.subheader("Quần thể NPC")
so_npc_muon = st.number_input("Số lượng NPC mong muốn", min_value=10, max_value=500, value=200, step=10)

if st.button("🧬 Sinh quần thể NPC mới", disabled=True):
    pass
st.caption("⚠️ population/generate.py (crossover + mutation từ gen gốc) là việc Tuần 2, chưa xong — nút này tạm khoá. Hiện dùng 3 NPC mẫu bên dưới để demo luồng chạy.")

st.divider()

# --- Chạy mô phỏng rút gọn (dùng thật engine/ đã viết) ---
st.subheader("Chạy mô phỏng")
st.caption("Bản rút gọn: chạy 1 lượt chọn-zone + xác suất mua cho từng NPC mẫu — dùng đúng công thức trong engine/, chưa phải vòng lặp tick đầy đủ (Tuần 3).")

if st.button("▶ Chạy mô phỏng cho layout này", type="primary"):
    layout = st.session_state.get("layout_json") or load_layout(f"{DATA_DIR}/layout_mau.json")
    catalog = st.session_state.get("catalog") or load_catalog(f"{DATA_DIR}/catalog_mau.json")
    npcs = load_npcs(f"{DATA_DIR}/genome_mau.json")  # thay bằng quần thể thật khi Tuần 2 xong

    if not catalog:
        st.error("Chưa có catalog. Sang Màn 2 nhập sản phẩm trước.")
    else:
        progress = st.progress(0, text="Đang chạy...")
        ket_qua = []
        tong_doanh_thu = 0

        for i, npc in enumerate(npcs):
            zone_chon = choose_next_zone(npc, layout, catalog, visited_zones=set())
            p_mua = xac_suat_mua_chinh(npc.state.current_need_product, npc.state.current_valence)
            da_mua = random.random() < p_mua
            gia = 0
            if da_mua:
                san_pham_kha_thi = [p for p in catalog if p["zone"] == zone_chon]
                if san_pham_kha_thi:
                    sp = random.choice(san_pham_kha_thi)
                    gia = sp["price"]
                    tong_doanh_thu += gia
            ket_qua.append({"npc_id": npc.npc_id, "zone_chon": zone_chon, "P_mua": round(p_mua, 2), "da_mua": da_mua, "gia": gia})
            progress.progress((i + 1) / len(npcs), text=f"NPC {i+1}/{len(npcs)}")

        st.session_state.last_run = {"ket_qua": ket_qua, "tong_doanh_thu": tong_doanh_thu}

        c1, c2 = st.columns(2)
        c1.metric("Doanh thu (bản rút gọn)", f"{tong_doanh_thu:,} đ")
        c2.metric("Tỷ lệ mua", f"{sum(r['da_mua'] for r in ket_qua) / len(ket_qua):.0%}")
        st.dataframe(pd.DataFrame(ket_qua), width='stretch')
        st.success("Xong. Sang Màn 4 để xem replay (bản đầy đủ dùng data mẫu, chưa nối với kết quả này).")