"""
Màn 1 — Layout Designer (mục 5.3).
Thao tác polygon: left-click thêm điểm, right-click đóng polygon, double-click xoá điểm.
Định dạng trả về: fabric.Path, key "path": [['M',x,y],['L',x,y],...,['z']].
"""
import json
import os
import sys

import streamlit as st
from streamlit_drawable_canvas import st_canvas

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Layout Designer", layout="wide")
apply_theme()
st.title("1 — Layout Designer")
st.caption("Vẽ từng zone bằng polygon tự do. Bắt buộc phải có 1 zone tên 'Entrance'.")

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
METERS_WIDE, METERS_TALL = 10, 10


def _extract_polygon_points_meters(poly_obj, canvas_w, canvas_h, m_w, m_h):
    left = poly_obj.get("left", 0) or 0
    top = poly_obj.get("top", 0) or 0
    scale_x = poly_obj.get("scaleX", 1) or 1
    scale_y = poly_obj.get("scaleY", 1) or 1
    pts_meters = []
    for cmd in poly_obj.get("path", []):
        if len(cmd) < 3:
            continue
        _, px, py = cmd[0], cmd[1], cmd[2]
        x_abs = left + px * scale_x
        y_abs = top + py * scale_y
        pts_meters.append([round(x_abs / canvas_w * m_w, 2), round(y_abs / canvas_h * m_h, 2)])
    return pts_meters


if "zones" not in st.session_state:
    st.session_state.zones = {}

col_canvas, col_side = st.columns([2, 1])

with col_canvas:
    canvas_result = st_canvas(
        fill_color="rgba(76, 201, 240, 0.25)",
        stroke_width=2,
        stroke_color="#4CC9F0",
        background_color="#0B0F14",
        drawing_mode="polygon",
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH,
        key="layout_canvas",
    )

with col_side:
    st.subheader("Zone đã vẽ")

    with st.expander("🔧 Debug: xem raw json_data"):
        st.json(canvas_result.json_data) if canvas_result.json_data is not None else st.write("Chưa vẽ gì.")

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        polygons_moi = [o for o in objects if o.get("type") == "polygon"]

        if polygons_moi:
            st.write(f"Canvas hiện có **{len(polygons_moi)}** polygon chưa đặt tên/lưu.")
            for i, poly in enumerate(polygons_moi):
                with st.form(key=f"form_zone_{i}"):
                    ten = st.text_input("Tên zone", key=f"ten_{i}", placeholder="VD: Beverage, Entrance")
                    luu = st.form_submit_button("Lưu zone này")
                    if luu and ten:
                        pts_meters = _extract_polygon_points_meters(poly, CANVAS_WIDTH, CANVAS_HEIGHT, METERS_WIDE, METERS_TALL)
                        st.session_state.zones[ten] = pts_meters
                        st.success(f"Đã lưu zone '{ten}' ({len(pts_meters)} điểm)")

    st.divider()
    st.write("**Danh sách zone đã lưu:**")
    for ten, pts in st.session_state.zones.items():
        c1, c2 = st.columns([3, 1])
        c1.write(f"`{ten}` — {len(pts)} điểm")
        if c2.button("Xoá", key=f"xoa_{ten}"):
            del st.session_state.zones[ten]
            st.rerun()

    if "Entrance" not in st.session_state.zones and st.session_state.zones:
        st.warning("⚠️ Chưa có zone tên 'Entrance' — bắt buộc phải có để NPC spawn.")

    st.divider()
    if st.button("💾 Lưu layout.json", type="primary", disabled=not st.session_state.zones):
        layout_out = {
            "store_size": [METERS_WIDE, METERS_TALL],
            "zones": {ten: {"polygon": pts} for ten, pts in st.session_state.zones.items()},
            "catalog": [],
            "spawn_rate_curve": [],
        }
        st.session_state.layout_json = layout_out
        st.code(json.dumps(layout_out, ensure_ascii=False, indent=2), language="json")
        st.success("Đã tạo layout.json trong session — Màn 2 sẽ đọc từ đây.")
