"""Màn 2 — Catalog Manager (mục 5.4)."""
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import apply_theme  # noqa: E402

st.set_page_config(page_title="Catalog Manager", layout="wide")
apply_theme()
st.title("2 — Catalog Manager")
st.caption("Category ở đây chính là 'vũ trụ' mà NPC dùng để chọn zone (mục 2.1 đặc tả).")

COLUMNS = ["product_id", "name", "category", "zone", "price"]

if "catalog" not in st.session_state:
    st.session_state.catalog = []

zones_da_ve = list(st.session_state.get("zones", {}).keys())
if not zones_da_ve:
    st.warning("⚠️ Chưa có zone nào từ Màn 1. Sang Màn 1 vẽ layout trước, hoặc vẫn nhập catalog rồi gán zone sau.")

st.subheader("Bảng sản phẩm")
df = pd.DataFrame(st.session_state.catalog, columns=COLUMNS)
edited = st.data_editor(
    df,
    num_rows="dynamic",
    width='stretch',
    column_config={
        "zone": st.column_config.SelectboxColumn("zone", options=zones_da_ve or ["(chưa có zone)"]),
        "price": st.column_config.NumberColumn("price", min_value=0, step=1000),
    },
    key="catalog_editor",
)
st.session_state.catalog = edited.to_dict("records")

st.divider()

with st.expander("➕ Thêm sản phẩm (form nhập tay)"):
    with st.form("form_them_sp", clear_on_submit=True):
        c1, c2 = st.columns(2)
        ten = c1.text_input("Tên sản phẩm")
        category = c2.text_input("Category")
        c3, c4 = st.columns(2)
        zone = c3.selectbox("Zone", zones_da_ve or ["(chưa có zone)"])
        gia = c4.number_input("Giá (VNĐ)", min_value=0, step=1000)
        them = st.form_submit_button("Thêm vào bảng")
        if them and ten and category:
            new_id = f"p{len(st.session_state.catalog) + 1:03d}"
            st.session_state.catalog.append({
                "product_id": new_id, "name": ten, "category": category,
                "zone": zone, "price": int(gia),
            })
            st.success(f"Đã thêm '{ten}'")
            st.rerun()

st.divider()

with st.expander("📁 Import file CSV/Excel"):
    file = st.file_uploader("Chọn file", type=["csv", "xlsx"])
    if file is not None:
        raw_df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
        st.write("Xem trước file gốc:")
        st.dataframe(raw_df.head())

        st.write("Ánh xạ cột file bạn upload → cột catalog cần:")
        mapping = {}
        cols_file = list(raw_df.columns)
        for target in ["name", "category", "zone", "price"]:
            mapping[target] = st.selectbox(f"Cột ứng với '{target}'", ["(không có)"] + cols_file, key=f"map_{target}")

        if st.button("Xem trước sau khi map"):
            missing = [t for t, c in mapping.items() if c == "(không có)" and t in ("category", "price")]
            if missing:
                st.error(f"Thiếu cột bắt buộc: {missing} — mỗi sản phẩm cần category và price (mục 5.4).")
            else:
                preview_rows = []
                for i, row in raw_df.iterrows():
                    preview_rows.append({
                        "product_id": f"p{len(st.session_state.catalog) + i + 1:03d}",
                        "name": row[mapping["name"]] if mapping["name"] != "(không có)" else f"SP {i+1}",
                        "category": row[mapping["category"]],
                        "zone": row[mapping["zone"]] if mapping["zone"] != "(không có)" else "",
                        "price": row[mapping["price"]],
                    })
                st.session_state["_import_preview"] = preview_rows
                st.dataframe(pd.DataFrame(preview_rows))

        if "_import_preview" in st.session_state and st.button("✅ Xác nhận import"):
            st.session_state.catalog.extend(st.session_state["_import_preview"])
            del st.session_state["_import_preview"]
            st.success("Đã import xong.")
            st.rerun()

st.divider()

zone_co_hang = {p.get("zone", "") for p in st.session_state.catalog}
zone_thieu_hang = [z for z in zones_da_ve if z != "Entrance" and z not in zone_co_hang]
if zone_thieu_hang:
    st.warning(f"⚠️ Zone chưa có sản phẩm nào: {', '.join(zone_thieu_hang)} (không chặn, chỉ cảnh báo).")

if st.button("💾 Lưu catalog", type="primary", disabled=not st.session_state.catalog):
    if "layout_json" in st.session_state:
        st.session_state.layout_json["catalog"] = st.session_state.catalog
    st.success(f"Đã lưu {len(st.session_state.catalog)} sản phẩm — Màn 3 sẽ đọc từ đây.")
