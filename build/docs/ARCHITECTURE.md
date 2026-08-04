# AIsle architecture

## Runtime flow

```text
Browser Canvas UI
  ├─ layout editor (wall, shelf, entrance, checkout)
  ├─ manual/GA population input
  └─ live render + trace
          │
          ▼
web/live-engine.js
  ├─ smart-object utility
  ├─ reachable access-point filtering
  ├─ A* navigation + hard collision
  ├─ stuck detection / replan / abandon
  └─ purchase and emotion state
          │
          ▼
backend/routes/api-router.mjs
          │
          ▼
backend/storage/project-store.mjs → runtime/*.json
```

The engine is UI-independent and deterministic for a fixed seed. The backend is intentionally small but layered: HTTP/static hosting, API routing and persistence do not share business logic.

## Smart-terrain rule

The simulation follows the object-centric idea used by The Sims: shelves advertise what need they can satisfy, while NPCs remain generic utility evaluators. Reachability is a hard prerequisite, not a utility penalty. An attractive shelf behind a sealed wall is therefore excluded rather than selected and reached through geometry.

## Navigation invariants

1. A* returns `null` when no connected route exists.
2. Diagonal movement cannot cut across a blocked corner.
3. Smoothed path segments must remain walkable from end to end.
4. Runtime movement and crowd separation re-check collision.
5. Failed routes trigger bounded replanning, then shelf abandonment and exit routing.
