# hobbit_sim.py

def create_grid(width=20, height=20):
    """Create a 2D grid filled with empty spaces"""
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append('.')
        grid.append(row)
    return grid

def print_grid(grid):
    """Print the grid with all entities"""
    for row in grid:
        print(' '.join(row))

def place_entity(grid, x, y, symbol):
    """Place an entity on the grid at position (x, y)"""
    grid[y][x] = symbol

if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()

    # Create the grid
    grid = create_grid(20, 20)

    # Place starting locations
    place_entity(grid, 0, 0, 'S')        # Shire (top-left)
    place_entity(grid, 19, 19, 'R')      # Rivendell (bottom-right)

    # Place hobbits near the Shire
    place_entity(grid, 1, 0, 'H')
    place_entity(grid, 0, 1, 'H')

    # Place a couple Nazgûl
    place_entity(grid, 10, 10, 'N')
    place_entity(grid, 15, 5, 'N')

    print_grid(grid)