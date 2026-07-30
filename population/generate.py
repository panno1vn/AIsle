"""
Sinh quần thể NPC bằng crossover + mutation từ gen gốc — mục 3 đặc tả kỹ thuật.

Tỷ lệ target_category_origin (mục 3.3, đã sửa theo A2 — chỉ kiểm tra ±3% ở
n=10.000 trong unit test, KHÔNG kiểm tra tỷ lệ này trên quần thể 200 thật vì
sai số chuẩn ở n=200 đã ~2.8%, code đúng vẫn trượt ngưỡng ~28% số lần chạy):

    catalog_sampled       80%   — target lấy từ 1 category có thật trong catalog
    crossover_inherited   10%   — target thừa hưởng từ 1 trong 2 "cha mẹ" khi lai
    phantom_mutation        6%   — target là category KHÔNG có thật trong catalog
    no_intent_mutation      4%   — không có target (target_category = None)

Gen gốc mặc định dưới đây (GEN_GOC_MAC_DINH) là do nhóm tự gán tay — thay thế
cho việc trích từ video thật (Phần D, không trên đường găng). Khi có dữ liệu
video/gán tay thật, truyền vào tham số `gen_goc` của generate_population().
"""
from __future__ import annotations

import random

from engine.models import NPC, Emotion, Genome, Movement, Need, NPCState

# 5 gen gốc mẫu — mỗi cái đại diện một "kiểu khách" quan sát được ngoài đời,
# ghi rõ trong báo cáo đây là ước lượng thủ công, không phải số đo thật.
GEN_GOC_MAC_DINH: list[Genome] = [
    Genome(  # khách vội, biết rõ mình cần gì
        need=Need(0.72, 0.02, 0.15, 0.01, None, "seed_manual"),
        emotion=Emotion(attractor=0.30, stability=0.65, dispersion=0.35, recovery_rate=0.18),
        movement=Movement(walk_speed=1.35, dwell_patience=4.5, movement_steadiness=0.75),
    ),
    Genome(  # khách dạo, thích khám phá
        need=Need(0.25, 0.01, 0.65, 0.02, None, "seed_manual"),
        emotion=Emotion(attractor=0.40, stability=0.45, dispersion=0.55, recovery_rate=0.10),
        movement=Movement(walk_speed=0.85, dwell_patience=9.0, movement_steadiness=0.50),
    ),
    Genome(  # khách trung tính, cân bằng
        need=Need(0.45, 0.015, 0.40, 0.015, None, "seed_manual"),
        emotion=Emotion(attractor=0.35, stability=0.55, dispersion=0.45, recovery_rate=0.14),
        movement=Movement(walk_speed=1.05, dwell_patience=6.0, movement_steadiness=0.62),
    ),
    Genome(  # khách dễ cáu, kiên nhẫn thấp
        need=Need(0.55, 0.025, 0.20, 0.01, None, "seed_manual"),
        emotion=Emotion(attractor=0.10, stability=0.35, dispersion=0.60, recovery_rate=0.08),
        movement=Movement(walk_speed=1.20, dwell_patience=3.0, movement_steadiness=0.55),
    ),
    Genome(  # khách dễ tính, kiên nhẫn cao
        need=Need(0.35, 0.01, 0.35, 0.02, None, "seed_manual"),
        emotion=Emotion(attractor=0.55, stability=0.75, dispersion=0.30, recovery_rate=0.20),
        movement=Movement(walk_speed=0.95, dwell_patience=8.0, movement_steadiness=0.80),
    ),
]

ORIGIN_WEIGHTS = [
    ("catalog_sampled", 0.80),
    ("crossover_inherited", 0.10),
    ("phantom_mutation", 0.06),
    ("no_intent_mutation", 0.04),
]

PHANTOM_CATEGORIES = ["ice_cream", "toys", "electronics", "flowers"]  # category KHÔNG có trong catalog mẫu
MUTATION_RATE = 0.12  # biên độ nhiễu khi mutate (12% giá trị gốc)


def _roll_origin(rng: random.Random) -> str:
    r = rng.random()
    cum = 0.0
    for origin, w in ORIGIN_WEIGHTS:
        cum += w
        if r < cum:
            return origin
    return ORIGIN_WEIGHTS[-1][0]


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _crossover_need(a: Need, b: Need, rng: random.Random) -> Need:
    """Lai 2 gen gốc: mỗi trường số lấy trung bình có nhiễu nhẹ; target lấy từ 1 trong 2 cha mẹ."""
    return Need(
        need_product_initial=_clamp((a.need_product_initial + b.need_product_initial) / 2),
        need_product_growth_rate=max(0.0, (a.need_product_growth_rate + b.need_product_growth_rate) / 2),
        need_explore_initial=_clamp((a.need_explore_initial + b.need_explore_initial) / 2),
        need_explore_growth_rate=max(0.0, (a.need_explore_growth_rate + b.need_explore_growth_rate) / 2),
        target_category=rng.choice([a.target_category, b.target_category]),
        target_category_origin="crossover_inherited",
    )


def _crossover_emotion(a: Emotion, b: Emotion) -> Emotion:
    return Emotion(
        attractor=_clamp((a.attractor + b.attractor) / 2, -1, 1),
        stability=_clamp((a.stability + b.stability) / 2),
        dispersion=_clamp((a.dispersion + b.dispersion) / 2),
        recovery_rate=_clamp((a.recovery_rate + b.recovery_rate) / 2),
    )


def _crossover_movement(a: Movement, b: Movement) -> Movement:
    return Movement(
        walk_speed=max(0.1, (a.walk_speed + b.walk_speed) / 2),
        dwell_patience=max(0.5, (a.dwell_patience + b.dwell_patience) / 2),
        movement_steadiness=_clamp((a.movement_steadiness + b.movement_steadiness) / 2),
    )


def _mutate_numeric(x: float, rng: random.Random, lo: float = 0.0, hi: float = 1.0) -> float:
    noise = rng.uniform(-MUTATION_RATE, MUTATION_RATE) * (hi - lo if hi > lo else 1.0)
    return _clamp(x + noise, lo, hi)


def _mutate_genome(g: Genome, rng: random.Random) -> Genome:
    """Nhiễu nhẹ toàn bộ trường số của 1 genome, giữ nguyên target_category gốc
    (việc đổi target_category do _roll_origin quyết định riêng, không nằm ở đây)."""
    n = g.need
    e = g.emotion
    m = g.movement
    return Genome(
        need=Need(
            need_product_initial=_mutate_numeric(n.need_product_initial, rng),
            need_product_growth_rate=max(0.0, n.need_product_growth_rate + rng.uniform(-0.005, 0.005)),
            need_explore_initial=_mutate_numeric(n.need_explore_initial, rng),
            need_explore_growth_rate=max(0.0, n.need_explore_growth_rate + rng.uniform(-0.005, 0.005)),
            target_category=n.target_category,
            target_category_origin=n.target_category_origin,
        ),
        emotion=Emotion(
            attractor=_mutate_numeric(e.attractor, rng, -1, 1),
            stability=_mutate_numeric(e.stability, rng),
            dispersion=_mutate_numeric(e.dispersion, rng),
            recovery_rate=_mutate_numeric(e.recovery_rate, rng),
        ),
        movement=Movement(
            walk_speed=max(0.1, m.walk_speed + rng.uniform(-0.15, 0.15)),
            dwell_patience=max(0.5, m.dwell_patience + rng.uniform(-1.0, 1.0)),
            movement_steadiness=_mutate_numeric(m.movement_steadiness, rng),
        ),
    )


def _gan_target_theo_origin(genome: Genome, origin: str, catalog: list[dict], rng: random.Random) -> Genome:
    """Ghi đè target_category + origin lên 1 genome đã lai/mutate, theo tỷ lệ đã roll."""
    categories_that_exist = sorted({p["category"] for p in catalog}) or ["beverage"]

    if origin == "catalog_sampled":
        target = rng.choice(categories_that_exist)
    elif origin == "phantom_mutation":
        target = rng.choice(PHANTOM_CATEGORIES)
    elif origin == "no_intent_mutation":
        target = None
    else:  # crossover_inherited: giữ nguyên target đã có từ bước _crossover_need
        target = genome.need.target_category
        if target is None:
            target = rng.choice(categories_that_exist)  # phòng khi cả 2 cha mẹ đều None

    genome.need.target_category = target
    genome.need.target_category_origin = origin
    return genome


def generate_population(
    n: int,
    catalog: list[dict],
    gen_goc: list[Genome] | None = None,
    seed: int | None = None,
) -> list[NPC]:
    """Sinh n NPC bằng crossover ngẫu nhiên 2 gen gốc + mutation, gán target_category
    theo đúng tỷ lệ ORIGIN_WEIGHTS. Đây là hàm chính của Tuần 2 (mục 3.5)."""
    rng = random.Random(seed)
    seeds = GEN_GOC_MAC_DINH if gen_goc is None else gen_goc
    if len(seeds) < 2:
        raise ValueError("Cần ít nhất 2 gen gốc để crossover (mục 3.2/3.4).")

    npcs: list[NPC] = []
    for i in range(n):
        cha, me = rng.sample(seeds, 2)
        lai = Genome(
            need=_crossover_need(cha.need, me.need, rng),
            emotion=_crossover_emotion(cha.emotion, me.emotion),
            movement=_crossover_movement(cha.movement, me.movement),
        )
        lai = _mutate_genome(lai, rng)

        origin = _roll_origin(rng)
        lai = _gan_target_theo_origin(lai, origin, catalog, rng)

        state = NPCState(
            position=[0.0, 0.0],
            current_need_product=lai.need.need_product_initial,
            current_need_explore=lai.need.need_explore_initial,
            current_valence=lai.emotion.attractor,
            status="TRANSIT",
        )
        npcs.append(NPC(npc_id=f"npc_{i:04d}", genome=lai, state=state))

    return npcs
