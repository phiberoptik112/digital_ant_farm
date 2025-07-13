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
    """
    def __init__(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                 strength: float = 100.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0):
        self._position = position  # (x, y)
        self._type = pheromone_type
        self._strength = strength
        self._max_strength = strength
        self._decay_rate = decay_rate  # Strength lost per tick
        self._creation_time = time.time()
        self._radius_of_influence = radius_of_influence  # Radius where this pheromone affects ants
        
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
        """Get the radius of influence for this pheromone."""
        return self._radius_of_influence
    
    @property
    def age(self) -> float:
        """Get the age of the pheromone in seconds."""
        return time.time() - self._creation_time
    
    def update(self) -> bool:
        """
        Update the pheromone (decay strength).
        Returns:
            bool: True if pheromone should be removed (strength <= 0)
        """
        self._strength -= self._decay_rate
        return self._strength <= 0
    
    def reinforce(self, additional_strength: float):
        """
        Reinforce the pheromone with additional strength.
        Args:
            additional_strength: Amount to add to current strength
        """
        self._strength = min(self._max_strength, self._strength + additional_strength)
    
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
        Check if a position is within the pheromone's influence radius.
        Args:
            position: Position to check
        Returns:
            bool: True if position is within influence radius
        """
        return self.distance_to(position) <= self._radius_of_influence
    
    def get_influence_strength(self, position: Tuple[float, float]) -> float:
        """
        Get the influence strength at a given position (decreases with distance).
        Args:
            position: Position to check
        Returns:
            float: Influence strength (0 if outside radius)
        """
        distance = self.distance_to(position)
        if distance > self._radius_of_influence:
            return 0.0
        
        # Linear falloff with distance
        influence = 1.0 - (distance / self._radius_of_influence)
        return self._strength * influence
    
    def __repr__(self):
        return f"Pheromone(pos={self._position}, type={self._type.name}, strength={self._strength:.1f})"


class PheromoneManager:
    """
    Manages all pheromones in the simulation with efficient spatial indexing.
    """
    def __init__(self, world_bounds: Tuple[float, float, float, float] = (0, 0, 800, 600)):
        self._pheromones: List[Pheromone] = []
        self._world_bounds = world_bounds
        self._spatial_grid: Dict[Tuple[int, int], List[Pheromone]] = {}
        self._grid_size = 40  # Size of each grid cell (should be >= max pheromone radius)
        
    def add_pheromone(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                     strength: float = 100.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0) -> Pheromone:
        """
        Add a new pheromone to the simulation.
        Args:
            position: Position of the pheromone
            pheromone_type: Type of pheromone
            strength: Initial strength
            decay_rate: Decay rate per tick
            radius_of_influence: Influence radius
        Returns:
            Pheromone: The created pheromone
        """
        pheromone = Pheromone(position, pheromone_type, strength, decay_rate, radius_of_influence)
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
                               radius: float = 50.0) -> Optional[Tuple[float, float]]:
        """
        Calculate the gradient direction of pheromones of a specific type.
        Args:
            position: Position to calculate gradient from
            pheromone_type: Type of pheromone to consider
            radius: Search radius
        Returns:
            Tuple[float, float] or None: Normalized direction vector, or None if no pheromones found
        """
        nearby_pheromones = self.get_pheromones_in_range(position, radius, pheromone_type)
        
        if not nearby_pheromones:
            return None
        
        # Calculate gradient vector
        gradient_x = 0.0
        gradient_y = 0.0
        
        for pheromone in nearby_pheromones:
            distance = pheromone.distance_to(position)
            if distance == 0:
                continue
            
            # Calculate influence strength
            influence = pheromone.get_influence_strength(position)
            
            # Calculate direction vector (from position to pheromone)
            dx = pheromone.position[0] - position[0]
            dy = pheromone.position[1] - position[1]
            
            # Normalize and weight by influence
            length = np.sqrt(dx*dx + dy*dy)
            gradient_x += (dx / length) * influence
            gradient_y += (dy / length) * influence
        
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
                          radius: float = 50.0) -> float:
        """
        Get the total pheromone strength at a position for a specific type.
        Args:
            position: Position to check
            pheromone_type: Type of pheromone
            radius: Search radius
        Returns:
            float: Total pheromone strength
        """
        nearby_pheromones = self.get_pheromones_in_range(position, radius, pheromone_type)
        return sum(pheromone.get_influence_strength(position) for pheromone in nearby_pheromones)
    
    def update_all(self):
        """
        Update all pheromones (decay and remove depleted ones).
        Called each simulation tick.
        """
        pheromones_to_remove = []
        
        for pheromone in self._pheromones:
            if pheromone.update():  # Returns True if should be removed
                pheromones_to_remove.append(pheromone)
        
        # Remove depleted pheromones
        for pheromone in pheromones_to_remove:
            self.remove_pheromone(pheromone)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about all pheromones.
        Returns:
            dict: Statistics including total pheromones, types, etc.
        """
        total_pheromones = len(self._pheromones)
        type_counts = {}
        total_strength = 0.0
        
        for pheromone in self._pheromones:
            pheromone_type = pheromone.type.name
            type_counts[pheromone_type] = type_counts.get(pheromone_type, 0) + 1
            total_strength += pheromone.strength
        
        return {
            'total_pheromones': total_pheromones,
            'type_counts': type_counts,
            'total_strength': total_strength,
            'average_strength': total_strength / total_pheromones if total_pheromones > 0 else 0
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
