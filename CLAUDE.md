# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a grid-based simulation of hobbits fleeing from Nazgûl to reach Rivendell. It's an autonomous simulation (no player input) where the outcome emerges from entity behaviors. The project emphasizes simplicity, incremental development, and playful exploration over optimization.
Inspired by Dwarf Fortress and Roguelikes

## Interaction Mode: Ask-First by Default

**Default behavior: Discussion and suggestions, NOT automatic edits**

This project uses an "ask mode" interaction pattern to support hands-on learning and skill development:

1. **Read and discuss by default** - Explore the codebase, answer questions, explain concepts
2. **Provide code snippets** - Show suggested changes as code blocks, not direct edits
3. **Wait for explicit permission** - Only use Edit/Write tools when the user clearly requests file changes
4. **Support manual editing** - Assume the user may implement suggestions in Cursor or other editors
5. **Enable human-in-the-loop learning** - User stays engaged with each change rather than reviewing bulk automated edits

### When to make direct file changes:
- User explicitly says "make the change", "edit the file", "update the code", "implement this"
- User requests automated fixes: "run the linter", "fix type errors", "format the code"
- User asks for specific tool use: "use the agent", "run the fixer"

### When to provide suggestions instead:
- General questions about the codebase
- Discussing potential improvements or features
- Explaining how to fix issues
- Reviewing code or architecture
- Any ambiguous requests - default to showing code snippets and asking if the user wants them applied

This approach makes it easier to:
- Learn Python hands-on by implementing suggestions yourself
- Track what changed and why (no mystery bulk edits)
- Roll back changes easily (manual git control)
- Stay engaged with the development process

## Development Commands

### Environment Setup
```bash
# One-time setup: create venv and install dependencies
uv sync
```

### Running
```bash
# Run the simulation
uv run python hobbit_sim.py

# Run all tests
uv run pytest .

# Run single test by name
uv run pytest test_hobbit_sim.py::test_move_toward_moves_diagonally

# Run tests with coverage
uv run pytest --cov=hobbit_sim --cov-report=term-missing
```

### Generating Example Runs
To capture simulation output for documentation or sharing:
```bash
# Generate a timestamped example run
uv run python hobbit_sim.py > examples/example_run_$(date +%Y-%m-%d).txt

# Or with full timestamp
uv run python hobbit_sim.py > examples/example_run_$(date +%Y-%m-%d_%H%M%S).txt
```

Example runs are stored in the `examples/` directory and can be referenced in README.md or shared with other developers to demonstrate the simulation's behavior.

### Linting and Type Checking
```bash
# Check linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy hobbit_sim.py test_hobbit_sim.py
```

**Important**: Line length limit is 100 characters (configured in pyproject.toml). mypy is configured with strict type checking - all functions require type annotations.

### Code Quality Workflow
After any code changes, the following checks must be run **sequentially** (one at a time, waiting for each to complete) to ensure code quality:

1. **Style guide compliance** - Uses `style-guide-fixer` agent to verify and fix all functions to use keyword-only parameters
2. **Ruff linting and formatting** - Uses `ruff-fixer` agent to check and auto-fix linting issues
3. **Type checking** - Uses `mypy-error-fixer` agent to find and fix type errors

**IMPORTANT: Run these agents ONE AT A TIME, not in parallel.**
- Wait for each agent to complete before running the next
- Running them in parallel can cause conflicts and file corruption
- Always run in the order listed above (style guide → ruff → mypy)

These are automated through specialized agents in `.claude/agents/` and should be invoked proactively after implementing features or fixing bugs.

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

## Design Philosophy

See [docs/DEVELOPMENT_APPROACH.md](docs/DEVELOPMENT_APPROACH.md) for full details.

1. **Easy mode first** - Start simple, avoid scope creep
2. **Single file initially** - Currently `hobbit_sim.py` + tests
3. **Print statements before visualizations** - ASCII art is sufficient
4. **Hardcoded before configurable** - Get it working first
5. **No premature optimization** - Pure Python is fine

This is a mind fitness project exploring new tech stacks (Python/mypy/ruff) and development stacks (Claude Code subagents) through sustainable practice - prioritize playful exploration, tiny wins, and forward momentum over perfect code. Build incrementally, one feature at a time.

## Testing Strategy

Tests are organized by scope:
- **Unit tests**: Individual movement functions (`test_move_toward_moves_diagonally`)
- **Integration tests**: Entity update functions with terrain (`test_hobbit_cannot_move_through_terrain`)
- **System tests**: Full simulation scenarios (`test_system_three_hobbits_escape_single_rider`)
- **Rendering tests**: Grid visualization (`test_render_world_shows_terrain`)

Skipped tests (marked with `@pytest.mark.skip`) represent future features, not current bugs.
