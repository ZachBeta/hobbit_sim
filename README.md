# Hobbit sim
our fellowship slowly learns the skills they need to continue their journey
starting with the goal of getting from the Shire to Crickhollow
which involves escaping a black rider when departing the Shire

## Setup

Install dependencies using `uv`:
```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev]"
```

## How to run

Simulation:
```bash
python hobbit_sim.py
```

Tests:
```bash
pytest .
pytest --cov=hobbit_sim --cov-report=term-missing
```

Linting and type checking:
```bash
ruff check .
ruff format .
mypy hobbit_sim.py test_hobbit_sim.py
```