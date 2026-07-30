"""
Test population generator — mục A2 của kế hoạch thực thi.

QUAN TRỌNG: tỷ lệ target_category_origin (80/10/6/4) chỉ được kiểm tra ở
n=10.000 với ngưỡng ±3%. KHÔNG kiểm tra ngưỡng chặt trên quần thể 200 thật —
sai số chuẩn ở n=200 đã ~2.8%, nên code đúng vẫn có thể trượt ~28% số lần
chạy nếu áp ngưỡng ±3% ở đó. Xem AIsle_ke_hoach_thuc_thi.md mục A2.

Chạy: pytest tests/test_population.py -v
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.models import load_catalog
from population.generate import ORIGIN_WEIGHTS, generate_population

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NGUONG_SAI_SO = 0.03  # ±3%, chỉ áp dụng ở n=10.000


def test_ty_le_target_category_origin_n_10000():
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    npcs = generate_population(10_000, catalog, seed=42)

    dem = Counter(npc.genome.need.target_category_origin for npc in npcs)
    tong = len(npcs)

    for origin, ky_vong in ORIGIN_WEIGHTS:
        thuc_te = dem[origin] / tong
        lech = abs(thuc_te - ky_vong)
        assert lech <= NGUONG_SAI_SO, (
            f"{origin}: kỳ vọng {ky_vong:.0%}, thực tế {thuc_te:.2%}, "
            f"lệch {lech:.2%} > ngưỡng {NGUONG_SAI_SO:.0%}"
        )


def test_gia_tri_so_trong_khoang_hop_le():
    """Sanity check: không có NaN, không có giá trị âm bất thường sau crossover+mutation."""
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    npcs = generate_population(2000, catalog, seed=1)

    for npc in npcs:
        assert 0.0 <= npc.state.current_need_product <= 1.0
        assert 0.0 <= npc.state.current_need_explore <= 1.0
        assert -1.0 <= npc.state.current_valence <= 1.0
        assert npc.genome.movement.walk_speed > 0
        assert npc.genome.movement.dwell_patience > 0


def test_khong_trung_id():
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    npcs = generate_population(500, catalog, seed=3)
    ids = [n.npc_id for n in npcs]
    assert len(ids) == len(set(ids)), "Có npc_id bị trùng"


def test_can_it_nhat_2_gen_goc():
    import pytest
    with pytest.raises(ValueError):
        generate_population(10, catalog=[], gen_goc=[], seed=1)
