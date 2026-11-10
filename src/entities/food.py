from typing import Tuple, Optional
import numpy as np
import time


def _distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


class FoodSource:
    """
    Represents a food source in the simulation with position, amount, and depletion mechanics.
    """
    def __init__(self, position: Tuple[float, float], amount: float = 100.0, 
                 max_amount: float = 100.0, depletion_rate: float = 1.0,
                 expiration_time: float = 30.0, refresh_time: float = 60.0,
                 patch_id: Optional[int] = None, expires: bool = True):
        self._position = position  # (x, y)
        self._amount = min(amount, max_amount)  # Current food amount
        self._max_amount = max_amount  # Maximum capacity
        self._depletion_rate = depletion_rate  # Amount removed per collection
        self._regeneration_rate = 0.0  # Amount regenerated per tick
        self._regeneration_cooldown = 0  # Ticks before regeneration starts
        self._max_regeneration_cooldown = 300  # 5 seconds at 60 FPS
        self._is_depleted = False
        # Forage-patch bookkeeping. expires=False skips the wall-clock refill.
        self.patch_id = patch_id
        self.expires = expires
        self.source_id: Optional[int] = None
        
        # Time-based expiration system
        self._expiration_time = expiration_time  # Time in seconds before food expires
        self._refresh_time = refresh_time  # Time in seconds before food refreshes
        self._spawn_time = time.time()  # When the food was created
        self._last_refresh_time = time.time()  # When the food was last refreshed
        self._is_expired = False
        self._expiration_rate = 1.0  # Rate at which food expires (amount per second)
        
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
    def is_expired(self) -> bool:
        """Check if the food source has expired."""
        return self._is_expired

    @property
    def is_available(self) -> bool:
        """Check if the food source is available (not depleted and not expired)."""
        return not self._is_depleted and not self._is_expired and self._amount > 0

    @property
    def depletion_percentage(self) -> float:
        """Get the percentage of food remaining (0-100)."""
        return (self._amount / self._max_amount) * 100.0

    @property
    def time_until_expiration(self) -> float:
        """Get time in seconds until food expires."""
        if self._is_expired:
            return 0.0
        elapsed = time.time() - self._spawn_time
        return max(0.0, self._expiration_time - elapsed)

    @property
    def time_until_refresh(self) -> float:
        """Get time in seconds until food refreshes."""
        if self.is_available:
            return 0.0
        elapsed = time.time() - self._last_refresh_time
        return max(0.0, self._refresh_time - elapsed)

    @property
    def visual_radius(self) -> float:
        """Get the visual radius based on current amount."""
        if self._is_depleted or self._is_expired:
            return 0.0
        
        ratio = self._amount / self._max_amount
        return self._min_radius + (self._base_radius - self._min_radius) * ratio

    @property
    def visual_color(self) -> Tuple[int, int, int]:
        """Get the visual color based on food state."""
        if self._is_expired:
            return (80, 40, 40)  # Dark red for expired
        elif self._is_depleted:
            return (60, 60, 60)  # Gray for depleted
        else:
            # Green to yellow based on amount
            ratio = self._amount / self._max_amount
            red = int(255 * (1 - ratio))
            green = 255
            blue = 0
            return (red, green, blue)

    def collect_food(self, amount: float = None) -> float:
        """
        Collect food from this source.
        Args:
            amount: Amount to collect (uses depletion_rate if None)
        Returns:
            float: Actual amount collected
        """
        if self._is_depleted or self._is_expired:
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
        
        if self._is_expired:
            self._is_expired = False
        
        space_available = self._max_amount - self._amount
        actual_amount = min(amount, space_available)
        self._amount += actual_amount
        
        return actual_amount

    def set_regeneration_rate(self, rate: float):
        """Set the regeneration rate (amount per tick)."""
        self._regeneration_rate = max(0.0, rate)

    def set_expiration_time(self, time_seconds: float):
        """Set the expiration time in seconds."""
        self._expiration_time = max(0.0, time_seconds)

    def set_refresh_time(self, time_seconds: float):
        """Set the refresh time in seconds."""
        self._refresh_time = max(0.0, time_seconds)

    def set_expiration_rate(self, rate: float):
        """Set the expiration rate (amount per second)."""
        self._expiration_rate = max(0.0, rate)

    def refresh_food(self):
        """Manually refresh the food source."""
        self._amount = self._max_amount
        self._is_depleted = False
        self._is_expired = False
        self._spawn_time = time.time()
        self._last_refresh_time = time.time()
        self._regeneration_cooldown = 0

    def update(self, delta_time: float = 1.0/60.0):
        """
        Update the food source (called each simulation tick).
        Handles regeneration, expiration, and refresh timers.
        Args:
            delta_time: Time elapsed since last update (in seconds)
        """
        # Patch morsels are eaten away and do not refill on a wall clock.
        if self.expires:
            current_time = time.time()

            # Handle time-based expiration
            if not self._is_expired and self.is_available:
                time_since_spawn = current_time - self._spawn_time
                if time_since_spawn >= self._expiration_time:
                    # Food has expired, start decaying
                    self._is_expired = True
                    self._last_refresh_time = current_time
                else:
                    # Gradually reduce food over time as it approaches expiration
                    time_remaining = self._expiration_time - time_since_spawn
                    if time_remaining < self._expiration_time * 0.5:  # Last 50% of time
                        decay_amount = self._expiration_rate * delta_time
                        self._amount = max(0, self._amount - decay_amount)
                        if self._amount <= 0:
                            self._is_expired = True
                            self._last_refresh_time = current_time

            # Handle refresh after expiration. Refills the same coordinates.
            if self._is_expired or self._is_depleted:
                time_since_last_refresh = current_time - self._last_refresh_time
                if time_since_last_refresh >= self._refresh_time:
                    self.refresh_food()
                    return
        
        # Handle regeneration cooldown
        if self._regeneration_cooldown > 0:
            self._regeneration_cooldown -= 1
            return
        
        # Handle regeneration
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
        return f"FoodSource(pos={self._position}, amount={self._amount:.1f}/{self._max_amount}, depleted={self._is_depleted}, expired={self._is_expired})"


class FoodManager:
    """
    Manages all food sources in the simulation with efficient spatial queries.
    """
    def __init__(self, world_bounds: Tuple[float, float, float, float] = (0, 0, 800, 600)):
        self._food_sources = []  # List of all food sources
        self._world_bounds = world_bounds
        self._spatial_grid = {}  # Simple spatial hash for efficient queries
        self._grid_size = 50  # Size of each grid cell
        
        # Food generation parameters (exposed for UI controls)
        self.num_food_sources = 8
        self.min_food_amount = 50.0
        self.max_food_amount = 150.0
        self.min_distance_between_food = 40.0
        self.expiration_time = 30.0  # seconds
        self.refresh_time = 60.0  # seconds
        self.expiration_rate = 2.0  # food units per second
        self.auto_generate = True

        # Forage patches (Neyman–Scott clusters). "patches" is the live mode;
        # "uniform" keeps the old scattered-crumb sampler.
        self.distribution = "patches"
        self.num_patches = 4
        self.morsels_per_patch = 6
        self.patch_sigma = 36.0
        self.min_morsel_spacing = 18.0
        self.min_patch_separation = 280.0
        self.min_nest_distance = 180.0
        self.morsel_amount = (40.0, 80.0)
        self.patch_respawn_delay = 25.0
        self._patches: list = []
        self._sim_time = 0.0
        self._nest_position: Optional[Tuple[float, float]] = None
        self._next_patch_id = 1
        self._next_source_id = 1
        self._sources_by_id: dict = {}
        
    def add_food_source(self, position: Tuple[float, float], amount: float = 100.0, 
                       max_amount: float = 100.0, depletion_rate: float = 1.0,
                       expiration_time: float = None, refresh_time: float = None,
                       patch_id: Optional[int] = None, expires: bool = True) -> FoodSource:
        """
        Add a new food source to the simulation.
        Args:
            position: Position of the food source
            amount: Initial food amount
            max_amount: Maximum food capacity
            depletion_rate: Amount removed per collection
            expiration_time: Time before food expires (uses manager default if None)
            refresh_time: Time before food refreshes (uses manager default if None)
            patch_id: Forage patch this morsel belongs to, if any
            expires: When False, skip the wall-clock expire-and-refill
        Returns:
            FoodSource: The created food source
        """
        if expiration_time is None:
            expiration_time = self.expiration_time
        if refresh_time is None:
            refresh_time = self.refresh_time
            
        food_source = FoodSource(
            position, amount, max_amount, depletion_rate,
            expiration_time, refresh_time,
            patch_id=patch_id, expires=expires,
        )
        food_source.set_expiration_rate(self.expiration_rate)
        food_source.source_id = self._next_source_id
        self._next_source_id += 1
        self._sources_by_id[food_source.source_id] = food_source
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
        source_id = getattr(food_source, "source_id", None)
        if source_id is not None:
            self._sources_by_id.pop(source_id, None)

    def get_nearest_food(self, position: Tuple[float, float], max_distance: float = float('inf')) -> Optional[FoodSource]:
        """
        Find the nearest available food source to a position.
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
                if not food_source.is_available:
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
                        if not food_source.is_available:
                            continue
                        
                        distance = food_source.distance_to(position)
                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_food = food_source
        
        return nearest_food

    def get_food_in_range(self, position: Tuple[float, float], range_radius: float) -> list:
        """
        Get all available food sources within a specified range.
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
                    if food_source.is_available and food_source.is_within_range(position, range_radius):
                        food_in_range.append(food_source)
        
        return food_in_range

    def generate_random_food(self, num_sources: int = None, min_amount: float = None, 
                           max_amount: float = None, min_distance: float = None):
        """
        Generate random food sources across the world.
        Args:
            num_sources: Number of food sources to generate (uses manager default if None)
            min_amount: Minimum food amount (uses manager default if None)
            max_amount: Maximum food amount (uses manager default if None)
            min_distance: Minimum distance between food sources (uses manager default if None)
        """
        if num_sources is None:
            num_sources = self.num_food_sources
        if min_amount is None:
            min_amount = self.min_food_amount
        if max_amount is None:
            max_amount = self.max_food_amount
        if min_distance is None:
            min_distance = self.min_distance_between_food
            
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

    def generate_patches(self, nest_position: Tuple[float, float]):
        """
        Place forage patches: parent centers far apart, morsels in a Gaussian clump.
        A clump is replaced somewhere else only after it has been eaten.
        Args:
            nest_position: Colony position. Patches stay at least min_nest_distance away.
        """
        self._nest_position = (float(nest_position[0]), float(nest_position[1]))
        self.distribution = "patches"
        for _attempt in range(30):
            self.clear_all_food()
            placed = True
            for _ in range(self.num_patches):
                existing = [patch["center"] for patch in self._patches]
                patch_id = self._next_patch_id
                self._next_patch_id += 1
                cluster = self._place_cluster(existing, avoid_center=None, avoid_distance=0.0, patch_id=patch_id)
                if cluster is None:
                    placed = False
                    break
                center, source_ids = cluster
                self._patches.append({
                    "id": patch_id,
                    "center": center,
                    "source_ids": source_ids,
                    "empty_for": 0.0,
                })
            if placed and len(self._patches) == self.num_patches:
                return
        raise RuntimeError("Could not place forage patches inside the playfield")

    def clear_all_food(self):
        """Remove all food sources from the simulation."""
        self._food_sources.clear()
        self._spatial_grid.clear()
        self._patches.clear()
        self._sources_by_id.clear()

    def regenerate_food(self, nest_position: Optional[Tuple[float, float]] = None):
        """
        Clear all food and generate a fresh layout.
        Patch mode samples new clumps. Uniform mode uses the scattered-crumb sampler.
        """
        if nest_position is not None:
            self._nest_position = (float(nest_position[0]), float(nest_position[1]))
        if self.distribution == "patches" and self._nest_position is not None:
            self.generate_patches(self._nest_position)
            return
        self.clear_all_food()
        if self.distribution != "patches":
            self.generate_random_food()

    def update_all(self, delta_time: float = 1.0/60.0):
        """
        Update all food sources (called each simulation tick).
        Args:
            delta_time: Time elapsed since last update (in seconds)
        """
        self._sim_time += float(delta_time)
        for food_source in list(self._food_sources):
            if food_source.expires:
                food_source.update(delta_time)

        # Patches respawn from summed delta_time. Do not sprinkle uniform crumbs between them.
        if self.distribution == "patches":
            self._advance_patches(float(delta_time))
            return

        # Auto-generate new food if enabled and we have fewer than target
        if self.auto_generate:
            available_food = len([f for f in self._food_sources if f.is_available])
            if available_food < self.num_food_sources // 2:  # Regenerate when below half
                needed = self.num_food_sources - len(self._food_sources)
                if needed > 0:
                    self.generate_random_food(needed)

    def active_patch_center(self, patch_id: int) -> Optional[Tuple[float, float]]:
        """Center of a patch that still has a morsel left to eat, otherwise None."""
        for patch in self._patches:
            if patch["id"] != patch_id:
                continue
            for source_id in patch["source_ids"]:
                source = self._sources_by_id.get(source_id)
                if source is not None and source.is_available:
                    return patch["center"]
            return None
        return None

    def cleanup_depleted(self):
        """Remove permanently depleted food sources to save memory."""
        sources_to_remove = []
        for food_source in self._food_sources:
            if (food_source.is_depleted or food_source.is_expired) and food_source._regeneration_rate == 0:
                # Only remove if it's been expired/depleted for a long time
                if food_source.time_until_refresh == 0:
                    sources_to_remove.append(food_source)
        
        for food_source in sources_to_remove:
            self.remove_food_source(food_source)

    def get_statistics(self) -> dict:
        """
        Get statistics about all food sources.
        Returns:
            dict: Statistics including total sources, total food, etc.
        """
        total_sources = len(self._food_sources)
        available_sources = len([f for f in self._food_sources if f.is_available])
        depleted_sources = len([f for f in self._food_sources if f.is_depleted])
        expired_sources = len([f for f in self._food_sources if f.is_expired])
        total_food = sum(f.amount for f in self._food_sources)
        total_capacity = sum(f.max_amount for f in self._food_sources)
        
        return {
            'total_sources': total_sources,
            'available_sources': available_sources,
            'depleted_sources': depleted_sources,
            'expired_sources': expired_sources,
            'total_food': total_food,
            'total_capacity': total_capacity,
            'utilization_percentage': (total_food / total_capacity * 100) if total_capacity > 0 else 0
        }

    def _playfield_bounds(self) -> Tuple[float, float, float, float]:
        """
        Open ground: inset from the screen edge and ending before the queen panel.
        The panel occupies x = 850–1200, so placement stops at x = 820.
        """
        x_min, y_min, x_max, y_max = self._world_bounds
        margin = 40.0
        left = x_min + margin
        top = y_min + margin
        right = min(x_max - margin, 820.0)
        bottom = y_max - margin
        if right <= left:
            right = x_max - margin
        if bottom <= top:
            bottom = y_max - margin
        return (left, top, right, bottom)

    def _center_bounds(self) -> Tuple[float, float, float, float]:
        """Playfield inset by 2 * patch_sigma so a clump stays on open ground."""
        left, top, right, bottom = self._playfield_bounds()
        inset = 2.0 * self.patch_sigma
        return (left + inset, top + inset, right - inset, bottom - inset)

    def _center_is_valid(self, x: float, y: float, existing_centers: list,
                         avoid_center: Optional[Tuple[float, float]], avoid_distance: float) -> bool:
        x0, y0, x1, y1 = self._center_bounds()
        if x < x0 or x > x1 or y < y0 or y > y1:
            return False
        if self._nest_position is not None:
            if _distance((x, y), self._nest_position) < self.min_nest_distance:
                return False
        for center in existing_centers:
            if _distance((x, y), center) < self.min_patch_separation:
                return False
        if avoid_center is not None and avoid_distance > 0.0:
            if _distance((x, y), avoid_center) < avoid_distance:
                return False
        return True

    def _sample_patch_center(self, existing_centers: list,
                             avoid_center: Optional[Tuple[float, float]] = None,
                             avoid_distance: float = 0.0) -> Optional[Tuple[float, float]]:
        """
        Sample one parent center. Eighty uniform draws, then a grid scan if those
        all land in the nest or inside another clump's exclusion.
        """
        x0, y0, x1, y1 = self._center_bounds()
        if x1 <= x0 or y1 <= y0:
            return None
        for _ in range(80):
            x = float(np.random.uniform(x0, x1))
            y = float(np.random.uniform(y0, y1))
            if self._center_is_valid(x, y, existing_centers, avoid_center, avoid_distance):
                return (x, y)

        step = 16.0
        candidates = []
        x = x0
        while x <= x1:
            y = y0
            while y <= y1:
                if self._center_is_valid(x, y, existing_centers, avoid_center, avoid_distance):
                    candidates.append((float(x), float(y)))
                y += step
            x += step
        if not candidates:
            return None
        return candidates[int(np.random.randint(0, len(candidates)))]

    def _sample_morsel(self, center: Tuple[float, float], sibling_positions: list) -> Optional[Tuple[float, float]]:
        """Gaussian offset around a patch center, kept on the playfield and off its siblings."""
        left, top, right, bottom = self._playfield_bounds()
        sigma = self.patch_sigma
        for _ in range(100):
            dx = float(np.random.normal(0.0, sigma))
            dy = float(np.random.normal(0.0, sigma))
            if float(np.hypot(dx, dy)) > 3.0 * sigma:
                continue
            x = center[0] + dx
            y = center[1] + dy
            if x < left or x > right or y < top or y > bottom:
                continue
            if self._nest_position is not None and _distance((x, y), self._nest_position) < self.min_nest_distance:
                continue
            too_close = False
            for sibling in sibling_positions:
                if _distance((x, y), sibling) < self.min_morsel_spacing:
                    too_close = True
                    break
            if too_close:
                continue
            return (x, y)
        return None

    def _fill_morsels(self, patch_id: int, center: Tuple[float, float]) -> list:
        """Create morsels_per_patch sources around center. Returns their source ids, or []."""
        low, high = self.morsel_amount
        for _attempt in range(15):
            created = []
            positions = []
            failed = False
            for _ in range(self.morsels_per_patch):
                position = self._sample_morsel(center, positions)
                if position is None:
                    failed = True
                    break
                amount = float(np.random.uniform(low, high))
                source = self.add_food_source(
                    position, amount, amount, patch_id=patch_id, expires=False,
                )
                created.append(source)
                positions.append(position)
            if not failed and len(created) == self.morsels_per_patch:
                return [source.source_id for source in created]
            for source in created:
                self.remove_food_source(source)
        return []

    def _place_cluster(self, existing_centers: list, avoid_center: Optional[Tuple[float, float]],
                       avoid_distance: float, patch_id: int):
        """Return (center, source_ids) for a new clump, or None if the rules cannot be met."""
        for _ in range(12):
            center = self._sample_patch_center(existing_centers, avoid_center, avoid_distance)
            if center is None:
                return None
            source_ids = self._fill_morsels(patch_id, center)
            if len(source_ids) == self.morsels_per_patch:
                return center, source_ids
        return None

    def _remove_sources_by_id(self, source_ids: list):
        for source_id in list(source_ids):
            source = self._sources_by_id.get(source_id)
            if source is not None:
                self.remove_food_source(source)

    def _patch_is_empty(self, patch: dict) -> bool:
        if not patch["source_ids"]:
            return True
        for source_id in patch["source_ids"]:
            source = self._sources_by_id.get(source_id)
            if source is not None and source.is_available:
                return False
        return True

    def _respawn_patch(self, patch: dict):
        """Drop the eaten morsels and sample a new center. The old spot stays empty."""
        old_center = tuple(patch["center"])
        self._remove_sources_by_id(patch["source_ids"])
        patch["source_ids"] = []
        existing = [other["center"] for other in self._patches if other["id"] != patch["id"]]
        # Prefer a center clear of the eaten clump (about two clump-widths, then one),
        # then any other legal center. Reuse the old center only if nothing else fits.
        shifts = (4.0 * self.patch_sigma, 2.0 * self.patch_sigma, 1.0, 0.0)
        for avoid_distance in shifts:
            avoid_center = old_center if avoid_distance > 0.0 else None
            cluster = self._place_cluster(existing, avoid_center, avoid_distance, patch["id"])
            if cluster is None:
                continue
            center, source_ids = cluster
            if avoid_distance > 0.0 and _distance(center, old_center) < avoid_distance:
                self._remove_sources_by_id(source_ids)
                continue
            patch["center"] = center
            patch["source_ids"] = source_ids
            patch["empty_for"] = 0.0
            return
        # No legal center this tick. Keep the patch empty and try again next update.
        patch["center"] = old_center
        patch["empty_for"] = self.patch_respawn_delay

    def _advance_patches(self, delta_time: float):
        for patch in self._patches:
            if self._patch_is_empty(patch):
                patch["empty_for"] += delta_time
                if patch["empty_for"] >= self.patch_respawn_delay:
                    self._respawn_patch(patch)
            else:
                patch["empty_for"] = 0.0

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
