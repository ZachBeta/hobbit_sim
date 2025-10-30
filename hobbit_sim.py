# hobbit_sim.py
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, TypedDict

Position = tuple[int, int]
GridDimensions = tuple[int, int]
Grid = list[list[str]]
EntityPositions = list[Position]


@dataclass
class WorldState:
    """Complete simulation state including map and entities."""

    # Map configuration (immutable during simulation)
    width: int
    height: int
    rivendell: Position
    terrain: set[Position]
    starting_hobbit_count: int
    starting_nazgul_count: int

    # Entity state (mutable during simulation)
    hobbits: EntityPositions
    nazgul: EntityPositions
    tick: int = 0

    @property
    def dimensions(self) -> GridDimensions:
        """Grid dimensions as tuple."""
        return (self.width, self.height)


class SimulationResult(TypedDict):
    """Result of running a simulation."""

    outcome: str
    ticks: int
    hobbits_escaped: int
    hobbits_captured: int


class TickCallback(Protocol):
    """Protocol for simulation tick callbacks with keyword-only parameters."""

    def __call__(
        self,
        *,
        state: WorldState,
    ) -> None:
        """Called each simulation tick with current world state."""
        ...


# Auto-detect environment (Rails-style)
def _get_log_filename() -> str:
    """Determine log filename based on environment"""
    if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
        # Test environment - single overwritable log
        return f"logs/test_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"
    else:
        # Development - timestamped log per run
        return f"logs/sim_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"


LOG_FILENAME = _get_log_filename()


@dataclass
class GameEvent:
    """Represents a game event with structured data and narrative formatting"""

    tick: int
    event_type: str
    data: dict[str, Any]

    def to_log_entry(self) -> dict:
        """Format for JSON logging (includes all data, including indices)"""
        return {"tick": self.tick, "event_type": self.event_type, "event_data": self.data}

    def to_narrative(self) -> str:
        """Format as narrative text for watching the simulation unfold"""
        formatter = EVENT_FORMATTERS.get(self.event_type)
        if formatter:
            return formatter(self.data)
        return f"[{self.event_type}] {self.data}"


class NarrativeBuffer:
    """Collects narrative output during a simulation tick"""

    _buffer: list[str] = []

    @classmethod
    def append(cls, message: str) -> None:
        """Add a message to the narrative buffer"""
        if message:  # Only add non-empty messages
            cls._buffer.append(message)

    @classmethod
    def flush(cls) -> None:
        """Print all buffered messages and clear the buffer"""
        for msg in cls._buffer:
            print(msg)
        cls._buffer.clear()


# Narrative formatters - tell the story of what's happening
EVENT_FORMATTERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "nazgul_movement": lambda d: (
        f"  Nazgûl[{d['nazgul_index']}] chasing Hobbit at {d['hobbit']} from {d['nazgul']}"
    ),
    # Evasion story
    "evasion_attempt": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: "
        f"evading from Nazgûl at {d['nazgul']}, trying {d['attempted_position']}"
    ),
    "evasion_success": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: "
        f"evasion successful → {d['new_position']}"
    ),
    "evasion_failure": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: "
        f"evasion blocked at {d['attempted_position']}, falling back to goal-seeking"
    ),
    # Safe travel (when not evading)
    "hobbit_safe_travel": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] safe - moving toward Rivendell "
        f"from {d['hobbit']} to {d['rivendell']}"
    ),
    # Game outcomes
    "victory": lambda d: "🎉 Victory! All hobbits reached Rivendell!",
    "defeat": lambda d: "💀 Defeat! Some hobbits were caught!",
    "hobbit_captured": lambda d: f"💀 Hobbit caught at {d['hobbit']}!",
    # Movement detail (sub-steps)
    "movement": lambda d: f"    → moved to {d['new_position']}",
    "movement_blocked": lambda d: f"    ✗ blocked at {d['entity']} (terrain/boundary)",
    # Nazgûl decision-making
    "nazgul_movement_attempt": lambda d: f"  Nazgûl at {d['nazgul']} seeking target",
    # Cleanup bookkeeping
    "hobbits_removed": lambda d: (
        f"  Removed {len(d['hobbits'])} hobbit(s)" if d["hobbits"] else ""
    ),
    # Evasion fallback (when evasion fails, try moving toward goal)
    "evasion_fallback_attempt": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: "
        f"fallback to goal {d['attempted_position']}"
    ),
    "evasion_fallback_success": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: "
        f"fallback successful → {d['new_position']}"
    ),
    "evasion_fallback_blocked": lambda d: (
        f"  Hobbit[{d['hobbit_index']}] step {d['step']}/2: fallback blocked at {d['current']}"
    ),
    # Nazgûl collision
    "nazgul_blocked": lambda d: (
        f"  Nazgûl[{d['nazgul_index']}] cannot move to {d['attempted_position']} (occupied)"
    ),
}


def emit_event(*, tick: int, event_type: str, **event_data: Any) -> None:
    """Emit a game event - handles both logging and narrative output"""
    event = GameEvent(tick=tick, event_type=event_type, data=event_data)

    # Write structured log
    log_entry = event.to_log_entry()
    with open(LOG_FILENAME, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")

    # Add narrative to buffer
    narrative = event.to_narrative()
    NarrativeBuffer.append(narrative)


def create_grid(*, dimensions: GridDimensions = (20, 20)) -> Grid:
    """Create a 2D grid filled with empty spaces"""
    width, height = dimensions
    grid = []
    for _y in range(height):
        row = []
        for _x in range(width):
            row.append(".")
        grid.append(row)
    return grid


def print_grid(*, grid: Grid) -> None:
    """Print the grid with all entities"""
    print(render_grid(grid=grid))
    print()


def render_world(*, world: WorldState) -> str:
    """Render world state as string (high-level test helper)

    Takes WorldState from create_world() and returns visual representation.
    Useful for testing complete scenes without manual entity placement.
    """
    # Create fresh grid
    grid = create_grid(dimensions=world.dimensions)

    # Place terrain (if any)
    for terrain_pos in world.terrain:
        place_entity(grid=grid, position=terrain_pos, symbol="#")

    # Place landmarks
    place_entity(grid=grid, position=(0, 0), symbol="S")  # Shire
    place_entity(grid=grid, position=world.rivendell, symbol="R")

    # Place hobbits
    for hobbit_pos in world.hobbits:
        place_entity(grid=grid, position=hobbit_pos, symbol="H")

    # Place nazgul
    for nazgul_pos in world.nazgul:
        place_entity(grid=grid, position=nazgul_pos, symbol="N")

    return render_grid(grid=grid)


def render_grid(*, grid: Grid) -> str:
    """Return grid as string (for testing and printing)

    Format: "H . .\nN . .\n. . ."
    """
    lines = []
    for row in grid:
        lines.append(" ".join(row))
    return "\n".join(lines)


def place_entity(*, grid: Grid, position: Position, symbol: str) -> None:
    """Place an entity on the grid at position"""
    x, y = position
    if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
        grid[y][x] = symbol


def move_toward(*, current: Position, target: Position) -> Position:
    """Move one step toward target using Manhattan distance (no diagonals).

    Prioritizes moving on the axis with greater distance first.
    """
    current_x, current_y = current
    target_x, target_y = target
    dx = abs(target_x - current_x)
    dy = abs(target_y - current_y)

    # Move on the axis with greater distance
    if dx > dy:
        # X axis is further - move horizontally
        if current_x < target_x:
            return current_x + 1, current_y
        elif current_x > target_x:
            return current_x - 1, current_y
    else:
        # Y axis is further (or equal) - move vertically
        if current_y < target_y:
            return current_x, current_y + 1
        elif current_y > target_y:
            return current_x, current_y - 1

    # Already at target
    return current_x, current_y


def find_nearest_hobbit(
    *, nazgul: Position, hobbits: EntityPositions
) -> tuple[Position | None, int]:
    """Find nearest Hobbit and Manhattan distance.

    Returns (hobbit_pos, distance) or (None, 999_999_999) when no hobbits exist.
    Distance is calculated as Manhattan distance: |dx| + |dy|.
    """
    if not hobbits:
        return None, 999_999_999  # Nine 9's for the Nine Rings of Men

    nazgul_x, nazgul_y = nazgul
    nearest = hobbits[0]
    min_dist = abs(nazgul_x - nearest[0]) + abs(nazgul_y - nearest[1])

    for hobbit in hobbits[1:]:
        dist = abs(nazgul_x - hobbit[0]) + abs(nazgul_y - hobbit[1])
        if dist < min_dist:
            min_dist = dist
            nearest = hobbit

    return nearest, min_dist


def move_with_speed(
    *,
    current: Position,
    target: Position,
    speed: int,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
) -> Position:
    """Move toward target for 'speed' steps, stopping at boundaries or terrain."""
    current_x, current_y = current
    width, height = dimensions
    if terrain is None:
        terrain = set()

    for _step in range(speed):
        new_x, new_y = move_toward(current=(current_x, current_y), target=target)

        # Check boundaries and terrain
        if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
            current_x, current_y = new_x, new_y
            emit_event(
                tick=tick,
                event_type="movement",
                entity=current,
                new_position=(current_x, current_y),
            )
        else:
            emit_event(
                tick=tick,
                event_type="movement_blocked",
                entity=current,
                new_position=(current_x, current_y),
            )
            # Hit boundary or terrain, stop moving
            break

    return current_x, current_y


def find_nearest_nazgul(
    *, hobbit: Position, nazgul: EntityPositions
) -> tuple[Position | None, int]:
    """Find nearest Nazgûl and Manhattan distance.

    Returns (nazgul_pos, distance) or (None, 999_999_999) when no Nazgûl exist.
    Distance is calculated as Manhattan distance: |dx| + |dy|.
    """
    if not nazgul:
        return None, 999_999_999  # Nine 9's for the Nine Rings of Men

    hobbit_x, hobbit_y = hobbit
    nearest = nazgul[0]
    min_dist = abs(hobbit_x - nearest[0]) + abs(hobbit_y - nearest[1])

    for naz in nazgul[1:]:
        dist = abs(hobbit_x - naz[0]) + abs(hobbit_y - naz[1])
        if dist < min_dist:
            min_dist = dist
            nearest = naz

    return nearest, min_dist


def move_away_from(
    *,
    current: Position,
    threat: Position,
    goal: Position | None = None,
) -> Position:
    """Move away from threat, with bias toward goal if provided.

    Strategy:
    1. Determine which axes move away from threat
    2. If goal provided, prefer the axis that also moves toward goal
    3. Otherwise, use normal distance priority
    """
    current_x, current_y = current
    threat_x, threat_y = threat
    dx = abs(threat_x - current_x)
    dy = abs(threat_y - current_y)

    # Calculate movement directions away from threat
    x_away = -1 if current_x < threat_x else 1 if current_x > threat_x else 0
    y_away = -1 if current_y < threat_y else 1 if current_y > threat_y else 0

    # If we have a goal, check which away-direction also moves toward goal
    if goal is not None:
        goal_x, goal_y = goal
        x_toward_goal = 1 if current_x < goal_x else -1 if current_x > goal_x else 0
        y_toward_goal = 1 if current_y < goal_y else -1 if current_y > goal_y else 0

        # Does fleeing on X axis also move toward goal?
        x_helps_goal = (x_away == x_toward_goal) if x_away != 0 else False
        # Does fleeing on Y axis also move toward goal?
        y_helps_goal = (y_away == y_toward_goal) if y_away != 0 else False

        # Prefer axis that helps with goal
        if x_helps_goal and not y_helps_goal and x_away != 0:
            return current_x + x_away, current_y
        if y_helps_goal and not x_helps_goal and y_away != 0:
            return current_x, current_y + y_away

    # Fall back to normal priority: larger distance first
    if dx >= dy and x_away != 0:
        return current_x + x_away, current_y
    elif y_away != 0:
        return current_x, current_y + y_away
    elif x_away != 0:
        return current_x + x_away, current_y

    return current_x, current_y


def calculate_perpendicular_moves(
    *,
    current: Position,
    threat: Position,
) -> list[Position]:
    """Calculate perpendicular escape moves when direct evasion is blocked.

    Returns 2 positions perpendicular to the primary threat axis.

    Logic:
    - If threat is primarily on X axis (east/west) → return north/south moves
    - If threat is primarily on Y axis (north/south) → return east/west moves

    Example:
        >>> calculate_perpendicular_moves(current=(10, 10), threat=(15, 10))
        [(10, 11), (10, 9)]  # Threat is east, so flee north/south

    Args:
        current: Hobbit's current position
        threat: Nearest Nazgûl position

    Returns:
        List of 2 perpendicular positions (not validated for terrain/bounds)
    """
    current_x, current_y = current
    threat_x, threat_y = threat

    # Calculate which axis the threat is primarily on
    dx = abs(threat_x - current_x)
    dy = abs(threat_y - current_y)

    # If threat is more on X axis, escape on Y axis (and vice versa)
    if dx >= dy:
        # Threat is east/west → flee north/south
        return [
            (current_x, current_y + 1),  # South
            (current_x, current_y - 1),  # North
        ]
    else:
        # Threat is north/south → flee east/west
        return [
            (current_x + 1, current_y),  # East
            (current_x - 1, current_y),  # West
        ]


def move_hobbit_one_step(
    *,
    current: Position,
    goal: Position,
    threats: EntityPositions,
    terrain: set[Position],
    dimensions: GridDimensions,
) -> Position:
    """Move hobbit one step based on perception of world.

    Hobbit autonomously decides behavior based on nearby threats:
    - If Nazgûl within danger distance (6): Generate evasion options
    - Otherwise: Move toward goal

    For each potential move, hobbit tries options in priority order:
    1. Direct escape (away from threat, biased toward goal)
    2. Perpendicular escape (sideways from threat)
    3. Toward goal (fallback - give up evasion)

    Returns first valid option, or current position if all blocked.

    Args:
        current: Hobbit's current position
        goal: Rivendell position
        threats: List of Nazgûl positions
        terrain: Set of impassable positions
        dimensions: Grid bounds (width, height)

    Returns:
        New position after one step (or current if all options blocked)
    """
    DANGER_DISTANCE = 6

    # Perceive: Find nearest threat
    nearest_threat, distance = find_nearest_nazgul(hobbit=current, nazgul=threats)

    # Decide: Generate options based on perception
    options: list[Position] = []

    if distance <= DANGER_DISTANCE and nearest_threat is not None:
        # Mode: EVADING - Generate multiple escape options

        # Priority 1: Direct escape (away from threat, toward goal if possible)
        options.append(move_away_from(current=current, threat=nearest_threat, goal=goal))

        # Priority 2: Perpendicular escape (sideways from threat)
        perpendicular = calculate_perpendicular_moves(current=current, threat=nearest_threat)
        options.extend(perpendicular)

        # Priority 3: Toward goal (fallback - give up evasion if trapped)
        options.append(move_toward(current=current, target=goal))
    else:
        # Mode: TRAVELING - Simple movement toward goal
        options.append(move_toward(current=current, target=goal))

    # Act: Try each option until one is valid
    for option in options:
        if is_valid_position(position=option, dimensions=dimensions, terrain=terrain):
            return option

    # All options blocked - stay put
    return current


def is_valid_position(
    *,
    position: Position,
    dimensions: GridDimensions,
    terrain: set[Position],
) -> bool:
    """Check if position is within bounds and not blocked by terrain."""
    x, y = position
    width, height = dimensions
    return 0 <= x < width and 0 <= y < height and position not in terrain


def update_hobbits(
    *,
    hobbits: EntityPositions,
    rivendell: Position,
    nazgul: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
) -> EntityPositions:
    """Move all hobbits toward Rivendell at speed 2.

    Each hobbit:
    1. Takes 2 steps (speed 2)
    2. Reassesses world after each step (greedy evaluation)
    3. Autonomously decides behavior based on perceived threats

    Returns new hobbit positions.
    """
    if terrain is None:
        terrain = set()

    new_hobbits = []

    for hobbit_pos in hobbits:
        current = hobbit_pos

        # Speed 2: Take 2 steps, reassessing after each
        for _step in range(2):
            current = move_hobbit_one_step(
                current=current,
                goal=rivendell,
                threats=nazgul,
                terrain=terrain,
                dimensions=dimensions,
            )

        new_hobbits.append(current)

    return new_hobbits


def update_nazgul(
    *,
    nazgul: EntityPositions,
    hobbits: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
) -> EntityPositions:
    """Move all Nazgûl toward nearest hobbit at speed 1. Returns new Nazgûl positions."""
    new_nazgul = set()
    width, height = dimensions
    if terrain is None:
        terrain = set()

    for nazgul_index, nazgul_pos in enumerate(nazgul):
        emit_event(
            tick=tick,
            event_type="nazgul_movement_attempt",
            nazgul=nazgul_pos,
            hobbits=hobbits,
        )
        target, distance = find_nearest_hobbit(nazgul=nazgul_pos, hobbits=hobbits)
        if target:
            emit_event(
                tick=tick,
                event_type="nazgul_movement",
                nazgul=nazgul_pos,
                nazgul_index=nazgul_index,
                hobbit=target,
            )
            new_x, new_y = move_with_speed(
                current=nazgul_pos,
                target=target,
                speed=1,
                dimensions=dimensions,
                tick=tick,
                terrain=terrain,
            )
            if (new_x, new_y) not in new_nazgul:
                new_nazgul.add((new_x, new_y))
            else:
                new_nazgul.add(nazgul_pos)
                emit_event(
                    tick=tick,
                    event_type="nazgul_blocked",
                    nazgul_index=nazgul_index,
                    nazgul=nazgul_pos,
                    attempted_position=(new_x, new_y),
                )
    return list(new_nazgul)


def create_world() -> WorldState:
    """Initialize world state (terrain, entities, landmarks)

    Returns WorldState with complete simulation configuration and initial entity positions.
    """
    WIDTH, HEIGHT = 20, 20
    rivendell = (18, 18)

    # Terrain - create border walls (but leave openings at Shire and Rivendell)
    terrain = set()

    # Add borders (all edges)
    for x in range(WIDTH):
        terrain.add((x, 0))  # Top border
        terrain.add((x, HEIGHT - 1))  # Bottom border
    for y in range(HEIGHT):
        terrain.add((0, y))  # Left border
        terrain.add((WIDTH - 1, y))  # Right border

    hobbits = [
        (1, 2),  # Pippin
        (2, 1),  # Sam
        (2, 2),  # Frodo
    ]

    # Initialize Nazgûl
    nazgul = [
        (18, 5),  # Far from hobbits
    ]

    starting_hobbit_count = len(hobbits)
    starting_nazgul_count = len(nazgul)

    return WorldState(
        width=WIDTH,
        height=HEIGHT,
        rivendell=rivendell,
        terrain=terrain,
        hobbits=hobbits,
        nazgul=nazgul,
        starting_hobbit_count=starting_hobbit_count,
        starting_nazgul_count=starting_nazgul_count,
        tick=0,
    )


def _render_simulation_state(
    *,
    state: WorldState,
) -> Grid:
    """
    Render current simulation state to a grid.

    Args:
        state: Complete world state

    Returns:
        Grid with all entities placed
    """
    # Create fresh grid
    grid = create_grid(dimensions=state.dimensions)

    # Place terrain
    for terrain_pos in state.terrain:
        place_entity(grid=grid, position=terrain_pos, symbol="#")

    # Place landmarks
    place_entity(grid=grid, position=(1, 1), symbol="S")  # Shire
    place_entity(grid=grid, position=state.rivendell, symbol="R")  # Rivendell

    # Place hobbits
    for hobbit_pos in state.hobbits:
        place_entity(grid=grid, position=hobbit_pos, symbol="H")

    # Place Nazgûl
    for nazgul_pos in state.nazgul:
        place_entity(grid=grid, position=nazgul_pos, symbol="N")

    return grid


def _run_simulation_loop(
    *,
    max_ticks: int | None = None,
    on_tick: TickCallback | None = None,
) -> SimulationResult:
    """
    Core simulation loop: create world, run until victory/defeat/timeout.

    Args:
        max_ticks: Optional limit on simulation length (for testing)
        on_tick: Optional callback called each tick with current world state

    Returns:
        Dict with keys: outcome, ticks, hobbits_escaped, hobbits_captured
    """
    state = create_world()

    while True:
        # Check timeout
        if max_ticks is not None and state.tick >= max_ticks:
            hobbits_escaped = sum(1 for h in state.hobbits if h == state.rivendell)
            hobbits_captured = state.starting_hobbit_count - len(state.hobbits)
            return {
                "outcome": "timeout",
                "ticks": state.tick,
                "hobbits_escaped": hobbits_escaped,
                "hobbits_captured": hobbits_captured,
            }

        # Check win condition if all hobbits are at Rivendell
        if all(h == state.rivendell for h in state.hobbits):
            emit_event(
                tick=state.tick,
                event_type="victory",
                hobbits=state.hobbits,
                nazgul=state.nazgul,
                rivendell=state.rivendell,
            )
            hobbits_escaped = len(state.hobbits)
            hobbits_captured = state.starting_hobbit_count - len(state.hobbits)
            return {
                "outcome": "victory",
                "ticks": state.tick,
                "hobbits_escaped": hobbits_escaped,
                "hobbits_captured": hobbits_captured,
            }

        # Check loss condition
        if len(state.hobbits) != state.starting_hobbit_count:
            emit_event(
                tick=state.tick,
                event_type="defeat",
                hobbits=state.hobbits,
                nazgul=state.nazgul,
                rivendell=state.rivendell,
            )
            hobbits_escaped = sum(1 for h in state.hobbits if h == state.rivendell)
            hobbits_captured = state.starting_hobbit_count - len(state.hobbits)
            return {
                "outcome": "defeat",
                "ticks": state.tick,
                "hobbits_escaped": hobbits_escaped,
                "hobbits_captured": hobbits_captured,
            }

        # Move entities
        state.hobbits = update_hobbits(
            hobbits=state.hobbits,
            rivendell=state.rivendell,
            nazgul=state.nazgul,
            dimensions=state.dimensions,
            tick=state.tick,
            terrain=state.terrain,
        )
        state.nazgul = update_nazgul(
            nazgul=state.nazgul,
            hobbits=state.hobbits,
            dimensions=state.dimensions,
            tick=state.tick,
            terrain=state.terrain,
        )

        # Check for captures (Nazgûl on same square as hobbit)
        hobbits_to_remove = []
        for hobbit in state.hobbits:
            for naz in state.nazgul:
                if hobbit == naz:
                    hobbits_to_remove.append(hobbit)
                    emit_event(
                        tick=state.tick,
                        event_type="hobbit_captured",
                        hobbit=hobbit,
                        nazgul=naz,
                    )
                    break

        for h in hobbits_to_remove:
            state.hobbits.remove(h)

        # Call display callback if provided
        if on_tick:
            on_tick(state=state)

        state.tick += 1


def run_simulation() -> None:
    """Run the interactive simulation with display and pacing."""

    def display_tick(
        *,
        state: WorldState,
    ) -> None:
        """Display callback for interactive simulation."""
        # Render the grid from current state
        grid = _render_simulation_state(state=state)

        print(f"=== Tick {state.tick} ===")
        print(f"Hobbits remaining: {len(state.hobbits)}")
        NarrativeBuffer.flush()
        print_grid(grid=grid)
        time.sleep(0.3)

    _run_simulation_loop(on_tick=display_tick)


if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    run_simulation()
