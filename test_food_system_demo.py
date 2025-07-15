#!/usr/bin/env python3
"""
Comprehensive test and demonstration of the Food System with time-based expiration and refresh mechanics.
This script tests all the requested features:
1. Randomized location and quantity
2. Time-based expiration
3. Refresh after a longer time period
4. Configurable parameters (equivalent to UI controls)
"""

import sys
import os
import time
import random
import numpy as np

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.food import FoodSource, FoodManager

def demonstrate_food_source_lifecycle():
    """Demonstrate the complete lifecycle of a food source."""
    print("=== Food Source Lifecycle Demonstration ===\n")
    
    # Create a food source with custom parameters
    food = FoodSource(
        position=(100, 100),
        amount=50.0,
        max_amount=100.0,
        depletion_rate=5.0,
        expiration_time=5.0,  # 5 seconds expiration
        refresh_time=3.0      # 3 seconds refresh
    )
    food.set_expiration_rate(10.0)  # 10 units per second decay
    
    print(f"Initial state: {food}")
    print(f"Available: {food.is_available}")
    print(f"Time until expiration: {food.time_until_expiration:.1f}s")
    print(f"Visual radius: {food.visual_radius:.1f}")
    print(f"Visual color: {food.visual_color}")
    print()
    
    # Simulate time passing
    start_time = time.time()
    while time.time() - start_time < 12:  # Run for 12 seconds
        current_time = time.time() - start_time
        food.update(delta_time=0.1)  # 100ms updates
        
        # Print status every second
        if int(current_time) != int(current_time - 0.1):
            print(f"Time: {current_time:.1f}s - {food}")
            print(f"  Available: {food.is_available}")
            print(f"  Time until expiration: {food.time_until_expiration:.1f}s")
            print(f"  Time until refresh: {food.time_until_refresh:.1f}s")
            print(f"  Visual radius: {food.visual_radius:.1f}")
            print(f"  Visual color: {food.visual_color}")
            print()
        
        time.sleep(0.1)  # 100ms delay
    
    print("=== Lifecycle demonstration complete ===\n")

def demonstrate_food_manager_parameters():
    """Demonstrate the configurable parameters of the food manager."""
    print("=== Food Manager Parameters Demonstration ===\n")
    
    # Create food manager with custom parameters
    manager = FoodManager(world_bounds=(0, 0, 500, 500))
    
    # Configure parameters (equivalent to UI controls)
    print("Configuring food system parameters:")
    manager.num_food_sources = 6
    manager.min_food_amount = 30.0
    manager.max_food_amount = 80.0
    manager.min_distance_between_food = 50.0
    manager.expiration_time = 8.0  # 8 seconds
    manager.refresh_time = 5.0     # 5 seconds
    manager.expiration_rate = 5.0  # 5 units per second
    manager.auto_generate = True
    
    print(f"  Number of food sources: {manager.num_food_sources}")
    print(f"  Food amount range: {manager.min_food_amount} - {manager.max_food_amount}")
    print(f"  Min distance between food: {manager.min_distance_between_food}")
    print(f"  Expiration time: {manager.expiration_time}s")
    print(f"  Refresh time: {manager.refresh_time}s")
    print(f"  Expiration rate: {manager.expiration_rate} units/second")
    print(f"  Auto-generate: {manager.auto_generate}")
    print()
    
    # Generate initial food sources
    print("Generating random food sources with configured parameters:")
    manager.generate_random_food()
    
    for i, food in enumerate(manager._food_sources):
        print(f"  Food {i+1}: pos={food.position}, amount={food.amount:.1f}")
    print()
    
    # Demonstrate statistics
    print("Initial statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Simulate time passing and show system behavior
    print("Simulating food system over time...")
    start_time = time.time()
    
    while time.time() - start_time < 15:  # Run for 15 seconds
        current_time = time.time() - start_time
        manager.update_all(delta_time=0.1)
        
        # Print statistics every 3 seconds
        if int(current_time) % 3 == 0 and int(current_time) != int(current_time - 0.1):
            print(f"\nTime: {current_time:.1f}s")
            stats = manager.get_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # Show food source states
            print("  Food source states:")
            for i, food in enumerate(manager._food_sources):
                state = "Available" if food.is_available else ("Expired" if food.is_expired else "Depleted")
                print(f"    Food {i+1}: {state} - {food.amount:.1f}/{food.max_amount}")
        
        time.sleep(0.1)
    
    print("\n=== Parameters demonstration complete ===\n")

def demonstrate_food_interaction():
    """Demonstrate ants interacting with food sources."""
    print("=== Food Interaction Demonstration ===\n")
    
    manager = FoodManager(world_bounds=(0, 0, 400, 400))
    
    # Create a few food sources at known locations
    food1 = manager.add_food_source((100, 100), 60.0, 60.0)
    food2 = manager.add_food_source((300, 300), 80.0, 80.0)
    food3 = manager.add_food_source((200, 200), 40.0, 40.0)
    
    print("Created food sources:")
    print(f"  Food 1: {food1}")
    print(f"  Food 2: {food2}")
    print(f"  Food 3: {food3}")
    print()
    
    # Simulate ant positions and food detection
    ant_positions = [(120, 120), (280, 320), (200, 180)]
    detection_radius = 30.0
    
    print("Simulating ant food detection:")
    for i, ant_pos in enumerate(ant_positions):
        print(f"  Ant {i+1} at {ant_pos}:")
        
        # Find nearest food
        nearest = manager.get_nearest_food(ant_pos, detection_radius)
        if nearest:
            distance = nearest.distance_to(ant_pos)
            print(f"    Nearest food: {nearest.position} (distance: {distance:.1f})")
        else:
            print("    No food within detection range")
        
        # Find all food in range
        food_in_range = manager.get_food_in_range(ant_pos, detection_radius)
        print(f"    Food sources in range: {len(food_in_range)}")
        for food in food_in_range:
            distance = food.distance_to(ant_pos)
            print(f"      {food.position} (distance: {distance:.1f})")
    
    print()
    
    # Simulate food collection
    print("Simulating food collection:")
    for i in range(3):
        print(f"  Collection round {i+1}:")
        
        # Collect food from each source
        collected1 = food1.collect_food(15.0)
        collected2 = food2.collect_food(20.0)
        collected3 = food3.collect_food(10.0)
        
        print(f"    Food 1: collected {collected1:.1f}, remaining {food1.amount:.1f}")
        print(f"    Food 2: collected {collected2:.1f}, remaining {food2.amount:.1f}")
        print(f"    Food 3: collected {collected3:.1f}, remaining {food3.amount:.1f}")
        print()
        
        # Update food sources
        manager.update_all(delta_time=1.0)
    
    print("=== Interaction demonstration complete ===\n")

def demonstrate_advanced_features():
    """Demonstrate advanced features like auto-generation and cleanup."""
    print("=== Advanced Features Demonstration ===\n")
    
    manager = FoodManager(world_bounds=(0, 0, 600, 600))
    
    # Configure for aggressive testing
    manager.num_food_sources = 4
    manager.expiration_time = 3.0
    manager.refresh_time = 2.0
    manager.auto_generate = True
    
    print("Testing auto-generation and cleanup:")
    print(f"Target food sources: {manager.num_food_sources}")
    print(f"Expiration time: {manager.expiration_time}s")
    print(f"Refresh time: {manager.refresh_time}s")
    print(f"Auto-generate: {manager.auto_generate}")
    print()
    
    # Generate initial food
    manager.generate_random_food()
    print(f"Initial food sources: {len(manager._food_sources)}")
    
    # Simulate rapid consumption and regeneration
    for round_num in range(5):
        print(f"\nRound {round_num + 1}:")
        
        # Deplete all food sources
        for food in manager._food_sources:
            while food.amount > 0:
                food.collect_food(10.0)
        
        print(f"  All food depleted. Available sources: {len([f for f in manager._food_sources if f.is_available])}")
        
        # Wait and update to trigger auto-generation
        time.sleep(1.0)
        for _ in range(10):
            manager.update_all(delta_time=0.1)
            time.sleep(0.1)
        
        stats = manager.get_statistics()
        print(f"  After update - Total: {stats['total_sources']}, Available: {stats['available_sources']}")
        
        # Test cleanup
        manager.cleanup_depleted()
        print(f"  After cleanup: {len(manager._food_sources)} sources remain")
    
    # Test manual regeneration
    print("\nTesting manual regeneration:")
    print(f"Before regeneration: {len(manager._food_sources)} sources")
    manager.regenerate_food()
    print(f"After regeneration: {len(manager._food_sources)} sources")
    
    # Test clear all
    print("\nTesting clear all:")
    manager.clear_all_food()
    print(f"After clear: {len(manager._food_sources)} sources")
    
    print("\n=== Advanced features demonstration complete ===\n")

def main():
    """Run all demonstrations."""
    print("🍃 Food System Comprehensive Demonstration 🍃")
    print("=" * 60)
    print()
    
    try:
        # Run all demonstrations
        demonstrate_food_source_lifecycle()
        demonstrate_food_manager_parameters()
        demonstrate_food_interaction()
        demonstrate_advanced_features()
        
        print("🎉 All demonstrations completed successfully!")
        print("\nThe food system includes:")
        print("✅ Randomized location and quantity")
        print("✅ Time-based expiration (food slowly expires)")
        print("✅ Refresh after longer time period")
        print("✅ Configurable parameters (equivalent to UI controls):")
        print("   - Number of food sources")
        print("   - Food amount range (min/max)")
        print("   - Expiration time")
        print("   - Refresh time")
        print("   - Expiration rate")
        print("   - Auto-generation toggle")
        print("   - Manual regeneration and clearing")
        print("\nTo run the full visual simulation (requires display):")
        print("python3 src/main.py")
        print("\nControls in the visual simulation:")
        print("- TAB: Toggle food system controls panel")
        print("- R: Regenerate all food")
        print("- C: Clear all food")
        print("- Use sliders to adjust parameters in real-time")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()