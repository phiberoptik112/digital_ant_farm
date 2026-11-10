#!/usr/bin/env python3
"""Headless checks for the pheromone concentration field.

The field obeys ∂C/∂t = S + D ∇²C − λ C. These tests inject dt. They do not
sleep on the wall clock, and they do not treat the retired per-frame
subtraction or the 8-blob burst as the specification.
"""

import math
import os
import sys
import traceback

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from entities.ant import Ant, AntState
from entities.pheromone import (
    DEFAULT_FOOD_Q,
    DEFAULT_FOLLOWER_THRESHOLD,
    DEFAULT_HOME_Q,
    FOOD_HALF_LIFE_SECONDS,
    PheromoneManager,
    PheromoneType,
)


WORLD = (0, 0, 800, 600)
FOOD = PheromoneType.FOOD_TRAIL
HOME = PheromoneType.HOME_TRAIL


def _manager(**kwargs):
    return PheromoneManager(world_bounds=WORLD, **kwargs)


def _close(actual, expected, tolerance=1e-8):
    scale = max(1.0, abs(expected))
    if abs(actual - expected) > tolerance * scale:
        raise AssertionError(f"expected {expected}, got {actual}")


def test_exponential_half_life():
    """Evaporation is C0 * exp(-λ t), and half-life does not depend on C0."""
    print("Testing exponential half-life...")
    lam = 0.25
    manager = _manager(diffusion=0.0, epsilon=0.0)
    manager.set_decay_rate(FOOD, lam)
    low = (120.0, 180.0)
    high = (420.0, 180.0)
    c_low = 8.0
    c_high = 40.0
    manager.deposit(low, FOOD, c_low)
    manager.deposit(high, FOOD, c_high)

    elapsed = 3.5
    manager.update_all(elapsed)
    _close(manager.concentration(low, FOOD), c_low * math.exp(-lam * elapsed))
    _close(manager.concentration(high, FOOD), c_high * math.exp(-lam * elapsed))

    # A second pair reaches half of its own start at the same t = ln(2)/λ.
    other = _manager(diffusion=0.0, epsilon=0.0)
    other.set_decay_rate(FOOD, lam)
    other.deposit(low, FOOD, c_low)
    other.deposit(high, FOOD, c_high)
    half_life = math.log(2.0) / lam
    other.update_all(half_life)
    _close(other.concentration(low, FOOD), c_low / 2.0)
    _close(other.concentration(high, FOOD), c_high / 2.0)

    # Many short steps match one step of the same simulated time.
    stepped = _manager(diffusion=0.0, epsilon=0.0)
    stepped.set_decay_rate(FOOD, lam)
    stepped.deposit(low, FOOD, c_low)
    for _ in range(60):
        stepped.update_all(elapsed / 60.0)
    _close(stepped.concentration(low, FOOD), c_low * math.exp(-lam * elapsed), tolerance=1e-8)
    print("✓ Exponential half-life passed")


def test_diffusion_conserves_mass_and_widens():
    """Diffusion moves mass into neighbors. The grid sum does not grow."""
    print("Testing mass-conserving diffusion...")
    manager = _manager(diffusion=20.0, epsilon=0.0)
    manager.set_decay_rate(FOOD, 0.0)
    manager.set_decay_rate(HOME, 0.0)
    source = (402.0, 303.0)
    manager.deposit(source, FOOD, 50.0)
    before = manager.total_mass(FOOD)
    peak_before = manager.peak(FOOD)
    cells_before = manager.get_statistics()["type_counts"][FOOD.name]
    assert cells_before == 1
    assert peak_before == 50.0

    manager.update_all(0.4)

    after = manager.total_mass(FOOD)
    field = manager._fields[FOOD]
    _close(after, before, tolerance=1e-6)
    assert field.min() >= 0.0
    assert manager.peak(FOOD) < peak_before
    assert manager.get_statistics()["type_counts"][FOOD.name] > cells_before

    # A large D is substepped: still no negatives and no new mass.
    hot = _manager(diffusion=800.0, epsilon=0.0)
    hot.set_decay_rate(FOOD, 0.0)
    hot.deposit(source, FOOD, 30.0)
    hot_before = hot.total_mass(FOOD)
    hot.update_all(1.0)
    assert hot._fields[FOOD].min() >= 0.0
    assert hot.total_mass(FOOD) <= hot_before + 1e-6
    _close(hot.total_mass(FOOD), hot_before, tolerance=1e-5)

    # Diffusion plus evaporation cannot increase the integral when nobody deposits.
    mixed = _manager(diffusion=10.0, epsilon=0.0)
    mixed.set_decay_rate(FOOD, 0.2)
    mixed.deposit(source, FOOD, 25.0)
    mixed_before = mixed.total_mass(FOOD)
    mixed.update_all(0.5)
    assert mixed.total_mass(FOOD) < mixed_before
    assert mixed._fields[FOOD].min() >= 0.0
    print("✓ Mass-conserving diffusion passed")


def test_additive_same_cell_deposits():
    """Two deposits in one cell sum, and a second pass raises the trail."""
    print("Testing additive same-cell deposits...")
    stacked = _manager(diffusion=0.0, epsilon=0.0)
    once = _manager(diffusion=0.0, epsilon=0.0)
    position = (150.0, 240.0)
    stacked.deposit(position, FOOD, 2.5)
    stacked.deposit(position, FOOD, 4.0)
    once.deposit(position, FOOD, 6.5)
    _close(stacked.concentration(position, FOOD), 6.5)
    _close(stacked.concentration(position, FOOD), once.concentration(position, FOOD))

    capped = _manager(diffusion=0.0, epsilon=0.0, saturation=5.0)
    capped.deposit(position, FOOD, 4.0)
    capped.deposit(position, FOOD, 4.0)
    _close(capped.concentration(position, FOOD), 5.0)

    trail = _manager(diffusion=0.0, epsilon=0.0)
    start = (120.0, 303.0)
    end = (180.0, 303.0)
    trail.deposit_segment(start, end, FOOD, 1.0)
    first = trail.concentration((150.0, 303.0), FOOD)
    assert first > 0.0
    trail.deposit_segment(start, end, FOOD, 1.0)
    second = trail.concentration((150.0, 303.0), FOOD)
    assert second > first
    _close(second, first * 2.0)
    print("✓ Additive same-cell deposits passed")


def test_segment_is_continuous_and_stationary_adds_nothing():
    """A constant-speed walk leaves a gap-free band. Standing still does not pile up."""
    print("Testing continuous deposition...")
    manager = _manager(diffusion=0.0, epsilon=0.0)
    manager.set_decay_rate(HOME, 0.0)
    y = 303.0
    ant = Ant(position=(48.0, y), orientation=0.0)
    ant.set_pheromone_manager(manager)
    ant.set_state(AntState.SEARCHING)
    ant._velocity = 2.0
    ant._max_velocity = 2.0
    velocity = 2.0
    for _ in range(120):
        previous = ant.position
        ant.move(velocity)
        added = ant.deposit_along_path(previous, ant.position, HOME, DEFAULT_HOME_Q)
        _close(added, DEFAULT_HOME_Q * velocity, tolerance=1e-6)

    row = manager._fields[HOME][int(y / manager.cell_size)]
    ix0 = int(52.0 / manager.cell_size)
    ix1 = int((ant.position[0] - 4.0) / manager.cell_size)
    assert ix1 - ix0 > 20
    assert np.all(row[ix0:ix1] > 0.0)
    # The retired pulse was velocity * 30 frames, about 60 px, which is 10 cells.
    assert ix1 - ix0 > 10

    still = ant.position
    before = manager.total_mass(HOME)
    added = ant.deposit_along_path(still, still, HOME, DEFAULT_HOME_Q)
    assert added == 0.0
    _close(manager.total_mass(HOME), before)
    print("✓ Continuous deposition passed")


def test_uniform_trail_is_not_fresher_at_the_nest():
    """A trail laid at one instant is flat along its length after evaporation."""
    print("Testing along-trail freshness...")
    manager = _manager(diffusion=0.0, epsilon=0.0)
    manager.set_decay_rate(FOOD, 0.05)
    nest_x = 220.0
    food_x = 520.0
    y = 303.0
    manager.deposit_segment((food_x + 40.0, y), (nest_x - 40.0, y), FOOD, DEFAULT_FOOD_Q)
    near_nest = manager.concentration((nest_x, y), FOOD)
    near_food = manager.concentration((food_x, y), FOOD)
    assert near_nest > 0.0 and near_food > 0.0
    _close(near_nest, near_food, tolerance=1e-6)
    manager.update_all(5.0)
    evaporated_nest = manager.concentration((nest_x, y), FOOD)
    evaporated_food = manager.concentration((food_x, y), FOOD)
    _close(evaporated_nest, evaporated_food, tolerance=1e-6)
    assert evaporated_nest < near_nest
    assert evaporated_nest <= evaporated_food * 1.01
    print("✓ Along-trail freshness passed")


def test_default_lifetime_and_no_mass_burst():
    """Default λ outlives the old ~1.3 s blob, and nothing adds an 8-blob burst."""
    print("Testing default lifetime and no delayed burst...")
    lam = math.log(2.0) / FOOD_HALF_LIFE_SECONDS
    short = _manager()
    assert abs(short.decay_rate(FOOD) - lam) < 1e-12
    cell = short.cell_size
    y = 303.0
    added = short.deposit_segment((200.0, y), (200.0 + cell, y), FOOD, DEFAULT_FOOD_Q)
    _close(added, DEFAULT_FOOD_Q * cell, tolerance=1e-6)
    initial = short.total_mass(FOOD)
    short.update_all(1.3)
    assert short.total_mass(FOOD) > initial * 0.9
    assert short.peak(FOOD) > short.follower_threshold

    ten = _manager()
    ten.deposit_segment((200.0, y), (200.0 + cell, y), FOOD, DEFAULT_FOOD_Q)
    ten.update_all(10.0)
    assert ten.peak(FOOD) > DEFAULT_FOLLOWER_THRESHOLD

    late = _manager()
    late.deposit_segment((200.0, y), (200.0 + cell, y), FOOD, DEFAULT_FOOD_Q)
    late_initial = late.total_mass(FOOD)
    late.update_all(8.0 * FOOD_HALF_LIFE_SECONDS)
    assert late.peak(FOOD) <= 10.0 * late.epsilon
    assert late.total_mass(FOOD) < late_initial * 0.02

    burst = _manager()
    burst.add_pheromone(
        (300.0, 300.0),
        FOOD,
        strength=10.0,
        can_spread=True,
        spread_delay=0.0,
        spread_strength_factor=0.4,
        spread_radius=40.0,
    )
    before = burst.total_mass(FOOD)
    burst.update_all(2.5)
    assert burst.total_mass(FOOD) <= before
    assert burst.total_mass(FOOD) < before * 1.05
    print("✓ Default lifetime and no delayed burst passed")


def test_follower_stays_on_ridge_and_heads_away_from_nest():
    """A recruit at the nest walks the food trail toward the food, not back home."""
    print("Testing trail recruitment...")
    manager = _manager()
    nest = (200.0, 303.0)
    food = (600.0, 303.0)
    carrier = Ant(position=food, orientation=180.0)
    carrier.set_pheromone_manager(manager)
    carrier.set_nest_position(nest)
    carrier.set_world_bounds(WORLD)
    carrier._max_velocity = 2.0
    carrier._velocity = 2.0
    carrier._turn_speed = 45.0
    carrier._acceleration = 5.0
    for _ in range(400):
        if carrier.distance_to(nest) <= 2.0:
            break
        previous = carrier.position
        dx = nest[0] - carrier.position[0]
        dy = nest[1] - carrier.position[1]
        carrier.turn_towards(float(np.rad2deg(np.arctan2(dy, dx))))
        carrier.accelerate(carrier._max_velocity)
        carrier.move(carrier._velocity)
        carrier.deposit_along_path(previous, carrier.position, FOOD, DEFAULT_FOOD_Q)
        manager.update_all(1.0 / 60.0)
    assert carrier.distance_to(nest) <= 4.0
    assert manager.peak(FOOD) > manager.follower_threshold

    # On the ridge, the steer vector points away from the nest (toward +x).
    on_trail = (360.0, 303.0)
    away = manager.get_pheromone_direction(
        on_trail, FOOD, radius=8.0, look_ahead=16.0, heading=0.0, nest_position=nest
    )
    assert away is not None
    assert away[0] > 0.9
    assert abs(away[1]) < 0.1

    # North of the ridge, the same rule pulls back onto it and still aims outbound.
    offset = (360.0, 309.0)
    pure_away_y = (offset[1] - nest[1]) / math.hypot(offset[0] - nest[0], offset[1] - nest[1])
    steered = manager.get_pheromone_direction(
        offset, FOOD, radius=8.0, look_ahead=16.0, heading=0.0, nest_position=nest
    )
    assert steered is not None
    assert steered[0] > 0.5
    assert steered[1] < pure_away_y

    follower = Ant(position=(230.0, 303.0), orientation=0.0)
    follower.set_pheromone_manager(manager)
    follower.set_nest_position(nest)
    follower.set_world_bounds(WORLD)
    follower.set_state(AntState.FOLLOWING_TRAIL)
    follower._food_sense_offset = 8.0
    follower._food_sensing_range = 16.0
    follower._max_velocity = 2.0
    follower._velocity = 2.0
    follower._turn_speed = 3.0
    follower._acceleration = 0.5
    reached = False
    for _ in range(500):
        previous = follower.position
        follower.step()
        follower.deposit_along_path(previous, follower.position, FOOD, DEFAULT_FOOD_Q)
        manager.update_all(1.0 / 60.0)
        if follower.distance_to(food) < 25.0:
            reached = True
            break
    assert reached, f"follower stopped at {follower.position}, state={follower.state}"
    assert follower.position[0] > 500.0
    print("✓ Trail recruitment passed")


def test_render_alpha_tracks_concentration():
    """Food stays green. Alpha follows C and is allowed to be 0."""
    print("Testing field raster...")
    empty = _manager()
    assert int(empty.rasterize()[..., 3].max()) == 0

    manager = _manager(diffusion=0.0)
    manager.set_decay_rate(FOOD, 0.0)
    position = (300.0, 303.0)
    manager.deposit(position, FOOD, 8.0)
    image = manager.rasterize()
    ix = int(position[0] / manager.cell_size)
    iy = int(position[1] / manager.cell_size)
    pixel = image[iy, ix]
    assert pixel[3] > 20
    assert pixel[1] > pixel[0]
    assert pixel[0] < 30

    faint = _manager(diffusion=0.0)
    faint.deposit(position, FOOD, 0.01)
    faint_pixel = faint.rasterize()[iy, ix]
    assert int(faint_pixel[3]) < 20
    print("✓ Field raster passed")


def main():
    tests = [
        test_exponential_half_life,
        test_diffusion_conserves_mass_and_widens,
        test_additive_same_cell_deposits,
        test_segment_is_continuous_and_stationary_adds_nothing,
        test_uniform_trail_is_not_fresher_at_the_nest,
        test_default_lifetime_and_no_mass_burst,
        test_follower_stays_on_ridge_and_heads_away_from_nest,
        test_render_alpha_tracks_concentration,
    ]
    for test in tests:
        test()
    print("\nAll pheromone field tests passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nTest failed: {exc}")
        traceback.print_exc()
        sys.exit(1)
