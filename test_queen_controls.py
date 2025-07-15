#!/usr/bin/env python3

# Simple test to validate the Queen Controls system logic
import sys
sys.path.append('src')

from entities.ant import Ant, AntCaste
from entities.colony import Colony
from entities.pheromone import PheromoneManager

def test_ant_caste_system():
    """Test that ant caste system works correctly."""
    print("Testing ant caste system...")
    
    # Test creating ants with different castes
    worker = Ant(position=(0, 0), caste=AntCaste.WORKER)
    soldier = Ant(position=(0, 0), caste=AntCaste.SOLDIER)
    scout = Ant(position=(0, 0), caste=AntCaste.SCOUT)
    nurse = Ant(position=(0, 0), caste=AntCaste.NURSE)
    
    print(f"Worker caste: {worker.caste}, color: {worker.get_caste_color()}")
    print(f"Soldier caste: {soldier.caste}, color: {soldier.get_caste_color()}")
    print(f"Scout caste: {scout.caste}, color: {scout.get_caste_color()}")
    print(f"Nurse caste: {nurse.caste}, color: {nurse.get_caste_color()}")
    
    # Test caste-specific properties
    assert worker.get_food_cost() == 10.0, "Worker food cost should be 10.0"
    assert soldier.get_food_cost() == 15.0, "Soldier food cost should be 15.0"
    assert scout.get_food_cost() == 12.0, "Scout food cost should be 12.0"
    assert nurse.get_food_cost() == 8.0, "Nurse food cost should be 8.0"
    
    print("✓ Ant caste system tests passed")

def test_colony_caste_management():
    """Test that colony can manage different ant castes."""
    print("\nTesting colony caste management...")
    
    # Create colony
    colony = Colony(position=(100, 100), max_population=50)
    colony.receive_food(200.0)  # Give enough food for testing
    
    # Test spawning different castes
    worker = colony.spawn_ant(AntCaste.WORKER)
    soldier = colony.spawn_ant(AntCaste.SOLDIER)
    scout = colony.spawn_ant(AntCaste.SCOUT)
    nurse = colony.spawn_ant(AntCaste.NURSE)
    
    assert worker is not None, "Should be able to spawn worker"
    assert soldier is not None, "Should be able to spawn soldier"
    assert scout is not None, "Should be able to spawn scout"
    assert nurse is not None, "Should be able to spawn nurse"
    
    # Test caste populations
    caste_pops = colony.get_caste_populations()
    assert caste_pops[AntCaste.WORKER] == 1, "Should have 1 worker"
    assert caste_pops[AntCaste.SOLDIER] == 1, "Should have 1 soldier"
    assert caste_pops[AntCaste.SCOUT] == 1, "Should have 1 scout"
    assert caste_pops[AntCaste.NURSE] == 1, "Should have 1 nurse"
    
    # Test spawning multiple ants
    workers = colony.spawn_multiple_ants(AntCaste.WORKER, 3)
    assert len(workers) == 3, "Should spawn 3 workers"
    assert colony.get_caste_population(AntCaste.WORKER) == 4, "Should have 4 workers total"
    
    print("✓ Colony caste management tests passed")

def test_colony_resource_management():
    """Test that colony correctly manages resources for different castes."""
    print("\nTesting colony resource management...")
    
    # Create colony with limited food
    colony = Colony(position=(100, 100), max_population=50)
    colony.receive_food(25.0)  # Only enough for 1 soldier or 2 workers
    
    # Test that we can check spawn capability
    assert colony.can_spawn_caste(AntCaste.WORKER, 2), "Should be able to spawn 2 workers"
    assert colony.can_spawn_caste(AntCaste.SOLDIER, 1), "Should be able to spawn 1 soldier"
    assert not colony.can_spawn_caste(AntCaste.SOLDIER, 2), "Should not be able to spawn 2 soldiers"
    
    # Test actual spawning
    soldiers = colony.spawn_multiple_ants(AntCaste.SOLDIER, 2)
    assert len(soldiers) == 1, "Should only spawn 1 soldier due to food limit"
    
    print("✓ Colony resource management tests passed")

def test_statistics_integration():
    """Test that statistics include caste information."""
    print("\nTesting statistics integration...")
    
    colony = Colony(position=(100, 100), max_population=50)
    colony.receive_food(100.0)
    
    # Spawn various castes
    colony.spawn_multiple_ants(AntCaste.WORKER, 3)
    colony.spawn_multiple_ants(AntCaste.SOLDIER, 2)
    colony.spawn_multiple_ants(AntCaste.SCOUT, 1)
    
    stats = colony.get_statistics()
    
    assert 'caste_populations' in stats, "Statistics should include caste populations"
    caste_pops = stats['caste_populations']
    
    assert caste_pops[AntCaste.WORKER] == 3, "Should have 3 workers in stats"
    assert caste_pops[AntCaste.SOLDIER] == 2, "Should have 2 soldiers in stats"
    assert caste_pops[AntCaste.SCOUT] == 1, "Should have 1 scout in stats"
    assert caste_pops[AntCaste.NURSE] == 0, "Should have 0 nurses in stats"
    
    print("✓ Statistics integration tests passed")

def test_queen_controls_logic():
    """Test the logic parts of queen controls without pygame."""
    print("\nTesting queen controls logic...")
    
    # We can't test the full UI without pygame, but we can test the logic
    colony = Colony(position=(100, 100), max_population=50)
    colony.receive_food(100.0)
    
    # Test the caste information structure
    ant_castes = {
        AntCaste.WORKER: {'name': 'Worker', 'cost': 10.0},
        AntCaste.SOLDIER: {'name': 'Soldier', 'cost': 15.0},
        AntCaste.SCOUT: {'name': 'Scout', 'cost': 12.0},
        AntCaste.NURSE: {'name': 'Nurse', 'cost': 8.0}
    }
    
    # Test that we can spawn each caste type
    for caste, info in ant_castes.items():
        if colony.can_spawn_caste(caste, 1):
            ant = colony.spawn_ant(caste)
            assert ant is not None, f"Should be able to spawn {info['name']}"
            assert ant.caste == caste, f"Spawned ant should have {caste} caste"
    
    print("✓ Queen controls logic tests passed")

if __name__ == "__main__":
    print("Running Queen Controls System Tests\n")
    
    test_ant_caste_system()
    test_colony_caste_management()
    test_colony_resource_management()
    test_statistics_integration()
    test_queen_controls_logic()
    
    print("\n✅ All tests passed! Queen Controls system is working correctly.")
    print("\nThe system provides:")
    print("- 4 different ant castes (Worker, Soldier, Scout, Nurse)")
    print("- Each caste has unique colors and properties")
    print("- Different food costs for different castes")
    print("- Population tracking by caste")
    print("- Extensible system for adding new castes")
    print("- Resource management for ant production")
    print("- UI for manual ant production (when pygame is available)")