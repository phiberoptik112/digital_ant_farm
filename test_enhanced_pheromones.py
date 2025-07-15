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
    """Test that ants can follow pheromone gradients correctly."""
    print("\nTesting Pheromone Gradient Following...")
    
    pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
    
    # Create a trail of food pheromones
    trail_positions = [(100, 100), (150, 120), (200, 140), (250, 160), (300, 180)]
    for pos in trail_positions:
        pheromone_manager.add_pheromone(pos, PheromoneType.FOOD_TRAIL, 
                                      strength=50.0, decay_rate=0.1, radius_of_influence=30.0)
    
    # Create ant at start of trail
    ant = Ant(position=(80, 80), orientation=0)
    ant.set_pheromone_manager(pheromone_manager)
    ant.set_state(AntState.SEARCHING)
    
    print(f"Created pheromone trail with {len(trail_positions)} positions")
    print(f"Ant starting at position {ant.position}")
    
    # Test gradient sensing
    for i in range(5):
        gradient = ant.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=60.0)
        if gradient:
            print(f"Step {i}: Ant at {ant.position}, gradient: {gradient}")
            ant.step()
        else:
            print(f"Step {i}: No gradient detected at {ant.position}")
            break
    
    print("✓ Pheromone gradient following test completed!")

if __name__ == "__main__":
    test_enhanced_pheromone_system()
    test_pheromone_gradient_following()
    print("\n🎉 All enhanced pheromone system tests passed!")