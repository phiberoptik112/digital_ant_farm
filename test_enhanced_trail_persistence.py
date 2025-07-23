#!/usr/bin/env python3
"""
Enhanced Trail Persistence Test
Demonstrates the improved pheromone system with trail reinforcement, quality tracking, and persistent trails.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import numpy as np
import time
from entities.pheromone import PheromoneType
from entities.ground import GroundSystem
from entities.ant import Ant, AntState
from entities.colony import Colony

def test_enhanced_trail_persistence():
    """Test the enhanced pheromone trail persistence system."""
    print("🧪 Testing Enhanced Trail Persistence System")
    print("=" * 50)
    
    # Initialize pygame for visualization
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Enhanced Trail Persistence Test')
    clock = pygame.time.Clock()
    
    # Create ground system
    ground_system = GroundSystem(world_bounds=(0, 0, 800, 600), cell_size=15.0)
    
    # Create a colony
    colony = Colony(position=(100, 300), max_population=20, spawn_rate=0.1)
    colony.set_pheromone_manager(ground_system)
    colony.set_world_bounds((0, 0, 800, 600))
    colony.receive_food(1000.0)
    
    # Create food sources
    food_sources = [
        {"pos": (600, 200), "radius": 25, "active": True},
        {"pos": (700, 400), "radius": 20, "active": True},
        {"pos": (500, 500), "radius": 30, "active": True}
    ]
    
    # Test phases
    test_phases = [
        "Phase 1: Initial Trail Creation",
        "Phase 2: Natural Trail Development",
        "Phase 3: Quality Development",
        "Phase 4: Network Formation",
        "Phase 5: Trail Persistence"
    ]
    
    current_phase = 0
    phase_start_time = time.time()
    phase_duration = 10  # seconds per phase
    
    # Statistics tracking
    stats_history = []
    
    running = True
    frame_count = 0
    
    print(f"Starting {test_phases[current_phase]}")
    
    while running and current_phase < len(test_phases):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Skip to next phase
                    current_phase += 1
                    if current_phase < len(test_phases):
                        print(f"\nStarting {test_phases[current_phase]}")
                        phase_start_time = time.time()
        
        # Check phase transition
        if time.time() - phase_start_time > phase_duration:
            current_phase += 1
            if current_phase < len(test_phases):
                print(f"\nStarting {test_phases[current_phase]}")
                phase_start_time = time.time()
        
        # Clear screen
        screen.fill((30, 30, 30))
        
        # Update systems
        ground_system.update_all(1.0/60.0)  # delta_time for 60 FPS
        colony.update()
        
        # Phase-specific behaviors
        if current_phase == 0:  # Initial Trail Creation
            # Spawn ants and let them create initial trails
            if frame_count % 60 == 0:  # Spawn ant every 2 seconds
                colony.spawn_ant()
        
        elif current_phase == 1:  # Natural Trail Development
            # Let trails develop naturally through ant behavior
            if frame_count % 300 == 0:  # Every 10 seconds
                print("  Trails developing naturally through ant activity...")
        
        elif current_phase == 2:  # Quality Development
            # Focus on developing high-quality trails
            if frame_count % 200 == 0:  # Every ~7 seconds
                # Show overall trail quality
                stats = ground_system.get_statistics()
                print(f"  Average trail quality: {stats['average_quality']:.2f}")
        
        elif current_phase == 3:  # Network Formation
            # Let the network develop naturally
            if frame_count % 400 == 0:  # Every ~13 seconds
                stats = ground_system.get_statistics()
                print(f"  Network stats: {stats['total_pheromones']} pheromones, "
                      f"{stats['high_quality_trails']} high-quality trails")
        
        elif current_phase == 4:  # Trail Persistence
            # Test trail persistence through natural decay
            if frame_count % 600 == 0:  # Every 20 seconds
                stats = ground_system.get_statistics()
                print(f"  Trail persistence: {stats['total_pheromones']} pheromones remaining")
        
        # Update ants
        for ant in colony.get_ants():
            # Apply basic ant behavior
            ant._max_velocity = 2.0
            ant._acceleration = 0.5
            ant._turn_speed = 3.0
            ant._detection_radius = 20.0
            ant._food_sensing_range = 60.0
            ant._home_sensing_range = 40.0
            


            # Check for food collision
            if ant.state == AntState.SEARCHING and not ant.carrying_food:
                found_food = False
                for food in food_sources:
                    if food["active"]:
                        dist = np.sqrt((ant.position[0] - food["pos"][0])**2 + 
                                     (ant.position[1] - food["pos"][1])**2)
                        if dist <= food["radius"]:
                            ant.set_carrying_food(True)
                            ant.set_state(AntState.RETURNING)
                            ant._food_source_position = food["pos"]  # Remember food source position
                            found_food = True
                            break

            # Check for nest collision when returning
            if ant.state == AntState.RETURNING and ant.carrying_food:
                dx = colony.position[0] - ant.position[0]
                dy = colony.position[1] - ant.position[1]
                distance = np.sqrt(dx*dx + dy*dy)
                if distance < 20:
                    colony.receive_food(5.0)
                    ant.set_carrying_food(False)
                    # Remember the food source position to return to it
                    if hasattr(ant, '_food_source_position'):
                        ant._return_to_food_source = True
                        ant.set_state(AntState.FOLLOWING_TRAIL)
                    else:
                        ant.set_state(AntState.SEARCHING)
                    continue

            # Update ant behavior
            if ant.state == AntState.RETURNING:
                # Move towards nest and deposit food trail pheromones
                nest_dir = (colony.position[0] - ant.position[0], colony.position[1] - ant.position[1])
                nest_dist = np.sqrt(nest_dir[0]**2 + nest_dir[1]**2)
                if nest_dist > 0:
                    nest_angle = np.rad2deg(np.arctan2(nest_dir[1], nest_dir[0]))
                    ant.turn_towards(nest_angle)
                    ant.accelerate(ant._max_velocity)
                    ant.move(ant._velocity)
                # Deposit food trail pheromones all the way to the nest
                ant.deposit_pheromone(PheromoneType.FOOD_TRAIL, 
                                    strength=40.0, 
                                    decay_rate=0.15,  # Moderate decay for good persistence
                                    radius_of_influence=12.0)  # Smaller radius
            elif ant.state == AntState.FOLLOWING_TRAIL and hasattr(ant, '_return_to_food_source') and ant._return_to_food_source:
                # Follow the food trail back to the food source
                food_direction = ant.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=60.0)
                if food_direction is not None:
                    # Convert direction vector to angle and turn towards it
                    angle = np.rad2deg(np.arctan2(food_direction[1], food_direction[0]))
                    ant.turn_towards(angle)
                    ant.accelerate(ant._max_velocity)
                    ant.move(ant._velocity)
                else:
                    # Lost the trail, search normally
                    ant._return_to_food_source = False
                    ant.set_state(AntState.SEARCHING)
                    ant.step()
            else:
                ant.step()
        
        # Render food sources
        for food in food_sources:
            if food["active"]:
                pygame.draw.circle(screen, (0, 255, 0), 
                                 (int(food["pos"][0]), int(food["pos"][1])), food["radius"])
                pygame.draw.circle(screen, (0, 200, 0), 
                                 (int(food["pos"][0]), int(food["pos"][1])), food["radius"], 2)
        
        # Enhanced pheromone rendering with quality visualization
        for pheromone in ground_system.all_pheromones:
            x, y = int(pheromone.position[0]), int(pheromone.position[1])
            
            # Enhanced alpha based on strength and quality
            base_alpha = max(20, min(255, int(pheromone.strength * 3)))
            quality_alpha = int(base_alpha * min(1.5, pheromone.trail_quality))
            alpha = min(255, quality_alpha)
            
            radius = int(pheromone.radius_of_influence)
            
            # Use enhanced color system
            if pheromone.type == PheromoneType.FOOD_TRAIL:
                base_color = pheromone.color  # Uses enhanced color method
                color = (*base_color, alpha)
            elif pheromone.type == PheromoneType.HOME_TRAIL:
                color = (100, 200, 255, alpha)  # Light blue
            else:
                color = (255, 100, 100, alpha)  # Red for danger
            
            # Create surface with per-pixel alpha
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # Draw gradient circle with quality-based intensity
            for r in range(radius, 0, -2):
                gradient_alpha = int(alpha * (r / radius) * 0.7)
                gradient_color = (*color[:3], gradient_alpha)
                pygame.draw.circle(s, gradient_color, (radius, radius), r)
            
            screen.blit(s, (x - radius, y - radius))
        
        # Draw colony
        colony_x, colony_y = int(colony.position[0]), int(colony.position[1])
        pygame.draw.circle(screen, (139, 69, 19), (colony_x, colony_y), int(colony.radius), 0)
        pygame.draw.circle(screen, (160, 82, 45), (colony_x, colony_y), int(colony.radius), 3)
        
        # Draw ants
        for ant in colony.get_ants():
            x, y = int(ant.position[0]), int(ant.position[1])
            ant_color = ant.get_caste_color()
            pygame.draw.circle(screen, ant_color, (x, y), 5)
            
            # Draw orientation
            rad = np.deg2rad(ant.orientation)
            end_x = int(x + 10 * np.cos(rad))
            end_y = int(y + 10 * np.sin(rad))
            darker_color = tuple(max(0, c - 50) for c in ant_color)
            pygame.draw.line(screen, darker_color, (x, y), (end_x, end_y), 2)
        
        # Display statistics
        stats = ground_system.get_statistics()
        colony_stats = colony.get_statistics()
        
        font = pygame.font.Font(None, 24)
        text_lines = [
            f"Phase: {test_phases[current_phase] if current_phase < len(test_phases) else 'Complete'}",
            f"Time: {time.time() - phase_start_time:.1f}s",
            f"Population: {colony_stats['population']}",
            f"Pheromones: {stats['total_pheromones']}",
            f"Food Trails: {stats['type_counts'].get('FOOD_TRAIL', 0)}",
            f"Home Trails: {stats['type_counts'].get('HOME_TRAIL', 0)}",
            f"Avg Quality: {stats['average_quality']:.2f}",
            f"High Quality: {stats['high_quality_trails']}",
            f"Total Usage: {stats['total_usage']}",
            f"FPS: {clock.get_fps():.1f}"
        ]
        
        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 22))
        
        # Display instructions
        instructions = [
            "SPACE - Next Phase",
            "ESC - Exit",
            "Watch trail quality development!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (10, 550 + i * 22))
        
        pygame.display.flip()
        clock.tick(30)  # 30 FPS for better observation
        frame_count += 1
    
    # Final statistics
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    final_stats = ground_system.get_statistics()
    print(f"Total pheromones: {final_stats['total_pheromones']}")
    print(f"Food trail pheromones: {final_stats['type_counts'].get('FOOD_TRAIL', 0)}")
    print(f"Home trail pheromones: {final_stats['type_counts'].get('HOME_TRAIL', 0)}")
    print(f"Average strength: {final_stats['average_strength']:.2f}")
    print(f"Total strength: {final_stats['total_strength']:.2f}")
    print(f"Average quality: {final_stats['average_quality']:.2f}")
    print(f"High quality trails: {final_stats['high_quality_trails']}")
    print(f"Total usage: {final_stats['total_usage']}")
    
    # Show trail statistics
    print(f"\n🏆 Trail Statistics:")
    print(f"  Average quality: {final_stats['average_quality']:.2f}")
    print(f"  High quality trails: {final_stats['high_quality_trails']}")
    print(f"  Total usage: {final_stats['total_usage']}")
    print(f"  Average usage per pheromone: {final_stats['average_usage']:.1f}")
    
    pygame.quit()
    print("\n✅ Enhanced trail persistence test completed!")

if __name__ == "__main__":
    test_enhanced_trail_persistence() 