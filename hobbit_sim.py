# hobbit_sim.py

def print_grid(width=20, height=20):
    """Print a simple ASCII grid"""
    for y in range(height):
        row = ""
        for x in range(width):
            row += ". "
        print(row)

if __name__ == "__main__":
    print("Hobbit Nazgûl Escape Simulation - v0")
    print()
    print_grid()