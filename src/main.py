import pygame
import numpy as np
from entities.ant import Ant, AntState
from entities.pheromone import PheromoneManager, PheromoneType

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Digital Ant Farm')
clock = pygame.time.Clock()
running = True

# --- Simulation Setup ---
pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
ants = []

# Create a few ants at random positions
for i in range(5):
    pos = (np.random.uniform(100, 700), np.random.uniform(100, 500))
    ant = Ant(position=pos, orientation=np.random.uniform(0, 360))
    ant.set_state(AntState.SEARCHING)
    ant.set_pheromone_manager(pheromone_manager)
    ants.append(ant)

# --- Main Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    screen.fill((30, 30, 30))

    # Update ants and pheromones
    for ant in ants:
        ant.step()
    pheromone_manager.update_all()

    # Draw pheromones (as faded circles)
    for pheromone in pheromone_manager._pheromones:
        x, y = int(pheromone.position[0]), int(pheromone.position[1])
        alpha = max(30, min(200, int(pheromone.strength * 2)))
        color = (0, 255, 128, alpha) if pheromone.type == PheromoneType.FOOD_TRAIL else (128, 128, 255, alpha)
        s = pygame.Surface((pheromone.radius_of_influence*2, pheromone.radius_of_influence*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (int(pheromone.radius_of_influence), int(pheromone.radius_of_influence)), int(pheromone.radius_of_influence), 0)
        screen.blit(s, (x - pheromone.radius_of_influence, y - pheromone.radius_of_influence))

    # Draw ants
    for ant in ants:
        x, y = int(ant.position[0]), int(ant.position[1])
        pygame.draw.circle(screen, (255, 255, 0), (x, y), 5)
        # Draw orientation as a line
        rad = np.deg2rad(ant.orientation)
        end_x = int(x + 10 * np.cos(rad))
        end_y = int(y + 10 * np.sin(rad))
        pygame.draw.line(screen, (255, 200, 0), (x, y), (end_x, end_y), 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

