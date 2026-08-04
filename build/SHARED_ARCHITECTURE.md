# AIsle dual-surface architecture

## Design model

Bản thiết kế lại kết hợp hai mẫu tham khảo:

- Working Model 2D: workspace object-centric, inspector thuộc tính, transport `Run / Pause / Reset / Single step`, timeline và output đo lường trong cùng ngữ cảnh.
- The Sims: environment-driven Utility AI. Kệ là “smart object” quảng bá category, valence và sản phẩm; mỗi NPC tự chấm utility theo need, explore, novelty và travel cost rồi tạo action queue.

## Shared live core

```text
Desktop Edge App Mode ─┐
                       ├── web/live-engine.js ── Node.js storage host
Web browser ────────────┘
```

`web/live-engine.js` không phụ thuộc DOM hoặc Canvas. Hai bề mặt dùng chung:

- `generatePopulation()` cho GA population.
- `manualPopulation()` cho test case nhập tay.
- `LiveSimulation.step()` cho utility, A*, emotion, purchase và collision từng tick.
- `snapshot()` cho KPI trực tiếp tại đúng thời điểm đang hiển thị.

Python `core.py` và Tkinter app được giữ lại làm legacy/reference, không còn là runtime mặc định.

## Manual NPC schema

| Field | Range | Meaning |
|---|---:|---|
| `npc_id` | unique text | Stable test identity |
| `target_category` | catalog category or missing category | Purchase intent |
| `need_product` | 0..1 | Initial product need |
| `need_growth` | 0..0.05 | Product need growth per minute |
| `need_explore` | 0..1 | Exploration drive |
| `explore_growth` | 0..0.04 | Exploration growth per minute |
| `attractor` | -1..1 | Baseline valence |
| `stability` | 0..1 | Resistance to environment |
| `dispersion` | 0..1 | Response amplitude |
| `recovery` | 0..0.5 | Recovery rate |
| `speed` | 0.65..1.9 m/s | Walk speed |
| `dwell` | 3..24 s | Shelf patience |
| `steadiness` | 0.2..1 | Movement steadiness |

Values outside ranges are clamped. Duplicate NPC IDs are rejected so tests and replay remain traceable.
