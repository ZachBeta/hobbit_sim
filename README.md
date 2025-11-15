# Hobbit Nazgûl Escape Simulation

A grid-based autonomous simulation where hobbits flee from Nazgûl to reach Rivendell. The outcome emerges from entity behaviors—no scripted victories, just AI making decisions and consequences playing out on a 20x20 grid.

Inspired by Dwarf Fortress and roguelikes, this project explores emergent gameplay through simple rules and incremental complexity.

## What Makes This Interesting

**Emergent Behavior from Simple Rules:**
- Hobbits move at speed 2, using evasion AI when Nazgûl get within distance 6
- Nazgûl move at speed 1, always chasing the nearest hobbit
- Terrain obstacles, pathfinding, and collision detection
- No predetermined outcomes—success or failure emerges from the chase

**Progressive Difficulty:**
- 3 maps with increasing challenge (Bag End → Woody End → Bucklebury Ferry)
- Multiple hobbits and multiple Nazgûl
- Named characters (Frodo, Sam, Pippin, Merry) with persistent behavior

**Incremental Development Approach:**
- Started with single hobbit escaping single Nazgûl on one map
- Gradually added multi-entity support, terrain, multiple maps, evasion AI
- Red/green/refactor workflow: build tight MVP first, clean up later
- Tests serve as "training corpus" for progressively complex scenarios

## Example Simulation Output

Here's what a typical simulation looks like (first two ticks of Map 1):

```
Hobbit Nazgûl Escape Simulation - v0

=== Tick 0 | Bag End ===
Hobbits remaining: 3
[hobbit_turn_start] {'hobbit': (1, 1), 'name': 'Frodo'}
[hobbit_moved] {'name': 'Frodo', 'from_pos': (1, 1), 'to_pos': (1, 2), 'step': 1}
[hobbit_moved] {'name': 'Frodo', 'from_pos': (1, 2), 'to_pos': (2, 2), 'step': 2}
[hobbit_turn_start] {'hobbit': (1, 1), 'name': 'Sam'}
[hobbit_moved] {'name': 'Sam', 'from_pos': (1, 1), 'to_pos': (1, 2), 'step': 1}
  Nazgûl at (18, 5) seeking target
  Nazgûl[0] chasing Hobbit at (2, 2) from (18, 5)
    → moved to (17, 5)
# # # # # # # # # # # # # # # # # # # #
# P . . . . . . . . . . . . . . . . . #
# S F . . . . . . . . . . . . . . . . #
# . . . . . . . . . . . . . . . . . . #
# . . . . . . . . . . . . . . . . . . #
# . . . . . . . . . . . . . . . . N . #
# . . . . . . . . . . . . . . . . . . #
...
```

**Legend:** `F/S/P/M` = hobbits (Frodo/Sam/Pippin/Merry), `N` = Nazgûl, `X` = exit to Rivendell, `#` = terrain

See the complete run with all three maps: [example_run_2025-11-15.txt](./examples/example_run_2025-11-15.txt)

## Setup

### 1. Install uv (Python package manager)

For installation options and information about uv, see [github.com/astral-sh/uv](https://github.com/astral-sh/uv).

### 2. Install project dependencies

```bash
# One-time setup: create venv and install dependencies
uv sync
```

This will create a virtual environment and install all required packages (pytest, mypy, ruff, etc.).

## Running the Simulation

```bash
# Run the full simulation (all 3 maps)
uv run python hobbit_sim.py

# Capture output to file for sharing
uv run python hobbit_sim.py > examples/example_run_$(date +%Y-%m-%d).txt
```

Sample runs are saved in `examples/` directory for documentation and sharing purposes.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest .

# Run specific test by name
uv run pytest test_hobbit_sim.py::test_move_toward_moves_diagonally

# Run with coverage report
uv run pytest --cov=hobbit_sim --cov-report=term-missing
```

**Current status:** 52 tests passing, 2 skipped (intentionally deferred features), 89% coverage

### Code Quality Automation

This project uses a 3-stage sequential pipeline of specialized agents for code quality:

1. **style-guide-fixer** - Enforces keyword-only parameters in function definitions
2. **ruff-fixer** - Python linting and formatting
3. **mypy-error-fixer** - Type checking with strict mode

These agents run automatically after code changes to maintain consistency. See `.claude/agents/` for implementation details.

```bash
# Manual linting and type checking
uv run ruff check .
uv run ruff format .
uv run mypy hobbit_sim.py test_hobbit_sim.py
```

### Documentation & Workflow

This is a **mind fitness project** emphasizing sustainable development and incremental progress. The documentation system helps manage cognitive load:

- **[NEXT_SESSION.md](./docs/NEXT_SESSION.md)** - "Setting out gym clothes the night before" - single source of truth for next coding session
- **[FEATURES.md](./docs/FEATURES.md)** - Feature development pipeline (Now/Soon/Maybe/Later)
- **[REFACTORING.md](./docs/REFACTORING.md)** - Bite-sized polish tasks (15-60 min)
- **[TESTS.md](./docs/TESTS.md)** - Test strategy and progressive difficulty scenarios
- **[DEVELOPMENT_APPROACH.md](./docs/DEVELOPMENT_APPROACH.md)** - Zone 1 pacing philosophy and approach

**Development philosophy:**
- Easy mode first (start simple, avoid scope creep)
- Single file initially (currently ~1000 lines in `hobbit_sim.py`)
- Print statements before visualizations (ASCII art is sufficient)
- Hardcoded before configurable (get it working first)
- Red/green/refactor (build → test → clean up)

## Future Vision

The long-term goal is a state-based LOTR narrative simulation with progressive complexity:

- **Current:** Hobbit escape mechanics (evasion, pursuit, terrain)
- **Next phase:** Tom Bombadil encounter (Old Man Willow, Barrow-wights)
- **Future:** Weathertop, Moria, tactical battles, spell/ability framework

See **[hobbit-sim-bombadil-design.md](./docs/hobbit-sim-bombadil-design.md)** and **[IDEAS.md](./docs/IDEAS.md)** for the full roadmap.

## Project Structure

```
hobbit_sim/
├── hobbit_sim.py              # Main simulation (single file ~1000 lines)
├── test_hobbit_sim.py         # Test suite (52 passing tests)
├── CLAUDE.md                  # Claude Code project instructions
├── README.md                  # This file
├── docs/                      # Planning, features, philosophy, roadmap
│   ├── NEXT_SESSION.md
│   ├── FEATURES.md
│   ├── REFACTORING.md
│   ├── TESTS.md
│   ├── DEVELOPMENT_APPROACH.md
│   ├── IDEAS.md
│   ├── hobbit-sim-bombadil-design.md
│   └── hobbit-sim-context.md
├── examples/                  # Example simulation outputs
│   └── example_run_2025-11-15.txt
├── logs/                      # JSONL event logs from simulation runs
└── .claude/agents/            # Specialized code quality agents
```

## Why This Project Exists

This is a mind fitness project exploring new stacks through sustainable, playful practice:
- **Tech stack:** Python, mypy (strict typing), ruff (linting), pytest (TDD)
- **Development stack:** Claude Code subagents, automated code quality pipelines, ask-first collaboration mode

It prioritizes:
- Playful exploration over optimization
- Tiny wins and forward momentum
- Sustainable practice and Zone 1 pacing (building capacity gradually)
- Progressive complexity (learning new patterns incrementally)

The approach: treat coding like endurance training—consistent practice at a sustainable pace builds skills better than unsustainable sprints.

The tests serve double duty: validation *and* training scenarios for increasingly complex hobbit AI behavior.

---

**Current simulation:** Multiple hobbits escaping multiple Nazgûl across three progressive maps.

**The goal:** Eventually simulate the full Fellowship's journey through Middle-earth, one narrative beat at a time.
