# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a grid-based simulation of hobbits fleeing from Nazgûl to reach Rivendell. It's an autonomous simulation (no player input) where the outcome emerges from entity behaviors. The project emphasizes simplicity, incremental development, and playful exploration over optimization.
Inspired by Dwarf Fortress and Roguelikes

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
uv pip install -e ".[dev]"
```

### Running
```bash
# Run the simulation
python hobbit_sim.py

# Run all tests
pytest .

# Run single test by name
pytest test_hobbit_sim.py::test_move_toward_moves_diagonally

# Run tests with coverage
pytest --cov=hobbit_sim --cov-report=term-missing
```

### Linting and Type Checking
```bash
# Check linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Type checking
mypy hobbit_sim.py test_hobbit_sim.py
```

**Important**: Line length limit is 100 characters (configured in pyproject.toml). mypy is configured with strict type checking - all functions require type annotations.

## Code Architecture

### Core Simulation Loop
The simulation runs in tick-based cycles in `run_simulation()`:
1. **Render** - Create grid, place entities (terrain, hobbits, Nazgûl)
2. **Check win/loss** - All hobbits at Rivendell = win, no hobbits left = loss
3. **Update entities** - Move hobbits (toward goal or evading), move Nazgûl (chase nearest hobbit)
4. **Resolve captures** - Remove hobbits that overlap with Nazgûl
5. **Repeat** with 0.3s delay

### World State Structure
World initialization (`create_world()`) returns a dict containing:
- `width`, `height`: Grid dimensions (20x20)
- `rivendell`: Goal position (19, 19)
- `terrain`: Set of impassable positions (borders with openings at Shire and Rivendell)
- `hobbits`: List of hobbit positions
- `nazgul`: List of Nazgûl positions

### Entity Behavior

**Hobbits** (`update_hobbits`):
- Speed: 2 squares/tick
- Behavior: If Nazgûl within distance 6, evade by moving away; otherwise move toward Rivendell
- Failed evasions fall back to moving toward goal

**Nazgûl** (`update_nazgul`):
- Speed: 1 square/tick
- Behavior: Chase nearest hobbit using Manhattan distance

### Movement System
- `move_toward()`: Single diagonal step toward target
- `move_away_from()`: Single diagonal step away from threat
- `move_with_speed()`: Multi-step movement with boundary and terrain collision
- All movement respects grid boundaries and terrain obstacles

### Rendering
Two rendering approaches:
1. **Manual**: `create_grid()` → `place_entity()` → `render_grid()` - Full control
2. **Automatic**: `render_world(world_dict)` - Renders complete scene from world state

Symbols: `H` = hobbit, `N` = Nazgûl, `S` = Shire, `R` = Rivendell, `#` = terrain, `.` = empty

### Event Logging
All significant events are logged to `logs/*.jsonl`:
- Test runs: `logs/test_<timestamp>.jsonl`
- Development: `logs/simulation_<timestamp>.jsonl`
- Events: movement attempts, evasions, captures, victories, defeats

## Design Philosophy (from INIT.md)

1. **Easy mode first** - Start simple, avoid scope creep
2. **Single file initially** - Currently `hobbit_sim.py` + tests
3. **Print statements before visualizations** - ASCII art is sufficient
4. **Hardcoded before configurable** - Get it working first
5. **No premature optimization** - Pure Python is fine

This is a mind fitness project for long COVID recovery - prioritize playful exploration, tiny wins, and forward momentum over perfect code. Build incrementally, one feature at a time.

## Testing Strategy

Tests are organized by scope:
- **Unit tests**: Individual movement functions (`test_move_toward_moves_diagonally`)
- **Integration tests**: Entity update functions with terrain (`test_hobbit_cannot_move_through_terrain`)
- **System tests**: Full simulation scenarios (`test_system_three_hobbits_escape_single_rider`)
- **Rendering tests**: Grid visualization (`test_render_world_shows_terrain`)

Skipped tests (marked with `@pytest.mark.skip`) represent future features, not current bugs.
