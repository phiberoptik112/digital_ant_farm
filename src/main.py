import pygame
import numpy as np
import time
from entities.ant import Ant, AntState, AntCaste
from entities.pheromone import PheromoneType
from entities.ground import GroundSystem
from entities.food import FoodManager
from entities.colony import Colony
from queen_controls import QueenControls
from ui_controls import FoodSystemUI

pygame.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Digital Ant Farm - Enhanced Colony & Pheromone System')
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
ground_system = GroundSystem(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), cell_size=15.0)
food_manager = FoodManager(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a colony at the center
colony = Colony(position=(400, 300), max_population=50, spawn_rate=0.05)
colony.set_pheromone_manager(ground_system)
colony.set_world_bounds((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
colony.receive_food(100.0)

# Create queen controls UI
queen_controls = QueenControls(x=850, y=50, width=350, height=500)

# Nest location (for compatibility with existing ant logic)
nest_pos = colony.position
nest_radius = 30

# Create food sources (static, for enhanced pheromone demo)
food_sources = [
    {"pos": (600, 150), "radius": 25, "active": True},
    {"pos": (700, 400), "radius": 20, "active": True},
    {"pos": (300, 450), "radius": 30, "active": True}
]

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
                ground_system.clear_all()
                colony.reset_ants_to_nest()
            elif event.key == pygame.K_TAB:
                # Toggle between queen controls and food controls
                pass  # TODO: Implement toggle between UI modes
            elif event.key == pygame.K_r:
                food_manager.regenerate_food()
            elif event.key == pygame.K_c:
                food_manager.clear_all_food()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is outside UI areas - reset sliders if so
            mouse_pos = pygame.mouse.get_pos()
            queen_controls_rect = pygame.Rect(queen_controls.x, queen_controls.y, queen_controls.width, queen_controls.height)
            
            if not queen_controls_rect.collidepoint(mouse_pos):
                # Click outside queen controls - reset all sliders
                queen_controls.reset_all_sliders()
            
            # Handle queen controls events
            queen_controls.handle_event(event, colony)
        else:
            # Handle queen controls events for other event types
            queen_controls.handle_event(event, colony)

    # Clear screen
    screen.fill((30, 30, 30))

    # Update systems
    food_manager.update_all(delta_time)
    ground_system.update_all(delta_time)
    colony.update()

    # Get behavior parameters from queen controls
    behavior_params = queen_controls.get_behavior_params()
    
    # --- Ant update and interaction logic ---
    for ant in colony.get_ants():
        # Apply behavior parameters to ant
        ant._max_velocity = behavior_params['ant_max_velocity']
        ant._acceleration = behavior_params['ant_acceleration']
        ant._turn_speed = behavior_params['ant_turn_speed']
        ant._detection_radius = behavior_params['ant_detection_radius']
        ant._food_sensing_range = behavior_params['food_sensing_range']
        ant._home_sensing_range = behavior_params['home_sensing_range']
        


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
                        ant._food_source_position = food["pos"]  # Remember food source position
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
                        ant._food_source_position = closest_food.position  # Remember food source position
                else:
                    dx = closest_food.position[0] - ant.position[0]
                    dy = closest_food.position[1] - ant.position[1]
                    distance = np.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        target_angle = np.rad2deg(np.arctan2(dy, dx))
                        ant.orientation = target_angle

        # Check for nest collision when returning (colony)
        if ant.state == AntState.RETURNING and ant.carrying_food:
            dx = colony.position[0] - ant.position[0]
            dy = colony.position[1] - ant.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            if distance < 20:
                colony.receive_food(getattr(ant, '_food_amount', 5.0))
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
                                strength=behavior_params['food_trail_strength'], 
                                decay_rate=behavior_params['food_trail_decay'], 
                                radius_of_influence=behavior_params['food_trail_radius'])
        elif ant.state == AntState.FOLLOWING_TRAIL and hasattr(ant, '_return_to_food_source') and ant._return_to_food_source:
            # Follow the food trail back to the food source
            food_direction = ant.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=behavior_params['food_sensing_range'])
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
    for pheromone in ground_system.all_pheromones:
        x, y = int(pheromone.position[0]), int(pheromone.position[1])
        alpha = max(20, min(255, int(pheromone.strength * 3)))
        radius = int(pheromone.radius_of_influence)
        # Use dynamic color for FOOD_TRAIL, static for others
        if pheromone.type == PheromoneType.FOOD_TRAIL:
            base_color = pheromone.color  # (R, G, B) from pheromone property
            color = (*base_color, alpha)
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

    # Draw colony
    colony_x, colony_y = int(colony.position[0]), int(colony.position[1])
    pygame.draw.circle(screen, (139, 69, 19), (colony_x, colony_y), int(colony.radius), 0)
    pygame.draw.circle(screen, (160, 82, 45), (colony_x, colony_y), int(colony.radius), 3)

    # Draw ants from the colony with caste-specific colors
    for ant in colony.get_ants():
        x, y = int(ant.position[0]), int(ant.position[1])
        ant_color = ant.get_caste_color()
        pygame.draw.circle(screen, ant_color, (x, y), 5)
        
        # Draw orientation as a line
        rad = np.deg2rad(ant.orientation)
        end_x = int(x + 10 * np.cos(rad))
        end_y = int(y + 10 * np.sin(rad))
        # Use a darker version of the caste color for the orientation line
        darker_color = tuple(max(0, c - 50) for c in ant_color)
        pygame.draw.line(screen, darker_color, (x, y), (end_x, end_y), 2)

    # Display colony statistics
    stats = colony.get_statistics()
    text_lines = [
        f"Population: {stats['population']}/{stats['max_population']}",
        f"Food: {stats['food_storage']:.1f}/{stats['max_food_storage']:.1f}",
        f"Level: {stats['development_level']}",
        f"Total Food: {stats['total_food_collected']:.1f}",
        "",
        "Ant Populations:",
        f"Workers: {stats['caste_populations'].get(AntCaste.WORKER, 0)}",
        f"Soldiers: {stats['caste_populations'].get(AntCaste.SOLDIER, 0)}",
        f"Scouts: {stats['caste_populations'].get(AntCaste.SCOUT, 0)}",
        f"Nurses: {stats['caste_populations'].get(AntCaste.NURSE, 0)}",
        "",
        f"Food Sources: {len(food_manager._food_sources) + len(food_sources)}",
        f"Pheromones: {len(ground_system.all_pheromones)}",
        f"FPS: {clock.get_fps():.1f}",
        "",
        "Trail Quality:",
        f"Avg Quality: {ground_system.get_statistics().get('average_quality', 0):.2f}",
        f"High Quality: {ground_system.get_statistics().get('high_quality_trails', 0)}",
        f"Total Usage: {ground_system.get_statistics().get('total_usage', 0)}"
    ]
    
    # Calculate statistics display area
    stats_y_start = 10
    stats_line_height = 22  # Reduced line height for better spacing
    
    for i, line in enumerate(text_lines):
        if line:  # Skip empty lines
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, stats_y_start + i * stats_line_height))

    # Draw the queen controls UI
    queen_controls.draw(screen, colony)

    # Draw instructions with proper spacing
    instructions = [
        "SPACE - Reset Simulation",
        "R - Regenerate Food",
        "C - Clear All Food",
        "ESC - Exit",
        "Watch the green pheromone trails!"
    ]
    
    # Calculate instructions position to avoid overlap with statistics
    # Statistics end at approximately: stats_y_start + len(text_lines) * stats_line_height
    stats_end_y = stats_y_start + len(text_lines) * stats_line_height
    instructions_y_start = stats_end_y + 40  # Add 40px buffer
    
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, (200, 200, 200))
        screen.blit(text, (10, instructions_y_start + i * 22))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

