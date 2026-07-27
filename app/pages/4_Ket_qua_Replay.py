"""
Màn 4 — Kết quả & Replay (mục 5.6).
Dùng Plotly animation frames thay cho custom canvas component — có sẵn
Play/Pause + thanh tua, không cần viết JS.

Đang đọc data/trajectory_mau.json (dữ liệu giả) để C/D code UI ngay,
không cần chờ engine thật ghi log. Khi Dev A xong run_simulation() thật,
chỉ cần đổi đường dẫn file nạp vào, layout hiển thị không đổi.
"""
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.models import load_layout, load_trajectory  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Kết quả & Replay", layout="wide")
apply_theme()
st.title("4 — Kết quả & Replay")
st.caption("Số liệu và replay cho layout đã chạy. Không có xếp hạng, không có gợi ý tối ưu.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

layout = load_layout(os.path.join(DATA_DIR, "layout_mau.json"))
traj = load_trajectory(os.path.join(DATA_DIR, "trajectory_mau.json"))
df = pd.DataFrame(traj)

# --- Khối số liệu đầu trang ---
c1, c2, c3, c4 = st.columns(4)
tong_khach = df["npc_id"].nunique()
so_mua = df[df["status"] == "PURCHASED"]["npc_id"].nunique()
ty_le_mua = so_mua / tong_khach if tong_khach else 0
valence_tb = df["current_valence"].mean()

c1.metric("Tổng khách (mẫu)", tong_khach)
c2.metric("Số khách đã mua", so_mua)
c3.metric("Tỷ lệ mua", f"{ty_le_mua:.0%}")
c4.metric("Cảm xúc trung bình", f"{valence_tb:+.2f}")

st.divider()

# --- Replay bằng Plotly animation frames ---
st.subheader("Replay di chuyển NPC")

color_map = {"TRANSIT": "#4CC9F0", "DWELL": "#FFC24B", "PURCHASED": "#3ddc84", "LEFT": "#8B96A5"}

fig = px.scatter(
    df.sort_values("t"),
    x="x", y="y",
    animation_frame="t",
    animation_group="npc_id",
    color="status",
    color_discrete_map=color_map,
    hover_name="npc_id",
    hover_data={"current_valence": ":.2f", "x": False, "y": False, "t": False},
    range_x=[0, layout["store_size"][0]],
    range_y=[0, layout["store_size"][1]],
)

# Vẽ zone polygon làm nền (mỗi zone 1 shape tĩnh)
for zname, zdata in layout["zones"].items():
    pts = zdata["polygon"]
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", fill="toself",
        fillcolor="rgba(76,201,240,0.08)", line=dict(color="rgba(76,201,240,0.4)"),
        name=zname, showlegend=False, hoverinfo="skip",
    ))

fig.update_layout(
    height=600,
    plot_bgcolor="#0B0F14", paper_bgcolor="#0B0F14",
    font_color="#E8ECF1",
    yaxis=dict(scaleanchor="x", scaleratio=1),  # giữ tỉ lệ 1:1 mét
)
st.plotly_chart(fig, width='stretch')

st.divider()

# --- Biểu đồ cột: % theo status hiện tại (placeholder cho target_category thật) ---
st.subheader("Trạng thái NPC theo thời gian")
trang_thai_theo_t = df.groupby(["t", "status"]).size().reset_index(name="so_luong")
fig2 = px.bar(trang_thai_theo_t, x="t", y="so_luong", color="status", color_discrete_map=color_map)
fig2.update_layout(height=300, plot_bgcolor="#0B0F14", paper_bgcolor="#0B0F14", font_color="#E8ECF1")
st.plotly_chart(fig2, width='stretch')

st.button("💾 Lưu kết quả vào Lịch sử", disabled=True, help="Màn 5 đang xây")