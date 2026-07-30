"""Home — cổng vào dashboard AIsle. Chi tiết theme xem app/theme.py."""
import os

import streamlit as st

from theme import apply_theme

st.set_page_config(page_title="AIsle — Store Simulator", layout="wide")
apply_theme()

APP_DIR = os.path.dirname(os.path.abspath(__file__))

MAN_HINH = [
    {"idx": "01", "title": "Layout Designer", "desc": "Vẽ zone polygon tự do cho cửa hàng.",
     "path": "pages/1_Layout_Designer.py"},
    {"idx": "02", "title": "Catalog Manager", "desc": "Nhập và quản lý danh sách hàng hoá.",
     "path": "pages/2_Catalog_Manager.py"},
    {"idx": "03", "title": "Cấu hình & Chạy", "desc": "Chọn thông số, chạy mô phỏng.",
     "path": "pages/3_Cau_hinh_Chay.py"},
    {"idx": "04", "title": "Kết quả & Replay", "desc": "Số liệu, biểu đồ, replay NPC di chuyển.",
     "path": "pages/4_Ket_qua_Replay.py"},
    {"idx": "05", "title": "Lịch sử", "desc": "So sánh các lần chạy trước.",
     "path": "pages/5_Lich_su.py"},
]
for man in MAN_HINH:
    man["done"] = os.path.exists(os.path.join(APP_DIR, man["path"]))
so_da_xong = sum(m["done"] for m in MAN_HINH)

st.markdown(
    """
    <div class="aisle-hero">
      <div class="aisle-eyebrow">Dashboard nội bộ · AIsle</div>
      <h1>Trước khi dời một cái kệ thật,<br>đi một vòng ở đây <span>trước</span>.</h1>
      <p class="lead">Vẽ layout, nhập hàng hoá, chạy mô phỏng — xem doanh thu ước tính
      trước khi đổi bất cứ thứ gì ngoài đời thật.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="aisle-stats">
      <div class="stat"><div class="num">{len(MAN_HINH)}</div><div class="label">màn hình trong dashboard</div></div>
      <div class="stat"><div class="num">{so_da_xong} / {len(MAN_HINH)}</div><div class="label">đã có UI chạy được</div></div>
      <div class="stat"><div class="num">PoC</div><div class="label">5 tuần · Product Design Module 2</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.write("")

st.markdown('<div class="aisle-eyebrow" style="margin-top:12px;">Đi qua từng gian</div>', unsafe_allow_html=True)
st.caption("5 bước từ ý tưởng đến con số — đi tuần tự lần đầu, sau đó ghé lại bất kỳ đâu qua sidebar.")
st.write("")

cols = st.columns(5, gap="medium")
for col, man in zip(cols, MAN_HINH):
    with col:
        with st.container(border=True, key=f"navcard_{man['idx']}"):
            trang_thai_html = (
                '<span class="status-pill status-done"><span class="dot"></span>Sẵn sàng</span>'
                if man["done"] else
                '<span class="status-pill status-pending">Đang xây</span>'
            )
            st.markdown(
                f"""
                <div class="card-idx">{man['idx']}</div>
                <div class="card-title">{man['title']}</div>
                <div class="card-desc">{man['desc']}</div>
                <div style="margin:10px 0;">{trang_thai_html}</div>
                """,
                unsafe_allow_html=True,
            )
            if man["done"]:
                st.page_link(man["path"], label="Mở màn hình →")
            else:
                st.caption("Sắp có mặt")

st.write("")
st.write("")
st.markdown(
    """
    <div style="border-top:1px solid var(--line); padding-top:16px; margin-top:8px;
                font-family:'IBM Plex Mono',monospace; font-size:.78rem; color:var(--text-dim);">
      AIsle — Digital Twin cho Cửa hàng Tiện lợi · Dự án học phần · 2026
    </div>
    """,
    unsafe_allow_html=True,
)
