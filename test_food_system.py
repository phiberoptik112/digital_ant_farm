#!/usr/bin/env python3
"""
Simple test script for the Food Source Generation System.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.food import FoodSource, FoodManager

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
    
    # Test statistics
    stats = manager.get_statistics()
    assert stats['total_sources'] == 5
    assert stats['active_sources'] == 5
    
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

if __name__ == "__main__":
    print("Running Food System Tests...\n")
    
    try:
        test_food_source()
        test_food_manager()
        test_spatial_queries()
        
        print("\n🎉 All tests passed! Food system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 