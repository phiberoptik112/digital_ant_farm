#!/usr/bin/env python3
"""Watch a food trail diffuse and evaporate.

This used to spawn eight extra discs after a delay. Spread is now the
concentration field: mass widens in place and the integral falls.
"""

import os
import sys
import time

import numpy as np
import pygame

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from entities.pheromone import PheromoneManager, PheromoneType


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def blit_field(screen, manager):
    rgba = np.ascontiguousarray(manager.rasterize())
    height, width = rgba.shape[:2]
    surface = pygame.image.frombuffer(rgba, (width, height), "RGBA").copy()
    screen.blit(pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pheromone field")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    manager = PheromoneManager(world_bounds=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    manager.deposit_segment((120, 300), (680, 300), PheromoneType.FOOD_TRAIL, 1.0)
    last = time.time()
    running = True
    while running:
        now = time.time()
        dt = now - last
        last = now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                manager.clear_all()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                manager.deposit(position, PheromoneType.FOOD_TRAIL, 8.0)
        manager.update_all(dt)
        screen.fill((30, 30, 30))
        blit_field(screen, manager)
        stats = manager.get_statistics()
        label = font.render(
            f"mass {stats['total_strength']:.1f}   active cells {stats['total_pheromones']}",
            True,
            (230, 230, 230),
        )
        screen.blit(label, (16, 16))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
