"""Per-type pheromone concentration fields.

The simulated quantity is a concentration grid per signal type:

    ∂C/∂t = S + D ∇²C − λ C

S is secretion added into the cells a walking ant crosses. Diffusion is an
explicit neighbor exchange with no-flux edges, so it redistributes mass and
does not create any. Evaporation is exponential in the simulated timestep.
"""

from enum import Enum, auto
import math
from typing import Dict, Optional, Tuple

import numpy as np


class PheromoneType(Enum):
    """Types of pheromones that ants can deposit."""

    FOOD_TRAIL = auto()
    HOME_TRAIL = auto()
    DANGER = auto()


# Cell size is a few pixels so a trail is several cells wide.
DEFAULT_CELL_SIZE = 6.0
# Half-lives are long enough for a nest-mate to reach a fresh trail.
FOOD_HALF_LIFE_SECONDS = 20.0
HOME_HALF_LIFE_SECONDS = 15.0
DANGER_HALF_LIFE_SECONDS = 10.0
# Amount secreted per pixel of travel.
DEFAULT_FOOD_Q = 1.0
DEFAULT_HOME_Q = 0.4
# px^2 / s. Small enough that a trail stays a ridge for one half-life.
DEFAULT_DIFFUSION = 4.0
DEFAULT_EPSILON = 1e-4
# Well above one ant's pass (about q * cell size) so repeat walks reinforce.
DEFAULT_SATURATION = 500.0
DEFAULT_FOLLOWER_THRESHOLD = 0.05
# Concentration that renders as fully opaque. One pass stays translucent so a
# busier trail reads as stronger.
DEFAULT_DISPLAY_SCALE = 16.0

TYPE_COLORS = {
    PheromoneType.FOOD_TRAIL: (0, 255, 100),
    PheromoneType.HOME_TRAIL: (100, 200, 255),
    PheromoneType.DANGER: (255, 100, 100),
}


def _half_life_to_lambda(half_life_seconds: float) -> float:
    return math.log(2.0) / half_life_seconds


class Pheromone:
    """Non-simulated descriptor.

    The manager stores a grid, not one of these per drop. The class remains so
    callers can still name a mark's position, type, strength, decay rate, and
    radius. Radius does not grow as strength falls, and color does not shift
    from green to red.
    """

    def __init__(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        strength: float = 1.0,
        decay_rate: float = 0.0,
        radius_of_influence: float = 0.0,
        **_legacy,
    ):
        self._position = position
        self._type = pheromone_type
        self._strength = float(strength)
        self._max_strength = float(strength)
        self._decay_rate = float(decay_rate)
        self._radius_of_influence = float(radius_of_influence)

    @property
    def position(self) -> Tuple[float, float]:
        return self._position

    @property
    def type(self) -> PheromoneType:
        return self._type

    @property
    def strength(self) -> float:
        return self._strength

    @property
    def max_strength(self) -> float:
        return self._max_strength

    @property
    def radius_of_influence(self) -> float:
        return self._radius_of_influence

    @property
    def color(self) -> Tuple[int, int, int]:
        return TYPE_COLORS.get(self._type, (255, 255, 255))

    def update(self, dt: float = 1.0 / 60.0) -> bool:
        """Exponential decay on this descriptor. Not used by the field solver."""
        if dt < 0.0:
            raise ValueError("dt must be >= 0")
        self._strength *= math.exp(-self._decay_rate * dt)
        return self._strength <= DEFAULT_EPSILON

    def __repr__(self) -> str:
        return (
            f"Pheromone(pos={self._position}, type={self._type.name}, "
            f"strength={self._strength:.3f})"
        )


class PheromoneManager:
    """Concentration grids for every pheromone type.

    Each step, after ants have deposited, call ``update_all(dt)``. That
    diffuses with a conservative Laplacian and then multiplies by exp(-λ dt).
    """

    def __init__(
        self,
        world_bounds: Tuple[float, float, float, float] = (0, 0, 800, 600),
        cell_size: float = DEFAULT_CELL_SIZE,
        diffusion: float = DEFAULT_DIFFUSION,
        epsilon: float = DEFAULT_EPSILON,
        saturation: float = DEFAULT_SATURATION,
        follower_threshold: float = DEFAULT_FOLLOWER_THRESHOLD,
        display_scale: float = DEFAULT_DISPLAY_SCALE,
    ):
        if cell_size <= 0.0:
            raise ValueError("cell_size must be positive")
        self._world_bounds = tuple(float(v) for v in world_bounds)
        self._cell_size = float(cell_size)
        width = self._world_bounds[2] - self._world_bounds[0]
        height = self._world_bounds[3] - self._world_bounds[1]
        self._nx = max(1, int(math.ceil(width / self._cell_size - 1e-9)))
        self._ny = max(1, int(math.ceil(height / self._cell_size - 1e-9)))
        self._fields: Dict[PheromoneType, np.ndarray] = {
            pheromone_type: np.zeros((self._ny, self._nx), dtype=np.float64)
            for pheromone_type in PheromoneType
        }
        self._lambda = {
            PheromoneType.FOOD_TRAIL: _half_life_to_lambda(FOOD_HALF_LIFE_SECONDS),
            PheromoneType.HOME_TRAIL: _half_life_to_lambda(HOME_HALF_LIFE_SECONDS),
            PheromoneType.DANGER: _half_life_to_lambda(DANGER_HALF_LIFE_SECONDS),
        }
        self._diffusion = {
            pheromone_type: float(diffusion) for pheromone_type in PheromoneType
        }
        self._epsilon = float(epsilon)
        self._saturation = float(saturation)
        self._follower_threshold = float(follower_threshold)
        self._display_scale = float(display_scale)

    @property
    def cell_size(self) -> float:
        return self._cell_size

    @property
    def shape(self) -> Tuple[int, int]:
        """(ny, nx) of each concentration grid."""
        return (self._ny, self._nx)

    @property
    def world_bounds(self) -> Tuple[float, float, float, float]:
        return self._world_bounds

    @property
    def epsilon(self) -> float:
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        self._epsilon = float(value)

    @property
    def saturation(self) -> float:
        return self._saturation

    @saturation.setter
    def saturation(self, value: float) -> None:
        self._saturation = float(value)

    @property
    def follower_threshold(self) -> float:
        return self._follower_threshold

    @follower_threshold.setter
    def follower_threshold(self, value: float) -> None:
        self._follower_threshold = float(value)

    def decay_rate(self, pheromone_type: PheromoneType) -> float:
        """λ for this type, in 1/seconds."""
        return self._lambda[pheromone_type]

    def set_decay_rate(self, pheromone_type: PheromoneType, decay_rate: float) -> None:
        if decay_rate < 0.0:
            raise ValueError("decay rate must be >= 0")
        self._lambda[pheromone_type] = float(decay_rate)

    def diffusion_rate(self, pheromone_type: PheromoneType) -> float:
        return self._diffusion[pheromone_type]

    def set_diffusion(self, pheromone_type: PheromoneType, diffusion: float) -> None:
        if diffusion < 0.0:
            raise ValueError("diffusion must be >= 0")
        self._diffusion[pheromone_type] = float(diffusion)

    def apply_behavior_params(self, params: dict) -> None:
        """Copy λ and D from the colony-behavior sliders."""
        if "food_trail_decay" in params:
            self.set_decay_rate(PheromoneType.FOOD_TRAIL, float(params["food_trail_decay"]))
        if "home_trail_decay" in params:
            self.set_decay_rate(PheromoneType.HOME_TRAIL, float(params["home_trail_decay"]))
        if "diffusion_rate" in params:
            diffusion = float(params["diffusion_rate"])
            for pheromone_type in PheromoneType:
                self.set_diffusion(pheromone_type, diffusion)

    def deposit(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        amount: float,
    ) -> float:
        """Add ``amount`` into the cell under ``position``. Returns the amount stored."""
        if amount <= 0.0 or not self._contains(position):
            return 0.0
        ix, iy = self._index(position)
        return self._add_cell(ix, iy, pheromone_type, amount)

    def deposit_segment(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        pheromone_type: PheromoneType,
        amount_per_pixel: float,
    ) -> float:
        """Secrete ``amount_per_pixel * distance`` along the segment.

        A stationary ant (zero distance) adds nothing. Mass is split across the
        cells the segment crosses in proportion to the length inside each cell.
        """
        if amount_per_pixel <= 0.0:
            return 0.0
        x0, y0 = float(start[0]), float(start[1])
        x1, y1 = float(end[0]), float(end[1])
        world_distance = math.hypot(x1 - x0, y1 - y0)
        if world_distance <= 1e-12:
            return 0.0

        origin_x, origin_y = self._world_bounds[0], self._world_bounds[1]
        cell = self._cell_size
        return self._deposit_dda(
            (x0 - origin_x) / cell,
            (y0 - origin_y) / cell,
            (x1 - origin_x) / cell,
            (y1 - origin_y) / cell,
            world_distance,
            pheromone_type,
            amount_per_pixel,
        )

    def add_pheromone(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        strength: float = 1.0,
        decay_rate: Optional[float] = None,
        radius_of_influence: Optional[float] = None,
        **_legacy,
    ) -> None:
        """Deposit ``strength`` into the cell under ``position``.

        Legacy blob arguments (per-frame decay, radius, spread delay, spread
        factor) are ignored. Spread is diffusion of the existing field.
        """
        del decay_rate, radius_of_influence
        self.deposit(position, pheromone_type, strength)

    def concentration(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
    ) -> float:
        """Concentration stored in the cell that contains ``position``."""
        if not self._contains(position):
            return 0.0
        ix, iy = self._index(position)
        return float(self._fields[pheromone_type][iy, ix])

    def sample(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
    ) -> float:
        """Bilinear sample of the grid. Outside the world this is 0."""
        x0, y0, x1, y1 = self._world_bounds
        x, y = float(position[0]), float(position[1])
        if x < x0 or y < y0 or x > x1 or y > y1:
            return 0.0
        cell = self._cell_size
        fx = (x - x0) / cell - 0.5
        fy = (y - y0) / cell - 0.5
        ix = math.floor(fx)
        iy = math.floor(fy)
        tx = fx - ix
        ty = fy - iy
        field = self._fields[pheromone_type]
        return (
            self._at(field, ix, iy) * (1.0 - tx) * (1.0 - ty)
            + self._at(field, ix + 1, iy) * tx * (1.0 - ty)
            + self._at(field, ix, iy + 1) * (1.0 - tx) * ty
            + self._at(field, ix + 1, iy + 1) * tx * ty
        )

    def get_total_strength(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        radius: float = 0.0,
    ) -> float:
        """Concentration at ``position``. ``radius`` is unused; the cell is the value."""
        del radius
        return self.sample(position, pheromone_type)

    def gradient(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        step: float = None,
    ) -> Tuple[float, float]:
        """Central difference (∂C/∂x, ∂C/∂y) from samples. Not a particle heading."""
        if step is None or step <= 0.0:
            step = self._cell_size
        x, y = float(position[0]), float(position[1])
        d_c_dx = (
            self.sample((x + step, y), pheromone_type)
            - self.sample((x - step, y), pheromone_type)
        ) / (2.0 * step)
        d_c_dy = (
            self.sample((x, y + step), pheromone_type)
            - self.sample((x, y - step), pheromone_type)
        ) / (2.0 * step)
        return (d_c_dx, d_c_dy)

    def get_pheromone_direction(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        radius: float = 8.0,
        look_ahead: float = None,
        heading: float = None,
        nest_position: Tuple[float, float] = None,
    ) -> Optional[Tuple[float, float]]:
        """Unit steering direction from the field.

        Food trails: stay on the ridge (turn toward the stronger lateral sample)
        and head away from the nest. This does not climb the along-trail slope.
        Home trails: a mild downhill repeller so explored ground reads as a region.
        Other types: the uphill gradient, or None when the field is flat.
        """
        if pheromone_type == PheromoneType.FOOD_TRAIL:
            return self._food_ridge_direction(
                position, radius, look_ahead, heading, nest_position
            )
        if pheromone_type == PheromoneType.HOME_TRAIL:
            return self._downhill_direction(position, pheromone_type, radius)
        return self._uphill_direction(position, pheromone_type, radius)

    def get_pheromones_in_range(
        self,
        position: Tuple[float, float],
        radius: float,
        pheromone_type: Optional[PheromoneType] = None,
    ):
        """Cell centers inside ``radius`` whose concentration is above zero.

        Each entry is ``(x, y, concentration, type)``. This replaces the old
        disc query; overlapping deposits are already one number per cell.
        """
        types = (
            (pheromone_type,)
            if pheromone_type is not None
            else tuple(PheromoneType)
        )
        x, y = float(position[0]), float(position[1])
        origin_x, origin_y = self._world_bounds[0], self._world_bounds[1]
        cell = self._cell_size
        ix0 = max(0, int(math.floor((x - radius - origin_x) / cell)))
        ix1 = min(self._nx - 1, int(math.floor((x + radius - origin_x) / cell)))
        iy0 = max(0, int(math.floor((y - radius - origin_y) / cell)))
        iy1 = min(self._ny - 1, int(math.floor((y + radius - origin_y) / cell)))
        found = []
        radius_sq = radius * radius
        for current_type in types:
            field = self._fields[current_type]
            for iy in range(iy0, iy1 + 1):
                cy = origin_y + (iy + 0.5) * cell
                dy = cy - y
                row = field[iy]
                for ix in range(ix0, ix1 + 1):
                    value = float(row[ix])
                    if value <= 0.0:
                        continue
                    cx = origin_x + (ix + 0.5) * cell
                    dx = cx - x
                    if dx * dx + dy * dy <= radius_sq:
                        found.append((cx, cy, value, current_type))
        return found

    def total_mass(self, pheromone_type: Optional[PheromoneType] = None) -> float:
        if pheromone_type is None:
            return float(sum(field.sum() for field in self._fields.values()))
        return float(self._fields[pheromone_type].sum())

    def peak(self, pheromone_type: PheromoneType) -> float:
        return float(self._fields[pheromone_type].max())

    def update_all(self, dt: float = 1.0 / 60.0) -> None:
        """Diffuse, then evaporate, then drop cells under epsilon.

        Diffusion is substepped so a large ``dt`` or ``D`` cannot go unstable.
        Evaporation is one exact factor, ``exp(-λ dt)``, so half-life does not
        depend on the frame rate.
        """
        if dt < 0.0:
            raise ValueError("dt must be >= 0")
        if dt == 0.0:
            return
        for pheromone_type, field in self._fields.items():
            diffusion = self._diffusion[pheromone_type]
            if diffusion > 0.0:
                self._diffuse_in_place(field, diffusion, dt)
            decay = self._lambda[pheromone_type]
            if decay > 0.0:
                field *= math.exp(-decay * dt)
            epsilon = self._epsilon
            if epsilon > 0.0:
                field[field < epsilon] = 0.0

    def get_statistics(self) -> dict:
        occupied = np.zeros((self._ny, self._nx), dtype=bool)
        type_counts = {}
        total_strength = 0.0
        for pheromone_type, field in self._fields.items():
            mask = field > 0.0
            type_counts[pheromone_type.name] = int(np.count_nonzero(mask))
            total_strength += float(field.sum())
            occupied |= mask
        total_cells = int(np.count_nonzero(occupied))
        return {
            "total_pheromones": total_cells,
            "type_counts": type_counts,
            "total_strength": total_strength,
            "average_strength": total_strength / total_cells if total_cells else 0.0,
            "grid_sum": total_strength,
        }

    def clear_all(self) -> None:
        for field in self._fields.values():
            field.fill(0.0)

    def rasterize(self) -> np.ndarray:
        """RGBA image of the grids, shape ``(ny, nx, 4)``.

        Food stays green and home stays light blue. Alpha is proportional to
        concentration and is 0 where the field is empty.
        """
        rgb = np.zeros((self._ny, self._nx, 3), dtype=np.float64)
        alpha = np.zeros((self._ny, self._nx), dtype=np.float64)
        scale = self._display_scale if self._display_scale > 0.0 else 1.0
        for pheromone_type in (
            PheromoneType.HOME_TRAIL,
            PheromoneType.FOOD_TRAIL,
            PheromoneType.DANGER,
        ):
            coverage = np.clip(self._fields[pheromone_type] / scale, 0.0, 1.0)
            if not np.any(coverage):
                continue
            color = np.asarray(TYPE_COLORS[pheromone_type], dtype=np.float64)
            inverse = 1.0 - coverage
            rgb = rgb * inverse[..., None] + color * coverage[..., None]
            alpha = coverage + alpha * inverse
        image = np.empty((self._ny, self._nx, 4), dtype=np.uint8)
        image[..., :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
        image[..., 3] = np.clip(np.rint(alpha * 255.0), 0, 255).astype(np.uint8)
        return image

    def _contains(self, position: Tuple[float, float]) -> bool:
        x0, y0, x1, y1 = self._world_bounds
        x, y = position
        return x0 <= x <= x1 and y0 <= y <= y1

    def _index(self, position: Tuple[float, float]) -> Tuple[int, int]:
        origin_x, origin_y = self._world_bounds[0], self._world_bounds[1]
        ix = int((position[0] - origin_x) / self._cell_size)
        iy = int((position[1] - origin_y) / self._cell_size)
        if ix >= self._nx:
            ix = self._nx - 1
        if iy >= self._ny:
            iy = self._ny - 1
        if ix < 0:
            ix = 0
        if iy < 0:
            iy = 0
        return ix, iy

    def _add_cell(
        self,
        ix: int,
        iy: int,
        pheromone_type: PheromoneType,
        amount: float,
    ) -> float:
        if amount <= 0.0 or ix < 0 or iy < 0 or ix >= self._nx or iy >= self._ny:
            return 0.0
        field = self._fields[pheromone_type]
        room = self._saturation - float(field[iy, ix])
        if room <= 0.0:
            return 0.0
        added = amount if amount < room else room
        field[iy, ix] += added
        return added

    def _deposit_dda(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        world_distance: float,
        pheromone_type: PheromoneType,
        amount_per_pixel: float,
    ) -> float:
        """Grid traversal. ``t`` runs from 0 at the start to 1 at the end."""
        dx = x1 - x0
        dy = y1 - y0
        ix = int(math.floor(x0))
        iy = int(math.floor(y0))
        step_x = 0 if dx == 0.0 else (1 if dx > 0.0 else -1)
        step_y = 0 if dy == 0.0 else (1 if dy > 0.0 else -1)

        if dx == 0.0:
            t_delta_x = math.inf
            t_max_x = math.inf
        else:
            t_delta_x = abs(1.0 / dx)
            if step_x > 0:
                t_max_x = (math.floor(x0) + 1.0 - x0) * t_delta_x
            else:
                t_max_x = (x0 - math.floor(x0)) * t_delta_x
        if dy == 0.0:
            t_delta_y = math.inf
            t_max_y = math.inf
        else:
            t_delta_y = abs(1.0 / dy)
            if step_y > 0:
                t_max_y = (math.floor(y0) + 1.0 - y0) * t_delta_y
            else:
                t_max_y = (y0 - math.floor(y0)) * t_delta_y

        # Sitting on a boundary and walking back across it: the current cell
        # contains none of the segment, so enter the neighbor immediately.
        if t_max_x == 0.0:
            t_max_x = t_delta_x
            ix += step_x
        if t_max_y == 0.0:
            t_max_y = t_delta_y
            iy += step_y

        added = 0.0
        t = 0.0
        max_steps = int(abs(dx) + abs(dy)) + 4
        for _ in range(max_steps):
            t_next = t_max_x if t_max_x < t_max_y else t_max_y
            if t_next > 1.0:
                t_next = 1.0
            span = t_next - t
            if span > 0.0:
                added += self._add_cell(
                    ix,
                    iy,
                    pheromone_type,
                    amount_per_pixel * world_distance * span,
                )
            if t_next >= 1.0 - 1e-15:
                break
            if t_max_x <= t_max_y:
                t = t_max_x
                t_max_x += t_delta_x
                ix += step_x
            else:
                t = t_max_y
                t_max_y += t_delta_y
                iy += step_y
        return added

    def _diffuse_in_place(self, field: np.ndarray, diffusion: float, dt: float) -> None:
        """Explicit Laplacian with no-flux edges.

        The discrete operator is a neighbor exchange: every unit that leaves a
        cell enters its neighbor, and the missing neighbor past the border is
        the edge cell itself, so the boundary flux is zero. The step is split
        so ``4 D dt / cell_size^2`` stays below 1 and the result cannot go
        negative or invent mass.
        """
        cell_area = self._cell_size * self._cell_size
        max_step = (0.2 * cell_area) / diffusion
        remaining = float(dt)
        while remaining > 1e-12:
            step = remaining if remaining < max_step else max_step
            padded = np.pad(field, 1, mode="edge")
            laplacian = (
                padded[2:, 1:-1]
                + padded[:-2, 1:-1]
                + padded[1:-1, 2:]
                + padded[1:-1, :-2]
                - 4.0 * field
            ) / cell_area
            field += (diffusion * step) * laplacian
            remaining -= step
        # Stable steps only produce negatives from roundoff. Snap those so the
        # stored field stays a concentration. An unstable step would show up
        # as created mass in the conservation checks.
        np.maximum(field, 0.0, out=field)

    def _food_ridge_direction(
        self,
        position: Tuple[float, float],
        radius: float,
        look_ahead: Optional[float],
        heading: Optional[float],
        nest_position: Optional[Tuple[float, float]],
    ) -> Optional[Tuple[float, float]]:
        away_x, away_y = self._away_from_nest(position, nest_position, heading)
        left_x, left_y = -away_y, away_x
        x, y = float(position[0]), float(position[1])
        lateral = radius if radius > 0.0 else self._cell_size
        ahead = lateral if look_ahead is None or look_ahead <= 0.0 else look_ahead
        food = PheromoneType.FOOD_TRAIL
        here = self.sample((x, y), food)
        left = self.sample((x + left_x * lateral, y + left_y * lateral), food)
        right = self.sample((x - left_x * lateral, y - left_y * lateral), food)
        forward = self.sample((x + away_x * ahead, y + away_y * ahead), food)
        if max(here, left, right, forward) < self._follower_threshold:
            return None
        scale = max(here, left, right, 1e-6)
        # Positive correction turns left (toward the stronger side).
        correction = float(np.clip((left - right) / scale, -1.0, 1.0))
        correction_rad = correction * math.radians(50.0)
        cosine = math.cos(correction_rad)
        sine = math.sin(correction_rad)
        steered_x = away_x * cosine - away_y * sine
        steered_y = away_x * sine + away_y * cosine
        return (steered_x, steered_y)

    def _away_from_nest(
        self,
        position: Tuple[float, float],
        nest_position: Optional[Tuple[float, float]],
        heading: Optional[float],
    ) -> Tuple[float, float]:
        if nest_position is not None:
            dx = float(position[0]) - float(nest_position[0])
            dy = float(position[1]) - float(nest_position[1])
            length = math.hypot(dx, dy)
            if length >= 1.0:
                return (dx / length, dy / length)
        if heading is None:
            return (1.0, 0.0)
        rad = math.radians(heading)
        return (math.cos(rad), math.sin(rad))

    def _downhill_direction(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        step: float,
    ) -> Optional[Tuple[float, float]]:
        gx, gy = self.gradient(position, pheromone_type, step)
        magnitude = math.hypot(gx, gy)
        if magnitude < self._follower_threshold / max(step, 1.0):
            return None
        return (-gx / magnitude, -gy / magnitude)

    def _uphill_direction(
        self,
        position: Tuple[float, float],
        pheromone_type: PheromoneType,
        step: float,
    ) -> Optional[Tuple[float, float]]:
        gx, gy = self.gradient(position, pheromone_type, step)
        magnitude = math.hypot(gx, gy)
        if magnitude < 1e-8:
            return None
        return (gx / magnitude, gy / magnitude)

    @staticmethod
    def _at(field: np.ndarray, ix: int, iy: int) -> float:
        height, width = field.shape
        if ix < 0 or iy < 0 or ix >= width or iy >= height:
            return 0.0
        return float(field[iy, ix])
