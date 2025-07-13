import pygame
import numpy as np
import time
from entities.ant import Ant, AntState
from entities.pheromone import PheromoneManager, PheromoneType
from entities.food import FoodManager
from ui_controls import FoodSystemUI

pygame.init()

# Screen setup
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('Digital Ant Farm - Food System')
clock = pygame.time.Clock()
running = True

# --- Simulation Setup ---
pheromone_manager = PheromoneManager(world_bounds=(0, 0, 1200, 800))
food_manager = FoodManager(world_bounds=(0, 0, 1200, 800))
ants = []

# Generate initial food sources
food_manager.generate_random_food()

# Create ants at random positions
for i in range(8):
    pos = (np.random.uniform(100, 1100), np.random.uniform(100, 700))
    ant = Ant(position=pos, orientation=np.random.uniform(0, 360))
    ant.set_state(AntState.SEARCHING)
    ant.set_pheromone_manager(pheromone_manager)
    ants.append(ant)

# UI Setup
food_ui = FoodSystemUI(850, 50, food_manager)

# Font for information display
font = pygame.font.Font(None, 24)

# Time tracking for delta time calculation
last_time = time.time()

# --- Main Loop ---
while running:
    # Calculate delta time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_TAB:
                food_ui.toggle_visibility()
            elif event.key == pygame.K_r:
                food_manager.regenerate_food()
            elif event.key == pygame.K_c:
                food_manager.clear_all_food()
        
        # Let UI handle events first
        food_ui.handle_event(event)
    
    # Clear screen
    screen.fill((30, 30, 30))
    
    # Update systems
    food_manager.update_all(delta_time)
    pheromone_manager.update_all()
    
    # Update ants with food interaction
    for ant in ants:
        # If ant is searching for food, check for nearby food sources
        if ant.state == AntState.SEARCHING and not ant.carrying_food:
            nearby_food = food_manager.get_food_in_range(ant.position, ant._detection_radius)
            if nearby_food:
                # Find the closest food source
                closest_food = min(nearby_food, key=lambda f: f.distance_to(ant.position))
                if closest_food.distance_to(ant.position) < 15:  # Close enough to collect
                    collected = closest_food.collect_food(5.0)
                    if collected > 0:
                        ant.set_carrying_food(True)
                        ant.set_state(AntState.RETURNING)
                        # TODO: Add nest position and make ant return to nest
                        # For now, we'll just have them wander around
                else:
                    # Move towards the closest food source
                    dx = closest_food.position[0] - ant.position[0]
                    dy = closest_food.position[1] - ant.position[1]
                    distance = np.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        # Set ant orientation towards food
                        target_angle = np.rad2deg(np.arctan2(dy, dx))
                        ant.orientation = target_angle
        
        # Update ant behavior
        ant.step()
    
    # Draw food sources
    for food_source in food_manager._food_sources:
        if food_source.visual_radius > 0:
            x, y = int(food_source.position[0]), int(food_source.position[1])
            radius = int(food_source.visual_radius)
            color = food_source.visual_color
            
            # Draw food source with transparency based on amount
            alpha = max(50, min(255, int(255 * food_source.amount / food_source.max_amount)))
            food_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(food_surface, (*color, alpha), (radius, radius), radius)
            screen.blit(food_surface, (x - radius, y - radius))
            
            # Draw border
            border_color = (255, 255, 255) if food_source.is_available else (100, 100, 100)
            pygame.draw.circle(screen, border_color, (x, y), radius, 2)
            
            # Draw expiration/refresh timer
            if food_source.is_available:
                time_left = food_source.time_until_expiration
                if time_left < 10:  # Show timer when < 10 seconds left
                    timer_text = font.render(f"{time_left:.1f}s", True, (255, 200, 200))
                    text_rect = timer_text.get_rect(center=(x, y - radius - 15))
                    screen.blit(timer_text, text_rect)
            else:
                refresh_time = food_source.time_until_refresh
                if refresh_time > 0:
                    timer_text = font.render(f"R:{refresh_time:.1f}s", True, (200, 200, 255))
                    text_rect = timer_text.get_rect(center=(x, y - radius - 15))
                    screen.blit(timer_text, text_rect)

    # Draw pheromones
    for pheromone in pheromone_manager._pheromones:
        x, y = int(pheromone.position[0]), int(pheromone.position[1])
        alpha = max(30, min(200, int(pheromone.strength * 2)))
        
        if pheromone.type == PheromoneType.FOOD_TRAIL:
            color = (0, 255, 128, alpha)
        else:
            color = (128, 128, 255, alpha)
        
        pheromone_surface = pygame.Surface((pheromone.radius_of_influence*2, pheromone.radius_of_influence*2), pygame.SRCALPHA)
        pygame.draw.circle(pheromone_surface, color, 
                          (int(pheromone.radius_of_influence), int(pheromone.radius_of_influence)), 
                          int(pheromone.radius_of_influence))
        screen.blit(pheromone_surface, (x - pheromone.radius_of_influence, y - pheromone.radius_of_influence))

    # Draw ants
    for ant in ants:
        x, y = int(ant.position[0]), int(ant.position[1])
        
        # Change ant color based on state
        if ant.carrying_food:
            ant_color = (255, 150, 0)  # Orange when carrying food
        elif ant.state == AntState.SEARCHING:
            ant_color = (255, 255, 0)  # Yellow when searching
        else:
            ant_color = (255, 200, 0)  # Default color
        
        pygame.draw.circle(screen, ant_color, (x, y), 5)
        
        # Draw orientation line
        rad = np.deg2rad(ant.orientation)
        end_x = int(x + 12 * np.cos(rad))
        end_y = int(y + 12 * np.sin(rad))
        pygame.draw.line(screen, (255, 200, 0), (x, y), (end_x, end_y), 2)
        
        # Draw detection radius when searching
        if ant.state == AntState.SEARCHING:
            pygame.draw.circle(screen, (100, 100, 100), (x, y), int(ant._detection_radius), 1)

    # Update and draw UI
    food_ui.update()
    food_ui.draw(screen)
    
    # Draw instructions
    instructions = [
        "TAB - Toggle Food Controls",
        "R - Regenerate Food",
        "C - Clear All Food",
        "ESC - Exit"
    ]
    
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, (200, 200, 200))
        screen.blit(text, (10, 10 + i * 25))
    
    # Draw simulation info
    info_text = [
        f"Ants: {len(ants)}",
        f"Food Sources: {len(food_manager._food_sources)}",
        f"Pheromones: {len(pheromone_manager._pheromones)}",
        f"FPS: {clock.get_fps():.1f}"
    ]
    
    for i, text in enumerate(info_text):
        info_surface = font.render(text, True, (200, 200, 200))
        screen.blit(info_surface, (10, 150 + i * 25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

