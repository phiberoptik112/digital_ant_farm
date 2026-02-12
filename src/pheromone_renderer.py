"""
Optimized pheromone rendering system with surface caching and performance improvements.
"""
import pygame
import numpy as np
from typing import Dict, Tuple, Optional
from entities.pheromone import Pheromone, PheromoneType

class PheromoneRenderer:
    """
    High-performance pheromone renderer with surface caching and optimized gradient rendering.
    """
    
    def __init__(self):
        self._surface_cache: Dict[Tuple, pygame.Surface] = {}
        self._max_cache_size = 100  # Limit cache size to prevent memory bloat
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Optimization settings
        self._gradient_rings = 4  # Limit to 4 rings for performance
        self._strength_buckets = 8  # Group similar strengths together
        self._radius_buckets = 6   # Group similar radii together
        
    def _get_cache_key(self, pheromone: Pheromone) -> Tuple:
        """
        Generate a cache key for a pheromone based on bucketed properties.
        This groups similar pheromones together to improve cache hit rate.
        """
        # Bucket strength into ranges
        strength_bucket = min(self._strength_buckets - 1, 
                            int(pheromone.strength / (100.0 / self._strength_buckets)))
        
        # Bucket outer radius into ranges
        outer_radius = pheromone.radius_of_influence
        outer_radius_bucket = min(self._radius_buckets - 1,
                          int(outer_radius / (80.0 / self._radius_buckets)))  # Assume max radius ~80
        
        # Bucket inner radius into ranges (for ring effect)
        inner_radius = pheromone.inner_radius
        inner_radius_bucket = min(self._radius_buckets - 1,
                          int(inner_radius / (60.0 / self._radius_buckets)))
        
        # Include type and basic properties
        return (
            pheromone.type,
            strength_bucket,
            outer_radius_bucket,
            inner_radius_bucket,
            int(pheromone.trail_quality * 2)  # Group quality into half-steps
        )
    
    def _create_pheromone_surface(self, pheromone: Pheromone) -> pygame.Surface:
        """
        Create an optimized pheromone surface with spreading ring effect.
        The pheromone is rendered as an expanding ring that fades from the center.
        """
        outer_radius = int(pheromone.radius_of_influence)
        inner_radius = int(pheromone.inner_radius)
        
        if outer_radius <= 0:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        
        surface = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
        color = pheromone.color
        center = (outer_radius, outer_radius)
        
        # Calculate base alpha from strength and quality
        base_alpha = max(20, min(255, int(pheromone.strength * 3 * pheromone.trail_quality)))
        
        ring_width = outer_radius - inner_radius
        if ring_width < 2:
            ring_width = 2
        
        # Draw the spreading ring with gradient
        num_rings = min(self._gradient_rings + 2, max(3, ring_width // 2))
        ring_step = max(1, ring_width // num_rings)
        
        for i in range(num_rings):
            # Calculate radius for this sub-ring (from outer to inner)
            r = outer_radius - i * ring_step
            if r <= inner_radius:
                break
            
            # Calculate distance from the concentration peak (middle of ring)
            ring_midpoint = (outer_radius + inner_radius) / 2
            dist_from_peak = abs(r - ring_midpoint)
            max_dist = ring_width / 2
            
            # Gaussian-like alpha falloff from peak
            if max_dist > 0:
                peak_factor = np.exp(-(dist_from_peak ** 2) / (2 * (max_dist * 0.7) ** 2))
            else:
                peak_factor = 1.0
            
            ring_alpha = int(base_alpha * peak_factor * 0.8)
            
            if ring_alpha > 3:  # Skip very faint rings
                ring_color = (*color, ring_alpha)
                pygame.draw.circle(surface, ring_color, center, r)
        
        # Draw faint residual in the dissipated center (if there's a hollow)
        if inner_radius > 3:
            center_alpha = int(base_alpha * 0.1)
            if center_alpha > 2:
                center_color = (*color, center_alpha)
                pygame.draw.circle(surface, center_color, center, inner_radius)
        
        return surface
    
    def get_pheromone_surface(self, pheromone: Pheromone) -> pygame.Surface:
        """
        Get a cached surface for the pheromone, creating it if necessary.
        """
        cache_key = self._get_cache_key(pheromone)
        
        if cache_key in self._surface_cache:
            self._cache_hits += 1
            return self._surface_cache[cache_key]
        
        # Cache miss - create new surface
        self._cache_misses += 1
        surface = self._create_pheromone_surface(pheromone)
        
        # Manage cache size
        if len(self._surface_cache) >= self._max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._surface_cache))
            del self._surface_cache[oldest_key]
        
        self._surface_cache[cache_key] = surface
        return surface
    
    def render_pheromones(self, screen: pygame.Surface, pheromones: list):
        """
        Render all pheromones to the screen using cached surfaces.
        """
        for pheromone in pheromones:
            surface = self.get_pheromone_surface(pheromone)
            x, y = int(pheromone.position[0]), int(pheromone.position[1])
            radius = int(pheromone.radius_of_influence)
            
            # Blit the cached surface
            screen.blit(surface, (x - radius, y - radius))
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self._surface_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate
        }
    
    def clear_cache(self):
        """Clear the surface cache."""
        self._surface_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


class OptimizedDistanceCalculator:
    """
    Optimized distance calculations using squared distances where possible.
    """
    
    @staticmethod
    def distance_squared(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate squared distance (faster than sqrt)."""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return dx * dx + dy * dy
    
    @staticmethod
    def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate actual distance when needed."""
        return np.sqrt(OptimizedDistanceCalculator.distance_squared(pos1, pos2))
    
    @staticmethod
    def is_within_range_squared(pos1: Tuple[float, float], pos2: Tuple[float, float], 
                              range_radius: float) -> bool:
        """Check if positions are within range using squared distance."""
        range_squared = range_radius * range_radius
        return OptimizedDistanceCalculator.distance_squared(pos1, pos2) <= range_squared


class BatchedAntUpdater:
    """
    Batched ant update system to reduce per-frame calculations.
    """
    
    def __init__(self, batch_size: int = 3):
        self.batch_size = batch_size
        self.frame_count = 0
        self._cached_behaviors = {}  # Cache behavior results
        
    def should_update_ant(self, ant_id: int) -> bool:
        """Determine if an ant should be updated this frame."""
        return (self.frame_count + ant_id) % self.batch_size == 0
    
    def update_frame(self):
        """Call this each frame to advance the batch counter."""
        self.frame_count += 1
    
    def cache_ant_behavior(self, ant_id: int, behavior_data: dict):
        """Cache behavior data for an ant."""
        self._cached_behaviors[ant_id] = {
            'data': behavior_data,
            'frame': self.frame_count
        }
    
    def get_cached_behavior(self, ant_id: int, max_age: int = 2) -> Optional[dict]:
        """Get cached behavior data if it's recent enough."""
        if ant_id in self._cached_behaviors:
            cached = self._cached_behaviors[ant_id]
            if self.frame_count - cached['frame'] <= max_age:
                return cached['data']
        return None