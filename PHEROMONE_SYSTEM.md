# Enhanced Pheromone Visualization System

## Overview

The Enhanced Pheromone Visualization System displays pheromones placed down by each ant as colored trails on the ground. This system provides a visual representation of ant communication and pathfinding behavior through chemical signals.

## Features

### 🟢 Pheromone Types & Colors

- **Food Trail Pheromones**: **Bright Green** `(0, 255, 100)` - Left by ants returning to nest with food
- **Home Trail Pheromones**: **Light Blue** `(100, 200, 255)` - Exploration trails left by searching ants
- **Danger Pheromones**: **Red** `(255, 100, 100)` - Warning signals (future feature)

### 🎨 Visual Enhancements

- **Gradient Rendering**: Pheromones are displayed as gradient circles that fade from center to edge
- **Strength-Based Alpha**: Pheromone opacity reflects its strength (stronger = more visible)
- **Radius of Influence**: Visual size matches the pheromone's actual influence radius
- **Real-time Decay**: Pheromones fade over time as they lose strength

### 🌊 **NEW: Pheromone Spreading**

- **Automatic Spreading**: Pheromones spread beyond their initial radius after a configurable delay
- **Lower Density Spread**: Spread deposits have reduced strength (configurable factor, default 40% of original)
- **Same Decay Time**: Spread deposits decay at the same rate as the original pheromone
- **Circular Pattern**: Spread deposits are placed in a circular pattern around the original deposit
- **Configurable Parameters**:
  - `spread_radius`: Distance from original deposit (default: 2x original radius)
  - `spread_strength_factor`: Strength multiplier for spread deposits (default: 0.4)
  - `spread_delay`: Time delay before spreading occurs (default: 2.0 seconds)
  - `can_spread`: Whether pheromone can spread (default: True)
- **No Recursive Spreading**: Spread deposits cannot spread further, preventing infinite propagation

### 🐜 Ant Behavior

- **Exploration Pheromones**: Ants deposit home trail pheromones every 30 frames while searching
- **Food Trail Creation**: Ants deposit food trail pheromones when returning to nest with food
- **Gradient Following**: Ants can sense and follow pheromone gradients to find food sources
- **Avoidance Behavior**: Ants avoid their own exploration trails to encourage new area exploration
- **Enhanced Coverage**: Spreading pheromones create larger influence areas, improving pathfinding

## How to Run

### Main Simulation
```bash
python3 src/main.py
```

### Controls
- **ESC**: Quit the simulation
- **SPACE**: Reset the simulation (clears all pheromones)

### Test System
```bash
python3 test_enhanced_pheromones.py
```

### Test Spreading System
```bash
python3 test_spreading_pheromones.py
```

## Technical Implementation

### Core Components

1. **PheromoneManager**: Manages all pheromones with spatial indexing for performance
2. **Pheromone Class**: Individual pheromone instances with position, type, strength, decay, and spreading properties
3. **Enhanced Rendering**: Gradient circles with alpha blending for realistic appearance
4. **Ant AI**: Improved behavior for pheromone deposition and following
5. **Spreading System**: Automatic creation of spread deposits after configurable delays

### Key Parameters

- **Pheromone Strength**: 40.0 for food trails, 20.0 for home trails
- **Decay Rate**: 0.5 for food trails, 0.3 for home trails
- **Radius of Influence**: 25.0 for food trails, 15.0 for home trails
- **Deposition Frequency**: Every 30 frames for exploration, every frame when returning
- **Spreading Parameters**:
  - **Spread Radius**: 2x original radius (default)
  - **Spread Strength Factor**: 0.4 (40% of original strength)
  - **Spread Delay**: 2.0 seconds
  - **Number of Spread Deposits**: 8 (arranged in a circle)

### Spreading Algorithm

```python
def _create_spread_deposits(self, original_pheromone: Pheromone):
    """Create spread deposits around an original pheromone."""
    if not original_pheromone.should_spread:
        return
    
    # Calculate spread strength
    spread_strength = original_pheromone.max_strength * original_pheromone.spread_strength_factor
    
    # Create spread deposits in a circle around the original
    num_deposits = 8  # Number of spread deposits to create
    spread_radius = original_pheromone.spread_radius
    
    for i in range(num_deposits):
        angle = (2 * math.pi * i) / num_deposits
        
        # Calculate position for spread deposit
        spread_x = original_pheromone.position[0] + math.cos(angle) * spread_radius
        spread_y = original_pheromone.position[1] + math.sin(angle) * spread_radius
        
        # Create spread deposit with same decay rate as original
        self.add_pheromone(
            position=(spread_x, spread_y),
            pheromone_type=original_pheromone.type,
            strength=spread_strength,
            decay_rate=original_pheromone._decay_rate,  # Same decay rate
            radius_of_influence=original_pheromone.radius_of_influence * 0.8,
            can_spread=False,  # Spread deposits don't spread further
            is_spread_deposit=True
        )
```

### Visualization Algorithm

```python
# Enhanced pheromone rendering (includes spread deposits)
for pheromone in pheromone_manager._pheromones:
    alpha = max(20, min(255, int(pheromone.strength * 3)))
    radius = int(pheromone.radius_of_influence)
    
    # Color based on type
    if pheromone.type == PheromoneType.FOOD_TRAIL:
        color = (0, 255, 100, alpha)  # Bright green
    elif pheromone.type == PheromoneType.HOME_TRAIL:
        color = (100, 200, 255, alpha)  # Light blue
    
    # Slightly different opacity for spread deposits
    if pheromone.is_spread_deposit:
        alpha = int(alpha * 0.8)  # Slightly more transparent
    
    # Gradient circle rendering
    for r in range(radius, 0, -2):
        gradient_alpha = int(alpha * (r / radius) * 0.7)
        gradient_color = (*color[:3], gradient_alpha)
        pygame.draw.circle(surface, gradient_color, center, r)
```

## Usage Examples

### Basic Pheromone Deposit
```python
# Standard pheromone with spreading enabled
pheromone_manager.add_pheromone(
    position=(100, 100),
    pheromone_type=PheromoneType.FOOD_TRAIL,
    strength=50.0,
    decay_rate=0.5,
    radius_of_influence=25.0,
    can_spread=True  # Default
)
```

### Custom Spreading Parameters
```python
# Custom spreading behavior
pheromone_manager.add_pheromone(
    position=(200, 200),
    pheromone_type=PheromoneType.HOME_TRAIL,
    strength=40.0,
    decay_rate=0.3,
    radius_of_influence=15.0,
    can_spread=True,
    spread_radius=60.0,  # Custom spread distance
    spread_strength_factor=0.6,  # 60% of original strength
    spread_delay=1.0  # Spread after 1 second
)
```

### No Spreading
```python
# Pheromone that doesn't spread
pheromone_manager.add_pheromone(
    position=(300, 300),
    pheromone_type=PheromoneType.FOOD_TRAIL,
    strength=30.0,
    can_spread=False  # Disable spreading
)
```

## Simulation Elements

### Nest
- **Brown circle** at position (100, 100)
- **Radius**: 30 pixels
- Ants spawn around the nest and return here with food

### Food Sources
- **Green circles** at various positions
- Ants search for these and carry food back to nest
- When found, ants switch to RETURNING state and deposit food trails

### Ants
- **Yellow**: Searching for food
- **Orange**: Carrying food back to nest
- **White lines**: Show ant orientation/direction

## Behavioral Patterns

### Foraging Cycle
1. **Exploration**: Ants leave nest and deposit home trail pheromones
2. **Food Discovery**: Ant finds food source and switches to returning state
3. **Trail Creation**: Ant deposits food trail pheromones while returning to nest
4. **Pheromone Spreading**: After delay, pheromones spread to create wider influence areas
5. **Trail Following**: Other ants detect food trails and follow them to food sources
6. **Reinforcement**: Multiple ants using the same trail strengthen the pheromone signal

### Emergent Behaviors
- **Trail Networks**: Multiple intersecting pheromone trails form complex networks
- **Efficient Pathfinding**: Ants find shortest paths to food sources over time
- **Collective Intelligence**: Individual simple rules create complex group behavior
- **Enhanced Coverage**: Spreading pheromones create larger search areas and improve path discovery
- **Gradient Fields**: Spread deposits create smoother pheromone gradients for better navigation

## Testing Results

The test script demonstrates:
- **Pheromone Deposition**: Ants successfully deposit both trail types
- **Gradient Following**: Ants can sense and follow pheromone gradients
- **Decay System**: Pheromones properly decay over time
- **Visual Rendering**: All pheromone types display with correct colors
- **Spreading Behavior**: Pheromones spread after configurable delays
- **Spread Deposit Properties**: Spread deposits have correct strength and decay rates

Example output:
```
Final Results:
Total pheromones: 65
Original deposits: 8
Spread deposits: 57
Food trail pheromones: 40
Home trail pheromones: 25
Average strength: 18.43
Total strength: 1197.95
```

## Performance Optimization

- **Spatial Indexing**: Pheromones are organized in a grid for efficient range queries
- **Culling**: Pheromones below minimum strength are automatically removed
- **Efficient Rendering**: Gradient circles are pre-calculated and cached
- **Spread Tracking**: Prevents duplicate spreading through state tracking
- **Boundary Checking**: Spread deposits are only created within world bounds

## Future Enhancements

- **Danger Pheromones**: Red warning signals when ants encounter obstacles
- **Trail Reinforcement**: Stronger trails from multiple ant usage
- **Pheromone Interaction**: Different pheromone types affecting each other
- **3D Visualization**: Height-based pheromone intensity display
- **Variable Spread Patterns**: Different spreading shapes (elliptical, directional)
- **Multi-stage Spreading**: Pheromones that spread multiple times over their lifetime

## Dependencies

- Python 3.7+
- pygame 2.6.1
- numpy 2.3.1

## Installation

```bash
pip install -r requirements.txt
```

---

🎉 **Watch the mesmerizing green pheromone trails spread and form complex networks as ants discover and communicate the locations of food sources!**