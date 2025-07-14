import pygame
import numpy as np
from entities.ant import Ant, AntState, AntCaste
from entities.pheromone import PheromoneManager, PheromoneType
from entities.colony import Colony
from queen_controls import QueenControls

pygame.init()

screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption('Digital Ant Farm')
clock = pygame.time.Clock()
running = True

# --- Simulation Setup ---
pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))

# Create a colony at the center
colony = Colony(position=(400, 300), max_population=50, spawn_rate=0.05)
colony.set_pheromone_manager(pheromone_manager)

# Give the colony some initial food so it can spawn ants
colony.receive_food(100.0)

# Create queen controls UI
queen_controls = QueenControls(x=820, y=50, width=350, height=500)

# --- Main Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        else:
            # Handle queen controls events
            queen_controls.handle_event(event, colony)

    screen.fill((30, 30, 30))

    # Update colony and pheromones
    colony.update()
    pheromone_manager.update_all()
    
    # Update individual ants (this is what makes them move!)
    for ant in colony.get_ants():
        ant.step()

    # Draw pheromones (as faded circles)
    for pheromone in pheromone_manager._pheromones:
        x, y = int(pheromone.position[0]), int(pheromone.position[1])
        alpha = max(30, min(200, int(pheromone.strength * 2)))
        color = (0, 255, 128, alpha) if pheromone.type == PheromoneType.FOOD_TRAIL else (128, 128, 255, alpha)
        s = pygame.Surface((pheromone.radius_of_influence*2, pheromone.radius_of_influence*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (int(pheromone.radius_of_influence), int(pheromone.radius_of_influence)), int(pheromone.radius_of_influence), 0)
        screen.blit(s, (x - pheromone.radius_of_influence, y - pheromone.radius_of_influence))

    # Draw colony (nest)
    colony_x, colony_y = int(colony.position[0]), int(colony.position[1])
    pygame.draw.circle(screen, (139, 69, 19), (colony_x, colony_y), int(colony.radius), 0)  # Brown nest
    pygame.draw.circle(screen, (160, 82, 45), (colony_x, colony_y), int(colony.radius), 3)  # Border

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
    font = pygame.font.Font(None, 24)
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
        f"Nurses: {stats['caste_populations'].get(AntCaste.NURSE, 0)}"
    ]
    
    for i, line in enumerate(text_lines):
        if line:  # Skip empty lines
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))

    # Draw the queen controls UI
    queen_controls.draw(screen, colony)

    # Draw simulation area boundary
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, 800, 600), 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

