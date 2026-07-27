"""
Theme dùng chung cho toàn bộ dashboard AIsle.

QUAN TRỌNG: gọi apply_theme() ở ĐẦU mỗi file trong app/pages/*.py (ngay sau
st.set_page_config), không chỉ ở Home.py — Streamlit chạy lại từ đầu mỗi khi
chuyển trang, CSS inject ở Home.py KHÔNG tự động mang sang trang khác.

Bảng màu/font kế thừa nguyên từ Brand/pitch/aisle-project-pitch.html để dashboard
và pitch deck nhất quán thương hiệu, không phải một bộ màu tách biệt.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root{
    --bg:#0B0F14; --panel:#121822; --line:#242E3D;
    --text:#E8ECF1; --text-dim:#8B96A5;
    --blue:#4CC9F0; --pink:#FF4D8D; --amber:#FFC24B; --green:#22C55E;
}

/* ---- nền tổng thể + lưới sàn cửa hàng (motif kế thừa từ pitch) ---- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stBottomBlockContainer"] { background-color:var(--bg) !important; }

[data-testid="stAppViewContainer"]{
    background-image:
        linear-gradient(rgba(36,46,61,.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(36,46,61,.5) 1px, transparent 1px);
    background-size:64px 64px;
}
[data-testid="stHeader"]{ background:transparent !important; }
footer{ visibility:hidden; }

/* ---- sidebar ---- */
[data-testid="stSidebar"]{ background-color:var(--bg) !important; border-right:1px solid var(--line); }
[data-testid="stSidebar"] *{ font-family:'Inter',sans-serif !important; color:var(--text-dim) !important; }
[data-testid="stSidebarNav"] a[aria-current="page"]{
    color:var(--text) !important; background:var(--panel) !important; border-radius:8px;
}

/* ---- typography chung ---- */
body, p, span, div, label{ font-family:'Inter',sans-serif; color:var(--text); }
h1,h2,h3,h4{ font-family:'Space Grotesk',sans-serif !important; color:var(--text) !important; }
.block-container{ padding-top:2.5rem; padding-bottom:4rem; max-width:1100px; }

/* ---- eyebrow label (mono, viết hoa, gạch ngang trước) ---- */
.aisle-eyebrow{
    font-family:'IBM Plex Mono',monospace; font-size:.78rem; letter-spacing:.14em;
    text-transform:uppercase; color:var(--blue); margin-bottom:14px;
    display:flex; align-items:center; gap:10px;
}
.aisle-eyebrow::before{ content:""; width:22px; height:1px; background:var(--blue); }

/* ---- hero ---- */
.aisle-hero h1{
    font-family:'Space Grotesk',sans-serif; font-weight:700; letter-spacing:-.02em;
    font-size:clamp(1.9rem,4vw,3rem); line-height:1.15; color:var(--text);
    margin:0 0 18px 0; max-width:760px;
}
.aisle-hero h1 span{ color:var(--blue); }
.aisle-hero .lead{ color:var(--text-dim); font-size:1.05rem; max-width:560px; margin-bottom:28px; }

/* ---- stat row (kế thừa .stat-row từ pitch) ---- */
.aisle-stats{
    display:flex; gap:1px; background:var(--line); border:1px solid var(--line);
    border-radius:14px; overflow:hidden; margin-bottom:8px;
}
.aisle-stats .stat{ background:var(--panel); padding:16px 22px; flex:1; }
.aisle-stats .num{ font-family:'IBM Plex Mono',monospace; font-size:1.3rem; color:var(--amber); font-weight:600; }
.aisle-stats .label{ color:var(--text-dim); font-size:.78rem; margin-top:4px; }

/* ---- status pill ---- */
.status-pill{
    display:inline-flex; align-items:center; gap:6px; font-family:'IBM Plex Mono',monospace;
    font-size:.7rem; padding:3px 10px; border-radius:100px;
}
.status-done{ color:var(--green); border:1px solid rgba(34,197,94,.35); }
.status-done .dot{ width:6px; height:6px; border-radius:50%; background:var(--green); animation:aisle-pulse 1.6s infinite; }
.status-pending{ color:var(--text-dim); border:1px solid var(--line); }
@keyframes aisle-pulse{ 0%,100%{opacity:1;} 50%{opacity:.3;} }

/* ---- nav card (bọc bằng st.container(border=True, key="navcard_...")) ---- */
[class*="st-key-navcard"]{
    background:var(--panel) !important; border:1px solid var(--line) !important;
    border-radius:14px !important; transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
[class*="st-key-navcard"]:hover{
    transform:translateY(-3px); border-color:var(--blue) !important;
    box-shadow:0 10px 28px rgba(76,201,240,.15);
}
.card-idx{ font-family:'IBM Plex Mono',monospace; color:var(--blue); font-size:.8rem; margin-bottom:8px; }
.card-title{ font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.05rem; color:var(--text); margin:2px 0 8px; }
.card-desc{ color:var(--text-dim); font-size:.85rem; line-height:1.45; min-height:2.6em; }

/* ---- st.page_link render ra như 1 dòng link mono màu xanh ---- */
[data-testid="stPageLink"]{ margin-top:4px; }
[data-testid="stPageLink"] p{
    font-family:'IBM Plex Mono',monospace !important; font-size:.82rem !important;
    color:var(--blue) !important; font-weight:500 !important;
}

@media (prefers-reduced-motion: reduce){
    [class*="st-key-navcard"], .status-done .dot { animation:none !important; transition:none !important; }
}
</style>
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)