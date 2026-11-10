#!/usr/bin/env python3
"""
Simple test script for the Food Source Generation System.
"""

import sys
import os
import time
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.food import FoodSource, FoodManager

NEST = (400.0, 300.0)
WORLD = (0, 0, 1200, 800)

def test_food_source():
    """Test basic FoodSource functionality."""
    print("Testing FoodSource...")
    
    # Create a food source
    food = FoodSource(position=(100, 100), amount=50.0, max_amount=100.0)
    
    # Test properties
    assert food.position == (100, 100)
    assert food.amount == 50.0
    assert food.max_amount == 100.0
    assert not food.is_depleted
    assert food.depletion_percentage == 50.0
    
    # Test food collection
    collected = food.collect_food(10.0)
    assert collected == 10.0
    assert food.amount == 40.0
    
    # Test depletion
    food.collect_food(40.0)
    assert food.is_depleted
    assert food.amount == 0.0
    
    print("✓ FoodSource tests passed!")

def test_food_manager():
    """Test FoodManager functionality."""
    print("Testing FoodManager...")
    
    # Create food manager
    manager = FoodManager(world_bounds=(0, 0, 800, 600))
    
    # Generate random food
    manager.generate_random_food(num_sources=5, min_amount=30.0, max_amount=80.0)
    
    # Test statistics. get_statistics reports available_sources.
    stats = manager.get_statistics()
    assert stats['total_sources'] == 5
    assert stats['available_sources'] == 5
    for food in manager._food_sources:
        assert food.expires is True
        assert food.patch_id is None
    
    # Test nearest food finding
    nearest = manager.get_nearest_food((400, 300))
    assert nearest is not None
    
    # Print all food source positions and distances to (400, 300)
    print("Generated food sources and distances to (400, 300):")
    for food in manager._food_sources:
        dist = food.distance_to((400, 300))
        print(f"  Food at {food.position} (distance: {dist:.2f})")
    
    # Test food in range (should not assert on count due to randomness)
    food_in_range = manager.get_food_in_range((400, 300), 100.0)
    print(f"Number of food sources within 100 units: {len(food_in_range)}")
    
    print("✓ FoodManager tests passed!")

def test_spatial_queries():
    """Test spatial query performance."""
    print("Testing spatial queries...")
    
    manager = FoodManager(world_bounds=(0, 0, 800, 600))
    
    # Add food sources at known positions
    manager.add_food_source((100, 100), 50.0)
    manager.add_food_source((200, 200), 50.0)
    manager.add_food_source((300, 300), 50.0)
    
    # Test nearest food
    nearest = manager.get_nearest_food((150, 150))
    assert nearest is not None
    assert nearest.position == (100, 100)  # Should be closest
    
    # Print distances to all food sources
    print("Distances from (150, 150) to all food sources:")
    for food in manager._food_sources:
        dist = food.distance_to((150, 150))
        in_range = dist <= 60.0
        print(f"  Food at {food.position} (distance: {dist:.2f}) - {'IN RANGE' if in_range else 'OUT OF RANGE'}")
    
    # Test food in range
    food_in_range = manager.get_food_in_range((150, 150), 60.0)
    print("Food sources within 60 units of (150, 150):")
    for food in food_in_range:
        dist = food.distance_to((150, 150))
        print(f"  Food at {food.position} (distance: {dist:.2f})")
    assert len(food_in_range) == 0  # None are within 60 units
    print("✓ Spatial query tests passed!")

def _assert_patch_layout(manager, nest):
    """Clump geometry: four separated patches, morsels inside each clump and off the nest."""
    assert manager.num_patches == 4
    assert manager.morsels_per_patch == 6
    assert manager.patch_sigma == 36.0
    assert manager.min_morsel_spacing == 18.0
    assert manager.min_patch_separation == 280.0
    assert manager.min_nest_distance == 180.0
    assert manager.morsel_amount == (40.0, 80.0)
    assert manager.patch_respawn_delay == 25.0
    assert len(manager._patches) == 4
    assert len(manager._food_sources) == 24

    left, top, right, bottom = manager._playfield_bounds()
    assert right <= 820.0
    centers = []
    for patch in manager._patches:
        assert len(patch["source_ids"]) == 6
        center = patch["center"]
        assert center[0] <= 820.0
        assert left <= center[0] <= right
        assert top <= center[1] <= bottom
        assert np.hypot(center[0] - nest[0], center[1] - nest[1]) >= manager.min_nest_distance - 1e-6
        centers.append(center)
        morsels = [manager._sources_by_id[source_id] for source_id in patch["source_ids"]]
        for morsel in morsels:
            assert morsel.patch_id == patch["id"]
            assert morsel.expires is False
            assert morsel.is_available
            low, high = manager.morsel_amount
            assert low <= morsel.amount <= high
            assert morsel.distance_to(center) <= 3.0 * manager.patch_sigma + 1e-6
            assert morsel.distance_to(nest) >= manager.min_nest_distance - 1e-6
            x, y = morsel.position
            assert left <= x <= right
            assert top <= y <= bottom
            assert x <= 820.0
        for index, morsel in enumerate(morsels):
            for other in morsels[index + 1:]:
                assert morsel.distance_to(other.position) >= manager.min_morsel_spacing - 1e-6
    for index, center in enumerate(centers):
        for other in centers[index + 1:]:
            gap = np.hypot(center[0] - other[0], center[1] - other[1])
            assert gap >= manager.min_patch_separation - 1e-6

def test_forage_patch_layout():
    """generate_patches yields four clumps of six morsels on the open playfield."""
    print("Testing forage patch layout...")
    for seed in range(8):
        np.random.seed(seed)
        manager = FoodManager(world_bounds=WORLD)
        manager.generate_patches(NEST)
        _assert_patch_layout(manager, NEST)
    print("✓ Forage patch layout tests passed!")

def test_patch_depletion_and_respawn():
    """An eaten clump stays empty through 24s, then reappears somewhere else."""
    print("Testing patch depletion and respawn...")
    for seed in range(6):
        np.random.seed(seed)
        manager = FoodManager(world_bounds=WORLD)
        manager.generate_patches(NEST)
        patch = manager._patches[0]
        patch_id = patch["id"]
        old_center = tuple(patch["center"])
        old_ids = list(patch["source_ids"])
        old_positions = {
            source_id: tuple(manager._sources_by_id[source_id].position)
            for source_id in old_ids
        }
        other_centers = {
            other["id"]: tuple(other["center"])
            for other in manager._patches
            if other["id"] != patch_id
        }

        for source_id in old_ids:
            source = manager._sources_by_id[source_id]
            collected = source.collect_food(source.amount)
            assert collected > 0.0
            assert source.amount == 0.0
            assert source.is_depleted
            assert not source.is_available

        manager.update_all(10.0)
        manager.update_all(14.0)
        patch = next(item for item in manager._patches if item["id"] == patch_id)
        assert tuple(patch["center"]) == old_center
        assert abs(patch["empty_for"] - 24.0) < 1e-6
        assert list(patch["source_ids"]) == old_ids
        assert len(manager._food_sources) == 24
        for source_id, position in old_positions.items():
            source = manager._sources_by_id[source_id]
            assert source.amount == 0.0
            assert tuple(source.position) == position
            assert not source.is_available

        manager.update_all(1.0)
        patch = next(item for item in manager._patches if item["id"] == patch_id)
        new_center = tuple(patch["center"])
        moved = np.hypot(new_center[0] - old_center[0], new_center[1] - old_center[1])
        assert new_center != old_center
        assert moved >= 2.0 * manager.patch_sigma - 1e-6
        assert new_center[0] <= 820.0
        assert set(patch["source_ids"]).isdisjoint(old_ids)
        assert len(patch["source_ids"]) == 6
        for source_id in patch["source_ids"]:
            source = manager._sources_by_id[source_id]
            nearby = manager.get_food_in_range(source.position, 0.0)
            assert source in nearby
        for source_id in old_ids:
            assert source_id not in manager._sources_by_id
        for other_id, center in other_centers.items():
            other = next(item for item in manager._patches if item["id"] == other_id)
            assert tuple(other["center"]) == center
            gap = np.hypot(new_center[0] - other["center"][0], new_center[1] - other["center"][1])
            assert gap >= manager.min_patch_separation - 1e-6
        _assert_patch_layout(manager, NEST)
    print("✓ Patch depletion and respawn tests passed!")

def test_no_immortal_piles_or_inplace_refill():
    """The three static piles are gone, and an eaten morsel does not refill where it was."""
    print("Testing removal of immortal piles and in-place refill...")
    main_path = os.path.join(os.path.dirname(__file__), "src", "main.py")
    with open(main_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    assert "food_sources = [" not in source
    for position in ("(600, 150)", "(700, 400)", "(300, 450)"):
        assert position not in source

    morsel = FoodSource((500, 200), amount=60.0, max_amount=60.0, expires=False, patch_id=1)
    morsel.collect_food(60.0)
    morsel._last_refresh_time = time.time() - 10000.0
    morsel._spawn_time = time.time() - 10000.0
    morsel.update(120.0)
    assert morsel.amount == 0.0
    assert morsel.is_depleted
    assert not morsel.is_available

    np.random.seed(2)
    manager = FoodManager(world_bounds=WORLD)
    assert manager.distribution == "patches"
    manager.update_all(2.0)
    assert manager._food_sources == []

    manager.generate_patches(NEST)
    for food in manager._food_sources:
        available = len([item for item in manager._food_sources if item.is_available])
        if available < manager.num_food_sources // 2:
            break
        food.collect_food(food.amount)
    before = len(manager._food_sources)
    positions = [tuple(food.position) for food in manager._food_sources]
    manager.update_all(1.0)
    assert len(manager._food_sources) == before
    assert [tuple(food.position) for food in manager._food_sources] == positions
    assert all(food.patch_id is not None and food.expires is False for food in manager._food_sources)
    print("✓ Immortal pile and in-place refill tests passed!")

if __name__ == "__main__":
    print("Running Food System Tests...\n")
    
    try:
        test_food_source()
        test_food_manager()
        test_spatial_queries()
        test_forage_patch_layout()
        test_patch_depletion_and_respawn()
        test_no_immortal_piles_or_inplace_refill()
        
        print("\n🎉 All tests passed! Food system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 