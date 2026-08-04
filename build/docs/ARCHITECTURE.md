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

## Spawn process

`layout.spawnRateCurve` is a list of `{minute, rate}` points, where `rate` is measured in arrivals per minute. The engine linearly interpolates the curve and samples a seeded non-homogeneous Poisson process with thinning. A fixed simulation seed therefore reproduces the same arrivals. Legacy layouts without a curve use the previous sine-shaped peak as a rate profile, normalized to the requested population size.

The shipped default curve is a design constant for the proof of concept, not a rate measured from a real store. NPCs with no accepted arrival before the configured duration remain unspawned, which is the expected behavior when a layout's rate curve has less capacity than the supplied population.

## Layout validation

Saving requires both `entrance` and `checkout` points. Shelf reachability is checked from the entrance with the same `PathGrid` and shelf access-point rules as the live engine. Missing required markers returns HTTP 400 and blocks persistence; unreachable shelves are returned as warnings and do not block saving.

## Performance baseline

Task 1.4 benchmark command: `node tests/benchmark.mjs`. On 2026-08-04 with Node.js 24 on the development Windows machine, two runs of 200 NPCs over 3,600 one-second ticks completed in **562-661 ms** (**0.156-0.184 ms/tick**), with all 200 NPCs spawned. This is comfortably below the 3-5 second optimization threshold, so the current pairwise separation and uncached shelf path evaluation remain in place. Spatial hashing and path caching should only be introduced after a future benchmark crosses that threshold, to avoid cache invalidation risk when layouts change.
