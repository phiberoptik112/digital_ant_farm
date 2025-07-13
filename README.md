# Digital Ant Farm - Food System

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
- **Pheromone trails**: Ants leave pheromone trails to guide other ants to food sources
- **State-based behavior**: Different visual indicators for searching, carrying food, and returning

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

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulation:
```bash
python3 src/main.py
```

3. Run the headless demonstration:
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

### Ant-Food Interaction
- Ants detect food sources within their detection radius
- Ants navigate towards the nearest available food source
- Visual indicators show ant detection ranges and food-seeking behavior
- Ants change color when carrying food (orange vs yellow)

### Performance Optimization
- Spatial grid system for efficient food detection queries
- Optimized rendering with transparency and surface caching
- Configurable cleanup of old food sources
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
├── entities/
│   ├── ant.py          # Ant behavior and movement
│   ├── food.py         # Food system implementation
│   └── pheromone.py    # Pheromone trail system
├── ui_controls.py      # Interactive UI components
└── main.py            # Main application with integrated systems
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

