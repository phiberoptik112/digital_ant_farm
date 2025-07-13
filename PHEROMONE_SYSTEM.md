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

### 🐜 Ant Behavior

- **Exploration Pheromones**: Ants deposit home trail pheromones every 30 frames while searching
- **Food Trail Creation**: Ants deposit food trail pheromones when returning to nest with food
- **Gradient Following**: Ants can sense and follow pheromone gradients to find food sources
- **Avoidance Behavior**: Ants avoid their own exploration trails to encourage new area exploration

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

## Technical Implementation

### Core Components

1. **PheromoneManager**: Manages all pheromones with spatial indexing for performance
2. **Pheromone Class**: Individual pheromone instances with position, type, strength, and decay
3. **Enhanced Rendering**: Gradient circles with alpha blending for realistic appearance
4. **Ant AI**: Improved behavior for pheromone deposition and following

### Key Parameters

- **Pheromone Strength**: 40.0 for food trails, 20.0 for home trails
- **Decay Rate**: 0.5 for food trails, 0.3 for home trails
- **Radius of Influence**: 25.0 for food trails, 15.0 for home trails
- **Deposition Frequency**: Every 30 frames for exploration, every frame when returning

### Visualization Algorithm

```python
# Enhanced pheromone rendering
for pheromone in pheromone_manager._pheromones:
    alpha = max(20, min(255, int(pheromone.strength * 3)))
    radius = int(pheromone.radius_of_influence)
    
    # Color based on type
    if pheromone.type == PheromoneType.FOOD_TRAIL:
        color = (0, 255, 100, alpha)  # Bright green
    elif pheromone.type == PheromoneType.HOME_TRAIL:
        color = (100, 200, 255, alpha)  # Light blue
    
    # Gradient circle rendering
    for r in range(radius, 0, -2):
        gradient_alpha = int(alpha * (r / radius) * 0.7)
        gradient_color = (*color[:3], gradient_alpha)
        pygame.draw.circle(surface, gradient_color, center, r)
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
4. **Trail Following**: Other ants detect food trails and follow them to food sources
5. **Reinforcement**: Multiple ants using the same trail strengthen the pheromone signal

### Emergent Behaviors
- **Trail Networks**: Multiple intersecting pheromone trails form complex networks
- **Efficient Pathfinding**: Ants find shortest paths to food sources over time
- **Collective Intelligence**: Individual simple rules create complex group behavior

## Testing Results

The test script demonstrates:
- **Pheromone Deposition**: Ants successfully deposit both trail types
- **Gradient Following**: Ants can sense and follow pheromone gradients
- **Decay System**: Pheromones properly decay over time
- **Visual Rendering**: All pheromone types display with correct colors

Example output:
```
Final Results:
Total pheromones: 40
Food trail pheromones: 25
Home trail pheromones: 15
Average strength: 25.06
Total strength: 1002.50
```

## Performance Optimization

- **Spatial Indexing**: Pheromones are organized in a grid for efficient range queries
- **Culling**: Pheromones below minimum strength are automatically removed
- **Efficient Rendering**: Gradient circles are pre-calculated and cached

## Future Enhancements

- **Danger Pheromones**: Red warning signals when ants encounter obstacles
- **Trail Reinforcement**: Stronger trails from multiple ant usage
- **Pheromone Interaction**: Different pheromone types affecting each other
- **3D Visualization**: Height-based pheromone intensity display

## Dependencies

- Python 3.7+
- pygame 2.6.1
- numpy 2.3.1

## Installation

```bash
pip install -r requirements.txt
```

---

🎉 **Watch the mesmerizing green pheromone trails form as ants discover and communicate the locations of food sources!**