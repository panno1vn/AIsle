"""Test cho engine/simulation.py — vòng lặp mô phỏng đầy đủ."""
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.models import load_catalog, load_layout
from engine.simulation import (
    duong_cong_mac_dinh, list_runs, load_run, run_simulation, save_run, sinh_thoi_diem_spawn,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _layout_catalog():
    layout = load_layout(os.path.join(DATA_DIR, "layout_mau.json"))
    catalog = load_catalog(os.path.join(DATA_DIR, "catalog_mau.json"))
    return layout, catalog


def test_run_simulation_ra_du_so_khach():
    layout, catalog = _layout_catalog()
    result = run_simulation(layout, catalog, so_phut=10, so_npc=50, seed=1)
    assert result["so_khach"] == 50
    assert len(result["purchase_log"]) == 50
    assert result["tong_doanh_thu"] >= 0
    assert 0.0 <= result["ty_le_mua"] <= 1.0


def test_run_simulation_tai_lap_duoc_voi_seed():
    layout, catalog = _layout_catalog()
    r1 = run_simulation(layout, catalog, so_phut=10, so_npc=50, seed=99)
    r2 = run_simulation(layout, catalog, so_phut=10, so_npc=50, seed=99)
    assert r1["tong_doanh_thu"] == r2["tong_doanh_thu"]
    assert r1["so_mua"] == r2["so_mua"]


def test_trajectory_log_co_du_truong():
    layout, catalog = _layout_catalog()
    result = run_simulation(layout, catalog, so_phut=5, so_npc=10, seed=1)
    row = result["trajectory_log"][0]
    for truong in ["npc_id", "t", "x", "y", "status", "current_valence"]:
        assert truong in row


def test_duong_cong_mac_dinh_khong_am():
    curve = duong_cong_mac_dinh(15)
    assert len(curve) == 15
    assert all(diem["rate"] > 0 for diem in curve)


def test_sinh_thoi_diem_spawn_tang_dan():
    import random
    curve = duong_cong_mac_dinh(10)
    times = sinh_thoi_diem_spawn(curve, random.Random(1))
    assert times == sorted(times)


def test_save_va_list_run(tmp_path):
    layout, catalog = _layout_catalog()
    result = run_simulation(layout, catalog, so_phut=5, so_npc=10, seed=1)
    out_dir = str(tmp_path / "runs")
    path = save_run(result, out_dir=out_dir)
    assert os.path.exists(path)

    runs = list_runs(out_dir)
    assert len(runs) == 1

    loaded = load_run(runs[0])
    assert loaded["so_khach"] == result["so_khach"]


def test_luu_nhieu_run_lien_tiep_khong_ghi_de(tmp_path):
    """Bug đã bắt được: chạy nhanh liên tiếp trong cùng 1 giây làm timestamp
    trùng nhau, save_run() cũ (chỉ có timestamp, không có suffix) sẽ ghi đè
    file trước đó. Test này đảm bảo lỗi không tái diễn."""
    layout, catalog = _layout_catalog()
    out_dir = str(tmp_path / "runs")
    for seed in [1, 2, 3]:
        result = run_simulation(layout, catalog, so_phut=5, so_npc=10, seed=seed)
        save_run(result, out_dir=out_dir)

    runs = list_runs(out_dir)
    assert len(runs) == 3, f"Kỳ vọng 3 file riêng biệt, thực tế có {len(runs)} — có thể bị ghi đè."
