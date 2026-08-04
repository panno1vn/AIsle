import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core import (DEFAULT_CATALOG, DEFAULT_LAYOUT, generate_population,
                  population_from_input, position_at, run_simulation, validate)


class CoreTests(unittest.TestCase):
    def test_population_distribution_and_bounds(self):
        population = generate_population(DEFAULT_CATALOG, 10_000, seed=42)
        counts = {}
        for npc in population:
            counts[npc.origin] = counts.get(npc.origin, 0) + 1
            self.assertLessEqual(.65, npc.speed)
            self.assertLessEqual(npc.speed, 1.9)
            self.assertLessEqual(0, npc.need_product)
            self.assertLessEqual(npc.need_product, 1)
        self.assertLess(abs(counts["catalog_sampled"] / 10_000 - .80), .03)
        self.assertLess(abs(counts["crossover_inherited"] / 10_000 - .10), .03)
        self.assertLess(abs(counts["phantom_mutation"] / 10_000 - .06), .02)
        self.assertLess(abs(counts["no_intent_mutation"] / 10_000 - .04), .02)

    def test_default_project_is_valid(self):
        self.assertEqual(validate(DEFAULT_LAYOUT, DEFAULT_CATALOG), [])

    def test_simulation_end_to_end(self):
        population = generate_population(DEFAULT_CATALOG, 150, seed=7)
        result = run_simulation(copy.deepcopy(DEFAULT_LAYOUT), copy.deepcopy(DEFAULT_CATALOG), population, 5, seed=7)
        self.assertEqual(len(result["agents"]), 150)
        self.assertLessEqual(0, result["conversion_rate"])
        self.assertLessEqual(result["conversion_rate"], 1)
        self.assertGreaterEqual(result["revenue"], 0)
        self.assertTrue(all(agent["segments"] for agent in result["agents"]))
        self.assertTrue(all(position_at(agent, agent["spawn"] + .01) for agent in result["agents"]))

    def test_manual_npc_input_runs_through_same_core(self):
        population = population_from_input([
            {"npc_id": "tester", "target_category": "beverage", "need_product": .95,
             "need_explore": .1, "speed": 1.4, "dwell": 6},
        ])
        result = run_simulation(copy.deepcopy(DEFAULT_LAYOUT), copy.deepcopy(DEFAULT_CATALOG), population, 5, seed=11)
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["origin_counts"]["manual_input"], 1)
        self.assertEqual(result["agents"][0]["id"], "tester")

    def test_manual_npc_ids_must_be_unique(self):
        with self.assertRaises(ValueError):
            population_from_input([{"npc_id": "same"}, {"npc_id": "same"}])


if __name__ == "__main__":
    unittest.main()
