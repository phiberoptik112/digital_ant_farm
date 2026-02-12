from enum import Enum, auto
from typing import Tuple, Optional, List, Dict
import numpy as np
import time

class PheromoneType(Enum):
    """Types of pheromones that ants can deposit."""
    FOOD_TRAIL = auto()  # Trail leading to food
    HOME_TRAIL = auto()  # Trail leading back to nest
    DANGER = auto()      # Warning pheromone

class Pheromone:
    """
    Represents a single pheromone deposit with position, type, strength, and decay.
    Enhanced with diffusion mechanics - pheromones spread outward over time while
    dissipating from the center, simulating real pheromone behavior.
    """
    def __init__(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                 strength: float = 100.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0,
                 diffusion_rate: float = 2.5, max_radius: float = 80.0):
        self._position = position  # (x, y)
        self._type = pheromone_type
        self._strength = strength
        self._max_strength = strength
        self._decay_rate = decay_rate  # Overall strength lost per tick
        self._creation_time = time.time()
        self._initial_radius = radius_of_influence  # Starting radius
        self._current_radius = radius_of_influence  # Current outer radius (grows over time)
        self._inner_radius = 0.0  # Inner dissipation radius (grows over time, hollow center)
        self._max_radius = max_radius  # Maximum spread radius
        
        # Diffusion parameters
        self._diffusion_rate = diffusion_rate  # How fast the pheromone spreads outward per tick
        self._dissipation_rate = diffusion_rate * 0.6  # How fast the center hollows out
        self._concentration_peak = 0.0  # Distance from center where concentration is highest
        
        # Trail persistence properties
        self._trail_quality = 1.0  # Quality factor based on usage frequency
        self._usage_count = 0  # Number of times this pheromone has been used for navigation
        


    @property
    def position(self) -> Tuple[float, float]:
        """Get the pheromone position."""
        return self._position
    
    @property
    def type(self) -> PheromoneType:
        """Get the pheromone type."""
        return self._type
    
    @property
    def strength(self) -> float:
        """Get the current pheromone strength."""
        return self._strength
    
    @property
    def max_strength(self) -> float:
        """Get the maximum pheromone strength."""
        return self._max_strength
    
    @property
    def radius_of_influence(self) -> float:
        """Get the current outer radius of influence (grows as pheromone diffuses)."""
        return self._current_radius
    
    @property
    def inner_radius(self) -> float:
        """Get the inner dissipation radius (center becomes hollow as it spreads)."""
        return self._inner_radius
    
    @property
    def ring_width(self) -> float:
        """Get the width of the active pheromone ring."""
        return max(0.0, self._current_radius - self._inner_radius)
    
    @property
    def concentration_peak_distance(self) -> float:
        """Get the distance from center where concentration is highest."""
        return self._concentration_peak
    
    @property
    def diffusion_progress(self) -> float:
        """Get how much the pheromone has diffused (0 = fresh, 1 = fully spread)."""
        if self._max_radius <= self._initial_radius:
            return 1.0
        return (self._current_radius - self._initial_radius) / (self._max_radius - self._initial_radius)
    
    @property
    def age(self) -> float:
        """Get the age of the pheromone in seconds."""
        return time.time() - self._creation_time
    

    
    @property
    def trail_quality(self) -> float:
        """Get the trail quality factor based on usage."""
        return self._trail_quality
    
    @property
    def usage_count(self) -> int:
        """Get the number of times this pheromone has been used."""
        return self._usage_count
    

    


    def mark_usage(self):
        """Mark this pheromone as being used for navigation."""
        self._usage_count += 1
        # Improve trail quality based on usage (diminishing returns)
        self._trail_quality = min(3.0, 1.0 + (self._usage_count * 0.1))

    def reinforce(self, additional_strength: float):
        """
        Reinforce the pheromone with additional strength.
        Args:
            additional_strength: Amount to add to current strength
        """
        self._strength = min(self._max_strength, self._strength + additional_strength)

    @property
    def color(self) -> Tuple[int, int, int]:
        """
        Get the current color of the pheromone as an RGB tuple, interpolating from green to red as it decays.
        Enhanced to show trail quality with brightness.
        Returns:
            Tuple[int, int, int]: (R, G, B) color
        """
        # Decay fraction: 0 (fresh) -> 1 (fully decayed)
        decay_fraction = 1.0 - max(0.0, min(self._strength / self._max_strength, 1.0))
        
        # Base color based on type
        if self._type == PheromoneType.FOOD_TRAIL:
            r = int(255 * decay_fraction)
            g = int(255 * (1.0 - decay_fraction))
            b = 0
        elif self._type == PheromoneType.HOME_TRAIL:
            r = 100
            g = 200
            b = 255
        else:  # DANGER
            r = 255
            g = 100
            b = 100
        
        # Apply trail quality brightness boost
        quality_boost = min(1.5, self._trail_quality)
        r = min(255, int(r * quality_boost))
        g = min(255, int(g * quality_boost))
        b = min(255, int(b * quality_boost))
        
        return (r, g, b)
    
    def update(self) -> bool:
        """
        Update the pheromone with diffusion mechanics.
        The pheromone spreads outward while the center dissipates.
        Returns:
            bool: True if pheromone should be removed (strength <= 0 or fully dissipated)
        """
        # Calculate decay rate based on trail quality (better trails decay slower)
        quality_decay_factor = max(0.3, 1.0 - (self._trail_quality - 1.0) * 0.2)
        effective_decay_rate = self._decay_rate * quality_decay_factor
        
        # Apply overall strength decay
        self._strength -= effective_decay_rate
        
        # Apply diffusion - expand outer radius
        if self._current_radius < self._max_radius:
            self._current_radius += self._diffusion_rate
            self._current_radius = min(self._current_radius, self._max_radius)
        
        # Apply dissipation - expand inner radius (hollow out center)
        # Inner radius grows slower than outer, creating an expanding ring
        if self._inner_radius < self._current_radius * 0.7:  # Inner can grow to 70% of outer
            self._inner_radius += self._dissipation_rate
            self._inner_radius = min(self._inner_radius, self._current_radius * 0.7)
        
        # Update concentration peak (where the pheromone is strongest)
        # Peak moves outward as the pheromone diffuses
        self._concentration_peak = (self._inner_radius + self._current_radius) / 2
        
        # Remove if strength depleted or ring width becomes negligible
        ring_width = self._current_radius - self._inner_radius
        return self._strength <= 0 or ring_width < 2.0
    
    def distance_to(self, position: Tuple[float, float]) -> float:
        """
        Calculate distance to a position.
        Args:
            position: Target position (x, y)
        Returns:
            float: Distance to the target
        """
        dx = position[0] - self._position[0]
        dy = position[1] - self._position[1]
        return np.sqrt(dx*dx + dy*dy)
    
    def is_within_range(self, position: Tuple[float, float]) -> bool:
        """
        Check if a position is within the pheromone's active influence area.
        Args:
            position: Position to check
        Returns:
            bool: True if position is within active ring area
        """
        distance = self.distance_to(position)
        # Position is in range if it's within the outer radius
        # (inner dissipated area still has weak influence)
        return distance <= self._current_radius
    
    def get_influence_strength(self, position: Tuple[float, float]) -> float:
        """
        Get the influence strength at a given position using ring-based diffusion model.
        Strongest at the concentration peak (middle of the ring), weaker at edges.
        Args:
            position: Position to check
        Returns:
            float: Influence strength (0 if outside radius or inside hollow center)
        """
        distance = self.distance_to(position)
        
        # Outside outer radius - no influence
        if distance > self._current_radius:
            return 0.0
        
        # Inside hollow center - reduced influence (dissipated)
        if distance < self._inner_radius:
            # Very weak residual scent in the dissipated center
            center_factor = 0.1 * (1.0 - distance / max(1.0, self._inner_radius))
            return self._strength * center_factor * self._trail_quality
        
        # Within the active ring - calculate ring-based influence
        ring_width = self._current_radius - self._inner_radius
        if ring_width <= 0:
            return 0.0
        
        # Distance from inner edge of ring (0 at inner, ring_width at outer)
        dist_from_inner = distance - self._inner_radius
        
        # Concentration profile: strongest at the middle of the ring
        # Uses a bell curve centered at ring midpoint
        ring_midpoint = ring_width / 2
        dist_from_peak = abs(dist_from_inner - ring_midpoint)
        
        # Gaussian-like falloff from peak
        peak_factor = np.exp(-(dist_from_peak ** 2) / (2 * (ring_width / 3) ** 2))
        
        # Apply trail quality factor
        return self._strength * peak_factor * self._trail_quality
    
    def __repr__(self):
        quality_info = f", quality={self._trail_quality:.2f}" if self._trail_quality > 1.0 else ""
        usage_info = f", uses={self._usage_count}" if self._usage_count > 0 else ""
        return f"Pheromone(pos={self._position}, type={self._type.name}, strength={self._strength:.1f}{quality_info}{usage_info})"


class PheromoneManager:
    """
    Manages all pheromones in the simulation with efficient spatial indexing.
    Enhanced with trail reinforcement and persistence mechanisms.
    """
    def __init__(self, world_bounds: Tuple[float, float, float, float] = (0, 0, 800, 600)):
        self._pheromones: List[Pheromone] = []
        self._world_bounds = world_bounds
        self._spatial_grid: Dict[Tuple[int, int], List[Pheromone]] = {}
        self._grid_size = 80  # Size of each grid cell (optimized for performance)
        

        
    def add_pheromone(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                     strength: float = 100.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0,
                     diffusion_rate: float = 2.5, max_radius: float = 80.0) -> Pheromone:
        """
        Add a new pheromone to the simulation with diffusion properties.
        The pheromone will spread outward over time while dissipating from the center.
        
        Args:
            position: Position of the pheromone
            pheromone_type: Type of pheromone
            strength: Initial strength
            decay_rate: Decay rate per tick
            radius_of_influence: Initial influence radius
            diffusion_rate: How fast the pheromone spreads outward per tick
            max_radius: Maximum radius the pheromone can spread to
        Returns:
            Pheromone: The created pheromone
        """
        pheromone = Pheromone(position, pheromone_type, strength, decay_rate, 
                             radius_of_influence, diffusion_rate, max_radius)
        
        self._pheromones.append(pheromone)
        self._add_to_spatial_grid(pheromone)
        return pheromone
    

    
    def remove_pheromone(self, pheromone: Pheromone):
        """
        Remove a pheromone from the simulation.
        Args:
            pheromone: The pheromone to remove
        """
        if pheromone in self._pheromones:
            self._pheromones.remove(pheromone)
            self._remove_from_spatial_grid(pheromone)
    
    def get_pheromone_direction(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                               radius: float = 50.0, mark_as_used: bool = False) -> Optional[Tuple[float, float]]:
        """
        Calculate the gradient direction of pheromones of a specific type.
        Enhanced with trail quality weighting.
        Args:
            position: Position to calculate gradient from
            pheromone_type: Type of pheromone to consider
            radius: Search radius
            mark_as_used: If True, mark pheromones as used (only set when actually following trail)
        Returns:
            Tuple[float, float] or None: Normalized direction vector, or None if no pheromones found
        """
        nearby_pheromones = self.get_pheromones_in_range(position, radius, pheromone_type)
        
        if not nearby_pheromones:
            return None
        
        # Calculate gradient vector with quality weighting
        gradient_x = 0.0
        gradient_y = 0.0
        total_weight = 0.0
        
        for pheromone in nearby_pheromones:
            distance = pheromone.distance_to(position)
            if distance == 0:
                continue
            
            # Calculate influence strength (already includes trail quality)
            influence = pheromone.get_influence_strength(position)
            
            # Additional quality weighting for better trails
            quality_weight = pheromone.trail_quality
            weighted_influence = influence * quality_weight
            
            # Calculate direction vector (from position to pheromone)
            dx = pheromone.position[0] - position[0]
            dy = pheromone.position[1] - position[1]
            
            # Normalize and weight by influence
            length = np.sqrt(dx*dx + dy*dy)
            gradient_x += (dx / length) * weighted_influence
            gradient_y += (dy / length) * weighted_influence
            total_weight += weighted_influence
            
            # Only mark pheromone as used if explicitly requested (when actually following)
            if mark_as_used:
                pheromone.mark_usage()
        
        # Normalize the gradient vector
        gradient_length = np.sqrt(gradient_x*gradient_x + gradient_y*gradient_y)
        if gradient_length > 0:
            return (gradient_x / gradient_length, gradient_y / gradient_length)
        
        return None
    
    def get_pheromones_in_range(self, position: Tuple[float, float], radius: float, 
                               pheromone_type: Optional[PheromoneType] = None) -> List[Pheromone]:
        """
        Get all pheromones within a specified range, optionally filtered by type.
        Args:
            position: Center position
            radius: Search radius
            pheromone_type: Optional filter for pheromone type
        Returns:
            List[Pheromone]: List of pheromones within range
        """
        pheromones_in_range = []
        nearby_cells = self._get_nearby_cells(position, radius)
        
        for cell_key in nearby_cells:
            if cell_key in self._spatial_grid:
                for pheromone in self._spatial_grid[cell_key]:
                    if pheromone_type is not None and pheromone.type != pheromone_type:
                        continue
                    
                    if pheromone.is_within_range(position) and pheromone.distance_to(position) <= radius:
                        pheromones_in_range.append(pheromone)
        
        return pheromones_in_range
    
    def get_total_strength(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                          radius: float = 50.0, mark_as_used: bool = False) -> float:
        """
        Get the total pheromone strength at a position for a specific type.
        Enhanced with trail quality weighting.
        Args:
            position: Position to check
            pheromone_type: Type of pheromone
            radius: Search radius
            mark_as_used: If True, mark pheromones as used (only set when actually using the info)
        Returns:
            float: Total pheromone strength (weighted by trail quality)
        """
        nearby_pheromones = self.get_pheromones_in_range(position, radius, pheromone_type)
        total_strength = 0.0
        
        for pheromone in nearby_pheromones:
            # Get influence strength (already includes trail quality)
            influence = pheromone.get_influence_strength(position)
            # Additional quality boost for high-quality trails
            quality_boost = min(2.0, pheromone.trail_quality)
            total_strength += influence * quality_boost
            
            # Only mark pheromone as used if explicitly requested
            if mark_as_used:
                pheromone.mark_usage()
        
        return total_strength
    
    def update_all(self):
        """
        Update all pheromones (decay and remove depleted ones).
        Called each simulation tick.
        """
        pheromones_to_remove = []
        
        for pheromone in self._pheromones:
            # Update pheromone (decay)
            if pheromone.update():  # Returns True if should be removed
                pheromones_to_remove.append(pheromone)
        
        # Remove depleted pheromones
        for pheromone in pheromones_to_remove:
            self.remove_pheromone(pheromone)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about all pheromones.
        Enhanced with trail quality and usage statistics.
        Returns:
            dict: Statistics including total pheromones, types, spread info, quality metrics, etc.
        """
        total_pheromones = len(self._pheromones)
        type_counts = {}
        total_strength = 0.0
        total_usage = 0
        total_quality = 0.0
        high_quality_trails = 0  # Trails with quality > 1.5
        
        for pheromone in self._pheromones:
            pheromone_type = pheromone.type.name
            type_counts[pheromone_type] = type_counts.get(pheromone_type, 0) + 1
            total_strength += pheromone.strength
            total_usage += pheromone.usage_count
            total_quality += pheromone.trail_quality
            
            if pheromone.trail_quality > 1.5:
                high_quality_trails += 1
        
        return {
            'total_pheromones': total_pheromones,
            'type_counts': type_counts,
            'total_strength': total_strength,
            'average_strength': total_strength / total_pheromones if total_pheromones > 0 else 0,
            'total_usage': total_usage,
            'average_usage': total_usage / total_pheromones if total_pheromones > 0 else 0,
            'average_quality': total_quality / total_pheromones if total_pheromones > 0 else 0,
            'high_quality_trails': high_quality_trails
        }
    
    def clear_all(self):
        """Remove all pheromones from the simulation."""
        self._pheromones.clear()
        self._spatial_grid.clear()
    

    
    def _get_cell_key(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Get the spatial grid cell key for a position."""
        x, y = position
        cell_x = int(x // self._grid_size)
        cell_y = int(y // self._grid_size)
        return (cell_x, cell_y)
    
    def _get_nearby_cells(self, position: Tuple[float, float], radius: float) -> set:
        """Get all cell keys that might contain pheromones within range."""
        center_cell = self._get_cell_key(position)
        cells_in_range = set()
        
        # Calculate how many cells we need to check
        cells_needed = int(radius // self._grid_size) + 1
        
        for dx in range(-cells_needed, cells_needed + 1):
            for dy in range(-cells_needed, cells_needed + 1):
                cell_key = (center_cell[0] + dx, center_cell[1] + dy)
                cells_in_range.add(cell_key)
        
        return cells_in_range
    
    def _add_to_spatial_grid(self, pheromone: Pheromone):
        """Add a pheromone to the spatial grid."""
        cell_key = self._get_cell_key(pheromone.position)
        if cell_key not in self._spatial_grid:
            self._spatial_grid[cell_key] = []
        self._spatial_grid[cell_key].append(pheromone)
    
    def _remove_from_spatial_grid(self, pheromone: Pheromone):
        """Remove a pheromone from the spatial grid."""
        cell_key = self._get_cell_key(pheromone.position)
        if cell_key in self._spatial_grid:
            if pheromone in self._spatial_grid[cell_key]:
                self._spatial_grid[cell_key].remove(pheromone)
            if not self._spatial_grid[cell_key]:  # Remove empty cells
                del self._spatial_grid[cell_key]

# Example usage:
# pheromone_manager = PheromoneManager(world_bounds=(0, 0, 800, 600))
# pheromone_manager.add_pheromone((100, 100), PheromoneType.FOOD_TRAIL, strength=50.0)
# direction = pheromone_manager.get_pheromone_direction((150, 150), PheromoneType.FOOD_TRAIL)
# if direction:
#     print(f"Pheromone gradient direction: {direction}")
