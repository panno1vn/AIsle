"""
Cơ chế Emotion & Utility chọn zone — mục 2.4 trong bản đặc tả.
"""
from __future__ import annotations

from .geometry import distance, zone_centroid
from .models import NPC


def match(zone_name: str, target_category: str | None, catalog: list[dict]) -> float:
    """1.0 nếu zone có bán đúng target_category, 0.0 nếu không (hoặc không có target)."""
    if target_category is None:
        return 0.0
    return 1.0 if any(p["zone"] == zone_name and p["category"] == target_category for p in catalog) else 0.0


def novelty_bonus(zone_name: str, visited_zones: set[str]) -> float:
    """Zone chưa từng ghé thì có điểm mới lạ cao hơn."""
    return 0.0 if zone_name in visited_zones else 1.0


def travel_penalty(from_pos: tuple[float, float], to_pos: tuple[float, float], weight: float = 0.05) -> float:
    return weight * distance(from_pos, to_pos)


def choose_next_zone(npc: NPC, layout: dict, catalog: list[dict], visited_zones: set[str]) -> str:
    """
    utility = need_product * match(zone, target_category)
            + need_explore * novelty_bonus(zone)
            - travel_penalty(distance)
    Trả về tên zone có utility cao nhất (loại 'Entrance' khỏi lựa chọn đích).
    """
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


def update_valence(npc: NPC, zone_base_valence: float, has_event: bool) -> float:
    """
    Có sự kiện (đi qua/dừng ở zone):
        current_valence += (zone.base_valence - v) * dispersion * (1 - stability)
    Không có sự kiện: hồi phục dần về attractor theo recovery_rate.
    """
    e = npc.genome.emotion
    v = npc.state.current_valence
    if has_event:
        v += (zone_base_valence - v) * e.dispersion * (1 - e.stability)
    else:
        v += (e.attractor - v) * e.recovery_rate
    return max(-1.0, min(1.0, v))