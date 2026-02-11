# Digital Ant Farm

A comprehensive ant colony simulation with an advanced food system featuring time-based expiration, automatic refresh, and real-time UI controls.

## Features

### 🍃 Advanced Food System
- **Randomized placement and quantity**: Food sources are randomly distributed with varying amounts
- **Time-based expiration**: Food gradually expires over time, independent of consumption
- **Automatic refresh**: Expired food sources automatically regenerate after a configurable time period
- **Real-time UI controls**: Adjust all food system parameters using interactive sliders and controls
- **Visual indicators**: Food sources show their state through color changes and countdown timers
- **Auto-generation**: System automatically maintains target number of food sources
- **Spatial optimization**: Efficient spatial grid system for fast food detection

### 🐜 Ant Behavior
- **Food seeking**: Ants actively search for and move towards nearby food sources
- **Food collection**: Ants collect food and change behavior when carrying it
- **Advanced pheromone trails**: Enhanced trail system with quality-based persistence and reinforcement
- **Trail learning**: Frequently used trails become stronger and last longer
- **State-based behavior**: Different visual indicators for searching, carrying food, and returning

### 🌍 Enhanced Pheromone System
- **Trail quality**: Pheromones improve quality based on usage frequency
- **Dynamic radius**: Pheromone influence radius expands as strength decays for better coverage
- **Quality-based decay**: High-quality trails decay slower, creating persistent pathways
- **Ground interaction**: Pheromones interact with ground properties affecting persistence
- **Visual feedback**: Brighter colors indicate higher quality, well-established trails
- **Usage tracking**: System tracks how often trails are used for reinforcement

### 🏞️ Ground System
- **Cellular ground**: World divided into cells with unique environmental properties
- **Moisture effects**: Ground moisture affects pheromone decay rates
- **Temperature variation**: Ground temperature influences pheromone evaporation
- **Porosity simulation**: Soil porosity affects how pheromones are absorbed
- **Dynamic environment**: Ground properties slowly change over time
- **Visual representation**: Ground cells display different colors based on properties

### 🎮 Interactive Controls
- **TAB**: Toggle the food system control panel
- **R**: Regenerate all food sources
- **C**: Clear all food sources
- **Real-time sliders** for:
  - Number of food sources (1-20)
  - Food amount range (min/max)
  - Expiration time (5-120 seconds)
  - Refresh time (10-180 seconds)
  - Expiration rate (0.1-10 units/second)
  - Auto-generation toggle
  - Manual regeneration and clearing

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulation:
```bash
python3 src/main.py
```

4. Run the headless demonstration:
```bash
python3 test_food_system_demo.py
```

## Food System Architecture

### Core Components

1. **FoodSource**: Individual food sources with:
   - Time-based expiration mechanics
   - Collection and depletion tracking
   - Visual state indicators
   - Automatic refresh capabilities

2. **FoodManager**: Manages all food sources with:
   - Spatial grid optimization for fast queries
   - Auto-generation of new food sources
   - Configurable parameters
   - Statistics tracking

3. **FoodSystemUI**: Interactive control panel with:
   - Real-time parameter adjustment
   - Visual feedback and statistics
   - Manual control buttons

### Key Features

#### Time-Based Expiration
- Food sources expire after a configurable time period
- Gradual decay during the final 50% of their lifetime
- Visual color changes from green → yellow → red → dark red (expired)
- Countdown timers appear when food is about to expire

#### Automatic Refresh
- Expired food sources automatically regenerate after a longer time period
- Configurable refresh time independent of expiration time
- Visual refresh countdown timers
- Seamless transition back to available state

#### UI Controls
The food system exposes all parameters through an interactive UI panel:
- **Number of food sources**: Controls target number of food sources
- **Food amount range**: Sets minimum and maximum food quantities
- **Expiration time**: Time in seconds before food expires
- **Refresh time**: Time in seconds before expired food regenerates
- **Expiration rate**: How fast food decays (units per second)
- **Auto-generation**: Toggle automatic food source generation
- **Manual controls**: Buttons to regenerate or clear all food

## Technical Implementation

### Food Source Lifecycle
1. **Spawn**: Food appears at random location with random amount
2. **Available**: Food can be collected by ants
3. **Aging**: Food gradually decays as it approaches expiration
4. **Expired**: Food becomes unavailable and shows refresh countdown
5. **Refresh**: Food regenerates to full capacity and restarts cycle

### Enhanced Pheromone System
- **Trail Quality System**: Pheromones track usage frequency and improve quality (1.0-3.0 multiplier)
- **Dynamic Radius**: Influence radius expands as pheromones decay (1.0x to 1.5x initial radius)
- **Quality-Based Decay**: High-quality trails decay 20-70% slower than standard pheromones
- **Usage Reinforcement**: Each use increases trail quality with diminishing returns
- **Visual Indicators**: Color brightness reflects trail quality and usage frequency

### Ground System Architecture
- **Cellular Grid**: World divided into cells with unique environmental properties
- **Ground Properties**: Each cell has moisture (0.3-0.8), porosity (0.2-0.7), temperature (0.6-1.0), and roughness (0.1-0.9)
- **Environmental Effects**: Ground conditions modify pheromone decay rates dynamically
- **Spatial Optimization**: Efficient cell-based lookups for pheromone interactions
- **Dynamic Environment**: Ground properties change slowly over time to simulate natural variation

### Ant-Food Interaction
- Ants detect food sources within their detection radius
- Ants navigate towards the nearest available food source
- Enhanced pathfinding using quality-weighted pheromone gradients
- Visual indicators show ant detection ranges and food-seeking behavior
- Ants change color when carrying food (orange vs yellow)

### Performance Optimization
- Spatial grid system for efficient food detection queries
- Cell-based ground system for optimized pheromone management
- Optimized rendering with transparency and surface caching
- Configurable cleanup of old food sources and depleted pheromones
- Delta-time based updates for smooth animation

## Testing

The system includes comprehensive tests demonstrating:
- Food source lifecycle with expiration and refresh
- Configurable parameters and their effects
- Ant-food interaction mechanics
- Advanced features like auto-generation and cleanup

Run the test suite:
```bash
python3 test_food_system_demo.py
```

## Project Structure

```
src/
├── main.py              # Main simulation loop and Pygame setup
├── ui_controls.py       # Interactive UI components
├── pheromone_renderer.py # Specialized rendering for pheromone visualization
├── queen_controls.py    # Advanced controls for queen ant management
└── entities/
    ├── ant.py           # Ant class with movement, state, and behavior logic
    ├── pheromone.py     # Enhanced pheromone system with quality tracking and persistence
    ├── food.py          # Food source mechanics with time-based expiration
    └── ground.py        # Ground system with environmental properties affecting pheromones
```

## Development

The food system is designed to be:
- **Modular**: Each component can be used independently
- **Configurable**: All parameters exposed through UI
- **Extensible**: Easy to add new food types or behaviors
- **Performant**: Optimized for real-time simulation

## Future Enhancements

Potential improvements include:
- Different food types with unique properties
- Seasonal food availability patterns
- Ant nest integration for food storage
- Advanced AI behaviors for optimal foraging
- Network-based multi-colony simulations

## Dependencies

- `pygame==2.6.1` - Game engine and graphics
- `numpy==2.3.1` - Mathematical operations and physics calculations

