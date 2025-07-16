#!/usr/bin/env python3
"""
Visual demonstration of the new spreading pheromone functionality.
Shows how pheromones spread over time with different visual effects.
"""

import pygame
import sys
import os
import time
import math
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.pheromone import Pheromone, PheromoneManager, PheromoneType

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
BLUE = (100, 200, 255)
RED = (255, 100, 100)
GRAY = (128, 128, 128)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def draw_pheromone_with_gradient(surface, pheromone, offset_x=0, offset_y=0):
    """Draw a pheromone with gradient effect."""
    x = int(pheromone.position[0] + offset_x)
    y = int(pheromone.position[1] + offset_y)
    
    # Choose color based on type
    if pheromone.type == PheromoneType.FOOD_TRAIL:
        base_color = GREEN
    elif pheromone.type == PheromoneType.HOME_TRAIL:
        base_color = BLUE
    else:
        base_color = RED
    
    # Calculate alpha based on strength
    alpha = max(20, min(255, int(pheromone.strength * 3)))
    
    # Make spread deposits slightly more transparent
    if pheromone.is_spread_deposit:
        alpha = int(alpha * 0.8)
    
    # Draw gradient circle
    radius = int(pheromone.radius_of_influence)
    for r in range(radius, 0, -2):
        gradient_alpha = int(alpha * (r / radius) * 0.7)
        gradient_color = (*base_color, gradient_alpha)
        
        # Create a surface for the circle with alpha
        circle_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, gradient_color, (r, r), r)
        
        # Blit the circle to the main surface
        surface.blit(circle_surface, (x - r, y - r))

def draw_info_panel(surface, font, pheromone_manager, frame_count):
    """Draw information panel showing current stats."""
    stats = pheromone_manager.get_statistics()
    
    info_texts = [
        f"Frame: {frame_count}",
        f"Total Pheromones: {stats['total_pheromones']}",
        f"Original Deposits: {stats['original_deposits']}",
        f"Spread Deposits: {stats['spread_deposits']}",
        f"Total Strength: {stats['total_strength']:.1f}",
        f"Average Strength: {stats['average_strength']:.1f}",
        "",
        "Press SPACE to add pheromone",
        "Press C to clear all",
        "Press ESC to quit"
    ]
    
    y_offset = 10
    for text in info_texts:
        if text:  # Don't render empty strings
            text_surface = font.render(text, True, WHITE)
            surface.blit(text_surface, (10, y_offset))
        y_offset += 25

def main():
    """Main demonstration function."""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Spreading Pheromones Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Create pheromone manager
    pheromone_manager = PheromoneManager(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Add some initial pheromones
    pheromone_manager.add_pheromone(
        position=(200, 200),
        pheromone_type=PheromoneType.FOOD_TRAIL,
        strength=50.0,
        decay_rate=0.2,
        radius_of_influence=25.0,
        can_spread=True,
        spread_radius=60.0,
        spread_strength_factor=0.4,
        spread_delay=3.0
    )
    
    pheromone_manager.add_pheromone(
        position=(600, 400),
        pheromone_type=PheromoneType.HOME_TRAIL,
        strength=40.0,
        decay_rate=0.15,
        radius_of_influence=20.0,
        can_spread=True,
        spread_radius=50.0,
        spread_strength_factor=0.5,
        spread_delay=2.0
    )
    
    frame_count = 0
    running = True
    
    print("Demo started!")
    print("- Watch the pheromones spread after a few seconds")
    print("- Press SPACE to add a new pheromone at a random location")
    print("- Press C to clear all pheromones")
    print("- Press ESC to quit")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Add a new pheromone at mouse position or random location
                    mouse_pos = pygame.mouse.get_pos()
                    if 50 < mouse_pos[0] < SCREEN_WIDTH - 50 and 50 < mouse_pos[1] < SCREEN_HEIGHT - 50:
                        pos = mouse_pos
                    else:
                        pos = (
                            200 + (frame_count * 50) % 400,
                            150 + (frame_count * 30) % 300
                        )
                    
                    pheromone_type = PheromoneType.FOOD_TRAIL if frame_count % 2 == 0 else PheromoneType.HOME_TRAIL
                    pheromone_manager.add_pheromone(
                        position=pos,
                        pheromone_type=pheromone_type,
                        strength=45.0,
                        decay_rate=0.1,
                        radius_of_influence=22.0,
                        can_spread=True,
                        spread_radius=55.0,
                        spread_strength_factor=0.45,
                        spread_delay=1.5
                    )
                elif event.key == pygame.K_c:
                    pheromone_manager.clear_all()
                    print("All pheromones cleared!")
        
        # Update pheromones
        pheromone_manager.update_all()
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw grid for reference
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw all pheromones
        for pheromone in pheromone_manager._pheromones:
            draw_pheromone_with_gradient(screen, pheromone)
        
        # Draw markers for original deposits
        for pheromone in pheromone_manager._pheromones:
            if not pheromone.is_spread_deposit:
                x = int(pheromone.position[0])
                y = int(pheromone.position[1])
                pygame.draw.circle(screen, WHITE, (x, y), 3)
                pygame.draw.circle(screen, BLACK, (x, y), 3, 1)
        
        # Draw info panel
        draw_info_panel(screen, font, pheromone_manager, frame_count)
        
        # Show spreading status for some pheromones
        y_offset = 300
        for i, pheromone in enumerate(pheromone_manager._pheromones[:3]):  # Show first 3
            if not pheromone.is_spread_deposit:
                status = "SPREAD" if pheromone.has_spread else f"WAIT {pheromone._spread_delay - pheromone.age:.1f}s"
                text = f"Pheromone {i+1}: {status}"
                text_surface = font.render(text, True, WHITE)
                screen.blit(text_surface, (10, y_offset))
                y_offset += 25
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
        frame_count += 1
        
        # Update every 60 frames (1 second)
        if frame_count % 60 == 0:
            stats = pheromone_manager.get_statistics()
            print(f"Frame {frame_count}: {stats['total_pheromones']} pheromones "
                  f"({stats['original_deposits']} original, {stats['spread_deposits']} spread)")
    
    # Cleanup
    pygame.quit()
    print("Demo ended!")

if __name__ == "__main__":
    main()