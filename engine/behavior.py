"""
Cơ chế Emotion & Utility chọn zone — mục 2.4 trong bản đặc tả.
"""
from __future__ import annotations

from .geometry import distance, zone_centroid
from .models import NPC


def match(zone_name: str, target_category: str | None, catalog: list[dict]) -> float:
    if target_category is None:
        return 0.0
    return 1.0 if any(p["zone"] == zone_name and p["category"] == target_category for p in catalog) else 0.0


def novelty_bonus(zone_name: str, visited_zones: set[str]) -> float:
    return 0.0 if zone_name in visited_zones else 1.0


def travel_penalty(from_pos: tuple[float, float], to_pos: tuple[float, float], weight: float = 0.05) -> float:
    return weight * distance(from_pos, to_pos)


def choose_next_zone(npc: NPC, layout: dict, catalog: list[dict], visited_zones: set[str]) -> str:
    need_p = npc.state.current_need_product
    need_e = npc.state.current_need_explore
    pos = tuple(npc.state.position)

    best_zone, best_score = None, float("-inf")
    for zname in layout["zones"]:
        if zname == "Entrance":
            continue
        centroid = zone_centroid(layout, zname)
        score = (
            need_p * match(zname, npc.genome.need.target_category, catalog)
            + need_e * novelty_bonus(zname, visited_zones)
            - travel_penalty(pos, centroid)
        )
        if score > best_score:
            best_zone, best_score = zname, score
    return best_zone


def zone_base_valence(zone_name: str, npc: NPC, catalog: list[dict]) -> float:
    """
    Heuristic đơn giản (CHƯA có trong đặc tả gốc, tự bổ sung để vòng lặp tick
    chạy được — cần ghi rõ trong báo cáo là giả định của nhóm, không phải số
    đo thật): zone khớp đúng target_category của NPC -> cảm xúc tích cực hơn
    zone không khớp. Zone không tồn tại sản phẩm nào -> hơi tiêu cực (đi lạc).
    """
    if match(zone_name, npc.genome.need.target_category, catalog) == 1.0:
        return 0.55
    co_hang = any(p["zone"] == zone_name for p in catalog)
    return 0.15 if co_hang else -0.15


def update_valence(npc: NPC, zone_base_valence: float, has_event: bool) -> float:
    e = npc.genome.emotion
    v = npc.state.current_valence
    if has_event:
        v += (zone_base_valence - v) * e.dispersion * (1 - e.stability)
    else:
        v += (e.attractor - v) * e.recovery_rate
    return max(-1.0, min(1.0, v))
