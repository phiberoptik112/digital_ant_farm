# Pheromone Field

Ants share a concentration field, one grid per signal type:

∂C/∂t = S + D ∇²C − λ C

S is secretion. D ∇²C spreads chemical that is already on the ground. −λ C is evaporation. The integral of C does not increase unless an ant deposits.

## State

`PheromoneManager` keeps a NumPy grid per `PheromoneType` (food, home, danger). Cell size is 6 px. Danger is a channel with no depositors yet.

There is no list of discs and no delayed ring of extra deposits. Diffusion is the spread.

## Each simulation step

The main loop already computes `delta_time`. The order is:

1. Deposit. An ant that is secreting adds `q * distance` into the cells its segment crosses. A stationary ant adds nothing. Overlapping and repeat walks add, up to a saturation cap well above one pass.
2. Diffuse. One explicit step, `C ← C + D dt ∇²C`, substepped when `D dt / cell²` would be unstable. Interior exchange conserves mass. The border is no-flux, so it does not create mass.
3. Evaporate. `C ← C * exp(-λ dt)`, then cells under a small epsilon are cleared. Half-life is `ln(2) / λ` for every concentration.

## Who secretes

- Searching ants lay home pheromone continuously, a small `q` per pixel.
- Ants carrying food lay food pheromone on the walk home.
- Ants following a food trail also lay food pheromone, so traffic keeps the trail.
- Deposits are not gated by a shared frame counter.

## How an ant reads the field

Samples are concentrations, not vectors toward a disc.

- On a food trail, the ant compares short left and right samples and turns toward the stronger side so it stays on the ridge. Its heading is biased away from the nest. It does not walk up the trail toward whichever end was laid last.
- Home pheromone is a mild downhill repeller, so explored ground is a region rather than a row of dots.

## Color

- Food stays `(0, 255, 100)`.
- Home stays `(100, 200, 255)`.
- Danger stays `(255, 100, 100)`.
- Opacity is proportional to concentration and reaches 0. There is no green-to-red decay and no minimum alpha.

## Defaults

| Quantity | Meaning | Default |
| --- | --- | --- |
| Food `q` | Amount per pixel while recruiting | 1.0 |
| Home `q` | Amount per pixel while searching | 0.4 |
| Food λ | Evaporation, 1/s (half-life 20 s) | ln(2)/20 |
| Home λ | Evaporation, 1/s (half-life 15 s) | ln(2)/15 |
| D | Diffusion, px²/s | 4 |
| Sense offset | Lateral sample distance, px | 8 |

The colony-behavior sliders edit these units. Decay is not a strength subtracted once per frame.

## Tests

```bash
.venv/bin/python test_pheromone_system.py
.venv/bin/python test_spreading_pheromones.py
```

`test_pheromone_system.py` checks exponential half-life, mass-conserving diffusion, and additive deposits, plus a recruit that reaches food by staying on the ridge and heading away from the nest. `test_spreading_pheromones.py` checks that the field widens on the first step and that the old 8-deposit burst does not add mass.
