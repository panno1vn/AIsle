"""
Tiện ích hình học cho zone polygon tự do (mục 2.2, 5.3).
Dùng Shapely — đã có trong stack chốt ở mục 0.4 điều kiện 3.
"""
from __future__ import annotations

import math

from shapely.geometry import Point, Polygon


def zone_polygon(layout: dict, zone_name: str) -> Polygon:
    pts = layout["zones"][zone_name]["polygon"]
    return Polygon(pts)


def zone_centroid(layout: dict, zone_name: str) -> tuple[float, float]:
    c = zone_polygon(layout, zone_name).centroid
    return (c.x, c.y)


def point_in_zone(layout: dict, zone_name: str, x: float, y: float) -> bool:
    return zone_polygon(layout, zone_name).contains(Point(x, y))


def which_zone(layout: dict, x: float, y: float) -> str | None:
    """NPC đang đứng ở toạ độ (x,y) thì đang ở zone nào? None nếu ở lối đi trống."""
    for zname in layout["zones"]:
        if point_in_zone(layout, zname, x, y):
            return zname
    return None


def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])