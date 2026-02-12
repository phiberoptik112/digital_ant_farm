from typing import Tuple, List, Dict, Optional
import numpy as np
import time
from .pheromone import Pheromone, PheromoneType

class GroundCell:
    """
    Represents a single cell of ground that can hold pheromone deposits.
    Ground cells have properties that affect pheromone persistence.
    """
    def __init__(self, position: Tuple[float, float], cell_size: float = 10.0):
        self.position = position  # Center of the cell
        self.cell_size = cell_size
        self.pheromones: List[Pheromone] = []
        
        # Ground properties that affect pheromone persistence
        self.moisture = np.random.uniform(0.3, 0.8)  # 0-1, affects decay rate
        self.porosity = np.random.uniform(0.2, 0.7)  # 0-1, affects absorption
        self.temperature = np.random.uniform(0.6, 1.0)  # 0-1, affects evaporation
        self.roughness = np.random.uniform(0.1, 0.9)  # 0-1, affects spread
        
        # Time tracking for environmental changes
        self.last_update = time.time()
    
    def add_pheromone(self, pheromone: Pheromone):
        """Add a pheromone to this ground cell."""
        self.pheromones.append(pheromone)
    
    def remove_pheromone(self, pheromone: Pheromone):
        """Remove a pheromone from this ground cell."""
        if pheromone in self.pheromones:
            self.pheromones.remove(pheromone)
    
    def get_total_strength(self, pheromone_type: PheromoneType) -> float:
        """Get total pheromone strength of a specific type in this cell."""
        total = 0.0
        for pheromone in self.pheromones:
            if pheromone.type == pheromone_type:
                total += pheromone.strength
        return total
    
    def get_pheromones_of_type(self, pheromone_type: PheromoneType) -> List[Pheromone]:
        """Get all pheromones of a specific type in this cell."""
        return [p for p in self.pheromones if p.type == pheromone_type]
    
    def update(self, delta_time: float = 1.0):
        """
        Update ground cell properties and pheromone decay rates.
        Ground conditions affect how quickly pheromones decay.
        """
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        # Slowly change ground properties over time (simulate environmental changes)
        if time_diff > 10.0:  # Update every 10 seconds
            self.moisture += np.random.uniform(-0.05, 0.05)
            self.moisture = np.clip(self.moisture, 0.1, 1.0)
            
            self.temperature += np.random.uniform(-0.02, 0.02)
            self.temperature = np.clip(self.temperature, 0.5, 1.0)
            
            self.last_update = current_time
        
        # Update pheromones with ground-modified decay and diffusion rates
        # Note: Actual removal is handled by GroundSystem.update_all() to keep lists in sync
        for pheromone in self.pheromones:
            # Calculate ground-modified rates
            ground_decay_multiplier = self._calculate_decay_multiplier()
            ground_diffusion_multiplier = self._calculate_diffusion_multiplier()
            
            # Apply modified decay
            modified_decay_rate = pheromone._decay_rate * ground_decay_multiplier
            pheromone._strength -= modified_decay_rate * delta_time
            
            # Apply diffusion - expand outer radius
            if pheromone._current_radius < pheromone._max_radius:
                modified_diffusion = pheromone._diffusion_rate * ground_diffusion_multiplier
                pheromone._current_radius += modified_diffusion * delta_time
                pheromone._current_radius = min(pheromone._current_radius, pheromone._max_radius)
            
            # Apply dissipation - expand inner radius (hollow out center)
            if pheromone._inner_radius < pheromone._current_radius * 0.7:
                modified_dissipation = pheromone._dissipation_rate * ground_diffusion_multiplier
                pheromone._inner_radius += modified_dissipation * delta_time
                pheromone._inner_radius = min(pheromone._inner_radius, pheromone._current_radius * 0.7)
            
            # Update concentration peak
            pheromone._concentration_peak = (pheromone._inner_radius + pheromone._current_radius) / 2
    
    def _calculate_decay_multiplier(self) -> float:
        """
        Calculate how ground properties affect pheromone decay.
        Lower values = slower decay (better persistence)
        Higher values = faster decay
        """
        # Moisture: Higher moisture = slower decay (pheromones dissolve less quickly)
        moisture_factor = 1.0 - (self.moisture * 0.3)  # 0.7 to 1.0
        
        # Temperature: Higher temperature = faster decay (more evaporation)
        temperature_factor = 0.8 + (self.temperature * 0.4)  # 0.8 to 1.2
        
        # Porosity: Higher porosity = slower decay (pheromones absorbed into ground)
        porosity_factor = 1.0 - (self.porosity * 0.2)  # 0.8 to 1.0
        
        return moisture_factor * temperature_factor * porosity_factor
    
    def _calculate_diffusion_multiplier(self) -> float:
        """
        Calculate how ground properties affect pheromone diffusion/spreading.
        Higher values = faster spreading
        Lower values = slower spreading
        """
        # Temperature: Higher temperature = faster diffusion
        temperature_factor = 0.6 + (self.temperature * 0.8)  # 0.6 to 1.4
        
        # Roughness: Higher roughness = slower diffusion (more obstacles)
        roughness_factor = 1.2 - (self.roughness * 0.5)  # 0.7 to 1.2
        
        # Porosity: Higher porosity = slightly faster diffusion (more pathways)
        porosity_factor = 0.9 + (self.porosity * 0.2)  # 0.9 to 1.1
        
        return temperature_factor * roughness_factor * porosity_factor
    
    def get_ground_color(self) -> Tuple[int, int, int]:
        """Get the visual color of this ground cell based on its properties."""
        # Base brown color
        base_r, base_g, base_b = 139, 69, 19
        
        # Modify based on moisture (darker when wet)
        moisture_factor = 1.0 - (self.moisture * 0.3)
        
        # Modify based on temperature (warmer = more reddish)
        temp_factor = 1.0 + (self.temperature - 0.8) * 0.2
        
        r = int(base_r * moisture_factor * temp_factor)
        g = int(base_g * moisture_factor)
        b = int(base_b * moisture_factor)
        
        return (r, g, b)

class GroundSystem:
    """
    Manages the ground grid and pheromone deposits with enhanced persistence.
    Ground cells have properties that affect pheromone behavior.
    """
    def __init__(self, world_bounds: Tuple[float, float, float, float], cell_size: float = 10.0):
        self.world_bounds = world_bounds
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_width = int((world_bounds[2] - world_bounds[0]) / cell_size) + 1
        self.grid_height = int((world_bounds[3] - world_bounds[1]) / cell_size) + 1
        
        # Initialize ground grid
        self.ground_grid: Dict[Tuple[int, int], GroundCell] = {}
        self._initialize_ground_grid()
        
        # Track all pheromones for compatibility with existing code
        self.all_pheromones: List[Pheromone] = []
    
    def _initialize_ground_grid(self):
        """Initialize the ground grid with cells."""
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                world_x = self.world_bounds[0] + x * self.cell_size
                world_y = self.world_bounds[1] + y * self.cell_size
                cell_key = (x, y)
                self.ground_grid[cell_key] = GroundCell((world_x, world_y), self.cell_size)
    
    def _get_cell_key(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Get the grid cell key for a world position."""
        x = int((position[0] - self.world_bounds[0]) / self.cell_size)
        y = int((position[1] - self.world_bounds[1]) / self.cell_size)
        return (x, y)
    
    def add_pheromone(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                     strength: float = 100.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0,
                     diffusion_rate: float = 2.5, max_radius: float = 80.0) -> Pheromone:
        """
        Add a pheromone to the ground system with diffusion properties.
        The pheromone will spread outward over time while dissipating from the center.
        
        Args:
            position: Position to place the pheromone
            pheromone_type: Type of pheromone
            strength: Initial strength
            decay_rate: How fast the overall strength decreases
            radius_of_influence: Initial radius of the pheromone
            diffusion_rate: How fast the pheromone spreads outward per tick
            max_radius: Maximum radius the pheromone can spread to
        """
        # Create the pheromone with diffusion parameters
        pheromone = Pheromone(position, pheromone_type, strength, decay_rate, 
                             radius_of_influence, diffusion_rate, max_radius)
        
        # Add to ground cell
        cell_key = self._get_cell_key(position)
        if cell_key in self.ground_grid:
            self.ground_grid[cell_key].add_pheromone(pheromone)
        
        # Track in all pheromones list for compatibility
        self.all_pheromones.append(pheromone)
        
        return pheromone
    
    def remove_pheromone(self, pheromone: Pheromone):
        """Remove a pheromone from the ground system."""
        # Remove from ground cell
        cell_key = self._get_cell_key(pheromone.position)
        if cell_key in self.ground_grid:
            self.ground_grid[cell_key].remove_pheromone(pheromone)
        
        # Remove from tracking list
        if pheromone in self.all_pheromones:
            self.all_pheromones.remove(pheromone)
    
    def get_pheromones_in_range(self, position: Tuple[float, float], radius: float, 
                               pheromone_type: Optional[PheromoneType] = None) -> List[Pheromone]:
        """Get all pheromones within range of a position."""
        pheromones_in_range = []
        
        # Get nearby cells
        center_cell = self._get_cell_key(position)
        cells_needed = int(radius / self.cell_size) + 2
        
        for dx in range(-cells_needed, cells_needed + 1):
            for dy in range(-cells_needed, cells_needed + 1):
                cell_key = (center_cell[0] + dx, center_cell[1] + dy)
                if cell_key in self.ground_grid:
                    cell = self.ground_grid[cell_key]
                    
                    # Get pheromones from this cell
                    cell_pheromones = cell.pheromones
                    if pheromone_type is not None:
                        cell_pheromones = cell.get_pheromones_of_type(pheromone_type)
                    
                    # Check distance for each pheromone
                    for pheromone in cell_pheromones:
                        distance = pheromone.distance_to(position)
                        if distance <= radius:
                            pheromones_in_range.append(pheromone)
        
        return pheromones_in_range
    
    def get_pheromone_direction(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                               radius: float = 50.0, mark_as_used: bool = False) -> Optional[Tuple[float, float]]:
        """
        Calculate the gradient direction of pheromones of a specific type.
        
        Args:
            position: Current position to calculate gradient from
            pheromone_type: Type of pheromone to consider
            radius: Search radius
            mark_as_used: If True, mark pheromones as used (only set when actually following trail)
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
    
    def get_total_strength(self, position: Tuple[float, float], pheromone_type: PheromoneType, 
                          radius: float = 50.0, mark_as_used: bool = False) -> float:
        """
        Get the total pheromone strength at a position for a specific type.
        
        Args:
            position: Position to check
            pheromone_type: Type of pheromone
            radius: Search radius
            mark_as_used: If True, mark pheromones as used (only set when actually using the info)
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
    
    def update_all(self, delta_time: float = 1.0):
        """Update all ground cells and their pheromones."""
        # Update all ground cells (applies decay and diffusion to pheromones)
        for cell in self.ground_grid.values():
            cell.update(delta_time)
        
        # Collect and remove depleted or fully diffused pheromones
        pheromones_to_remove = []
        for p in self.all_pheromones:
            # Remove if strength depleted
            if p._strength <= 0:
                pheromones_to_remove.append(p)
            # Remove if ring width becomes negligible (fully diffused)
            elif (p._current_radius - p._inner_radius) < 2.0:
                pheromones_to_remove.append(p)
        
        for pheromone in pheromones_to_remove:
            self.remove_pheromone(pheromone)
    
    def get_statistics(self) -> dict:
        """Get statistics about all pheromones in the ground system."""
        total_pheromones = len(self.all_pheromones)
        type_counts = {}
        total_strength = 0.0
        total_usage = 0
        total_quality = 0.0
        high_quality_trails = 0
        total_diffusion = 0.0
        avg_ring_width = 0.0
        
        for pheromone in self.all_pheromones:
            pheromone_type = pheromone.type.name
            type_counts[pheromone_type] = type_counts.get(pheromone_type, 0) + 1
            total_strength += pheromone.strength
            total_usage += pheromone.usage_count
            total_diffusion += pheromone.diffusion_progress
            avg_ring_width += pheromone.ring_width
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
            'high_quality_trails': high_quality_trails,
            'average_diffusion': total_diffusion / total_pheromones if total_pheromones > 0 else 0,
            'average_ring_width': avg_ring_width / total_pheromones if total_pheromones > 0 else 0
        }
    
    def clear_all(self):
        """Remove all pheromones from the ground system."""
        self.all_pheromones.clear()
        for cell in self.ground_grid.values():
            cell.pheromones.clear()
    
    def get_ground_cell_at(self, position: Tuple[float, float]) -> Optional[GroundCell]:
        """Get the ground cell at a specific position."""
        cell_key = self._get_cell_key(position)
        return self.ground_grid.get(cell_key) 