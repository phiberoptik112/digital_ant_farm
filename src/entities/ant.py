import numpy as np
from enum import Enum, auto
from typing import Tuple, Optional
from entities.pheromone import PheromoneManager, PheromoneType

class AntState(Enum):
    IDLE = auto()
    SEARCHING = auto()
    RETURNING = auto()
    FOLLOWING_TRAIL = auto()

class AntCaste(Enum):
    WORKER = auto()
    SOLDIER = auto()
    SCOUT = auto()
    NURSE = auto()

class Ant:
    """
    Represents an ant entity in the simulation with position, orientation, state, and carrying status.
    """
    def __init__(self, position: Tuple[float, float], orientation: float = 0.0, energy: float = 100.0, caste: AntCaste = AntCaste.WORKER):
        self._position = position  # (x, y)
        self._orientation = orientation  # Angle in degrees
        self._energy = energy
        self._carrying_food = False
        self._state = AntState.IDLE
        self._caste = caste
        
        # Movement parameters (modified by caste)
        self._velocity = 0.0  # Current speed
        self._max_velocity = 2.0  # Maximum speed
        self._acceleration = 0.5  # How quickly speed changes
        self._turn_speed = 3.0  # Degrees per frame for turning
        self._detection_radius = 20.0  # Radius for detecting food/pheromones
        
        # Apply caste-specific modifiers
        self._apply_caste_modifiers()
        
        # Boundary constraints (can be set by simulation)
        self._world_bounds = (0, 0, 800, 600)  # (x_min, y_min, x_max, y_max)

    def _apply_caste_modifiers(self):
        """Apply caste-specific modifiers to ant properties."""
        if self._caste == AntCaste.WORKER:
            # Workers are balanced - no modifiers
            pass
        elif self._caste == AntCaste.SOLDIER:
            # Soldiers are slower but stronger
            self._max_velocity *= 0.8
            self._detection_radius *= 1.3
        elif self._caste == AntCaste.SCOUT:
            # Scouts are faster with better detection
            self._max_velocity *= 1.4
            self._detection_radius *= 1.5
            self._turn_speed *= 1.2
        elif self._caste == AntCaste.NURSE:
            # Nurses are slower but more efficient
            self._max_velocity *= 0.9
            self._detection_radius *= 0.8

    @property
    def position(self) -> Tuple[float, float]:
        """Get the ant's current position."""
        return self._position

    @property
    def orientation(self) -> float:
        """Get the ant's current orientation in degrees."""
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value

    @property
    def energy(self) -> float:
        """Get the ant's current energy level."""
        return self._energy

    @property
    def carrying_food(self) -> bool:
        """Check if the ant is currently carrying food."""
        return self._carrying_food

    @property
    def state(self) -> AntState:
        """Get the ant's current state."""
        return self._state

    @property
    def velocity(self) -> float:
        """Get the ant's current velocity."""
        return self._velocity

    @property
    def detection_radius(self) -> float:
        """Get the ant's detection radius."""
        return self._detection_radius

    @property
    def caste(self) -> AntCaste:
        """Get the ant's caste."""
        return self._caste

    def get_caste_color(self) -> Tuple[int, int, int]:
        """Get the display color for this ant's caste."""
        caste_colors = {
            AntCaste.WORKER: (255, 255, 0),    # Yellow
            AntCaste.SOLDIER: (255, 0, 0),     # Red
            AntCaste.SCOUT: (0, 255, 0),       # Green
            AntCaste.NURSE: (255, 192, 203)    # Pink
        }
        return caste_colors.get(self._caste, (255, 255, 255))

    def get_food_cost(self) -> float:
        """Get the food cost to produce this ant caste."""
        costs = {
            AntCaste.WORKER: 10.0,
            AntCaste.SOLDIER: 15.0,
            AntCaste.SCOUT: 12.0,
            AntCaste.NURSE: 8.0
        }
        return costs.get(self._caste, 10.0)

    def set_state(self, new_state: AntState) -> bool:
        """
        Change the ant's state with validation.
        Args:
            new_state: The new state to transition to
        Returns:
            bool: True if transition was successful
        """
        # Add validation logic here if needed
        self._state = new_state
        return True

    def set_position(self, position: Tuple[float, float]):
        """Set the ant's position."""
        self._position = position

    def set_orientation(self, orientation: float):
        """Set the ant's orientation in degrees."""
        self._orientation = orientation % 360  # Normalize to 0-360

    def set_energy(self, energy: float):
        """Set the ant's energy level."""
        self._energy = max(0.0, min(100.0, energy))  # Clamp between 0-100

    def set_carrying_food(self, carrying: bool):
        """Set whether the ant is carrying food."""
        self._carrying_food = carrying
        # Adjust movement parameters when carrying food
        if carrying:
            self._max_velocity *= 0.7  # Slow down when carrying
        else:
            self._max_velocity /= 0.7  # Restore normal speed

    def set_world_bounds(self, bounds: Tuple[float, float, float, float]):
        """Set the world boundaries for collision detection."""
        self._world_bounds = bounds

    def move(self, step_size: float = 1.0):
        """
        Move the ant forward in the direction of its current orientation.
        Args:
            step_size (float): Distance to move in the current orientation.
        """
        # Assuming orientation is in degrees, convert to radians
        rad = np.deg2rad(self._orientation)
        dx = step_size * np.cos(rad)
        dy = step_size * np.sin(rad)
        new_x = self._position[0] + dx
        new_y = self._position[1] + dy
        
        # Check boundary constraints
        x_min, y_min, x_max, y_max = self._world_bounds
        new_x = max(x_min, min(x_max, new_x))
        new_y = max(y_min, min(y_max, new_y))
        
        self._position = (new_x, new_y)

    def accelerate(self, target_velocity: float):
        """
        Gradually change velocity towards target.
        Args:
            target_velocity: The target velocity to approach
        """
        if self._velocity < target_velocity:
            self._velocity = min(target_velocity, self._velocity + self._acceleration)
        elif self._velocity > target_velocity:
            self._velocity = max(target_velocity, self._velocity - self._acceleration)

    def turn_towards(self, target_angle: float):
        """
        Turn towards a target angle.
        Args:
            target_angle: Target angle in degrees
        """
        # Calculate shortest rotation direction
        angle_diff = (target_angle - self._orientation) % 360
        if angle_diff > 180:
            angle_diff -= 360
        
        # Apply turning
        if abs(angle_diff) <= self._turn_speed:
            self._orientation = target_angle
        else:
            turn_direction = 1 if angle_diff > 0 else -1
            self._orientation = (self._orientation + turn_direction * self._turn_speed) % 360

    def random_walk(self, randomness: float = 0.3):
        """
        Perform a random walk with configurable randomness.
        Args:
            randomness: How much random turning to apply (0-1)
        """
        # Randomly adjust orientation
        if np.random.random() < randomness:
            turn_amount = np.random.uniform(-30, 30)  # Random turn between -30 and +30 degrees
            self._orientation = (self._orientation + turn_amount) % 360
        
        # Move forward
        self.accelerate(self._max_velocity)
        self.move(self._velocity)

    def set_pheromone_manager(self, pheromone_manager: PheromoneManager):
        """Associate a PheromoneManager with this ant."""
        self._pheromone_manager = pheromone_manager

    def deposit_pheromone(self, pheromone_type: PheromoneType, strength: float = 50.0, decay_rate: float = 1.0, radius_of_influence: float = 20.0,
                         can_spread: bool = True, spread_radius: float = None, spread_strength_factor: float = 0.4,
                         spread_delay: float = 2.0):
        """Deposit a pheromone at the ant's current position."""
        if hasattr(self, '_pheromone_manager') and self._pheromone_manager:
            self._pheromone_manager.add_pheromone(self._position, pheromone_type, strength, decay_rate, radius_of_influence,
                                                can_spread, spread_radius, spread_strength_factor, spread_delay)

    def sense_pheromone_gradient(self, pheromone_type: PheromoneType, radius: float = 50.0):
        """Sense the pheromone gradient and return a direction vector (dx, dy) or None."""
        if hasattr(self, '_pheromone_manager') and self._pheromone_manager:
            return self._pheromone_manager.get_pheromone_direction(self._position, pheromone_type, radius)
        return None

    def step(self):
        """
        Update the ant's behavior based on its current state.
        This method should be called each simulation tick.
        """
        if self._state == AntState.SEARCHING:
            # Try to follow food trail pheromones first
            food_direction = self.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=60.0)
            if food_direction is not None:
                # Convert direction vector to angle and turn towards it
                angle = np.rad2deg(np.arctan2(food_direction[1], food_direction[0]))
                self.turn_towards(angle)
                self.accelerate(self._max_velocity)
                self.move(self._velocity)
                self.set_state(AntState.FOLLOWING_TRAIL)
            else:
                # If no food trail, try to avoid home trails to explore new areas
                home_direction = self.sense_pheromone_gradient(PheromoneType.HOME_TRAIL, radius=40.0)
                if home_direction is not None:
                    # Move away from home trails to explore
                    avoid_angle = np.rad2deg(np.arctan2(-home_direction[1], -home_direction[0]))
                    self.turn_towards(avoid_angle)
                    self.accelerate(self._max_velocity * 0.8)
                    self.move(self._velocity)
                else:
                    self._random_walk()
        elif self._state == AntState.RETURNING:
            # This state is now handled in main.py for better control
            pass
        elif self._state == AntState.FOLLOWING_TRAIL:
            # Follow food trail pheromones
            direction = self.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=60.0)
            if direction is not None:
                angle = np.rad2deg(np.arctan2(direction[1], direction[0]))
                self.turn_towards(angle)
                self.accelerate(self._max_velocity)
                self.move(self._velocity)
            else:
                # Lost the trail, search with low randomness
                self.set_state(AntState.SEARCHING)
                self.random_walk(randomness=0.3)
        # Add more states as needed

    def _random_walk(self):
        """
        Perform a random walk step for searching behavior.
        """
        self.random_walk(randomness=0.3)

    def _return_to_nest(self):
        """
        Move towards the nest location.
        This method assumes nest location is known (set externally).
        """
        if hasattr(self, '_nest_position'):
            nest_dir = (self._nest_position[0] - self._position[0], 
                       self._nest_position[1] - self._position[1])
            nest_dist = np.sqrt(nest_dir[0]**2 + nest_dir[1]**2)
            if nest_dist > 0:
                nest_angle = np.rad2deg(np.arctan2(nest_dir[1], nest_dir[0]))
                self.turn_towards(nest_angle)
                self.accelerate(self._max_velocity)
                self.move(self._velocity)
            else:
                # At nest, stop moving
                self.accelerate(0)
        else:
            # No nest position set, just move forward
            self.accelerate(self._max_velocity)
            self.move(self._velocity)

    def _follow_pheromone_trail(self):
        """
        Follow pheromone trail with improved behavior.
        """
        direction = self.sense_pheromone_gradient(PheromoneType.FOOD_TRAIL, radius=50.0)
        if direction is not None:
            angle = np.rad2deg(np.arctan2(direction[1], direction[0]))
            self.turn_towards(angle)
            self.accelerate(self._max_velocity)
            self.move(self._velocity)
        else:
            # Lost the trail, search with low randomness
            self.random_walk(randomness=0.1)

    def set_nest_position(self, nest_position: Tuple[float, float]):
        """Set the nest position for this ant."""
        self._nest_position = nest_position

    def get_nest_position(self) -> Optional[Tuple[float, float]]:
        """Get the nest position if set."""
        return getattr(self, '_nest_position', None)

    def distance_to(self, other_position: Tuple[float, float]) -> float:
        """
        Calculate distance to another position.
        Args:
            other_position: Target position (x, y)
        Returns:
            float: Distance to the target
        """
        dx = other_position[0] - self._position[0]
        dy = other_position[1] - self._position[1]
        return np.sqrt(dx*dx + dy*dy)

    def is_within_range(self, target_position: Tuple[float, float], range_radius: float = None) -> bool:
        """
        Check if a target is within detection range.
        Args:
            target_position: Position to check
            range_radius: Detection radius (uses default if None)
        Returns:
            bool: True if target is within range
        """
        if range_radius is None:
            range_radius = self._detection_radius
        return self.distance_to(target_position) <= range_radius

    def __repr__(self):
        return (f"Ant(position={self._position}, orientation={self._orientation}, "
                f"energy={self._energy}, carrying_food={self._carrying_food}, state={self._state.name})")

# Example usage:
# ant = Ant(position=(100, 100), orientation=45.0)
# ant.set_state(AntState.SEARCHING)
# ant.step()  # Update behavior based on current state
