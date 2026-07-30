"""
engine/simulation.py — vòng lặp mô phỏng đầy đủ, nối tất cả các mảnh lại
(mục 4, 8.1 đặc tả kỹ thuật). Đây là phần còn thiếu quan trọng nhất được xác
định trong lịch 3 người (Tuần 3, việc của A) — cả Màn 3 lẫn Màn 4 đều phụ
thuộc vào file này.

Đơn giản hoá có chủ đích so với đặc tả gốc (ghi rõ để không hiểu nhầm là bug):
  - Mỗi NPC đi 1-3 zone (random) trước khi ra quầy, KHÔNG mô phỏng từng bước
    đi centimet-by-centimet — đủ để có replay và số liệu hợp lý, không cần
    dựng full physics-step cho PoC.
  - zone_base_valence dùng heuristic tự định nghĩa (engine/behavior.py), vì
    đặc tả gốc không có công thức này — ghi rõ trong docstring của hàm đó.
"""
from __future__ import annotations

import os
import random
import time
import json
from datetime import datetime

from engine.behavior import choose_next_zone, update_valence, zone_base_valence
from engine.geometry import zone_centroid
from engine.purchase import xac_suat_mua_chinh, xac_suat_mua_them
from population.generate import generate_population


def duong_cong_mac_dinh(so_phut: int) -> list[dict]:
    """λ(t) mặc định hình sin quanh giờ cao điểm — dùng khi chưa có video (Phần D)."""
    import math
    return [{"minute": m, "rate": max(0.5, round(4 + 3 * math.sin(m / 3), 1))} for m in range(so_phut)]


def sinh_thoi_diem_spawn(curve: list[dict], rng: random.Random) -> list[float]:
    """Sinh thời điểm khách đến (giây) theo Poisson process, rate thay đổi theo phút (mục 8.1)."""
    thoi_diem = []
    for diem in curve:
        so_khach_phut_nay = _poisson(diem["rate"], rng)
        for _ in range(so_khach_phut_nay):
            t = diem["minute"] * 60 + rng.uniform(0, 60)
            thoi_diem.append(t)
    return sorted(thoi_diem)


def _poisson(lam: float, rng: random.Random) -> int:
    """Sinh 1 số ngẫu nhiên Poisson(lam) bằng thuật toán Knuth — tránh phụ thuộc numpy ở đây."""
    if lam <= 0:
        return 0
    L = pow(2.718281828459045, -lam)
    k, p = 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def run_simulation(
    layout: dict,
    catalog: list[dict],
    so_phut: int = 15,
    so_npc: int = 200,
    curve: list[dict] | None = None,
    gen_goc=None,
    seed: int | None = None,
) -> dict:
    """
    Chạy 1 lượt mô phỏng đầy đủ. Trả về dict gồm:
      trajectory_log, purchase_log, tong_doanh_thu, so_khach, so_mua, meta
    """
    rng = random.Random(seed)
    curve = curve or duong_cong_mac_dinh(so_phut)

    npcs = generate_population(so_npc, catalog, gen_goc=gen_goc, seed=seed)
    thoi_diem_spawn = sinh_thoi_diem_spawn(curve, rng)
    if not thoi_diem_spawn:
        thoi_diem_spawn = [0.0]

    entrance = zone_centroid(layout, "Entrance") if "Entrance" in layout["zones"] else (0.0, 0.0)

    trajectory_log = []
    purchase_log = []
    tong_doanh_thu = 0
    so_mua = 0

    for i, npc in enumerate(npcs):
        t = thoi_diem_spawn[i % len(thoi_diem_spawn)]
        npc.state.position = list(entrance)
        trajectory_log.append({
            "npc_id": npc.npc_id, "t": round(t, 1), "x": entrance[0], "y": entrance[1],
            "status": "TRANSIT", "current_valence": round(npc.state.current_valence, 3),
        })

        visited: set[str] = set()
        so_buoc = rng.randint(1, 3)
        zone_cuoi = None

        for _ in range(so_buoc):
            zone = choose_next_zone(npc, layout, catalog, visited)
            if zone is None:
                break
            visited.add(zone)
            zone_cuoi = zone
            centroid = zone_centroid(layout, zone)
            npc.state.position = list(centroid)

            base_v = zone_base_valence(zone, npc, catalog)
            npc.state.current_valence = update_valence(npc, base_v, has_event=True)
            npc.state.current_need_product = max(0.0, npc.state.current_need_product - 0.15)

            t += npc.genome.movement.dwell_patience * rng.uniform(0.5, 1.0)
            trajectory_log.append({
                "npc_id": npc.npc_id, "t": round(t, 1), "x": centroid[0], "y": centroid[1],
                "status": "DWELL", "current_valence": round(npc.state.current_valence, 3),
            })

        # --- quyết định mua ở zone cuối cùng ghé qua ---
        p_mua = xac_suat_mua_chinh(npc.state.current_need_product, npc.state.current_valence)
        da_mua = rng.random() < p_mua
        gia = 0
        san_pham_mua = None

        if da_mua and zone_cuoi:
            ung_vien = [p for p in catalog if p["zone"] == zone_cuoi]
            if ung_vien:
                sp = rng.choice(ung_vien)
                gia = sp["price"]
                san_pham_mua = sp["product_id"]
                tong_doanh_thu += gia
                so_mua += 1

        # --- cross-sell impulse ở quầy (mục 3.3 bước 3), nếu có zone "Checkout" ---
        mua_them = False
        if "Checkout" in layout["zones"]:
            p_impulse = xac_suat_mua_them(npc.state.current_valence)
            if rng.random() < p_impulse:
                impulse_items = [p for p in catalog if p["zone"] == "Checkout"]
                if impulse_items:
                    sp2 = rng.choice(impulse_items)
                    tong_doanh_thu += sp2["price"]
                    mua_them = True

        status_cuoi = "PURCHASED" if da_mua else "LEFT"
        trajectory_log.append({
            "npc_id": npc.npc_id, "t": round(t + 5, 1),
            "x": npc.state.position[0], "y": npc.state.position[1],
            "status": status_cuoi, "current_valence": round(npc.state.current_valence, 3),
        })

        purchase_log.append({
            "npc_id": npc.npc_id, "zone_cuoi": zone_cuoi, "P_mua": round(p_mua, 3),
            "da_mua": da_mua, "san_pham": san_pham_mua, "gia": gia, "mua_them_impulse": mua_them,
        })

    return {
        "meta": {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "so_phut": so_phut, "so_npc": so_npc, "seed": seed,
        },
        "trajectory_log": trajectory_log,
        "purchase_log": purchase_log,
        "tong_doanh_thu": tong_doanh_thu,
        "so_khach": len(npcs),
        "so_mua": so_mua,
        "ty_le_mua": round(so_mua / len(npcs), 3) if npcs else 0,
    }


def save_run(result: dict, out_dir: str = "data/runs") -> str:
    """Lưu 1 lần chạy ra data/runs/run_<timestamp>_<random>.json — Màn 5 đọc từ đây.

    Có suffix ngẫu nhiên 4 ký tự vì timestamp chỉ chính xác tới giây — nếu chạy
    2 lần mô phỏng liên tiếp trong cùng 1 giây (engine hiện chạy 200 NPC chỉ mất
    ~0.1s nên hoàn toàn có thể xảy ra), thiếu suffix sẽ làm file sau ghi đè file
    trước. Đã bắt lỗi này bằng cách tự test chạy 3 lần liên tiếp.
    """
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    rand_suffix = f"{random.randint(0, 0xFFFF):04x}"
    path = os.path.join(out_dir, f"run_{ts}_{rand_suffix}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return path


def list_runs(out_dir: str = "data/runs") -> list[str]:
    if not os.path.isdir(out_dir):
        return []
    return sorted(
        [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.startswith("run_") and f.endswith(".json")],
        reverse=True,
    )


def load_run(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
