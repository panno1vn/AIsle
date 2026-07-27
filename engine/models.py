"""
Data model cốt lõi cho kiến trúc Oxyte.
Khớp đúng schema mục 2.3 (genome) và 2.4 (Emotion & Utility) trong
ke-hoach-poc-mo-phong-khach-hang.md.

Không còn liên quan gì tới bản AIsle rule-based cũ (products.json/simulate.py cũ)
— đã bỏ hẳn theo quyết định của leader.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal, Optional


# ---------------------------------------------------------------------------
# Genome (mục 2.3)
# ---------------------------------------------------------------------------

@dataclass
class Need:
    need_product_initial: float
    need_product_growth_rate: float
    need_explore_initial: float
    need_explore_growth_rate: float
    target_category: Optional[str]
    target_category_origin: Literal[
        "seed_manual", "catalog_sampled", "crossover_inherited",
        "phantom_mutation", "no_intent_mutation",
    ]


@dataclass
class Emotion:
    attractor: float       # điểm neo cảm xúc NPC hồi phục về
    stability: float        # 0-1, càng cao càng ít dao động
    dispersion: float       # 0-1, biên độ phản ứng với zone.base_valence
    recovery_rate: float    # tốc độ hồi phục về attractor mỗi tick


@dataclass
class Movement:
    walk_speed: float             # m/s
    dwell_patience: float          # số tick tối đa chịu dừng lại 1 zone
    movement_steadiness: float     # 0-1, 1/(1+cv(v))


@dataclass
class Genome:
    need: Need
    emotion: Emotion
    movement: Movement


# ---------------------------------------------------------------------------
# State runtime (mục 2.3, phần "state")
# ---------------------------------------------------------------------------

Status = Literal["TRANSIT", "DWELL", "PURCHASED", "LEFT"]


@dataclass
class NPCState:
    position: list[float]
    current_need_product: float
    current_need_explore: float
    current_valence: float
    status: Status = "TRANSIT"
    dwell_ticks_left: int = 0
    current_zone: Optional[str] = None


@dataclass
class NPC:
    npc_id: str
    genome: Genome
    state: NPCState

    @classmethod
    def from_dict(cls, d: dict) -> "NPC":
        g = d["genome"]
        genome = Genome(
            need=Need(**g["need"]),
            emotion=Emotion(**g["emotion"]),
            movement=Movement(**g["movement"]),
        )
        s = d["state"]
        state = NPCState(
            position=list(s["position"]),
            current_need_product=s["current_need_product"],
            current_need_explore=s["current_need_explore"],
            current_valence=s["current_valence"],
            status=s.get("status", "TRANSIT"),
        )
        return cls(npc_id=d["npc_id"], genome=genome, state=state)

    def to_dict(self) -> dict:
        return {
            "npc_id": self.npc_id,
            "genome": {
                "need": vars(self.genome.need),
                "emotion": vars(self.genome.emotion),
                "movement": vars(self.genome.movement),
            },
            "state": vars(self.state),
        }


# ---------------------------------------------------------------------------
# Loaders — đọc data/*.json (mẫu giả hoặc thật, cùng 1 schema)
# ---------------------------------------------------------------------------

def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_layout(path: str) -> dict:
    """Trả về dict có 'zones' (mỗi zone có 'polygon') và 'spawn_rate_curve'."""
    return load_json(path)


def load_catalog(path: str) -> list[dict]:
    return load_json(path)["catalog"]


def load_npcs(path: str) -> list[NPC]:
    raw = load_json(path)
    return [NPC.from_dict(d) for d in raw["npcs"]]


def load_trajectory(path: str) -> list[dict]:
    return load_json(path)["trajectory_log"]