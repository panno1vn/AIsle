"""
Màn 5 — Lịch sử (mới, chưa từng có trước đây).

Đọc tất cả các lần chạy đã lưu trong data/runs/ (do Màn 3 ghi ra qua
engine.simulation.save_run), hiển thị bảng so sánh + biểu đồ doanh thu.
Đây là màn phục vụ persona "Area Manager" (anh Đức, xem Personas.md) — người
cần so sánh khách quan nhiều đề xuất trước khi duyệt ngân sách, không phải
persona "Manager một cửa hàng" (chị Hồng) vốn chỉ cần xem 1 kết quả gần nhất
ở Màn 4.
"""
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.simulation import list_runs, load_run  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Lịch sử", layout="wide")
apply_theme()
st.title("5 — Lịch sử")
st.caption("So sánh các lần chạy trước — không xếp hạng tự động, Manager tự đọc và quyết định.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
RUNS_DIR = os.path.join(DATA_DIR, "runs")

cac_run_path = list_runs(RUNS_DIR)

if not cac_run_path:
    st.info("Chưa có lần chạy nào được lưu. Sang Màn 3 để chạy mô phỏng đầu tiên.")
    # LƯU Ý: st.page_link ở đây từng báo lỗi khi test bằng
    # streamlit.testing.v1.AppTest.from_file("pages/5_Lich_su.py") — đã xác minh
    # đây là giới hạn của cách test cô lập 1 trang con (PagesManager tìm nhầm
    # thư mục "pages/pages/" thay vì "app/pages/"), KHÔNG phải bug thật. Khi chạy
    # thật qua `streamlit run app/Home.py`, main_script_path luôn là Home.py nên
    # không gặp lỗi này. Tương tự với st.switch_page ở cuối file.
    st.page_link("pages/3_Cau_hinh_Chay.py", label="→ Sang Màn 3")
    st.stop()

# --- Tổng hợp bảng so sánh ---
hang = []
for p in cac_run_path:
    r = load_run(p)
    hang.append({
        "file": os.path.basename(p),
        "thời điểm": r["meta"]["created_at"],
        "số NPC": r["meta"]["so_npc"],
        "số phút": r["meta"]["so_phut"],
        "doanh thu": r["tong_doanh_thu"],
        "tỷ lệ mua": r["ty_le_mua"],
    })
bang_so_sanh = pd.DataFrame(hang)

st.subheader(f"Tất cả lần chạy ({len(bang_so_sanh)})")
st.dataframe(
    bang_so_sanh.style.format({"doanh thu": "{:,.0f} đ", "tỷ lệ mua": "{:.0%}"}),
    width='stretch',
)

st.divider()

# --- Biểu đồ so sánh doanh thu qua các lần chạy ---
st.subheader("Doanh thu qua các lần chạy")
chart_df = bang_so_sanh.copy()
chart_df["nhãn"] = chart_df["file"].str.replace("run_", "").str.replace(".json", "")
fig = px.bar(chart_df, x="nhãn", y="doanh thu", color="tỷ lệ mua", color_continuous_scale="Blues")
fig.update_layout(
    height=380, plot_bgcolor="#0B0F14", paper_bgcolor="#0B0F14", font_color="#E8ECF1",
    xaxis_title="Lần chạy", yaxis_title="Doanh thu (đ)",
)
st.plotly_chart(fig, width='stretch')

st.divider()

# --- Xem chi tiết 1 lần chạy cụ thể ---
st.subheader("Xem chi tiết 1 lần chạy")
lua_chon = st.selectbox("Chọn lần chạy", options=[os.path.basename(p) for p in cac_run_path])
run_chon = load_run(next(p for p in cac_run_path if os.path.basename(p) == lua_chon))

c1, c2, c3 = st.columns(3)
c1.metric("Doanh thu", f"{run_chon['tong_doanh_thu']:,} đ")
c2.metric("Tỷ lệ mua", f"{run_chon['ty_le_mua']:.0%}")
c3.metric("Số khách", run_chon["so_khach"])

with st.expander("Xem purchase_log đầy đủ"):
    st.dataframe(pd.DataFrame(run_chon["purchase_log"]), width='stretch')

if st.button("👁️ Xem replay lần chạy này ở Màn 4"):
    st.session_state.last_run = run_chon
    st.switch_page("pages/4_Ket_qua_Replay.py")
