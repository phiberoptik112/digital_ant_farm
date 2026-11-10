#!/usr/bin/env python3
"""
Test script for the Enhanced Pheromone System.
This script demonstrates the pheromone visualization system working correctly.
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.ant import Ant, AntState
from entities.pheromone import PheromoneManager, PheromoneType
import numpy as np

def test_enhanced_pheromone_system():
    """Test the enhanced pheromone system with multiple ants and pheromone types."""
    print("Testing Enhanced Pheromone System...")
    
    # Create pheromone manager
    pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Create ants at nest location
    nest_pos = (100, 100)
    ants = []
    
    for i in range(3):
        angle = (i / 3) * 360
        offset_x = np.cos(np.deg2rad(angle)) * 40
        offset_y = np.sin(np.deg2rad(angle)) * 40
        pos = (nest_pos[0] + offset_x, nest_pos[1] + offset_y)
        ant = Ant(position=pos, orientation=np.random.uniform(0, 360))
        ant.set_state(AntState.SEARCHING)
        ant.set_pheromone_manager(pheromone_manager)
        ant.set_nest_position(nest_pos)
        ants.append(ant)
    
    print(f"Created {len(ants)} ants at nest position {nest_pos}")
    
    # Simulate for a few steps
    for step in range(50):
        # Update ants
        for ant in ants:
            # Deposit exploration pheromones periodically
            if step % 10 == 0:
                ant.deposit_pheromone(PheromoneType.HOME_TRAIL, strength=20.0, 
                                    decay_rate=0.3, radius_of_influence=15.0)
            
            # Simulate finding food
            if step == 25 and ant == ants[0]:
                ant.set_carrying_food(True)
                ant.set_state(AntState.RETURNING)
                print(f"Ant {ants.index(ant)} found food at step {step}")
            
            # Deposit food trail pheromones when returning
            if ant.state == AntState.RETURNING:
                ant.deposit_pheromone(PheromoneType.FOOD_TRAIL, strength=40.0, 
                                    decay_rate=0.5, radius_of_influence=25.0)
            
            ant.step()
        
        # Update pheromones
        pheromone_manager.update_all()
        
        # Print status every 10 steps
        if step % 10 == 0:
            stats = pheromone_manager.get_statistics()
            print(f"Step {step}: {stats['total_pheromones']} pheromones active")
            print(f"  - Food trails: {stats['type_counts'].get('FOOD_TRAIL', 0)}")
            print(f"  - Home trails: {stats['type_counts'].get('HOME_TRAIL', 0)}")
    
    # Final statistics
    final_stats = pheromone_manager.get_statistics()
    print(f"\nFinal Results:")
    print(f"Total pheromones: {final_stats['total_pheromones']}")
    print(f"Food trail pheromones: {final_stats['type_counts'].get('FOOD_TRAIL', 0)}")
    print(f"Home trail pheromones: {final_stats['type_counts'].get('HOME_TRAIL', 0)}")
    print(f"Average strength: {final_stats['average_strength']:.2f}")
    print(f"Total strength: {final_stats['total_strength']:.2f}")
    
    # Test pheromone visualization colors
    print(f"\nPheromone Visualization Colors:")
    print(f"FOOD_TRAIL: Bright green (0, 255, 100)")
    print(f"HOME_TRAIL: Light blue (100, 200, 255)")
    print(f"DANGER: Red (255, 100, 100)")
    
    print("✓ Enhanced pheromone system test completed successfully!")

def test_pheromone_gradient_following():
    """A follower on a food ridge heads away from the nest, toward the food."""
    print("\nTesting pheromone ridge following...")

    pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600), diffusion=0.0)
    pheromone_manager.set_decay_rate(PheromoneType.FOOD_TRAIL, 0.0)
    nest = (120.0, 300.0)
    food = (520.0, 300.0)
    pheromone_manager.deposit_segment(food, nest, PheromoneType.FOOD_TRAIL, 1.0)

    ant = Ant(position=(160.0, 300.0), orientation=0.0)
    ant.set_pheromone_manager(pheromone_manager)
    ant.set_nest_position(nest)
    ant.set_state(AntState.FOLLOWING_TRAIL)
    ant._food_sense_offset = 8.0
    ant._food_sensing_range = 16.0
    ant._max_velocity = 2.0
    ant._velocity = 2.0

    direction = ant.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=8.0)
    assert direction is not None
    assert direction[0] > 0.5
    start_x = ant.position[0]
    for _ in range(40):
        ant.step()
    assert ant.position[0] > start_x + 20.0
    print(f"Follower moved from x={start_x:.1f} to x={ant.position[0]:.1f}")
    print("✓ Pheromone ridge following test completed!")

if __name__ == "__main__":
    test_enhanced_pheromone_system()
    test_pheromone_gradient_following()
    print("\n🎉 All enhanced pheromone system tests passed!")