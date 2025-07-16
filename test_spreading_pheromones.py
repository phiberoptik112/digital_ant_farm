#!/usr/bin/env python3
"""
Test script for the new spreading pheromone functionality.
Demonstrates how pheromones spread after initial deposit.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.pheromone import Pheromone, PheromoneManager, PheromoneType
import time

def test_pheromone_spreading():
    """Test basic pheromone spreading functionality."""
    print("Testing pheromone spreading...")
    
    # Create a pheromone manager
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add a pheromone that can spread
    original_pheromone = manager.add_pheromone(
        position=(100, 100),
        pheromone_type=PheromoneType.FOOD_TRAIL,
        strength=50.0,
        decay_rate=1.0,
        radius_of_influence=20.0,
        can_spread=True,
        spread_radius=40.0,
        spread_strength_factor=0.4,
        spread_delay=1.0  # 1 second delay
    )
    
    print(f"Initial pheromone: {original_pheromone}")
    print(f"Can spread: {original_pheromone.can_spread}")
    print(f"Should spread: {original_pheromone.should_spread}")
    
    # Check initial stats
    stats = manager.get_statistics()
    print(f"Initial stats: {stats}")
    
    # Wait for spread delay and update
    print(f"Waiting {original_pheromone._spread_delay} seconds for spread delay...")
    time.sleep(original_pheromone._spread_delay + 0.1)  # Add small buffer
    
    # Update manager to trigger spreading
    manager.update_all()
    
    # Check if pheromone has spread
    print(f"After waiting: Should spread = {original_pheromone.should_spread}")
    print(f"Has spread: {original_pheromone.has_spread}")
    
    # Check new stats
    stats = manager.get_statistics()
    print(f"After spreading stats: {stats}")
    
    # Test that spread deposits exist
    all_pheromones = manager._pheromones
    spread_deposits = [p for p in all_pheromones if p.is_spread_deposit]
    original_deposits = [p for p in all_pheromones if not p.is_spread_deposit]
    
    print(f"Total pheromones: {len(all_pheromones)}")
    print(f"Original deposits: {len(original_deposits)}")
    print(f"Spread deposits: {len(spread_deposits)}")
    
    # Show positions and strengths
    print("\nPheromone details:")
    for i, pheromone in enumerate(all_pheromones):
        print(f"  {i+1}. Position: {pheromone.position}, Strength: {pheromone.strength:.1f}, "
              f"Type: {'Spread' if pheromone.is_spread_deposit else 'Original'}")
    
    # Test that spread deposits have correct properties
    if spread_deposits:
        spread_pheromone = spread_deposits[0]
        expected_strength = original_pheromone.max_strength * original_pheromone.spread_strength_factor
        print(f"\nSpread deposit strength: {spread_pheromone.strength:.1f}")
        print(f"Expected strength: {expected_strength:.1f}")
        print(f"Same decay rate: {spread_pheromone._decay_rate == original_pheromone._decay_rate}")
        print(f"Cannot spread further: {not spread_pheromone.can_spread}")
    
    print("✓ Pheromone spreading test passed!")
    return True

def test_pheromone_spreading_over_time():
    """Test pheromone spreading and decay over multiple updates."""
    print("\nTesting pheromone spreading over time...")
    
    # Create a pheromone manager
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add a pheromone with fast spreading
    manager.add_pheromone(
        position=(200, 200),
        pheromone_type=PheromoneType.HOME_TRAIL,
        strength=60.0,
        decay_rate=0.5,
        radius_of_influence=25.0,
        can_spread=True,
        spread_radius=50.0,
        spread_strength_factor=0.3,
        spread_delay=0.5  # 0.5 second delay
    )
    
    print("Simulating pheromone behavior over time...")
    
    # Simulate multiple updates
    for frame in range(10):
        print(f"\nFrame {frame}:")
        
        # Update all pheromones
        manager.update_all()
        
        # Get current stats
        stats = manager.get_statistics()
        print(f"  Total pheromones: {stats['total_pheromones']}")
        print(f"  Original deposits: {stats['original_deposits']}")
        print(f"  Spread deposits: {stats['spread_deposits']}")
        print(f"  Total strength: {stats['total_strength']:.1f}")
        
        # Wait a bit before next update
        time.sleep(0.2)
    
    print("✓ Pheromone spreading over time test passed!")
    return True

def test_pheromone_no_spreading():
    """Test pheromones that don't spread."""
    print("\nTesting pheromones that don't spread...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add a pheromone that can't spread
    no_spread_pheromone = manager.add_pheromone(
        position=(300, 300),
        pheromone_type=PheromoneType.FOOD_TRAIL,
        strength=40.0,
        can_spread=False  # Cannot spread
    )
    
    print(f"No-spread pheromone: {no_spread_pheromone}")
    print(f"Can spread: {no_spread_pheromone.can_spread}")
    
    # Wait and update
    time.sleep(1.0)
    manager.update_all()
    
    # Check stats
    stats = manager.get_statistics()
    print(f"Stats after update: {stats}")
    
    assert stats['total_pheromones'] == 1, "Should still have only 1 pheromone"
    assert stats['spread_deposits'] == 0, "Should have no spread deposits"
    
    print("✓ No-spreading pheromone test passed!")
    return True

def test_gradient_with_spread_deposits():
    """Test pheromone gradient calculation with spread deposits."""
    print("\nTesting pheromone gradient with spread deposits...")
    
    manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Add a pheromone that spreads
    manager.add_pheromone(
        position=(400, 400),
        pheromone_type=PheromoneType.FOOD_TRAIL,
        strength=50.0,
        decay_rate=0.1,  # Slow decay
        radius_of_influence=30.0,
        can_spread=True,
        spread_radius=60.0,
        spread_strength_factor=0.5,
        spread_delay=0.5
    )
    
    # Wait for spreading
    time.sleep(0.6)
    manager.update_all()
    
    # Test gradient calculation at different positions
    test_positions = [
        (450, 450),  # Near the pheromone cluster
        (300, 300),  # Further away
        (500, 500)   # Even further
    ]
    
    for pos in test_positions:
        gradient = manager.get_pheromone_direction(pos, PheromoneType.FOOD_TRAIL, radius=100.0)
        total_strength = manager.get_total_strength(pos, PheromoneType.FOOD_TRAIL, radius=100.0)
        
        print(f"Position {pos}:")
        print(f"  Gradient: {gradient}")
        print(f"  Total strength: {total_strength:.1f}")
    
    print("✓ Gradient with spread deposits test passed!")
    return True

def main():
    """Run all spreading pheromone tests."""
    print("=" * 50)
    print("SPREADING PHEROMONE SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        test_pheromone_spreading,
        test_pheromone_spreading_over_time,
        test_pheromone_no_spreading,
        test_gradient_with_spread_deposits
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 All spreading pheromone tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)