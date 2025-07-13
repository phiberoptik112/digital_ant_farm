from typing import Tuple, Optional
import numpy as np

class FoodSource:
    """
    Represents a food source in the simulation with position, amount, and depletion mechanics.
    """
    def __init__(self, position: Tuple[float, float], amount: float = 100.0, 
                 max_amount: float = 100.0, depletion_rate: float = 1.0):
        self._position = position  # (x, y)
        self._amount = min(amount, max_amount)  # Current food amount
        self._max_amount = max_amount  # Maximum capacity
        self._depletion_rate = depletion_rate  # Amount removed per collection
        self._regeneration_rate = 0.0  # Amount regenerated per tick
        self._regeneration_cooldown = 0  # Ticks before regeneration starts
        self._max_regeneration_cooldown = 300  # 5 seconds at 60 FPS
        self._is_depleted = False
        
        # Visual properties
        self._base_radius = 10.0  # Base visual radius
        self._min_radius = 3.0   # Minimum radius when nearly depleted

    @property
    def position(self) -> Tuple[float, float]:
        """Get the food source position."""
        return self._position

    @property
    def amount(self) -> float:
        """Get the current food amount."""
        return self._amount

    @property
    def max_amount(self) -> float:
        """Get the maximum food capacity."""
        return self._max_amount

    @property
    def is_depleted(self) -> bool:
        """Check if the food source is depleted."""
        return self._is_depleted

    @property
    def depletion_percentage(self) -> float:
        """Get the percentage of food remaining (0-100)."""
        return (self._amount / self._max_amount) * 100.0

    @property
    def visual_radius(self) -> float:
        """Get the visual radius based on current amount."""
        if self._is_depleted:
            return 0.0
        
        ratio = self._amount / self._max_amount
        return self._min_radius + (self._base_radius - self._min_radius) * ratio

    def collect_food(self, amount: float = None) -> float:
        """
        Collect food from this source.
        Args:
            amount: Amount to collect (uses depletion_rate if None)
        Returns:
            float: Actual amount collected
        """
        if self._is_depleted:
            return 0.0
        
        if amount is None:
            amount = self._depletion_rate
        
        actual_amount = min(amount, self._amount)
        self._amount -= actual_amount
        
        # Check if depleted
        if self._amount <= 0:
            self._amount = 0
            self._is_depleted = True
            self._regeneration_cooldown = self._max_regeneration_cooldown
        
        return actual_amount

    def add_food(self, amount: float) -> float:
        """
        Add food to this source (for regeneration or manual addition).
        Args:
            amount: Amount to add
        Returns:
            float: Actual amount added
        """
        if self._is_depleted:
            self._is_depleted = False
        
        space_available = self._max_amount - self._amount
        actual_amount = min(amount, space_available)
        self._amount += actual_amount
        
        return actual_amount

    def set_regeneration_rate(self, rate: float):
        """Set the regeneration rate (amount per tick)."""
        self._regeneration_rate = max(0.0, rate)

    def update(self):
        """
        Update the food source (called each simulation tick).
        Handles regeneration and cooldown timers.
        """
        if self._regeneration_cooldown > 0:
            self._regeneration_cooldown -= 1
            return
        
        if self._is_depleted and self._regeneration_rate > 0:
            self.add_food(self._regeneration_rate)

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

    def is_within_range(self, position: Tuple[float, float], range_radius: float) -> bool:
        """
        Check if a position is within range of this food source.
        Args:
            position: Position to check
            range_radius: Detection radius
        Returns:
            bool: True if position is within range
        """
        return self.distance_to(position) <= range_radius

    def __repr__(self):
        return f"FoodSource(pos={self._position}, amount={self._amount:.1f}/{self._max_amount}, depleted={self._is_depleted})"


class FoodManager:
    """
    Manages all food sources in the simulation with efficient spatial queries.
    """
    def __init__(self, world_bounds: Tuple[float, float, float, float] = (0, 0, 800, 600)):
        self._food_sources = []  # List of all food sources
        self._world_bounds = world_bounds
        self._spatial_grid = {}  # Simple spatial hash for efficient queries
        self._grid_size = 50  # Size of each grid cell
        
    def add_food_source(self, position: Tuple[float, float], amount: float = 100.0, 
                       max_amount: float = 100.0, depletion_rate: float = 1.0) -> FoodSource:
        """
        Add a new food source to the simulation.
        Args:
            position: Position of the food source
            amount: Initial food amount
            max_amount: Maximum food capacity
            depletion_rate: Amount removed per collection
        Returns:
            FoodSource: The created food source
        """
        food_source = FoodSource(position, amount, max_amount, depletion_rate)
        self._food_sources.append(food_source)
        self._add_to_spatial_grid(food_source)
        return food_source

    def remove_food_source(self, food_source: FoodSource):
        """
        Remove a food source from the simulation.
        Args:
            food_source: The food source to remove
        """
        if food_source in self._food_sources:
            self._food_sources.remove(food_source)
            self._remove_from_spatial_grid(food_source)

    def get_nearest_food(self, position: Tuple[float, float], max_distance: float = float('inf')) -> Optional[FoodSource]:
        """
        Find the nearest non-depleted food source to a position.
        Args:
            position: Position to search from
            max_distance: Maximum search distance
        Returns:
            FoodSource or None: Nearest food source within range
        """
        nearest_food = None
        nearest_distance = max_distance
        
        # Handle infinite max_distance case
        if max_distance == float('inf'):
            # Search all food sources
            for food_source in self._food_sources:
                if food_source.is_depleted:
                    continue
                
                distance = food_source.distance_to(position)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_food = food_source
        else:
            # Use spatial grid for efficient querying
            nearby_cells = self._get_nearby_cells(position, max_distance)
            
            for cell_key in nearby_cells:
                if cell_key in self._spatial_grid:
                    for food_source in self._spatial_grid[cell_key]:
                        if food_source.is_depleted:
                            continue
                        
                        distance = food_source.distance_to(position)
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_food = food_source
        
        return nearest_food

    def get_food_in_range(self, position: Tuple[float, float], range_radius: float) -> list:
        """
        Get all food sources within a specified range.
        Args:
            position: Center position
            range_radius: Search radius
        Returns:
            list: List of food sources within range
        """
        food_in_range = []
        nearby_cells = self._get_nearby_cells(position, range_radius)
        
        for cell_key in nearby_cells:
            if cell_key in self._spatial_grid:
                for food_source in self._spatial_grid[cell_key]:
                    if not food_source.is_depleted and food_source.is_within_range(position, range_radius):
                        food_in_range.append(food_source)
        
        return food_in_range

    def generate_random_food(self, num_sources: int = 5, min_amount: float = 50.0, 
                           max_amount: float = 150.0, min_distance: float = 30.0):
        """
        Generate random food sources across the world.
        Args:
            num_sources: Number of food sources to generate
            min_amount: Minimum food amount
            max_amount: Maximum food amount
            min_distance: Minimum distance between food sources
        """
        x_min, y_min, x_max, y_max = self._world_bounds
        
        for _ in range(num_sources):
            attempts = 0
            max_attempts = 100
            
            while attempts < max_attempts:
                # Generate random position
                x = np.random.uniform(x_min + 20, x_max - 20)
                y = np.random.uniform(y_min + 20, y_max - 20)
                position = (x, y)
                
                # Check distance to existing food sources
                too_close = False
                for existing_food in self._food_sources:
                    if existing_food.distance_to(position) < min_distance:
                        too_close = True
                        break
                
                if not too_close:
                    # Create food source
                    amount = np.random.uniform(min_amount, max_amount)
                    self.add_food_source(position, amount, amount)
                    break
                
                attempts += 1

    def update_all(self):
        """Update all food sources (called each simulation tick)."""
        for food_source in self._food_sources:
            food_source.update()

    def cleanup_depleted(self):
        """Remove permanently depleted food sources to save memory."""
        depleted_sources = [food for food in self._food_sources if food.is_depleted and food._regeneration_rate == 0]
        for food_source in depleted_sources:
            self.remove_food_source(food_source)

    def get_statistics(self) -> dict:
        """
        Get statistics about all food sources.
        Returns:
            dict: Statistics including total sources, total food, etc.
        """
        total_sources = len(self._food_sources)
        active_sources = len([f for f in self._food_sources if not f.is_depleted])
        total_food = sum(f.amount for f in self._food_sources)
        total_capacity = sum(f.max_amount for f in self._food_sources)
        
        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'depleted_sources': total_sources - active_sources,
            'total_food': total_food,
            'total_capacity': total_capacity,
            'utilization_percentage': (total_food / total_capacity * 100) if total_capacity > 0 else 0
        }

    def _get_cell_key(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Get the spatial grid cell key for a position."""
        x, y = position
        cell_x = int(x // self._grid_size)
        cell_y = int(y // self._grid_size)
        return (cell_x, cell_y)

    def _get_nearby_cells(self, position: Tuple[float, float], range_radius: float) -> set:
        """Get all cell keys that might contain food sources within range."""
        center_cell = self._get_cell_key(position)
        cells_in_range = set()
        
        # Calculate how many cells we need to check
        cells_needed = int(range_radius // self._grid_size) + 1
        
        for dx in range(-cells_needed, cells_needed + 1):
            for dy in range(-cells_needed, cells_needed + 1):
                cell_key = (center_cell[0] + dx, center_cell[1] + dy)
                cells_in_range.add(cell_key)
        
        return cells_in_range

    def _add_to_spatial_grid(self, food_source: FoodSource):
        """Add a food source to the spatial grid."""
        cell_key = self._get_cell_key(food_source.position)
        if cell_key not in self._spatial_grid:
            self._spatial_grid[cell_key] = []
        self._spatial_grid[cell_key].append(food_source)

    def _remove_from_spatial_grid(self, food_source: FoodSource):
        """Remove a food source from the spatial grid."""
        cell_key = self._get_cell_key(food_source.position)
        if cell_key in self._spatial_grid:
            if food_source in self._spatial_grid[cell_key]:
                self._spatial_grid[cell_key].remove(food_source)
            if not self._spatial_grid[cell_key]:  # Remove empty cells
                del self._spatial_grid[cell_key]

# Example usage:
# food_manager = FoodManager(world_bounds=(0, 0, 800, 600))
# food_manager.generate_random_food(num_sources=10)
# nearest_food = food_manager.get_nearest_food((100, 100))
# if nearest_food:
#     collected = nearest_food.collect_food(5.0)
