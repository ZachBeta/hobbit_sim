# hobbit_sim.py
import json
import os
import sys
import time

Position = tuple[int, int]
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
        return f"logs/simulation_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"


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
    for x, y in world.get("terrain", []):
        place_entity(grid, x, y, "#")

    # Place landmarks
    place_entity(grid, 0, 0, "S")  # Shire
    rivendell = world["rivendell"]
    place_entity(grid, rivendell[0], rivendell[1], "R")

    # Place hobbits
    for hx, hy in world["hobbits"]:
        place_entity(grid, hx, hy, "H")

    # Place nazgul
    for nx, ny in world["nazgul"]:
        place_entity(grid, nx, ny, "N")

    return render_grid(grid)


def render_grid(grid: Grid) -> str:
    """Return grid as string (for testing and printing)

    Format: "H . .\nN . .\n. . ."
    """
    lines = []
    for row in grid:
        lines.append(" ".join(row))
    return "\n".join(lines)


def place_entity(grid: Grid, x: int, y: int, symbol: str) -> None:
    """Place an entity on the grid at position (x, y)"""
    if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
        grid[y][x] = symbol


def move_toward(current_x: int, current_y: int, target_x: int, target_y: int) -> Position:
    """Move one step toward target. Returns new (x, y)"""
    new_x = current_x
    new_y = current_y

    # Move on X axis first
    if current_x < target_x:
        new_x += 1
    elif current_x > target_x:
        new_x -= 1

    if current_y < target_y:
        new_y += 1
    elif current_y > target_y:
        new_y -= 1

    return new_x, new_y


def find_nearest_hobbit(nazgul_x: int, nazgul_y: int, hobbits: EntityPositions) -> Position | None:
    """Find the nearest hobbit to this Nazgûl"""
    if not hobbits:
        return None

    nearest = hobbits[0]
    min_dist = abs(nazgul_x - nearest[0]) + abs(nazgul_y - nearest[1])

    for hobbit in hobbits[1:]:
        dist = abs(nazgul_x - hobbit[0]) + abs(nazgul_y - hobbit[1])
        if dist < min_dist:
            min_dist = dist
            nearest = hobbit

    return nearest


def move_with_speed(
    x: int,
    y: int,
    target_x: int,
    target_y: int,
    speed: int,
    width: int,
    height: int,
    terrain: set[Position] | None = None,
) -> Position:
    """Move toward target for 'speed' steps, stopping at boundaries or terrain."""
    current_x, current_y = x, y
    if terrain is None:
        terrain = set()

    for _step in range(speed):
        new_x, new_y = move_toward(current_x, current_y, target_x, target_y)

        # Check boundaries and terrain
        if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
            current_x, current_y = new_x, new_y
        else:
            # Hit boundary or terrain, stop moving
            break

    return current_x, current_y


def find_nearest_nazgul(
    hobbit_x: int, hobbit_y: int, nazgul: EntityPositions
) -> tuple[Position | None, float]:
    """Find nearest Nazgûl and distance. Returns (nazgul_pos, distance) or (None, infinity)"""
    if not nazgul:
        return None, float("inf")

    nearest = nazgul[0]
    min_dist = abs(hobbit_x - nearest[0]) + abs(hobbit_y - nearest[1])

    for naz in nazgul[1:]:
        dist = abs(hobbit_x - naz[0]) + abs(hobbit_y - naz[1])
        if dist < min_dist:
            min_dist = dist
            nearest = naz

    return nearest, min_dist


def move_away_from(current_x: int, current_y: int, threat_x: int, threat_y: int) -> Position:
    """Move one step AWAY from threat. Returns new (x, y)"""
    new_x = current_x
    new_y = current_y

    # Move opposite direction on X axis first
    if current_x < threat_x:
        new_x -= 1
    elif current_x > threat_x:
        new_x += 1

    if current_y < threat_y:
        new_y -= 1
    elif current_y > threat_y:
        new_y += 1

    return new_x, new_y


def update_hobbits(
    hobbits: EntityPositions,
    rivendell: Position,
    nazgul: EntityPositions,
    width: int,
    height: int,
    tick: int,
    terrain: set[Position] | None = None,
) -> EntityPositions:
    """Move all hobbits toward Rivendell at speed 2. Returns new hobbit positions."""
    new_hobbits = []
    DANGER_DISTANCE = 6
    if terrain is None:
        terrain = set()

    for hx, hy in hobbits:
        nearest_naz, distance = find_nearest_nazgul(hx, hy, nazgul)

        if distance <= DANGER_DISTANCE and nearest_naz is not None:
            # PANIC! Run away from Nazgûl
            current_x, current_y = hx, hy
            for _step in range(2):  # speed 2
                log_event(tick, "evasion_attempt", {"hobbit": (hx, hy), "nazgul": nearest_naz})
                new_x, new_y = move_away_from(current_x, current_y, nearest_naz[0], nearest_naz[1])

                # Check if evasion move is valid (boundaries and terrain)
                if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
                    current_x, current_y = new_x, new_y
                    log_event(
                        tick,
                        "evasion_success",
                        {
                            "hobbit": (hx, hy),
                            "nazgul": nearest_naz,
                            "new_position": (current_x, current_y),
                        },
                    )
                else:
                    log_event(
                        tick,
                        "evasion_failure",
                        {
                            "hobbit": (hx, hy),
                            "nazgul": nearest_naz,
                            "new_position": (current_x, current_y),
                        },
                    )
                    # Can't evade in that direction - try moving toward goal instead
                    new_x, new_y = move_toward(current_x, current_y, rivendell[0], rivendell[1])
                    if 0 <= new_x < width and 0 <= new_y < height and (new_x, new_y) not in terrain:
                        current_x, current_y = new_x, new_y

            new_hobbits.append((current_x, current_y))
        else:
            # Safe - move toward Rivendell
            log_event(tick, "hobbit_movement_attempt", {"hobbit": (hx, hy), "rivendell": rivendell})
            new_x, new_y = move_with_speed(
                hx,
                hy,
                rivendell[0],
                rivendell[1],
                speed=2,
                width=width,
                height=height,
                terrain=terrain,
            )
            new_hobbits.append((new_x, new_y))

    return new_hobbits


def update_nazgul(
    nazgul: EntityPositions,
    hobbits: EntityPositions,
    width: int,
    height: int,
    tick: int,
    terrain: set[Position] | None = None,
) -> EntityPositions:
    """Move all Nazgûl toward nearest hobbit at speed 1. Returns new Nazgûl positions."""
    new_nazgul = []
    if terrain is None:
        terrain = set()

    for nx, ny in nazgul:
        log_event(tick, "nazgul_movement_attempt", {"nazgul": (nx, ny), "hobbits": hobbits})
        target = find_nearest_hobbit(nx, ny, hobbits)
        if target:
            log_event(tick, "nazgul_movement", {"nazgul": (nx, ny), "hobbit": target})
            new_x, new_y = move_with_speed(
                nx, ny, target[0], target[1], speed=1, width=width, height=height, terrain=terrain
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
    rivendell = (19, 19)

    # Terrain - create border walls (but leave openings at Shire and Rivendell)
    terrain = set()

    # Add borders (all edges)
    for x in range(WIDTH):
        terrain.add((x, 0))  # Top border
        terrain.add((x, HEIGHT - 1))  # Bottom border
    for y in range(HEIGHT):
        terrain.add((0, y))  # Left border
        terrain.add((WIDTH - 1, y))  # Right border

    # Remove borders at Shire (0,0) and Rivendell (19,19) to allow entry
    terrain.discard((0, 0))
    terrain.discard((19, 19))

    # Initialize hobbits
    hobbits = [
        (1, 0),  # Pippin
        (0, 1),  # Sam
        (1, 1),  # Frodo
    ]

    # Initialize Nazgûl
    nazgul = [
        (18, 12),  # Far from hobbits
    ]

    return {
        "width": WIDTH,
        "height": HEIGHT,
        "rivendell": rivendell,
        "terrain": terrain,
        "hobbits": hobbits,
        "nazgul": nazgul,
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

    tick = 0
    while True:
        # Create fresh grid
        grid = create_grid(WIDTH, HEIGHT)

        # Place terrain
        for tx, ty in terrain:
            place_entity(grid, tx, ty, "#")

        # Place landmarks
        place_entity(grid, 0, 0, "S")  # Shire
        place_entity(grid, rivendell[0], rivendell[1], "R")  # Rivendell

        # Place hobbits
        for hx, hy in hobbits:
            place_entity(grid, hx, hy, "H")

        # Place Nazgûl
        for nx, ny in nazgul:
            place_entity(grid, nx, ny, "N")

        # Print state
        print(f"=== Tick {tick} ===")
        print(f"Hobbits remaining: {len(hobbits)}")
        print_grid(grid)

        # Check win condition if all hobbits are at Rivendell
        if all(h == rivendell for h in hobbits):
            log_event(
                tick, "victory", {"hobbits": hobbits, "nazgul": nazgul, "rivendell": rivendell}
            )
            print("🎉 Victory! All hobbits reached Rivendell!")
            break
        # Check lose condition if all hobbits are caught
        if not hobbits:
            log_event(
                tick, "defeat", {"hobbits": hobbits, "nazgul": nazgul, "rivendell": rivendell}
            )
            print("💀 Defeat! All hobbits were caught!")
            break

        # Move entities
        hobbits = update_hobbits(
            hobbits, rivendell, nazgul, WIDTH, HEIGHT, tick=tick, terrain=terrain
        )
        nazgul = update_nazgul(nazgul, hobbits, WIDTH, HEIGHT, tick=tick, terrain=terrain)

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
        tick += 1
        time.sleep(0.3)  # Slow down for readability


if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    run_simulation()
