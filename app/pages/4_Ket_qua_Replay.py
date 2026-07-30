"""
Màn 4 — Kết quả & Replay (mục 5.6).

NÂNG CẤP so với bản trước: ưu tiên đọc kết quả THẬT từ lần chạy gần nhất ở
Màn 3 (session_state.last_run, hoặc file mới nhất trong data/runs/ nếu mở
Màn 4 trực tiếp mà chưa qua Màn 3 trong session này). Chỉ dùng
trajectory_mau.json khi chưa có lần chạy thật nào — để trang không bao giờ
trống trơn, nhưng luôn ưu tiên dữ liệu thật khi có.
"""
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.models import load_layout, load_trajectory  # noqa: E402
from engine.simulation import list_runs, load_run  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Kết quả & Replay", layout="wide")
apply_theme()
st.title("4 — Kết quả & Replay")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
layout = st.session_state.get("layout_json") or load_layout(os.path.join(DATA_DIR, "layout_mau.json"))

# --- Chọn nguồn dữ liệu: kết quả thật gần nhất, hay data mẫu ---
nguon = "mẫu"
if "last_run" in st.session_state:
    result = st.session_state.last_run
    traj = result["trajectory_log"]
    nguon = f"lần chạy vừa rồi ({result['meta']['created_at']})"
else:
    cac_run = list_runs(os.path.join(DATA_DIR, "runs"))
    if cac_run:
        result = load_run(cac_run[0])
        traj = result["trajectory_log"]
        nguon = f"lần chạy gần nhất trên đĩa ({os.path.basename(cac_run[0])})"
    else:
        traj = load_trajectory(os.path.join(DATA_DIR, "trajectory_mau.json"))
        result = None

if result is None:
    st.caption("📁 Đang xem **dữ liệu mẫu** — chưa có lần chạy thật nào. Sang Màn 3 để chạy mô phỏng.")
else:
    st.caption(f"📊 Đang xem **{nguon}**.")

df = pd.DataFrame(traj)

# --- Khối số liệu đầu trang ---
c1, c2, c3, c4 = st.columns(4)
tong_khach = df["npc_id"].nunique()
so_mua = df[df["status"] == "PURCHASED"]["npc_id"].nunique()
ty_le_mua = so_mua / tong_khach if tong_khach else 0
valence_tb = df["current_valence"].mean()

c1.metric("Tổng khách", tong_khach)
c2.metric("Số khách đã mua", so_mua)
c3.metric("Tỷ lệ mua", f"{ty_le_mua:.0%}")
c4.metric("Cảm xúc trung bình", f"{valence_tb:+.2f}")

if result:
    st.metric("Doanh thu (bao gồm impulse)", f"{result['tong_doanh_thu']:,} đ")

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

for zname, zdata in layout["zones"].items():
    pts = zdata["polygon"]
    if len(pts) < 3:
        continue
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", fill="toself",
        fillcolor="rgba(76,201,240,0.08)", line=dict(color="rgba(76,201,240,0.4)"),
        name=zname, showlegend=False, hoverinfo="skip",
    ))

fig.update_layout(
    height=600, plot_bgcolor="#0B0F14", paper_bgcolor="#0B0F14", font_color="#E8ECF1",
    yaxis=dict(scaleanchor="x", scaleratio=1),
)
st.plotly_chart(fig, width='stretch')

st.divider()

st.subheader("Trạng thái NPC theo thời gian")
trang_thai_theo_t = df.groupby(["t", "status"]).size().reset_index(name="so_luong")
fig2 = px.bar(trang_thai_theo_t, x="t", y="so_luong", color="status", color_discrete_map=color_map)
fig2.update_layout(height=300, plot_bgcolor="#0B0F14", paper_bgcolor="#0B0F14", font_color="#E8ECF1")
st.plotly_chart(fig2, width='stretch')
