#!/usr/bin/env python3
"""Diffusion replaces the delayed 8-blob burst.

Spread used to spawn eight new deposits after a wall-clock delay and add
mass. These checks inject dt, do not sleep, and require the grid sum to fall
or hold while the spot widens on the first step.
"""

import os
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from entities.pheromone import PheromoneManager, PheromoneType


def test_diffusion_widens_immediately_without_creating_mass():
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600), diffusion=12.0, epsilon=0.0)
    manager.set_decay_rate(PheromoneType.FOOD_TRAIL, 0.0)
    manager.add_pheromone(
        position=(400.0, 300.0),
        pheromone_type=PheromoneType.FOOD_TRAIL,
        strength=40.0,
        can_spread=True,
        spread_radius=40.0,
        spread_strength_factor=0.4,
        spread_delay=2.0,
    )
    before = manager.total_mass(PheromoneType.FOOD_TRAIL)
    cells_before = manager.get_statistics()["type_counts"]["FOOD_TRAIL"]
    assert cells_before == 1
    assert before == 40.0

    # The old burst waited 2 seconds. Diffusion is visible on the first step.
    manager.update_all(1.0 / 60.0)
    assert manager.get_statistics()["type_counts"]["FOOD_TRAIL"] > 1
    assert manager.peak(PheromoneType.FOOD_TRAIL) < 40.0
    assert abs(manager.total_mass(PheromoneType.FOOD_TRAIL) - before) < 1e-6

    # Holding through the old delay must not multiply the deposit by 1 + 8 * 0.4.
    manager.update_all(2.0)
    assert manager.total_mass(PheromoneType.FOOD_TRAIL) <= before + 1e-6
    assert manager.total_mass(PheromoneType.FOOD_TRAIL) < before * 2.0
    assert "spread_deposits" not in manager.get_statistics()


def test_evaporation_does_not_wait_for_a_spread_clock():
    manager = PheromoneManager(world_bounds=(0, 0, 400, 400), diffusion=0.0, epsilon=0.0)
    manager.set_decay_rate(PheromoneType.FOOD_TRAIL, 0.4)
    manager.deposit((80.0, 80.0), PheromoneType.FOOD_TRAIL, 12.0)
    manager.deposit((200.0, 80.0), PheromoneType.FOOD_TRAIL, 3.0)
    manager.update_all(1.0)
    strong = manager.concentration((80.0, 80.0), PheromoneType.FOOD_TRAIL)
    weak = manager.concentration((200.0, 80.0), PheromoneType.FOOD_TRAIL)
    # Same fraction remains. The weaker mark is not deleted early by a fixed subtract.
    assert abs((strong / 12.0) - (weak / 3.0)) < 1e-9
    assert strong > 12.0 * 0.5
    assert weak > 0.0


def main():
    test_diffusion_widens_immediately_without_creating_mass()
    test_evaporation_does_not_wait_for_a_spread_clock()
    print("Diffusion checks passed. The 8-blob burst is gone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Test failed: {exc}")
        traceback.print_exc()
        sys.exit(1)
