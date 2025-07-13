import pygame
import numpy as np
from entities.ant import Ant, AntState
from entities.pheromone import PheromoneManager, PheromoneType

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Digital Ant Farm - Enhanced Pheromone System')
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
ants = []

# Create nest location
nest_pos = (100, 100)
nest_radius = 30

# Create food sources
food_sources = [
    {"pos": (600, 150), "radius": 25, "active": True},
    {"pos": (700, 400), "radius": 20, "active": True},
    {"pos": (300, 450), "radius": 30, "active": True}
]

# Create ants at nest location
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

# Frame counter for pheromone deposition
frame_count = 0

# --- Main Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Reset simulation
                pheromone_manager.clear_all()
                for ant in ants:
                    ant.set_position((nest_pos[0] + np.random.uniform(-20, 20), 
                                    nest_pos[1] + np.random.uniform(-20, 20)))
                    ant.set_state(AntState.SEARCHING)
                    ant.set_carrying_food(False)
                    ant.set_nest_position(nest_pos)
    
    screen.fill((30, 30, 30))
    frame_count += 1
    
    # Update ants and pheromones
    for ant in ants:
        # Deposit exploration pheromones periodically while searching
        if ant.state == AntState.SEARCHING and frame_count % 30 == 0:
            ant.deposit_pheromone(PheromoneType.HOME_TRAIL, strength=20.0, 
                                decay_rate=0.3, radius_of_influence=15.0)
        
        # Check for food collision
        if ant.state == AntState.SEARCHING and not ant.carrying_food:
            for food in food_sources:
                if food["active"]:
                    dist = np.sqrt((ant.position[0] - food["pos"][0])**2 + 
                                 (ant.position[1] - food["pos"][1])**2)
                    if dist <= food["radius"]:
                        ant.set_carrying_food(True)
                        ant.set_state(AntState.RETURNING)
                        break
        
        # Check for nest collision when returning
        if ant.state == AntState.RETURNING and ant.carrying_food:
            dist = np.sqrt((ant.position[0] - nest_pos[0])**2 + 
                         (ant.position[1] - nest_pos[1])**2)
            if dist <= nest_radius:
                ant.set_carrying_food(False)
                ant.set_state(AntState.SEARCHING)
        
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
    
    pheromone_manager.update_all()

    # Enhanced pheromone rendering
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

    # Draw nest
    pygame.draw.circle(screen, BROWN, (int(nest_pos[0]), int(nest_pos[1])), nest_radius)
    pygame.draw.circle(screen, (160, 82, 45), (int(nest_pos[0]), int(nest_pos[1])), nest_radius, 3)

    # Draw food sources
    for food in food_sources:
        if food["active"]:
            pygame.draw.circle(screen, GREEN, (int(food["pos"][0]), int(food["pos"][1])), food["radius"])
            pygame.draw.circle(screen, (0, 200, 0), (int(food["pos"][0]), int(food["pos"][1])), food["radius"], 2)

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

    # Draw UI information
    font = pygame.font.Font(None, 36)
    info_text = font.render("SPACE: Reset | ESC: Quit | Watch the green pheromone trails!", True, WHITE)
    screen.blit(info_text, (10, 10))
    
    # Stats
    stats_text = font.render(f"Pheromones: {len(pheromone_manager._pheromones)}", True, WHITE)
    screen.blit(stats_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

