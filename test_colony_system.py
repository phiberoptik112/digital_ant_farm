#!/usr/bin/env python3
"""
Test script for the Colony Management System.
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.colony import Colony
from entities.pheromone import PheromoneManager, PheromoneType
from entities.ant import Ant, AntState

def test_colony_basic():
    """Test basic Colony functionality."""
    print("Testing basic Colony...")
    
    # Create a colony
    colony = Colony(position=(400, 300), max_population=10, spawn_rate=0.5)
    
    # Test properties
    assert colony.position == (400, 300)
    assert colony.radius == 30.0
    assert colony.population == 0
    assert colony.max_population == 10
    assert colony.food_storage == 0.0
    
    # Test initial statistics
    stats = colony.get_statistics()
    assert stats['population'] == 0
    assert stats['total_ants_spawned'] == 0
    assert stats['total_food_collected'] == 0.0
    
    print("✓ Basic Colony tests passed!")

def test_colony_spawning():
    """Test ant spawning functionality."""
    print("Testing colony spawning...")
    
    colony = Colony(position=(400, 300), max_population=5, spawn_rate=1.0)
    
    # Test spawning without food (should fail)
    ant = colony.spawn_ant()
    assert ant is None
    
    # Add food and test spawning
    colony.receive_food(50.0)
    ant = colony.spawn_ant()
    assert ant is not None
    assert colony.population == 1
    assert colony.food_storage == 40.0  # 50 - 10 for spawning
    
    # Test spawning at max population
    for _ in range(10):  # Try to spawn more than max
        colony.receive_food(20.0)
        ant = colony.spawn_ant()
    
    assert colony.population <= colony.max_population
    
    print("✓ Colony spawning tests passed!")

def test_food_management():
    """Test food storage and consumption."""
    print("Testing food management...")
    
    colony = Colony(position=(400, 300), max_population=3)
    
    # Test food reception
    received = colony.receive_food(25.0)
    assert received == 25.0
    assert colony.food_storage == 25.0
    
    # Test food storage limits
    received = colony.receive_food(2000.0)  # More than max storage
    assert received <= colony.max_food_storage
    assert colony.food_storage == colony.max_food_storage
    
    # Test food consumption during update
    initial_food = colony.food_storage
    colony.spawn_ant()  # Add an ant
    colony.update()  # Should consume food
    assert colony.food_storage < initial_food
    
    print("✓ Food management tests passed!")

def test_colony_update():
    """Test colony update and lifecycle management."""
    print("Testing colony update...")
    
    colony = Colony(position=(400, 300), max_population=3)
    colony.receive_food(100.0)
    
    # Spawn some ants
    for _ in range(3):
        colony.spawn_ant()
    
    initial_population = colony.population
    
    # Update colony (should consume food, potentially spawn new ants)
    colony.update()
    
    # Population should be managed (spawning, death, etc.)
    assert colony.population >= 0
    assert colony.population <= colony.max_population
    
    print("✓ Colony update tests passed!")

def test_colony_statistics():
    """Test colony statistics tracking."""
    print("Testing colony statistics...")
    
    colony = Colony(position=(400, 300), max_population=5)
    
    # Add some activity
    colony.receive_food(50.0)
    colony.spawn_ant()
    colony.spawn_ant()
    
    stats = colony.get_statistics()
    
    # Check key statistics
    assert stats['population'] == 2
    assert stats['total_ants_spawned'] == 2
    assert stats['total_food_collected'] == 50.0
    assert stats['food_storage'] == 30.0  # 50 - 20 for spawning
    assert stats['development_level'] == 1
    assert 'colony_age_seconds' in stats
    assert 'food_per_ant' in stats
    assert 'survival_rate' in stats
    
    print("✓ Colony statistics tests passed!")

def test_colony_development():
    """Test colony development and leveling up."""
    print("Testing colony development...")
    
    colony = Colony(position=(400, 300), max_population=5)
    
    initial_level = colony.development_level
    initial_max_pop = colony.max_population
    
    # Add enough food to gain experience and level up
    for _ in range(20):
        colony.receive_food(100.0)  # Should give 10 XP each
        colony.update()
    
    # Check if colony leveled up
    stats = colony.get_statistics()
    if stats['development_level'] > initial_level:
        assert colony.max_population > initial_max_pop
        print(f"  Colony leveled up to level {stats['development_level']}")
    
    print("✓ Colony development tests passed!")

def test_colony_with_pheromones():
    """Test colony integration with pheromone system."""
    print("Testing colony-pheromone integration...")
    
    pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    colony = Colony(position=(400, 300), max_population=3)
    
    # Link colony to pheromone manager
    colony.set_pheromone_manager(pheromone_manager)
    
    # Spawn an ant (should be linked to pheromone manager)
    colony.receive_food(20.0)
    ant = colony.spawn_ant()
    
    assert ant is not None
    # The ant should be able to deposit pheromones
    ant.deposit_pheromone(PheromoneType.FOOD_TRAIL, strength=30.0)
    
    # Check that pheromone was deposited
    pheromones = pheromone_manager.get_pheromones_in_range((400, 300), 50.0)
    assert len(pheromones) > 0
    
    print("✓ Colony-pheromone integration tests passed!")

def test_ant_lifecycle():
    """Test ant lifecycle management within colony."""
    print("Testing ant lifecycle...")
    
    colony = Colony(position=(400, 300), max_population=5)
    colony.receive_food(50.0)
    
    # Spawn ants
    ants = []
    for _ in range(3):
        ant = colony.spawn_ant()
        ants.append(ant)
    
    initial_population = colony.population
    
    # Simulate ant death by removing directly
    if ants:
        colony.remove_ant(ants[0])
        assert colony.population == initial_population - 1
    
    # Test getting ants in range
    ants_in_range = colony.get_ants_in_range((400, 300), 50.0)
    assert len(ants_in_range) <= colony.population
    
    print("✓ Ant lifecycle tests passed!")

if __name__ == "__main__":
    print("Running Colony System Tests...\n")
    
    try:
        test_colony_basic()
        test_colony_spawning()
        test_food_management()
        test_colony_update()
        test_colony_statistics()
        test_colony_development()
        test_colony_with_pheromones()
        test_ant_lifecycle()
        
        print("\n🎉 All colony system tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 