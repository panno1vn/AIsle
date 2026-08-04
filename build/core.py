"""Pure-Python simulation core for the AIsle desktop application.

This module deliberately has no Tkinter dependency. The GUI is only a client of
generate_population() and run_simulation(), matching the architecture contract.
"""
from __future__ import annotations

import heapq
import math
import random
import time
from dataclasses import asdict, dataclass
from typing import Callable, Optional


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def distance(a: dict, b: dict) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


SEED_GENOMES = [
    dict(need_product=.72, need_growth=.018, need_explore=.24, explore_growth=.008,
         attractor=.32, stability=.66, dispersion=.36, recovery=.14,
         speed=1.42, dwell=8.2, steadiness=.82, target="beverage"),
    dict(need_product=.35, need_growth=.012, need_explore=.68, explore_growth=.014,
         attractor=.12, stability=.44, dispersion=.57, recovery=.09,
         speed=.92, dwell=13.5, steadiness=.54, target="snack"),
    dict(need_product=.58, need_growth=.021, need_explore=.42, explore_growth=.009,
         attractor=.48, stability=.74, dispersion=.28, recovery=.18,
         speed=1.18, dwell=10.2, steadiness=.73, target="personal-care"),
    dict(need_product=.83, need_growth=.026, need_explore=.15, explore_growth=.006,
         attractor=-.04, stability=.52, dispersion=.48, recovery=.12,
         speed=1.56, dwell=6.4, steadiness=.88, target="instant-food"),
    dict(need_product=.21, need_growth=.007, need_explore=.77, explore_growth=.017,
         attractor=.25, stability=.39, dispersion=.62, recovery=.08,
         speed=1.03, dwell=15.1, steadiness=.47, target="candy"),
    dict(need_product=.49, need_growth=.016, need_explore=.51, explore_growth=.011,
         attractor=.41, stability=.81, dispersion=.22, recovery=.20,
         speed=1.27, dwell=9.6, steadiness=.76, target="household"),
]


DEFAULT_LAYOUT = {
    "width": 12.0, "height": 8.0,
    "walls": [
        {"id": "w1", "x1": .2, "y1": .2, "x2": 11.8, "y2": .2},
        {"id": "w2", "x1": .2, "y1": .2, "x2": .2, "y2": 7.8},
        {"id": "w3", "x1": 11.8, "y1": .2, "x2": 11.8, "y2": 7.8},
        {"id": "w4", "x1": .2, "y1": 7.8, "x2": 4.8, "y2": 7.8},
        {"id": "w5", "x1": 7.2, "y1": 7.8, "x2": 11.8, "y2": 7.8},
    ],
    "shelves": [
        {"id": "s1", "label": "Do uong", "category": "beverage", "x": 1.3, "y": 1.2, "w": 2.5, "h": .7, "valence": .42},
        {"id": "s2", "label": "Do an nhanh", "category": "instant-food", "x": 4.75, "y": 1.2, "w": 2.5, "h": .7, "valence": .18},
        {"id": "s3", "label": "Snack", "category": "snack", "x": 8.2, "y": 1.2, "w": 2.5, "h": .7, "valence": .55},
        {"id": "s4", "label": "Cham soc ca nhan", "category": "personal-care", "x": 2.1, "y": 4.1, "w": .75, "h": 2.1, "valence": .08},
        {"id": "s5", "label": "Gia dung", "category": "household", "x": 5.25, "y": 4.1, "w": .75, "h": 2.1, "valence": -.05},
        {"id": "s6", "label": "Keo & gum", "category": "candy", "x": 8.4, "y": 5.75, "w": 1.8, "h": .65, "valence": .62},
    ],
    "entrance": {"x": 6.0, "y": 7.55},
    "checkout": {"x": 9.5, "y": 6.85},
}


DEFAULT_CATALOG = [
    {"id": "p001", "name": "Nuoc khoang", "category": "beverage", "shelf": "s1", "price": 10000},
    {"id": "p002", "name": "Tra xanh", "category": "beverage", "shelf": "s1", "price": 12000},
    {"id": "p003", "name": "Mi ly", "category": "instant-food", "shelf": "s2", "price": 15000},
    {"id": "p004", "name": "Com nam", "category": "instant-food", "shelf": "s2", "price": 22000},
    {"id": "p005", "name": "Snack khoai tay", "category": "snack", "shelf": "s3", "price": 18000},
    {"id": "p006", "name": "Banh quy", "category": "snack", "shelf": "s3", "price": 24000},
    {"id": "p007", "name": "Khan giay", "category": "personal-care", "shelf": "s4", "price": 18000},
    {"id": "p008", "name": "Nuoc rua tay", "category": "personal-care", "shelf": "s4", "price": 32000},
    {"id": "p009", "name": "Nuoc rua chen", "category": "household", "shelf": "s5", "price": 38000},
    {"id": "p010", "name": "Tui rac", "category": "household", "shelf": "s5", "price": 26000},
    {"id": "p011", "name": "Keo gum", "category": "candy", "shelf": "s6", "price": 8000},
    {"id": "p012", "name": "Socola thanh", "category": "candy", "shelf": "s6", "price": 16000},
]


@dataclass
class Genome:
    npc_id: str
    origin: str
    target_category: Optional[str]
    need_product: float
    need_growth: float
    need_explore: float
    explore_growth: float
    attractor: float
    stability: float
    dispersion: float
    recovery: float
    speed: float
    dwell: float
    steadiness: float


def genome_from_input(data: dict, index: int = 0) -> Genome:
    """Build one validated NPC genome from a user-authored form/CSV row."""
    def number(key: str, default: float, low: float, high: float) -> float:
        try:
            value = float(data.get(key, default))
        except (TypeError, ValueError):
            value = default
        return clamp(value, low, high)

    target = str(data.get("target_category", "")).strip() or None
    return Genome(
        npc_id=str(data.get("npc_id", "")).strip() or f"manual_{index + 1:04d}",
        origin="manual_input", target_category=target,
        need_product=number("need_product", .6, 0, 1),
        need_growth=number("need_growth", .015, 0, .05),
        need_explore=number("need_explore", .4, 0, 1),
        explore_growth=number("explore_growth", .01, 0, .04),
        attractor=number("attractor", .2, -1, 1),
        stability=number("stability", .6, 0, 1),
        dispersion=number("dispersion", .4, 0, 1),
        recovery=number("recovery", .15, 0, .5),
        speed=number("speed", 1.2, .65, 1.9),
        dwell=number("dwell", 10, 3, 24),
        steadiness=number("steadiness", .7, .2, 1),
    )


def population_from_input(rows: list[dict]) -> list[Genome]:
    """Convert manually entered NPC rows while rejecting duplicate IDs."""
    population = [genome_from_input(row, index) for index, row in enumerate(rows)]
    ids = [npc.npc_id for npc in population]
    if len(ids) != len(set(ids)):
        raise ValueError("NPC ID bi trung. Moi NPC can mot ID duy nhat.")
    return population


def _mutate(value: float, spread: float, rng: random.Random, low: float, high: float) -> float:
    return clamp(value + (rng.random() + rng.random() - 1) * spread, low, high)


def generate_population(catalog: list[dict], n: int = 180, seed: int = 42) -> list[Genome]:
    """Generate one finite population using uniform crossover + bounded mutation."""
    rng = random.Random(seed)
    category_bag = [p["category"] for p in catalog if p.get("category")]
    categories = set(category_bag)
    result = []
    for index in range(n):
        father, mother = rng.choice(SEED_GENOMES), rng.choice(SEED_GENOMES)
        gene = lambda key: (father if rng.random() < .5 else mother)[key]
        roll = rng.random()
        if roll < .80:
            origin = "catalog_sampled"
            target = rng.choice(category_bag) if category_bag else None
        elif roll < .90:
            inherited = rng.choice([father["target"], mother["target"]])
            if inherited in categories:
                origin, target = "crossover_inherited", inherited
            else:
                origin = "catalog_sampled"
                target = rng.choice(category_bag) if category_bag else None
        elif roll < .96:
            origin = "phantom_mutation"
            target = rng.choice(["frozen-food", "pet-care", "fresh-bakery", "organic"])
            if target in categories:
                target = "missing-" + target
        else:
            origin, target = "no_intent_mutation", None
        result.append(Genome(
            npc_id=f"npc_{index + 1:04d}", origin=origin, target_category=target,
            need_product=_mutate(gene("need_product"), .1, rng, 0, 1),
            need_growth=_mutate(gene("need_growth"), .006, rng, 0, .05),
            need_explore=_mutate(gene("need_explore"), .1, rng, 0, 1),
            explore_growth=_mutate(gene("explore_growth"), .004, rng, 0, .04),
            attractor=_mutate(gene("attractor"), .12, rng, -1, 1),
            stability=_mutate(gene("stability"), .1, rng, 0, 1),
            dispersion=_mutate(gene("dispersion"), .1, rng, 0, 1),
            recovery=_mutate(gene("recovery"), .04, rng, 0, .5),
            speed=_mutate(gene("speed"), .18, rng, .65, 1.9),
            dwell=_mutate(gene("dwell"), 2.5, rng, 3, 24),
            steadiness=_mutate(gene("steadiness"), .12, rng, .2, 1),
        ))
    return result


class Grid:
    """Small A* grid cached once for the layout."""

    def __init__(self, layout: dict, cell: float = .25):
        self.layout, self.cell = layout, cell
        self.cols = math.ceil(layout["width"] / cell)
        self.rows = math.ceil(layout["height"] / cell)
        self.blocked: set[tuple[int, int]] = set()
        self._mark_obstacles()

    def _mark_obstacles(self) -> None:
        margin = .28
        for shelf in self.layout["shelves"]:
            for row in range(math.floor((shelf["y"] - margin) / self.cell), math.ceil((shelf["y"] + shelf["h"] + margin) / self.cell) + 1):
                for col in range(math.floor((shelf["x"] - margin) / self.cell), math.ceil((shelf["x"] + shelf["w"] + margin) / self.cell) + 1):
                    if 0 <= col < self.cols and 0 <= row < self.rows:
                        self.blocked.add((col, row))
        for wall in self.layout["walls"]:
            steps = max(2, math.ceil(math.hypot(wall["x2"] - wall["x1"], wall["y2"] - wall["y1"]) / .12))
            for i in range(steps + 1):
                x = wall["x1"] + (wall["x2"] - wall["x1"]) * i / steps
                y = wall["y1"] + (wall["y2"] - wall["y1"]) * i / steps
                for ox in (-.18, 0, .18):
                    for oy in (-.18, 0, .18):
                        self.blocked.add((round((x + ox) / self.cell), round((y + oy) / self.cell)))

    def ok(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows and (col, row) not in self.blocked

    def nearest(self, col: int, row: int) -> tuple[int, int]:
        if self.ok(col, row):
            return col, row
        for radius in range(1, 14):
            for r in range(row - radius, row + radius + 1):
                for c in range(col - radius, col + radius + 1):
                    if self.ok(c, r):
                        return c, r
        return clamp(col, 0, self.cols - 1), clamp(row, 0, self.rows - 1)

    def line_of_sight(self, a: dict, b: dict) -> bool:
        steps = max(1, math.ceil(distance(a, b) / (self.cell * .45)))
        for i in range(1, steps):
            t = i / steps
            col = math.floor((a["x"] + (b["x"] - a["x"]) * t) / self.cell)
            row = math.floor((a["y"] + (b["y"] - a["y"]) * t) / self.cell)
            if not self.ok(col, row):
                return False
        return True

    def path(self, start: dict, end: dict) -> list[dict]:
        sc, sr = self.nearest(round(start["x"] / self.cell), round(start["y"] / self.cell))
        ec, er = self.nearest(round(end["x"] / self.cell), round(end["y"] / self.cell))
        frontier = [(0.0, sc, sr)]
        costs = {(sc, sr): 0.0}
        previous: dict[tuple[int, int], tuple[int, int]] = {}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        found = False
        while frontier:
            _, col, row = heapq.heappop(frontier)
            if (col, row) == (ec, er):
                found = True
                break
            for dc, dr in directions:
                nc, nr = col + dc, row + dr
                if not self.ok(nc, nr):
                    continue
                if dc and dr and (not self.ok(col + dc, row) or not self.ok(col, row + dr)):
                    continue
                new_cost = costs[(col, row)] + (math.sqrt(2) if dc and dr else 1)
                if new_cost < costs.get((nc, nr), math.inf):
                    costs[(nc, nr)] = new_cost
                    previous[(nc, nr)] = (col, row)
                    heuristic = math.hypot(nc - ec, nr - er)
                    heapq.heappush(frontier, (new_cost + heuristic, nc, nr))
        if not found:
            return [dict(start), dict(end)]
        cells, current = [], (ec, er)
        while current != (sc, sr):
            cells.append(current)
            current = previous[current]
        cells.append((sc, sr))
        points = [{"x": (c + .5) * self.cell, "y": (r + .5) * self.cell} for c, r in reversed(cells)]
        points[0], points[-1] = dict(start), dict(end)
        smooth, index = [points[0]], 0
        while index < len(points) - 1:
            far = index + 1
            for candidate in range(len(points) - 1, index + 1, -1):
                if self.line_of_sight(points[index], points[candidate]):
                    far = candidate
                    break
            smooth.append(points[far])
            index = far
        return smooth


def _access_point(shelf: dict, origin: dict, layout: dict) -> dict:
    candidates = [
        {"x": shelf["x"] - .38, "y": shelf["y"] + shelf["h"] / 2},
        {"x": shelf["x"] + shelf["w"] + .38, "y": shelf["y"] + shelf["h"] / 2},
        {"x": shelf["x"] + shelf["w"] / 2, "y": shelf["y"] - .38},
        {"x": shelf["x"] + shelf["w"] / 2, "y": shelf["y"] + shelf["h"] + .38},
    ]
    for point in candidates:
        point["x"] = clamp(point["x"], .3, layout["width"] - .3)
        point["y"] = clamp(point["y"], .3, layout["height"] - .3)
    return min(candidates, key=lambda point: distance(origin, point))


def _path_length(path: list[dict]) -> float:
    return sum(distance(path[i - 1], path[i]) for i in range(1, len(path)))


def _spawn_times(n: int, duration: float, rng: random.Random) -> list[float]:
    times = []
    while len(times) < n:
        t = rng.random() * duration
        phase = t / duration
        weight = .55 + .55 * math.sin(phase * math.pi) + .18 * math.sin(phase * math.pi * 4 + .7)
        if rng.random() < weight / 1.28:
            times.append(t)
    return sorted(times)


def _sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def run_simulation(
    layout: dict,
    catalog: list[dict],
    population: list[Genome],
    duration_minutes: int,
    seed: int = 42,
    crowd_avoidance: bool = True,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    """Run a deterministic finite simulation and return compact path segments."""
    started = time.perf_counter()
    rng = random.Random(seed)
    duration = duration_minutes * 60
    grid = Grid(layout)
    spawns = _spawn_times(len(population), duration, rng)
    shelf_products = {s["id"]: [p for p in catalog if p.get("shelf") == s["id"]] for s in layout["shelves"]}
    catalog_categories = {p.get("category") for p in catalog if p.get("category")}
    agents, purchases = [], []
    dwell_by_shelf = {s["id"]: 0.0 for s in layout["shelves"]}
    converted = main_buyers = impulse_buyers = missing = 0
    for index, npc in enumerate(population):
        segments, visited = [], set()
        position, current_time = dict(layout["entrance"]), spawns[index]
        valence = npc.attractor
        bought = bought_main = bought_impulse = False
        if npc.target_category and npc.target_category not in catalog_categories:
            missing += 1

        def utility(shelf: dict) -> float:
            products = shelf_products[shelf["id"]]
            match = any(p["category"] == npc.target_category for p in products)
            novelty = shelf["id"] not in visited
            center = {"x": shelf["x"] + shelf["w"] / 2, "y": shelf["y"] + shelf["h"] / 2}
            return ((npc.need_product + npc.need_growth * current_time / 60) * match
                    + (npc.need_explore + npc.explore_growth * current_time / 60) * novelty
                    - .05 * distance(position, center) + rng.random() * .08)

        shelves = list(layout["shelves"])
        route = [max(shelves, key=utility)] if shelves else []
        if len(shelves) > 1 and rng.random() < npc.need_explore * .75:
            route.append(rng.choice([s for s in shelves if s not in route]))
        if len(shelves) > 2 and rng.random() < npc.need_explore * .3:
            route.append(rng.choice([s for s in shelves if s not in route]))
        for shelf in route:
            target = _access_point(shelf, position, layout)
            path = grid.path(position, target)
            travel = _path_length(path) / npc.speed
            segments.append({"t0": current_time, "t1": current_time + travel, "status": "TRANSIT", "path": path})
            current_time += travel
            position = dict(target)
            dwell = npc.dwell * (.78 + rng.random() * .44)
            segments.append({"t0": current_time, "t1": current_time + dwell, "status": "DWELL", "point": dict(position), "shelf": shelf["id"]})
            dwell_by_shelf[shelf["id"]] += dwell
            current_time += dwell
            visited.add(shelf["id"])
            valence = clamp(valence + (shelf["valence"] - valence) * npc.dispersion * (1 - npc.stability), -1, 1)
            products = shelf_products[shelf["id"]]
            matched = [p for p in products if p["category"] == npc.target_category]
            if not bought_main and matched:
                probability = _sigmoid(3 * clamp(npc.need_product + npc.need_growth * current_time / 60, 0, 1) + 1.5 * valence - 2)
                if rng.random() < probability:
                    product = rng.choice(matched)
                    purchases.append({"npc_id": npc.npc_id, "product_id": product["id"], "purchase_type": "main", "tick": round(current_time), "price": product["price"]})
                    bought = bought_main = True
            if products and rng.random() < .08 * ((valence + 1) / 2):
                choices = [p for p in products if not any(x["npc_id"] == npc.npc_id and x["product_id"] == p["id"] for x in purchases)]
                if choices:
                    product = rng.choice(choices)
                    purchases.append({"npc_id": npc.npc_id, "product_id": product["id"], "purchase_type": "impulse_cross_sell", "tick": round(current_time), "price": product["price"]})
                    bought = bought_impulse = True
        destinations = [layout["checkout"], layout["entrance"]] if bought else [layout["entrance"]]
        for destination_index, target in enumerate(destinations):
            path = grid.path(position, target)
            travel = _path_length(path) / npc.speed
            status = "PURCHASED" if bought and destination_index == 0 else "LEAVING"
            segments.append({"t0": current_time, "t1": current_time + travel, "status": status, "path": path})
            current_time += travel
            position = dict(target)
            if bought and destination_index == 0:
                segments.append({"t0": current_time, "t1": current_time + 4, "status": "PURCHASED", "point": dict(position)})
                current_time += 4
        if bought:
            converted += 1
            main_buyers += int(bought_main)
            impulse_buyers += int(bought_impulse)
        offset = {"x": (rng.random() - .5) * .13, "y": (rng.random() - .5) * .13} if crowd_avoidance else {"x": 0, "y": 0}
        agents.append({"id": npc.npc_id, "origin": npc.origin, "target": npc.target_category,
                       "spawn": spawns[index], "end": current_time, "valence": valence,
                       "segments": segments, "offset": offset})
        if on_progress and (index % 8 == 0 or index == len(population) - 1):
            on_progress((index + 1) / len(population), f"NPC {index + 1}/{len(population)}")
    origins = {key: 0 for key in ("catalog_sampled", "crossover_inherited", "phantom_mutation", "no_intent_mutation", "manual_input")}
    for npc in population:
        origins[npc.origin] += 1
    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": seed,
        "n": len(population), "duration_minutes": duration_minutes,
        "layout": layout, "catalog": catalog, "agents": agents, "purchases": purchases,
        "dwell_by_shelf": dwell_by_shelf, "revenue": sum(p["price"] for p in purchases),
        "conversion_rate": converted / len(population), "main_rate": main_buyers / len(population),
        "impulse_rate": impulse_buyers / len(population), "missing_rate": missing / len(population),
        "origin_counts": origins, "population": [asdict(npc) for npc in population],
        "elapsed_ms": round((time.perf_counter() - started) * 1000),
    }


def _path_position(path: list[dict], travelled: float) -> dict:
    remaining = travelled
    for index in range(1, len(path)):
        length = distance(path[index - 1], path[index])
        if remaining <= length:
            ratio = remaining / length if length else 1
            return {"x": path[index - 1]["x"] + (path[index]["x"] - path[index - 1]["x"]) * ratio,
                    "y": path[index - 1]["y"] + (path[index]["y"] - path[index - 1]["y"]) * ratio}
        remaining -= length
    return dict(path[-1])


def position_at(agent: dict, timestamp: float) -> Optional[dict]:
    if timestamp < agent["spawn"] or timestamp > agent["end"]:
        return None
    segment = next((s for s in agent["segments"] if s["t0"] <= timestamp <= s["t1"]), agent["segments"][-1])
    if "path" in segment:
        ratio = clamp((timestamp - segment["t0"]) / max(.001, segment["t1"] - segment["t0"]), 0, 1)
        point = _path_position(segment["path"], _path_length(segment["path"]) * ratio)
    else:
        point = dict(segment["point"])
    return {"x": point["x"] + agent["offset"]["x"], "y": point["y"] + agent["offset"]["y"],
            "status": segment["status"], "valence": agent["valence"]}


def validate(layout: dict, catalog: list[dict]) -> list[tuple[str, str]]:
    issues = []
    if not layout.get("entrance"):
        issues.append(("error", "Thieu loi vao"))
    if not layout.get("checkout"):
        issues.append(("error", "Thieu quay thu ngan"))
    if not layout.get("shelves"):
        issues.append(("error", "Chua co ke hang"))
    if not catalog:
        issues.append(("error", "Catalog dang trong"))
    shelf_ids = {s["id"] for s in layout.get("shelves", [])}
    invalid = [p for p in catalog if p.get("shelf") not in shelf_ids]
    if invalid:
        issues.append(("warning", f"{len(invalid)} san pham chua gan ke hop le"))
    return issues
