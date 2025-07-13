#!/usr/bin/env python3
"""
Test script for the Pheromone System.
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.pheromone import Pheromone, PheromoneManager, PheromoneType

def test_pheromone_basic():
    """Test basic Pheromone functionality."""
    print("Testing basic Pheromone...")
    
    # Create a pheromone
    pheromone = Pheromone(position=(100, 100), pheromone_type=PheromoneType.FOOD_TRAIL, 
                         strength=50.0, decay_rate=1.0)
    
    # Test properties
    assert pheromone.position == (100, 100)
    assert pheromone.type == PheromoneType.FOOD_TRAIL
    assert pheromone.strength == 50.0
    assert pheromone.max_strength == 50.0
    assert not pheromone.age < 0  # Age should be non-negative
    
    # Test distance calculation
    distance = pheromone.distance_to((150, 150))
    expected_distance = ((150-100)**2 + (150-100)**2)**0.5
    assert abs(distance - expected_distance) < 0.01
    
    # Test influence calculation
    influence = pheromone.get_influence_strength((110, 100))  # 10 units away
    print(f"  Distance: {pheromone.distance_to((110, 100))}")
    print(f"  Radius of influence: {pheromone.radius_of_influence}")
    print(f"  Influence strength: {influence}")
    assert influence > 0  # Should have some influence
    assert influence < pheromone.strength  # Should be less than full strength
    
    print("✓ Basic Pheromone tests passed!")

def test_pheromone_decay():
    """Test pheromone decay functionality."""
    print("Testing pheromone decay...")
    
    pheromone = Pheromone(position=(100, 100), pheromone_type=PheromoneType.FOOD_TRAIL, 
                         strength=10.0, decay_rate=2.0)
    
    initial_strength = pheromone.strength
    
    # Test decay
    should_remove = pheromone.update()
    assert not should_remove  # Should not be removed yet
    assert pheromone.strength == initial_strength - 2.0
    
    # Test reinforcement
    pheromone.reinforce(5.0)
    assert pheromone.strength == pheromone.max_strength  # Should be capped at max_strength
    
    # Test complete decay
    for _ in range(10):  # Decay until strength <= 0
        should_remove = pheromone.update()
        if should_remove:
            break
    
    assert should_remove  # Should be marked for removal
    assert pheromone.strength <= 0
    
    print("✓ Pheromone decay tests passed!")

def test_pheromone_manager():
    """Test PheromoneManager functionality."""
    print("Testing PheromoneManager...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add pheromones
    pheromone1 = manager.add_pheromone((100, 100), PheromoneType.FOOD_TRAIL, strength=50.0, radius_of_influence=100.0)
    pheromone2 = manager.add_pheromone((200, 200), PheromoneType.FOOD_TRAIL, strength=30.0, radius_of_influence=100.0)
    pheromone3 = manager.add_pheromone((300, 300), PheromoneType.HOME_TRAIL, strength=40.0, radius_of_influence=100.0)
    
    # Test statistics
    stats = manager.get_statistics()
    assert stats['total_pheromones'] == 3
    assert stats['type_counts']['FOOD_TRAIL'] == 2
    assert stats['type_counts']['HOME_TRAIL'] == 1
    
    # Test pheromones in range
    food_pheromones = manager.get_pheromones_in_range((150, 150), 100.0, PheromoneType.FOOD_TRAIL)
    print("Food trail pheromones and their distances to (150, 150):")
    for p in manager._pheromones:
        if p.type == PheromoneType.FOOD_TRAIL:
            print(f"  Pheromone at {p.position}, distance: {p.distance_to((150, 150))}")
    print(f"Number of food trail pheromones in range: {len(food_pheromones)}")
    assert len(food_pheromones) == 2
    
    all_pheromones = manager.get_pheromones_in_range((150, 150), 100.0)
    assert len(all_pheromones) == 2  # Only food trail pheromones are within range
    
    # Test total strength
    total_strength = manager.get_total_strength((150, 150), PheromoneType.FOOD_TRAIL, 100.0)
    assert total_strength > 0
    
    print("✓ PheromoneManager tests passed!")

def test_gradient_calculation():
    """Test pheromone gradient direction calculation."""
    print("Testing gradient calculation...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Create a simple gradient scenario
    manager.add_pheromone((100, 100), PheromoneType.FOOD_TRAIL, strength=50.0, radius_of_influence=100.0)
    manager.add_pheromone((120, 100), PheromoneType.FOOD_TRAIL, strength=50.0, radius_of_influence=100.0)
    
    # Test gradient direction (should point towards the pheromones)
    direction = manager.get_pheromone_direction((150, 100), PheromoneType.FOOD_TRAIL, 100.0)
    assert direction is not None
    
    # Direction should point towards the pheromones (negative x direction)
    assert direction[0] < 0  # Should point left (towards pheromones)
    assert abs(direction[1]) < 0.1  # Should be mostly horizontal
    
    # Test with no pheromones
    direction = manager.get_pheromone_direction((500, 500), PheromoneType.FOOD_TRAIL, 50.0)
    assert direction is None
    
    print("✓ Gradient calculation tests passed!")

def test_spatial_indexing():
    """Test spatial indexing performance."""
    print("Testing spatial indexing...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add many pheromones
    for i in range(10):
        x = 100 + i * 20
        y = 100 + i * 20
        manager.add_pheromone((x, y), PheromoneType.FOOD_TRAIL, strength=30.0)
    
    # Test efficient querying
    start_time = time.time()
    pheromones = manager.get_pheromones_in_range((200, 200), 100.0, PheromoneType.FOOD_TRAIL)
    query_time = time.time() - start_time
    
    print(f"  Query time: {query_time:.4f} seconds")
    print(f"  Found {len(pheromones)} pheromones in range")
    
    assert query_time < 0.01  # Should be very fast
    assert len(pheromones) > 0
    
    print("✓ Spatial indexing tests passed!")

def test_pheromone_update():
    """Test pheromone update and cleanup."""
    print("Testing pheromone update and cleanup...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add pheromones with different decay rates
    manager.add_pheromone((100, 100), PheromoneType.FOOD_TRAIL, strength=5.0, decay_rate=5.0)
    manager.add_pheromone((200, 200), PheromoneType.FOOD_TRAIL, strength=10.0, decay_rate=1.0)
    
    initial_count = len(manager._pheromones)
    
    # Update once - first pheromone should be removed
    manager.update_all()
    
    # Check that one pheromone was removed
    assert len(manager._pheromones) == initial_count - 1
    
    # Update a few more times - second pheromone should be removed
    for _ in range(10):
        manager.update_all()
    
    # All pheromones should be removed
    assert len(manager._pheromones) == 0
    
    print("✓ Pheromone update and cleanup tests passed!")

if __name__ == "__main__":
    print("Running Pheromone System Tests...\n")
    
    try:
        test_pheromone_basic()
        test_pheromone_decay()
        test_pheromone_manager()
        test_gradient_calculation()
        test_spatial_indexing()
        test_pheromone_update()
        
        print("\n🎉 All pheromone system tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 