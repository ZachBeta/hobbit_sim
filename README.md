# Hobbit sim
our fellowship slowly learns the skills they need to continue their journey
starting with the goal of getting from the Shire to Crickhollow
which involves escaping a black rider when departing the Shire

## Setup

Install dependencies using `uv`:
```bash
# One-time setup: create venv and install dependencies
uv sync
```

## How to run

Simulation:
```bash
uv run python hobbit_sim.py
```

Tests:
```bash
uv run pytest .
uv run pytest --cov=hobbit_sim --cov-report=term-missing
```

Linting and type checking:
```bash
uv run ruff check .
uv run ruff format .
uv run mypy hobbit_sim.py test_hobbit_sim.py
```