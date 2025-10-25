# hobbit_sim.py
import json
import os
import sys
import time

Position = tuple[int, int]
GridDimensions = tuple[int, int]
Grid = list[list[str]]
EntityPositions = list[Position]


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


def log_event(tick: int, event_type: str, event_data: dict) -> None:
    """Log an event to the log file"""
    with open(LOG_FILENAME, "a") as f:
        json.dump({"tick": tick, "event_type": event_type, "event_data": event_data}, f)
        f.write("\n")


def create_grid(width: int = 20, height: int = 20) -> Grid:
    """Create a 2D grid filled with empty spaces"""
    grid = []
    for _y in range(height):
        row = []
        for _x in range(width):
            row.append(".")
        grid.append(row)
    return grid


def print_grid(grid: Grid) -> None:
    """Print the grid with all entities"""
    print(render_grid(grid))
    print()


def render_world(world: dict) -> str:
    """Render world state as string (high-level test helper)

    Takes world dict from create_world() and returns visual representation.
    Useful for testing complete scenes without manual entity placement.
    """
    WIDTH = world["width"]
    HEIGHT = world["height"]

    # Create fresh grid
    grid = create_grid(WIDTH, HEIGHT)

    # Place terrain (if any)
    for terrain_pos in world.get("terrain", []):
        place_entity(grid, terrain_pos, "#")

    # Place landmarks
    place_entity(grid, (0, 0), "S")  # Shire
    rivendell = world["rivendell"]
    place_entity(grid, rivendell, "R")

    # Place hobbits
    for hobbit_pos in world["hobbits"]:
        place_entity(grid, hobbit_pos, "H")

    # Place nazgul
    for nazgul_pos in world["nazgul"]:
        place_entity(grid, nazgul_pos, "N")

    return render_grid(grid)


def render_grid(grid: Grid) -> str:
    """Return grid as string (for testing and printing)

    Format: "H . .\nN . .\n. . ."
    """
    lines = []
    for row in grid:
        lines.append(" ".join(row))
    return "\n".join(lines)


def place_entity(grid: Grid, position: Position, symbol: str) -> None:
    """Place an entity on the grid at position"""
    x, y = position
    if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
        grid[y][x] = symbol


def move_toward(current: Position, target: Position) -> Position:
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
    nazgul: Position, hobbits: EntityPositions
) -> tuple[Position | None, float]:
    """Find nearest Hobbit and distance.

    Returns (hobbit_pos, distance) or (None, infinity)
    """
    if not hobbits:
        return None, float("inf")

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
        new_x, new_y = move_toward((current_x, current_y), target)

        # Check boundaries and terrain
        if (
            0 <= new_x < width
            and 0 <= new_y < height
            and (new_x, new_y) not in terrain
        ):
            current_x, current_y = new_x, new_y
            log_event(
                tick,
                "movement",
                {"entity": current, "new_position": (current_x, current_y)},
            )
        else:
            log_event(
                tick,
                "movement_blocked",
                {"entity": current, "new_position": (current_x, current_y)},
            )
            # Hit boundary or terrain, stop moving
            break

    return current_x, current_y


def find_nearest_nazgul(hobbit: Position, nazgul: EntityPositions) -> tuple[Position | None, float]:
    """Find nearest Nazgûl and distance.

    Returns (nazgul_pos, distance) or (None, infinity)
    """
    if not nazgul:
        return None, float("inf")

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


def update_hobbits(
    hobbits: EntityPositions,
    rivendell: Position,
    nazgul: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
    debug_output: list[str] | None = None,
) -> EntityPositions:
    """Move all hobbits toward Rivendell at speed 2. Returns new hobbit positions."""
    new_hobbits = []
    DANGER_DISTANCE = 6
    width, height = dimensions
    if terrain is None:
        terrain = set()

    def debug(msg: str) -> None:
        if debug_output is not None:
            debug_output.append(msg)
        else:
            print(msg)

    for hobbit_index, hobbit_pos in enumerate(hobbits):
        nearest_naz, distance = find_nearest_nazgul(hobbit_pos, nazgul)

        if distance <= DANGER_DISTANCE and nearest_naz is not None:
            # PANIC! Run away from Nazgûl
            current_x, current_y = hobbit_pos
            for step in range(2):  # speed 2
                debug(f"  Hobbit[{hobbit_index}] step {step + 1}/2: at ({current_x},{current_y})")
                log_event(
                    tick,
                    "evasion_attempt",
                    {"hobbit": hobbit_pos, "nazgul": nearest_naz, "goal": rivendell},
                )
                new_x, new_y = move_away_from(
                    (current_x, current_y),
                    nearest_naz,
                    goal=rivendell,
                )
                debug(
                    f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                    f"evading from Nazgûl at {nearest_naz}, trying ({new_x},{new_y})"
                )

                # Check if evasion move is valid (boundaries and terrain)
                if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
                    debug(
                        f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                        f"evasion move successful from "
                        f"({current_x},{current_y}) to ({new_x},{new_y})"
                    )
                    current_x, current_y = new_x, new_y
                    log_event(
                        tick,
                        "evasion_success",
                        {
                            "hobbit": hobbit_pos,
                            "nazgul": nearest_naz,
                            "new_position": (current_x, current_y),
                        },
                    )
                else:
                    debug(
                        f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                        f"evasion move failed from "
                        f"({current_x},{current_y}) to ({new_x},{new_y})"
                    )
                    log_event(
                        tick,
                        "evasion_failure",
                        {
                            "hobbit": hobbit_pos,
                            "nazgul": nearest_naz,
                            "new_position": (current_x, current_y),
                        },
                    )
                    # Can't evade in that direction - try moving toward goal
                    new_x, new_y = move_toward((current_x, current_y), rivendell)
                    debug(
                        f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                        f"moving toward goal from ({current_x},{current_y}) "
                        f"to ({new_x},{new_y})"
                    )
                    if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
                        current_x, current_y = new_x, new_y
                        debug(
                            f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                            f"moving toward goal successful from "
                            f"({current_x},{current_y}) to ({new_x},{new_y})"
                        )
                    else:
                        debug(
                            f"  Hobbit[{hobbit_index}] step {step + 1}/2: "
                            f"moving toward goal failed from "
                            f"({current_x},{current_y}) to ({new_x},{new_y})"
                        )

            new_hobbits.append((current_x, current_y))
        else:
            debug(
                f"  Hobbit[{hobbit_index}] safe - move toward Rivendell "
                f"from {hobbit_pos} to {rivendell}"
            )
            # Safe - move toward Rivendell
            log_event(
                tick,
                "hobbit_movement_attempt",
                {"hobbit": hobbit_pos, "rivendell": rivendell},
            )
            # TODO: pull steps above out a layer so they don't accidentally
            # move into the danger zone
            new_x, new_y = move_with_speed(
                hobbit_pos,
                rivendell,
                speed=2,
                dimensions=dimensions,
                tick=tick,
                terrain=terrain,
            )
            new_hobbits.append((new_x, new_y))

    return new_hobbits


def update_nazgul(
    nazgul: EntityPositions,
    hobbits: EntityPositions,
    dimensions: GridDimensions,
    tick: int,
    terrain: set[Position] | None = None,
    debug_output: list[str] | None = None,
) -> EntityPositions:
    """Move all Nazgûl toward nearest hobbit at speed 1. Returns new Nazgûl positions."""
    new_nazgul = []
    width, height = dimensions
    if terrain is None:
        terrain = set()

    def debug(msg: str) -> None:
        if debug_output is not None:
            debug_output.append(msg)
        else:
            print(msg)

    for nazgul_index, nazgul_pos in enumerate(nazgul):
        log_event(tick, "nazgul_movement_attempt", {"nazgul": nazgul_pos, "hobbits": hobbits})
        target, distance = find_nearest_hobbit(nazgul_pos, hobbits)
        if target:
            debug(f"  Nazgûl[{nazgul_index}] chasing Hobbit at {target}")
            log_event(tick, "nazgul_movement", {"nazgul": nazgul_pos, "hobbit": target})
            new_x, new_y = move_with_speed(
                nazgul_pos,
                target,
                speed=1,
                dimensions=dimensions,
                tick=tick,
                terrain=terrain,
            )
            new_nazgul.append((new_x, new_y))
    return new_nazgul


def create_world() -> dict:
    """Initialize world state (terrain, entities, landmarks)

    Returns dict with:
    - width, height: grid dimensions
    - rivendell: goal position
    - terrain: set of impassable coordinates
    - hobbits: list of hobbit positions
    - nazgul: list of nazgul positions
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

    return {
        "width": WIDTH,
        "height": HEIGHT,
        "rivendell": rivendell,
        "terrain": terrain,
        "hobbits": hobbits,
        "nazgul": nazgul,
        "starting_hobbit_count": starting_hobbit_count,
        "starting_nazgul_count": starting_nazgul_count,
    }


def run_simulation() -> None:
    """Run the main simulation"""

    # Goal location
    world = create_world()
    WIDTH = world["width"]
    HEIGHT = world["height"]
    rivendell = world["rivendell"]
    terrain = world["terrain"]
    hobbits = world["hobbits"]
    nazgul = world["nazgul"]

    dimensions = (WIDTH, HEIGHT)
    tick = 0
    while True:
        debug_buffer: list[str] = []

        # Check win condition if all hobbits are at Rivendell
        if all(h == rivendell for h in hobbits):
            log_event(
                tick, "victory", {"hobbits": hobbits, "nazgul": nazgul, "rivendell": rivendell}
            )
            print("🎉 Victory! All hobbits reached Rivendell!")
            break
        if len(hobbits) != world["starting_hobbit_count"]:
            log_event(
                tick, "defeat", {"hobbits": hobbits, "nazgul": nazgul, "rivendell": rivendell}
            )
            print("💀 Defeat! Some hobbits were caught!")
            break

        # Move entities
        hobbits = update_hobbits(
            hobbits,
            rivendell,
            nazgul,
            dimensions,
            tick=tick,
            terrain=terrain,
            debug_output=debug_buffer,
        )
        nazgul = update_nazgul(
            nazgul,
            hobbits,
            dimensions,
            tick=tick,
            terrain=terrain,
            debug_output=debug_buffer,
        )

        # Check for captures (Nazgûl on same square as hobbit)
        hobbits_to_remove = []
        for hobbit in hobbits:
            for naz in nazgul:
                if hobbit == naz:
                    hobbits_to_remove.append(hobbit)
                    log_event(tick, "hobbit_captured", {"hobbit": hobbit, "nazgul": naz})
                    print(f"💀 Hobbit caught at {hobbit}!")
                    break

        for h in hobbits_to_remove:
            hobbits.remove(h)
        log_event(tick, "hobbits_removed", {"hobbits": hobbits_to_remove})

        # Create fresh grid with NEW positions
        grid = create_grid(WIDTH, HEIGHT)

        # Place terrain
        for terrain_pos in terrain:
            place_entity(grid, terrain_pos, "#")

        # Place landmarks
        place_entity(grid, (1, 1), "S")  # Shire
        place_entity(grid, rivendell, "R")  # Rivendell

        # Place hobbits
        for hobbit_pos in hobbits:
            place_entity(grid, hobbit_pos, "H")

        # Place Nazgûl
        for nazgul_pos in nazgul:
            place_entity(grid, nazgul_pos, "N")

        # Print state
        print(f"=== Tick {tick} ===")
        print(f"Hobbits remaining: {len(hobbits)}")

        # Print debug output
        if debug_buffer:
            for line in debug_buffer:
                print(line)

        print_grid(grid)
        tick += 1
        time.sleep(0.3)  # Slow down for readability


if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    run_simulation()
