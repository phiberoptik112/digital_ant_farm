import pygame
import numpy as np
import time
from entities.ant import Ant, AntState
from entities.pheromone import PheromoneManager, PheromoneType
from entities.food import FoodManager
from entities.colony import Colony
from ui_controls import FoodSystemUI

pygame.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Digital Ant Farm - Enhanced Pheromone & Food System')
clock = pygame.time.Clock()
running = True

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# --- Simulation Setup ---
pheromone_manager = PheromoneManager(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
food_manager = FoodManager(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
colony = Colony(position=(100, 100), max_population=20, spawn_rate=0.05)
colony.set_pheromone_manager(pheromone_manager)
colony.receive_food(100.0)

# Nest location
nest_pos = (100, 100)
nest_radius = 30

# Create food sources (static, for enhanced pheromone demo)
food_sources = [
    {"pos": (600, 150), "radius": 25, "active": True},
    {"pos": (700, 400), "radius": 20, "active": True},
    {"pos": (300, 450), "radius": 30, "active": True}
]

# Create ants at nest location
ants = []
for i in range(8):
    angle = (i / 8) * 360
    offset_x = np.cos(np.deg2rad(angle)) * 40
    offset_y = np.sin(np.deg2rad(angle)) * 40
    pos = (nest_pos[0] + offset_x, nest_pos[1] + offset_y)
    ant = Ant(position=pos, orientation=np.random.uniform(0, 360))
    ant.set_state(AntState.SEARCHING)
    ant.set_pheromone_manager(pheromone_manager)
    ant.set_world_bounds((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    ant.set_nest_position(nest_pos)
    ants.append(ant)

# UI Setup
food_ui = FoodSystemUI(850, 50, food_manager)

# Font for information display
font = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 36)

# Time tracking for delta time calculation
last_time = time.time()

# Frame counter for pheromone deposition
frame_count = 0

# --- Main Loop ---
while running:
    # Calculate delta time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    frame_count += 1

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Reset simulation (reset ants to nest, clear pheromones)
                pheromone_manager.clear_all()
                for ant in ants:
                    ant.set_position((nest_pos[0] + np.random.uniform(-20, 20), 
                                    nest_pos[1] + np.random.uniform(-20, 20)))
                    ant.set_state(AntState.SEARCHING)
                    ant.set_carrying_food(False)
                    ant.set_nest_position(nest_pos)
            elif event.key == pygame.K_TAB:
                food_ui.toggle_visibility()
            elif event.key == pygame.K_r:
                food_manager.regenerate_food()
            elif event.key == pygame.K_c:
                food_manager.clear_all_food()
        food_ui.handle_event(event)

    # Clear screen
    screen.fill((30, 30, 30))

    # Update systems
    food_manager.update_all(delta_time)
    pheromone_manager.update_all()
    colony.update()

    # --- Ant update and interaction logic ---
    for ant in ants:
        # Deposit exploration pheromones periodically while searching
        if ant.state == AntState.SEARCHING and frame_count % 30 == 0:
            ant.deposit_pheromone(PheromoneType.HOME_TRAIL, strength=20.0, 
                                decay_rate=0.3, radius_of_influence=15.0)

        # Check for food collision (static food sources)
        if ant.state == AntState.SEARCHING and not ant.carrying_food:
            found_food = False
            for food in food_sources:
                if food["active"]:
                    dist = np.sqrt((ant.position[0] - food["pos"][0])**2 + 
                                 (ant.position[1] - food["pos"][1])**2)
                    if dist <= food["radius"]:
                        ant.set_carrying_food(True)
                        ant.set_state(AntState.RETURNING)
                        found_food = True
                        break
            if found_food:
                continue  # skip food_manager if static food found

        # Check for food collision (food_manager)
        if ant.state == AntState.SEARCHING and not ant.carrying_food:
            nearby_food = food_manager.get_food_in_range(ant.position, ant._detection_radius)
            if nearby_food:
                closest_food = min(nearby_food, key=lambda f: f.distance_to(ant.position))
                if closest_food.distance_to(ant.position) < 15:
                    collected = closest_food.collect_food(5.0)
                    if collected > 0:
                        ant.set_carrying_food(True)
                        ant.set_state(AntState.RETURNING)
                        ant._food_amount = collected
                        ant._home_position = colony.position
                else:
                    dx = closest_food.position[0] - ant.position[0]
                    dy = closest_food.position[1] - ant.position[1]
                    distance = np.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        target_angle = np.rad2deg(np.arctan2(dy, dx))
                        ant.orientation = target_angle

        # Check for nest collision when returning (static nest)
        if ant.state == AntState.RETURNING and ant.carrying_food:
            dist = np.sqrt((ant.position[0] - nest_pos[0])**2 + 
                         (ant.position[1] - nest_pos[1])**2)
            if dist <= nest_radius:
                ant.set_carrying_food(False)
                ant.set_state(AntState.SEARCHING)
                continue

        # Check for nest collision when returning (colony)
        if ant.state == AntState.RETURNING and ant.carrying_food:
            dx = colony.position[0] - ant.position[0]
            dy = colony.position[1] - ant.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            if distance < 20:
                colony.receive_food(getattr(ant, '_food_amount', 5.0))
                ant.set_carrying_food(False)
                ant.set_state(AntState.SEARCHING)
                continue

        # Update ant behavior
        if ant.state == AntState.RETURNING:
            # Move towards nest and deposit food trail pheromones
            nest_dir = (nest_pos[0] - ant.position[0], nest_pos[1] - ant.position[1])
            nest_dist = np.sqrt(nest_dir[0]**2 + nest_dir[1]**2)
            if nest_dist > 0:
                nest_angle = np.rad2deg(np.arctan2(nest_dir[1], nest_dir[0]))
                ant.turn_towards(nest_angle)
                ant.accelerate(ant._max_velocity)
                ant.move(ant._velocity)
            # Deposit food trail pheromones
            ant.deposit_pheromone(PheromoneType.FOOD_TRAIL, strength=40.0, 
                                decay_rate=0.5, radius_of_influence=25.0)
        else:
            ant.step()

    # --- Rendering ---

    # Draw food sources (static, for enhanced pheromone demo)
    for food in food_sources:
        if food["active"]:
            pygame.draw.circle(screen, GREEN, (int(food["pos"][0]), int(food["pos"][1])), food["radius"])
            pygame.draw.circle(screen, (0, 200, 0), (int(food["pos"][0]), int(food["pos"][1])), food["radius"], 2)

    # Draw food sources (food_manager)
    for food_source in food_manager._food_sources:
        if food_source.visual_radius > 0:
            x, y = int(food_source.position[0]), int(food_source.position[1])
            radius = int(food_source.visual_radius)
            color = food_source.visual_color
            alpha = max(50, min(255, int(255 * food_source.amount / food_source.max_amount)))
            food_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(food_surface, (*color, alpha), (radius, radius), radius)
            screen.blit(food_surface, (x - radius, y - radius))
            border_color = (255, 255, 255) if food_source.is_available else (100, 100, 100)
            pygame.draw.circle(screen, border_color, (x, y), radius, 2)
            if food_source.is_available:
                time_left = food_source.time_until_expiration
                if time_left < 10:
                    timer_text = font.render(f"{time_left:.1f}s", True, (255, 200, 200))
                    text_rect = timer_text.get_rect(center=(x, y - radius - 15))
                    screen.blit(timer_text, text_rect)
            else:
                refresh_time = food_source.time_until_refresh
                if refresh_time > 0:
                    timer_text = font.render(f"R:{refresh_time:.1f}s", True, (200, 200, 255))
                    text_rect = timer_text.get_rect(center=(x, y - radius - 15))
                    screen.blit(timer_text, text_rect)

    # Enhanced pheromone rendering (gradient, per-pixel alpha)
    for pheromone in pheromone_manager._pheromones:
        x, y = int(pheromone.position[0]), int(pheromone.position[1])
        alpha = max(20, min(255, int(pheromone.strength * 3)))
        radius = int(pheromone.radius_of_influence)
        # Different colors for different pheromone types
        if pheromone.type == PheromoneType.FOOD_TRAIL:
            color = (0, 255, 100, alpha)  # Bright green for food trails
        elif pheromone.type == PheromoneType.HOME_TRAIL:
            color = (100, 200, 255, alpha)  # Light blue for exploration trails
        else:
            color = (255, 100, 100, alpha)  # Red for danger
        # Create surface with per-pixel alpha
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Draw gradient circle for more realistic pheromone appearance
        for r in range(radius, 0, -2):
            gradient_alpha = int(alpha * (r / radius) * 0.7)
            gradient_color = (*color[:3], gradient_alpha)
            pygame.draw.circle(s, gradient_color, (radius, radius), r)
        screen.blit(s, (x - radius, y - radius))

    # Draw nest (static nest)
    pygame.draw.circle(screen, BROWN, (int(nest_pos[0]), int(nest_pos[1])), nest_radius)
    pygame.draw.circle(screen, (160, 82, 45), (int(nest_pos[0]), int(nest_pos[1])), nest_radius, 3)

    # Draw colony (for food_manager system, at same nest position for now)
    colony_x, colony_y = int(colony.position[0]), int(colony.position[1])
    pygame.draw.circle(screen, (139, 69, 19), (colony_x, colony_y), int(colony.radius), 0)
    pygame.draw.circle(screen, (160, 82, 45), (colony_x, colony_y), int(colony.radius), 3)

    # Draw ants with enhanced visualization
    for ant in ants:
        x, y = int(ant.position[0]), int(ant.position[1])
        # Different colors based on state
        if ant.carrying_food:
            ant_color = (255, 165, 0)  # Orange when carrying food
        elif ant.state == AntState.RETURNING:
            ant_color = (255, 100, 100)  # Red when returning
        else:
            ant_color = (255, 255, 0)  # Yellow when searching
        pygame.draw.circle(screen, ant_color, (x, y), 6)
        # Draw orientation as a line
        rad = np.deg2rad(ant.orientation)
        end_x = int(x + 12 * np.cos(rad))
        end_y = int(y + 12 * np.sin(rad))
        pygame.draw.line(screen, (255, 255, 255), (x, y), (end_x, end_y), 2)
        if ant.state == AntState.SEARCHING:
            pygame.draw.circle(screen, (100, 100, 100), (x, y), int(ant._detection_radius), 1)

    # Update and draw UI
    food_ui.update()
    food_ui.draw(screen)

    # Draw instructions
    instructions = [
        "SPACE - Reset Simulation",
        "TAB - Toggle Food Controls",
        "R - Regenerate Food",
        "C - Clear All Food",
        "ESC - Exit",
        "Watch the green pheromone trails!"
    ]
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, (200, 200, 200))
        screen.blit(text, (10, 10 + i * 25))

    # Draw simulation info
    info_text = [
        f"Ants: {len(ants)}",
        f"Food Sources: {len(food_manager._food_sources) + len(food_sources)}",
        f"Pheromones: {len(pheromone_manager._pheromones)}",
        f"Colony Food: {colony.get_statistics()['food_storage']:.1f}",
        f"FPS: {clock.get_fps():.1f}"
    ]
    for i, text in enumerate(info_text):
        info_surface = font.render(text, True, (200, 200, 200))
        screen.blit(info_surface, (10, 180 + i * 25))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

