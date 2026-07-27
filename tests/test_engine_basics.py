"""
Test khởi điểm cho engine. Dev B mở rộng ở Tuần 2 theo mục A2 —
đặc biệt bài test cây quyết định target_category cần chạy ở n=10.000,
KHÔNG kiểm tra ±3% trên quần thể 200 (xem lý do trong AIsle_ke_hoach_thuc_thi.md, mục A2).

Chạy: pytest tests/ -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.models import load_catalog, load_layout, load_npcs
from engine.behavior import choose_next_zone
from engine.purchase import xac_suat_mua_chinh, xac_suat_mua_them

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def test_xac_suat_mua_chinh_hop_ly():
    """2 ca kiểm tra từ mục A3 của kế hoạch thực thi."""
    p_cao = xac_suat_mua_chinh(current_need_product=0.8, current_valence=0.0)
    p_thap = xac_suat_mua_chinh(current_need_product=0.2, current_valence=-0.5)
    assert 0.5 < p_cao < 0.7, f"kỳ vọng ≈0.6, ra {p_cao}"
    assert 0.05 < p_thap < 0.2, f"kỳ vọng ≈0.1, ra {p_thap}"


def test_xac_suat_mua_chinh_don_dieu_theo_nhu_cau():
    """Nhu cầu cao hơn (cùng cảm xúc) phải luôn cho xác suất mua cao hơn."""
    p1 = xac_suat_mua_chinh(current_need_product=0.2, current_valence=0.0)
    p2 = xac_suat_mua_chinh(current_need_product=0.8, current_valence=0.0)
    assert p2 > p1


def test_xac_suat_mua_them_trong_khoang_0_1():
    for v in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        p = xac_suat_mua_them(v)
        assert 0.0 <= p <= 0.08


def test_choose_next_zone_uu_tien_dung_category():
    """NPC có target_category khớp catalog phải chọn đúng zone bán category đó
    (khi zone đó không quá xa so với các lựa chọn khác)."""
    layout = load_layout(os.path.join(DATA_DIR, "layout_mau.json"))
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    npcs = load_npcs(os.path.join(DATA_DIR, "genome_mau.json"))

    npc_beverage = next(n for n in npcs if n.genome.need.target_category == "beverage")
    chosen = choose_next_zone(npc_beverage, layout, catalog, visited_zones=set())
    assert chosen == "Beverage"


def test_load_data_mau_khong_loi():
    """Sanity check: 3 file mẫu load được, không rỗng."""
    layout = load_layout(os.path.join(DATA_DIR, "layout_mau.json"))
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    npcs = load_npcs(os.path.join(DATA_DIR, "genome_mau.json"))
    assert "Entrance" in layout["zones"]
    assert len(catalog) > 0
    assert len(npcs) > 0