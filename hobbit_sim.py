# hobbit_sim.py
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, TypedDict

# Type aliases for grid and positioning
Position = tuple[int, int]  # Grid coordinates (x, y) - use for any single location
GridDimensions = tuple[int, int]  # Grid bounds (width, height)
Grid = list[list[str]]  # 2D grid of display symbols for rendering
EntityPositions = list[Position]  # Multiple entity locations (for Nazgûl groups, etc.)

# Hobbit identity types
HobbitId = int  # Unique identifier for a hobbit (0=Frodo, 1=Sam, etc.)
Hobbits = dict[HobbitId, Position]  # Maps hobbit IDs to their current positions

# Hobbit identification by list index
# Maps hobbit index to display name/symbol
HOBBIT_NAMES = {
    0: "Frodo",
    1: "Sam",
    2: "Pippin",
    3: "Merry",
}


def get_hobbit_name(*, hobbit_id: int) -> str:
    """Get display name for hobbit by ID.

    Returns the hobbit's name from HOBBIT_NAMES, or a generic fallback.

    Args:
        hobbit_id: The hobbit's unique identifier

    Returns:
        Hobbit name like "Frodo" or fallback "Hobbit 4"
    """
    return HOBBIT_NAMES.get(hobbit_id, f"Hobbit {hobbit_id}")


# Movement constants
DANGER_DISTANCE = 6  # Distance at which hobbits start evading Nazgûl
HOBBIT_SPEED = 2  # Steps per tick for hobbit movement
NAZGUL_SPEED = 1  # Steps per tick for Nazgûl movement

# World configuration
WORLD_WIDTH = 20
WORLD_HEIGHT = 20


@dataclass
class WorldState:
    """Complete simulation state including map and entities."""

    # Map configuration (immutable during simulation)
    width: int
    height: int
    map_id: int
    rivendell: Position  # Legacy field, now same as exit_position
    exit_position: Position  # Where hobbits transition/win
    entry_symbol: str  # Display symbol for map entry
    exit_symbol: str  # Display symbol for map exit
    terrain: set[Position]
    starting_hobbit_count: int
    starting_nazgul_count: int

    # Entity state (mutable during simulation)
    hobbits: Hobbits
    nazgul: EntityPositions
    tick: int = 0

    @property
    def dimensions(self) -> GridDimensions:
        """Grid dimensions as tuple."""
        return (self.width, self.height)


@dataclass
class MapConfig:
    """Configuration for a single map in the journey."""

    map_id: int
    name: str  # Display name like "Bag End", "Shire Forest"
    entry_position: Position  # Where hobbits spawn
    exit_position: Position  # Where hobbits transition to next map
    entry_symbol: str  # Render symbol for entry ('B', 'F', 'C')
    exit_symbol: str  # Render symbol for exit (typically 'X')
    hobbit_spawns: Position  # Single position where all hobbits start
    nazgul_spawns: list[Position]  # List of Nazgûl starting positions


# Map definitions for 3-stage journey
MAP_DEFINITIONS: dict[int, MapConfig] = {
    0: MapConfig(
        map_id=0,
        name="Bag End",
        entry_position=(1, 1),
        exit_position=(18, 18),
        entry_symbol="B",
        exit_symbol="X",
        hobbit_spawns=(1, 1),
        nazgul_spawns=[(18, 5)],
    ),
    1: MapConfig(
        map_id=1,
        name="Shire Forest",
        entry_position=(1, 1),
        exit_position=(18, 18),
        entry_symbol="F",
        exit_symbol="X",
        hobbit_spawns=(1, 1),
        nazgul_spawns=[(18, 5), (18, 10)],  # Two Nazgûl in forest
    ),
    2: MapConfig(
        map_id=2,
        name="Crickhollow",
        entry_position=(1, 1),
        exit_position=(18, 18),
        entry_symbol="C",
        exit_symbol="X",
        hobbit_spawns=(1, 1),
        nazgul_spawns=[(18, 5), (15, 5), (18, 10)],  # Three riders closing in
    ),
}


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


def get_hobbit_symbol(*, index: int) -> str:
    """Get display symbol for hobbit by index.

    Returns first letter of hobbit's name: F, S, P, M
    Falls back to 'H' for unknown indices.
    """
    name = HOBBIT_NAMES.get(index)
    if name:
        return name[0]  # First letter: F, S, P, M
    return "H"  # Fallback for unknown hobbits


def render_world(*, world: WorldState, show_hobbit_ids: bool = False) -> str:
    """Render world state as string (high-level test helper)

    Takes WorldState from create_world() and returns visual representation.
    Useful for testing complete scenes without manual entity placement.

    Args:
        world: Current world state to render
        show_hobbit_ids: If True, show hobbit index (0,1,2,3). If False, show 'H'
    """
    # Create fresh grid
    grid = create_grid(dimensions=world.dimensions)

    # Place terrain (if any)
    for terrain_pos in world.terrain:
        place_entity(grid=grid, position=terrain_pos, symbol="#")

    # Place landmarks
    place_entity(grid=grid, position=world.exit_position, symbol=world.exit_symbol)

    # Place hobbits with optional IDs
    for hobbit_id, hobbit_pos in world.hobbits.items():
        symbol = get_hobbit_symbol(index=hobbit_id) if show_hobbit_ids else "H"
        place_entity(grid=grid, position=hobbit_pos, symbol=symbol)

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
    *, nazgul: Position, hobbit_positions: EntityPositions
) -> tuple[Position | None, int]:
    """Find nearest Hobbit and Manhattan distance.

    Returns (hobbit_pos, distance) or (None, 999_999_999) when no hobbits exist.
    Distance is calculated as Manhattan distance: |dx| + |dy|.
    """
    if not hobbit_positions:
        return None, 999_999_999  # Nine 9's for the Nine Rings of Men

    nazgul_x, nazgul_y = nazgul
    nearest = hobbit_positions[0]
    min_dist = abs(nazgul_x - nearest[0]) + abs(nazgul_y - nearest[1])

    for hobbit in hobbit_positions[1:]:
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
    occupied_positions: set[Position] | None = None,
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
        occupied_positions: Set of positions occupied by other hobbits (for collision avoidance)

    Returns:
        New position after one step (or current if all options blocked)
    """
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
        if is_valid_position(
            position=option,
            dimensions=dimensions,
            terrain=terrain,
            occupied_positions=occupied_positions,
        ):
            return option

    # All options blocked - stay put
    return current


def is_valid_position(
    *,
    position: Position,
    dimensions: GridDimensions,
    terrain: set[Position],
    occupied_positions: set[Position] | None = None,
) -> bool:
    """Check if position is within bounds and not blocked by terrain or other hobbits."""
    x, y = position
    width, height = dimensions

    # Check bounds and terrain
    if not (0 <= x < width and 0 <= y < height and position not in terrain):
        return False

    # Check collision with other hobbits (if tracking occupied positions)
    if occupied_positions is not None and position in occupied_positions:
        return False

    return True


def _hobbit_positions(*, hobbits: Hobbits) -> list[Position]:
    """Get hobbit positions as list from dict."""
    return list(hobbits.values())


def all_hobbits_at_exit(*, hobbits: Hobbits, exit_position: Position) -> bool:
    """Check if all hobbits have reached the map exit.

    Args:
        hobbits: Dict mapping hobbit IDs to positions
        exit_position: Target position for map exit

    Returns:
        True if all hobbits are at the exit position, False otherwise
    """
    if not hobbits:
        return False
    return all(pos == exit_position for pos in hobbits.values())


def update_hobbits(
    *,
    hobbits: Hobbits,
    rivendell: Position,
    nazgul: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
) -> Hobbits:
    """Move all hobbits toward Rivendell at speed 2.

    Each hobbit:
    1. Takes 2 steps (speed 2)
    2. Reassesses world after each step (greedy evaluation)
    3. Autonomously decides behavior based on perceived threats

    Returns new hobbit positions as dict.
    """
    return _update_hobbits_dict(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=dimensions,
        tick=tick,
        terrain=terrain,
    )


def _update_hobbits_dict(
    *,
    hobbits: Hobbits,
    rivendell: Position,
    nazgul: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
) -> Hobbits:
    """Internal dict-based version of update_hobbits.

    Move all hobbits toward Rivendell at speed 2.
    Works with dict[HobbitId, Position] for explicit identity tracking.

    Each hobbit:
    1. Takes 2 steps (speed 2)
    2. Reassesses world after each step (greedy evaluation)
    3. Autonomously decides behavior based on perceived threats

    Returns new hobbit positions as dict.
    """
    if terrain is None:
        terrain = set()

    new_hobbits = {}
    occupied_positions: set[Position] = set()

    for hobbit_id, hobbit_pos in hobbits.items():
        current = hobbit_pos
        hobbit_name = get_hobbit_name(hobbit_id=hobbit_id)

        emit_event(
            tick=tick,
            event_type="hobbit_turn_start",
            hobbit=current,
            name=hobbit_name,
        )

        # Take HOBBIT_SPEED steps, reassessing after each
        for step in range(HOBBIT_SPEED):
            next_pos = move_hobbit_one_step(
                current=current,
                goal=rivendell,
                threats=nazgul,
                terrain=terrain,
                dimensions=dimensions,
                occupied_positions=occupied_positions,
            )
            if next_pos != current:
                emit_event(
                    tick=tick,
                    event_type="hobbit_moved",
                    name=hobbit_name,
                    from_pos=current,
                    to_pos=next_pos,
                    step=step + 1,
                )
            current = next_pos

        new_hobbits[hobbit_id] = current
        # Track this hobbit's position as occupied (unless at goal/Rivendell)
        if current != rivendell:
            occupied_positions.add(current)

    return new_hobbits


def update_nazgul(
    *,
    nazgul: EntityPositions,
    hobbit_positions: EntityPositions,
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
            hobbits=hobbit_positions,
        )
        target, distance = find_nearest_hobbit(nazgul=nazgul_pos, hobbit_positions=hobbit_positions)
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
                speed=NAZGUL_SPEED,
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


def create_map(*, map_id: int) -> WorldState:
    """Initialize world state for a specific map in the journey.

    Args:
        map_id: Map identifier (0=Bag End, 1=Shire Forest, 2=Crickhollow)

    Returns:
        WorldState configured for the specified map with spawned entities.
    """
    # Load map configuration
    if map_id not in MAP_DEFINITIONS:
        raise ValueError(f"Invalid map_id: {map_id}. Valid IDs: {list(MAP_DEFINITIONS.keys())}")

    config = MAP_DEFINITIONS[map_id]

    # Terrain - create border walls (leave openings at entry and exit)
    terrain = set()

    # Add borders (all edges)
    for x in range(WORLD_WIDTH):
        terrain.add((x, 0))  # Top border
        terrain.add((x, WORLD_HEIGHT - 1))  # Bottom border
    for y in range(WORLD_HEIGHT):
        terrain.add((0, y))  # Left border
        terrain.add((WORLD_WIDTH - 1, y))  # Right border

    # Spawn hobbits at configured position (all together)
    hobbits = {
        0: config.hobbit_spawns,  # Frodo
        1: config.hobbit_spawns,  # Sam
        2: config.hobbit_spawns,  # Pippin
    }

    # Spawn Nazgûl from config
    nazgul = list(config.nazgul_spawns)

    starting_hobbit_count = len(hobbits)
    starting_nazgul_count = len(nazgul)

    return WorldState(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        map_id=config.map_id,
        rivendell=config.exit_position,  # Legacy field
        exit_position=config.exit_position,
        entry_symbol=config.entry_symbol,
        exit_symbol=config.exit_symbol,
        terrain=terrain,
        hobbits=hobbits,
        nazgul=nazgul,
        starting_hobbit_count=starting_hobbit_count,
        starting_nazgul_count=starting_nazgul_count,
        tick=0,
    )


def create_world() -> WorldState:
    """Initialize world state (terrain, entities, landmarks)

    Backward compatibility wrapper - creates Map 0 (Bag End).

    Returns WorldState with complete simulation configuration and initial entity positions.
    """
    return create_map(map_id=0)


def transition_to_next_map(*, current_state: WorldState) -> WorldState | None:
    """Transition to the next map in the journey, preserving hobbit identities.

    Args:
        current_state: Current world state with hobbits at exit

    Returns:
        New WorldState for next map with hobbits respawned at entry, or None if journey complete
    """
    next_map_id = current_state.map_id + 1

    # Check if there's a next map
    if next_map_id not in MAP_DEFINITIONS:
        return None  # Journey complete! Victory!

    # Create new map
    new_state = create_map(map_id=next_map_id)

    # Preserve hobbit IDs, place all at new map's entry position
    new_state.hobbits = dict.fromkeys(
        current_state.hobbits.keys(),
        new_state.hobbits[0],  # All hobbits spawn at same position
    )

    return new_state


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

    # Place landmarks (exit point for current map)
    place_entity(grid=grid, position=state.exit_position, symbol=state.exit_symbol)

    # Place hobbits with identity
    for hobbit_id, hobbit_pos in state.hobbits.items():
        symbol = get_hobbit_symbol(index=hobbit_id)
        place_entity(grid=grid, position=hobbit_pos, symbol=symbol)

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
            hobbit_positions = _hobbit_positions(hobbits=state.hobbits)
            hobbits_escaped = sum(1 for h in hobbit_positions if h == state.rivendell)
            hobbits_captured = state.starting_hobbit_count - len(state.hobbits)
            return {
                "outcome": "timeout",
                "ticks": state.tick,
                "hobbits_escaped": hobbits_escaped,
                "hobbits_captured": hobbits_captured,
            }

        # Check if all hobbits reached exit (map transition or final victory)
        if all_hobbits_at_exit(hobbits=state.hobbits, exit_position=state.exit_position):
            # Try to transition to next map
            next_state = transition_to_next_map(current_state=state)

            if next_state is None:
                # No more maps - final victory!
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
            else:
                # Transition to next map
                emit_event(
                    tick=state.tick,
                    event_type="map_transition",
                    hobbits=state.hobbits,
                    nazgul=state.nazgul,
                    rivendell=state.rivendell,
                    from_map_id=state.map_id,
                    to_map_id=next_state.map_id,
                )
                state = next_state
                continue  # Continue simulation on new map

        # Check loss condition
        if len(state.hobbits) != state.starting_hobbit_count:
            emit_event(
                tick=state.tick,
                event_type="defeat",
                hobbits=state.hobbits,
                nazgul=state.nazgul,
                rivendell=state.rivendell,
            )
            hobbit_positions = _hobbit_positions(hobbits=state.hobbits)
            hobbits_escaped = sum(1 for h in hobbit_positions if h == state.rivendell)
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
            hobbit_positions=_hobbit_positions(hobbits=state.hobbits),
            dimensions=state.dimensions,
            tick=state.tick,
            terrain=state.terrain,
        )

        # Check for captures (Nazgûl on same square as hobbit)
        hobbit_ids_to_remove = []
        for hobbit_id, hobbit_pos in state.hobbits.items():
            for naz in state.nazgul:
                if hobbit_pos == naz:
                    hobbit_ids_to_remove.append(hobbit_id)
                    emit_event(
                        tick=state.tick,
                        event_type="hobbit_captured",
                        hobbit=hobbit_pos,
                        nazgul=naz,
                    )
                    break
        for hid in hobbit_ids_to_remove:
            del state.hobbits[hid]

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

        # Get map name from definitions
        map_name = MAP_DEFINITIONS[state.map_id].name

        print(f"=== Tick {state.tick} | {map_name} ===")
        print(f"Hobbits remaining: {len(state.hobbits)}")
        NarrativeBuffer.flush()
        print_grid(grid=grid)
        time.sleep(0.3)

    _run_simulation_loop(on_tick=display_tick)


if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    run_simulation()
