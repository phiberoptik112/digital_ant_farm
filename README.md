
# Digital Ant Farm

A Python-based ant colony simulation using Pygame that demonstrates emergent behavior through pheromone trails and foraging patterns.

## Features

- **Ant Movement & Behavior**: Ants with realistic movement patterns, state management (idle, searching, returning, following trails), and energy systems
- **Pheromone System**: Layered pheromone trails with decay, different types (food trails, home trails, danger), and radius-based influence
- **Food Sources**: Depleting food sources with regeneration mechanics and visual feedback
- **Real-time Visualization**: 60 FPS Pygame simulation with visual pheromone trails and ant orientation indicators

## Project Structure

```
src/
├── main.py              # Main simulation loop and Pygame setup
└── entities/
    ├── ant.py           # Ant class with movement, state, and behavior logic
    ├── pheromone.py     # Pheromone system with PheromoneManager
    └── food.py          # Food source mechanics
```

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python src/main.py
```

**Controls:**
- ESC or close window to exit

## Current Implementation

- 5 ants spawn at random positions in searching state
- Ants move with realistic physics (acceleration, turning speed, boundary detection)
- Pheromone trails are deposited and decay over time
- Visual representation shows ants as yellow circles with orientation lines
- Pheromone trails appear as translucent colored circles (green for food trails, blue for home trails)

## Dependencies

- `pygame==2.6.1` - Game engine and graphics
- `numpy==2.3.1` - Mathematical operations and physics calculations

