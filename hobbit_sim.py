# hobbit_sim.py
import time

Position = tuple[int, int]
Grid = list[list[str]]
EntityPositions = list[Position]

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
    for row in grid:
        print(" ".join(row))
    print()


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


def move_with_speed(x: int, y: int, target_x: int, target_y: int, speed: int, width: int, height: int) -> Position:
    """Move toward target for 'speed' steps, stopping at boundaries."""
    current_x, current_y = x, y

    for _step in range(speed):
        new_x, new_y = move_toward(current_x, current_y, target_x, target_y)

        # Check boundaries
        if 0 <= new_x < width and 0 <= new_y < height:
            current_x, current_y = new_x, new_y
        else:
            # Hit boundary, stop moving
            break

    return current_x, current_y


def find_nearest_nazgul(hobbit_x: int, hobbit_y: int, nazgul: EntityPositions) -> tuple[Position | None, float]:
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


def update_hobbits(hobbits: EntityPositions, rivendell: Position, nazgul: EntityPositions, width: int, height: int) -> EntityPositions:
    """Move all hobbits toward Rivendell at speed 2. Returns new hobbit positions."""
    new_hobbits = []
    DANGER_DISTANCE = 6

    for hx, hy in hobbits:
        nearest_naz, distance = find_nearest_nazgul(hx, hy, nazgul)

        if distance <= DANGER_DISTANCE:
            # PANIC! Run away from Nazgûl
            current_x, current_y = hx, hy
            for _step in range(2):  # speed 2
                new_x, new_y = move_away_from(current_x, current_y, nearest_naz[0], nearest_naz[1])

                # Check if evasion move is valid
                if 0 <= new_x < width and 0 <= new_y < height:
                    current_x, current_y = new_x, new_y
                else:
                    # Can't evade in that direction - try moving toward goal instead
                    new_x, new_y = move_toward(current_x, current_y, rivendell[0], rivendell[1])
                    if 0 <= new_x < width and 0 <= new_y < height:
                        current_x, current_y = new_x, new_y

            new_hobbits.append((current_x, current_y))
        else:
            # Safe - move toward Rivendell
            new_x, new_y = move_with_speed(
                hx, hy, rivendell[0], rivendell[1], speed=2, width=width, height=height
            )
            new_hobbits.append((new_x, new_y))

    return new_hobbits


def update_nazgul(nazgul: EntityPositions, hobbits: EntityPositions, width: int, height: int) -> EntityPositions:
    """Move all Nazgûl toward nearest hobbit at speed 1. Returns new Nazgûl positions."""
    new_nazgul = []
    for nx, ny in nazgul:
        target = find_nearest_hobbit(nx, ny, hobbits)
        if target:
            new_x, new_y = move_with_speed(
                nx, ny, target[0], target[1], speed=1, width=width, height=height
            )
            new_nazgul.append((new_x, new_y))
    return new_nazgul


def run_simulation() -> None:
    """Run the main simulation"""
    WIDTH = 20
    HEIGHT = 20

    # Goal location
    rivendell = (19, 19)

    # Initialize hobbits (x, y)
    hobbits = [
        (1, 0),  # Pippin
        (0, 1),  # Sam
        (1, 1),  # Frodo
        # (2, 1) # Merry
    ]

    # Initialize Nazgûl
    nazgul = [
        # (10, 10), # manhattan distance 20
        # (15, 5), # manhattan distance 20
        # (8, 15), # manhattan distance 23
        # (12, 3), # manhattan distance 15
        # (5, 8), # manhattan distance 13
        (18, 12),  # manhattan distance 30
        # (7, 7), # manhattan distance 14
        # (14, 14), # manhattan distance 28
        # (11, 18) # manhattan distance 29
    ]

    tick = 0

    while True:
        # Create fresh grid
        grid = create_grid(WIDTH, HEIGHT)

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
            print("🎉 Victory! All hobbits reached Rivendell!")
            break
        # Check lose condition if all hobbits are caught
        if not hobbits:
            print("💀 Defeat! All hobbits were caught!")
            break

        # Move entities
        hobbits = update_hobbits(hobbits, rivendell, nazgul, WIDTH, HEIGHT)
        nazgul = update_nazgul(nazgul, hobbits, WIDTH, HEIGHT)

        # Check for captures (Nazgûl on same square as hobbit)
        hobbits_to_remove = []
        for hobbit in hobbits:
            for naz in nazgul:
                if hobbit == naz:
                    hobbits_to_remove.append(hobbit)
                    print(f"💀 Hobbit caught at {hobbit}!")
                    break

        for h in hobbits_to_remove:
            hobbits.remove(h)

        tick += 1
        time.sleep(0.3)  # Slow down for readability


if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    run_simulation()
