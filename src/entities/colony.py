from typing import Tuple, List, Dict, Optional
import numpy as np
import time
from entities.ant import Ant, AntState, AntCaste
from entities.pheromone import PheromoneManager, PheromoneType

class Colony:
    """
    Represents an ant colony with central management, spawning, and resource tracking.
    """
    def __init__(self, position: Tuple[float, float], radius: float = 30.0, 
                 max_population: int = 100, spawn_rate: float = 0.1):
        self._position = position  # (x, y) center of the colony
        self._radius = radius  # Physical radius of the colony
        self._max_population = max_population
        self._spawn_rate = spawn_rate  # Probability of spawning per tick
        self._spawn_cooldown = 0  # Ticks between spawns
        self._min_spawn_cooldown = 60  # Minimum ticks between spawns (1 second at 60 FPS)
        
        # Resource management
        self._food_storage = 54000.0 # setting this to give the colony an initial food supply of 15 hours of food
        self._max_food_storage = 100000.0
        self._food_consumption_rate = 0.1  # Food consumed per ant per tick
        
        # Population tracking
        self._ants: List[Ant] = []
        self._ant_lifespans: Dict[int, float] = {}  # Track when each ant was created
        self._max_ant_lifespan = 1800.0  # Maximum ant lifespan in seconds
        
        # Caste population tracking
        self._caste_populations: Dict[AntCaste, int] = {
            AntCaste.WORKER: 0,
            AntCaste.SOLDIER: 0,
            AntCaste.SCOUT: 0,
            AntCaste.NURSE: 0
        }
        
        # Statistics
        self._total_food_collected = 0.0
        self._total_ants_spawned = 0
        self._total_ants_died = 0
        self._creation_time = time.time()
        
        # Development and growth
        self._development_level = 1
        self._experience_points = 0.0
        self._health = 100.0
        self._max_health = 100.0
        
        # Associated managers (set externally)
        self._pheromone_manager: Optional[PheromoneManager] = None
        
        # World bounds for ants
        self._world_bounds = (0, 0, 800, 600)  # Default bounds, should be set externally
        
    @property
    def position(self) -> Tuple[float, float]:
        """Get the colony position."""
        return self._position
    
    @property
    def radius(self) -> float:
        """Get the colony radius."""
        return self._radius
    
    @property
    def population(self) -> int:
        """Get the current ant population."""
        return len(self._ants)
    
    @property
    def max_population(self) -> int:
        """Get the maximum population capacity."""
        return self._max_population
    
    @property
    def food_storage(self) -> float:
        """Get the current food storage amount."""
        return self._food_storage
    
    @property
    def max_food_storage(self) -> float:
        """Get the maximum food storage capacity."""
        return self._max_food_storage
    
    @property
    def health(self) -> float:
        """Get the colony health."""
        return self._health
    
    @property
    def development_level(self) -> int:
        """Get the colony development level."""
        return self._development_level
    
    def set_pheromone_manager(self, pheromone_manager: PheromoneManager):
        """Set the pheromone manager for this colony."""
        self._pheromone_manager = pheromone_manager
    
    def set_world_bounds(self, bounds: Tuple[float, float, float, float]):
        """
        Set the world boundaries for the colony and all its ants.
        Args:
            bounds: (x_min, y_min, x_max, y_max) boundaries
        """
        self._world_bounds = bounds
        # Update existing ants with new world bounds
        for ant in self._ants:
            ant.set_world_bounds(bounds)
    
    def spawn_ant(self, caste: AntCaste = AntCaste.WORKER) -> Optional[Ant]:
        """
        Spawn a new ant of a specific caste at the colony position.
        Args:
            caste: The caste of ant to spawn
        Returns:
            Ant or None: The spawned ant, or None if spawning failed
        """
        if self.population >= self._max_population:
            print(f"[DEBUG] Spawn failed: Colony at max population ({self._max_population})")
            return None
        
        # Check if we have enough food for this caste
        food_cost = self._get_caste_food_cost(caste)
        if self._food_storage < food_cost:
            print(f"[DEBUG] Spawn failed: Not enough food ({self._food_storage:.1f} < {food_cost:.1f}) for {caste.name}")
            return None
        
        # Create ant at colony position with slight random offset
        offset_x = np.random.uniform(-self._radius * 0.5, self._radius * 0.5)
        offset_y = np.random.uniform(-self._radius * 0.5, self._radius * 0.5)
        ant_position = (self._position[0] + offset_x, self._position[1] + offset_y)
        
        ant = Ant(position=ant_position, orientation=np.random.uniform(0, 360), caste=caste)
        ant.set_state(AntState.SEARCHING)
        
        # Set world bounds for the new ant
        ant.set_world_bounds(self._world_bounds)
        
        # Associate with pheromone manager if available
        if self._pheromone_manager:
            ant.set_pheromone_manager(self._pheromone_manager)
        
        # Add to colony
        self._ants.append(ant)
        self._ant_lifespans[id(ant)] = time.time()
        self._total_ants_spawned += 1
        
        # Update caste population
        self._caste_populations[caste] += 1
        
        # Consume food for spawning
        self._food_storage -= food_cost
        
        print(f"[DEBUG] Spawned {caste.name} ant (ID: {id(ant)}) at {ant_position}, food left: {self._food_storage:.1f}")
        
        return ant

    def spawn_multiple_ants(self, caste: AntCaste, count: int) -> List[Ant]:
        """
        Spawn multiple ants of a specific caste.
        Args:
            caste: The caste of ants to spawn
            count: Number of ants to spawn
        Returns:
            List[Ant]: List of successfully spawned ants
        """
        spawned_ants = []
        for _ in range(count):
            ant = self.spawn_ant(caste)
            if ant:
                spawned_ants.append(ant)
            else:
                break  # Stop if we can't spawn more
        return spawned_ants

    def _get_caste_food_cost(self, caste: AntCaste) -> float:
        """Get the food cost for spawning a specific caste."""
        costs = {
            AntCaste.WORKER: 10.0,
            AntCaste.SOLDIER: 15.0,
            AntCaste.SCOUT: 12.0,
            AntCaste.NURSE: 8.0
        }
        return costs.get(caste, 10.0)

    def can_spawn_caste(self, caste: AntCaste, count: int = 1) -> bool:
        """
        Check if we can spawn a specific number of ants of a given caste.
        Args:
            caste: The caste to check
            count: Number of ants to spawn
        Returns:
            bool: True if we can spawn the requested ants
        """
        if self.population + count > self._max_population:
            return False
        
        food_cost = self._get_caste_food_cost(caste) * count
        return self._food_storage >= food_cost

    def get_caste_population(self, caste: AntCaste) -> int:
        """Get the current population of a specific caste."""
        return self._caste_populations.get(caste, 0)

    def get_caste_populations(self) -> Dict[AntCaste, int]:
        """Get all caste populations."""
        return self._caste_populations.copy()
    
    def receive_food(self, amount: float) -> float:
        """
        Receive food from returning ants.
        Args:
            amount: Amount of food to add
        Returns:
            float: Actual amount added (may be limited by storage capacity)
        """
        space_available = self._max_food_storage - self._food_storage
        actual_amount = min(amount, space_available)
        self._food_storage += actual_amount
        self._total_food_collected += actual_amount
        
        # Gain experience for food collection
        self._experience_points += actual_amount * 0.1
        
        return actual_amount
    
    def update(self):
        """
        Update the colony (called each simulation tick).
        Handles spawning, food consumption, ant lifecycle, and development.
        """
        # Consume food for ant maintenance
        food_needed = self.population * self._food_consumption_rate
        if self._food_storage >= food_needed:
            self._food_storage -= food_needed
        else:
            # Not enough food - some ants may die
            self._food_storage = 0
            if np.random.random() < 0.01:  # 1% chance per tick of ant death
                print(f"[DEBUG] Starvation event: Not enough food for all ants. Attempting to remove a random ant.")
                self._remove_random_ant()
        
        # Handle ant spawning
        if self._spawn_cooldown <= 0:
            if np.random.random() < self._spawn_rate:
                self.spawn_ant()
                self._spawn_cooldown = self._min_spawn_cooldown
        else:
            self._spawn_cooldown -= 1
        
        # Update ant lifespans and remove old ants
        current_time = time.time()
        ants_to_remove = []
        
        for ant in self._ants:
            ant_id = id(ant)
            if ant_id in self._ant_lifespans:
                age = current_time - self._ant_lifespans[ant_id]
                if age > self._max_ant_lifespan:
                    print(f"[DEBUG] Ant (ID: {ant_id}, caste: {ant.caste.name}) died of old age (age: {age:.1f}s)")
                    ants_to_remove.append(ant)
        
        for ant in ants_to_remove:
            self._remove_ant(ant)
        
        # Check for development level up
        self._check_development()
    
    def _remove_ant(self, ant: Ant):
        """Remove an ant from the colony."""
        if ant in self._ants:
            self._ants.remove(ant)
            ant_id = id(ant)
            if ant_id in self._ant_lifespans:
                del self._ant_lifespans[ant_id]
            
            # Update caste population tracking
            if ant.caste in self._caste_populations:
                self._caste_populations[ant.caste] = max(0, self._caste_populations[ant.caste] - 1)
            
            self._total_ants_died += 1
            print(f"[DEBUG] Ant (ID: {ant_id}, caste: {ant.caste.name}) removed from colony. Total died: {self._total_ants_died}")
    
    def _remove_random_ant(self):
        """Remove a random ant from the colony (due to starvation)."""
        if self._ants:
            ant = np.random.choice(self._ants)
            print(f"[DEBUG] Ant (ID: {id(ant)}, caste: {ant.caste.name}) died of starvation.")
            self._remove_ant(ant)
    
    def _check_development(self):
        """Check if the colony should level up."""
        required_xp = self._development_level * 1000  # XP needed for next level
        
        if self._experience_points >= required_xp:
            self._development_level += 1
            self._experience_points -= required_xp
            
            # Benefits of leveling up
            self._max_population += 20
            self._max_food_storage += 200
            self._health = min(self._max_health, self._health + 20)
            self._spawn_rate += 0.02  # Slightly faster spawning
            print(f"[DEBUG] Colony leveled up! New level: {self._development_level}, max pop: {self._max_population}, max food: {self._max_food_storage}, spawn rate: {self._spawn_rate:.2f}")
    
    def get_ants_in_range(self, position: Tuple[float, float], radius: float) -> List[Ant]:
        """
        Get all ants within a specified range of a position.
        Args:
            position: Center position
            radius: Search radius
        Returns:
            List[Ant]: List of ants within range
        """
        ants_in_range = []
        for ant in self._ants:
            distance = ant.distance_to(position)
            if distance <= radius:
                ants_in_range.append(ant)
        return ants_in_range
    
    def get_nest_position(self) -> Tuple[float, float]:
        """Get the nest position (same as colony position)."""
        return self._position
    
    def is_ant_at_nest(self, ant: Ant, threshold: float = 10.0) -> bool:
        """
        Check if an ant is at the nest.
        Args:
            ant: The ant to check
            threshold: Distance threshold to consider "at nest"
        Returns:
            bool: True if ant is at the nest
        """
        return ant.distance_to(self._position) <= threshold
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive colony statistics.
        Returns:
            dict: Statistics including population, food, efficiency, etc.
        """
        current_time = time.time()
        colony_age = current_time - self._creation_time
        
        # Calculate efficiency metrics
        food_per_ant = self._total_food_collected / max(1, self._total_ants_spawned)
        survival_rate = 1.0 - (self._total_ants_died / max(1, self._total_ants_spawned))
        
        # Calculate current ant ages
        current_ages = []
        for ant in self._ants:
            ant_id = id(ant)
            if ant_id in self._ant_lifespans:
                age = current_time - self._ant_lifespans[ant_id]
                current_ages.append(age)
        
        avg_ant_age = np.mean(current_ages) if current_ages else 0.0
        
        return {
            'population': self.population,
            'max_population': self._max_population,
            'food_storage': self._food_storage,
            'max_food_storage': self._max_food_storage,
            'health': self._health,
            'development_level': self._development_level,
            'experience_points': self._experience_points,
            'total_food_collected': self._total_food_collected,
            'total_ants_spawned': self._total_ants_spawned,
            'total_ants_died': self._total_ants_died,
            'colony_age_seconds': colony_age,
            'food_per_ant': food_per_ant,
            'survival_rate': survival_rate,
            'average_ant_age': avg_ant_age,
            'spawn_rate': self._spawn_rate,
            'food_consumption_rate': self._food_consumption_rate,
            'caste_populations': self._caste_populations.copy()
        }
    
    def get_ants(self) -> List[Ant]:
        """Get all ants in the colony."""
        return self._ants.copy()
    
    def add_ant(self, ant: Ant):
        """Add an ant to the colony (for external management)."""
        if ant not in self._ants and self.population < self._max_population:
            self._ants.append(ant)
            self._ant_lifespans[id(ant)] = time.time()
            # Update caste population tracking
            if ant.caste in self._caste_populations:
                self._caste_populations[ant.caste] += 1
            if self._pheromone_manager:
                ant.set_pheromone_manager(self._pheromone_manager)
    
    def remove_ant(self, ant: Ant):
        """Remove an ant from the colony (for external management)."""
        self._remove_ant(ant)
    
    def reset_ants_to_nest(self):
        """Reset all ants to the nest position and set them to searching state."""
        for ant in self._ants:
            # Reset ant position to near colony center
            offset_x = np.random.uniform(-self._radius * 0.5, self._radius * 0.5)
            offset_y = np.random.uniform(-self._radius * 0.5, self._radius * 0.5)
            ant._position = (self._position[0] + offset_x, self._position[1] + offset_y)
            ant.set_state(AntState.SEARCHING)
            ant.set_carrying_food(False)
            # Ensure they have the correct world bounds
            ant.set_world_bounds(self._world_bounds)
    
    def __repr__(self):
        return f"Colony(pos={self._position}, pop={self.population}/{self._max_population}, food={self._food_storage:.1f}, level={self._development_level})"

# Example usage:
# colony = Colony(position=(400, 300), max_population=50)
# colony.set_pheromone_manager(pheromone_manager)
# ant = colony.spawn_ant()
# colony.receive_food(25.0)
# stats = colony.get_statistics()
