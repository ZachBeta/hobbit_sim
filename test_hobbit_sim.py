# test_hobbit_sim.py
import pytest

from hobbit_sim import (
    find_nearest_hobbit,
    find_nearest_nazgul,
    move_away_from,
    move_toward,
    move_with_speed,
    update_hobbits,
    update_nazgul,
)


def test_hobbit_evading_at_south_edge_doesnt_get_stuck() -> None:
    """
    Scenario: Hobbit at bottom edge (y=18), Nazgûl approaching from north
    Bug: Hobbit tries to move south (away), hits boundary, doesn't move at all
    Expected: Hobbit should move laterally (east or west) along edge to evade
    """
    # Setup: Hobbit at south edge, Nazgûl to the north
    hobbits = [(10, 19)]  # At south edge
    nazgul = [(10, 15)]  # 4 squares north (within danger distance 6)
    rivendell = (19, 19)  # Goal is east along same edge

    # Move hobbits (should evade)
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Assert: Hobbit should have moved (not stuck at same position)
    assert new_hobbits[0] != (10, 19), "Hobbit should move when evading at edge"

    # Assert: Hobbit moved laterally toward goal (east), not stuck going south
    assert new_hobbits[0][0] > 10, "Hobbit should move east toward goal"
    assert new_hobbits[0][1] == 19, "Hobbit should stay on south edge"


def test_hobbit_evading_at_south_edge_with_terrain_doesnt_get_stuck() -> None:
    """
    Scenario: Hobbit at bottom edge (y=18), Nazgûl approaching from north
    Bug: Hobbit tries to move south (away), hits boundary, doesn't move at all
    Expected: Hobbit should move laterally (east or west) along edge to evade
    """
    # Setup: Hobbit at south edge, Nazgûl to the north
    hobbits = [(10, 18)]  # At south edge
    nazgul = [(10, 15)]  # 4 squares north (within danger distance 6)
    rivendell = (19, 19)  # Goal is east along same edge

    terrain = set()
    for x in range(20):
        terrain.add((x, 19))  # Bottom border

    # Move hobbits (should evade)
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
        terrain=terrain,
    )

    assert new_hobbits[0] == (12, 18), "Hobbit should move east toward goal"


def test_move_away_from_uses_manhattan_movement() -> None:
    """move_away_from should mirror move_toward logic (Manhattan)"""
    # Equal distances: should flee on Y axis (tiebreaker)
    assert move_away_from(current=(10, 10), threat=(11, 11)) == (9, 10)

    # Threat to the east (larger dx): flee west
    assert move_away_from(current=(10, 10), threat=(15, 11)) == (9, 10)

    # Threat to the south (larger dy): flee north
    assert move_away_from(current=(10, 10), threat=(11, 15)) == (10, 9)


def test_find_nearest_nazgul_returns_closest() -> None:
    assert find_nearest_nazgul(hobbit=(10, 10), nazgul=[(11, 11), (9, 10)]) == ((9, 10), 1)


def test_move_with_speed_uses_manhattan_movement() -> None:
    """move_with_speed should use Manhattan movement (one axis at a time)"""
    # Equal distances: should move on Y axis (tiebreaker)
    assert move_with_speed(
        current=(10, 10), target=(11, 11), speed=1, dimensions=(20, 20), tick=0
    ) == (10, 11)

    # With speed=2, should move Y then X (alternating)
    result = move_with_speed(
        current=(10, 10), target=(12, 12), speed=2, dimensions=(20, 20), tick=0
    )
    assert result in [(11, 11), (10, 12)], f"Should move 2 steps Manhattan-style, got {result}"


def test_move_with_speed_uses_manhattan_movement_with_speed() -> None:
    assert move_with_speed(
        current=(10, 10), target=(11, 11), speed=1, dimensions=(20, 20), tick=0
    ) == (10, 11)
    assert move_with_speed(
        current=(10, 10), target=(11, 11), speed=2, dimensions=(20, 20), tick=0
    ) == (11, 11)


def test_find_nearest_hobbit_returns_closest() -> None:
    assert find_nearest_hobbit(nazgul=(10, 10), hobbits=[(11, 11), (9, 10)]) == ((9, 10), 1)


def test_find_nearest_hobbit_with_no_hobbits() -> None:
    assert find_nearest_hobbit(nazgul=(10, 10), hobbits=[]) == (None, float("inf"))


@pytest.mark.skip(
    reason="Distance calculations return float (Euclidean-style) but movement uses "
    "Manhattan distance. Consider making distance calculations consistent with movement system."
)
def test_distance_calculations_use_manhattan_distance() -> None:
    """
    Distance calculations should match movement system (Manhattan distance).
    Currently find_nearest_* returns float suggesting Euclidean distance.

    Example: point (0,0) to (3,4)
    - Manhattan: |3| + |4| = 7
    - Euclidean: sqrt(3² + 4²) = 5.0

    Movement uses Manhattan, but distance return type (float) suggests Euclidean.
    """
    # Test that distances are calculated as Manhattan (|dx| + |dy|)
    # not Euclidean (sqrt(dx² + dy²))
    pass


def test_hobbits_can_stack_on_same_square_if_exiting_to_goal() -> None:
    """Two hobbits trying to move to same square - second one should be blocked"""
    hobbits = [(0, 0), (1, 0)]  # Side by side
    nazgul = [(10, 10)]  # Far away
    rivendell = (2, 0)  # East

    # Both want to move to (2, 0)
    # First hobbit gets there, second should be blocked
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Should have 1 position (stacking)
    assert len(set(new_hobbits)) == 1, "Hobbits should stack"
    assert new_hobbits[0] == (2, 0)


def test_nazgul_cannot_stack_on_same_square() -> None:
    """Two Nazgûl chasing same hobbit shouldn't stack"""
    hobbits = [(10, 10)]
    nazgul = [(9, 10), (11, 10)]  # Both sides of hobbit

    # Both want to move toward (10, 10)
    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbits=hobbits,
        dimensions=(20, 20),
        tick=0,
        terrain=set(),
    )

    # Should have 2 distinct positions
    assert len(set(new_nazgul)) == 2, "Nazgûl should not stack"
    assert new_nazgul[0] == (10, 10)
    assert new_nazgul[1] == (11, 10)


@pytest.mark.skip(reason="Evasion logic is still too strange.")
def test_hobbits_fleeing_to_corner_cannot_stack() -> None:
    """Two hobbits evading toward same corner square should not stack"""
    # Setup: Two hobbits in a line, Nazgûl chasing from behind
    hobbits = [(1, 1), (1, 2)]  # Vertical line
    nazgul = [(2, 1), (2, 2), (2, 3), (1, 3)]  # South of both, within danger distance
    rivendell = (4, 4)  # Northwest corner - both will flee there

    # Both hobbits will try to flee northwest (away from nazgul)
    # Both want to reach (4, 4) area
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Should NOT stack on same square
    assert len(set(new_hobbits)) == 2, f"Hobbits stacked! {new_hobbits}"
    assert new_hobbits[0] == (0, 1)
    assert new_hobbits[1] == (0, 2)


def test_nazgul_can_move_onto_hobbit_square_for_capture() -> None:
    """Nazgûl can move onto a hobbit square for capture"""
    hobbits = [(10, 10)]
    nazgul = [(9, 10)]

    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbits=hobbits,
        dimensions=(20, 20),
        tick=0,
        terrain=set(),
    )

    assert new_nazgul[0] == (10, 10)


@pytest.mark.skip(
    reason="Not implemented. In fact this test should prove that a hobbit will not "
    "move to a nazgul square for capture."
)
def test_hobbit_will_not_move_onto_nazgul_square_for_capture() -> None:
    """Hobbit will not move onto a nazgul square for capture"""
    hobbits = [(9, 10)]
    nazgul = [(10, 10)]
    rivendell = (19, 19)

    # Hobbit moving toward Rivendell will pass through Nazgûl
    # This should be ALLOWED (capture detection happens after movement)
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Movement should happen (even though it leads to capture)
    assert new_hobbits[0] != (9, 10), "Hobbit should be able to evade capture"


def test_hobbit_reaches_goal_when_no_threat() -> None:
    """Baseline: Hobbit should reach Rivendell when Nazgûl is far away"""
    hobbits = [(5, 5)]
    rivendell = (10, 10)
    nazgul = [(50, 50)]  # Way out of danger distance

    for tick in range(20):
        if hobbits[0] == rivendell:
            return  # Success!
        hobbits = update_hobbits(
            hobbits=hobbits,
            rivendell=rivendell,
            nazgul=nazgul,
            dimensions=(60, 60),
            tick=tick,
        )

    pytest.fail("Should reach goal when no threat")


def test_hobbit_flees_forward_when_chased_from_behind() -> None:
    """When Nazgûl is behind hobbit, fleeing should move toward goal"""
    hobbits = [(10, 10)]
    rivendell = (18, 18)  # Southeast
    nazgul = [(5, 5)]  # Behind (northwest)

    # Move once
    hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Hobbit should flee SOUTHEAST (away from threat + toward goal)
    assert hobbits[0][0] > 10, "Should move east"
    assert hobbits[0][1] > 10, "Should move south"


def test_hobbit_evades_perpendicular_threat() -> None:
    """When threat is to the side, hobbit should evade without losing ground"""
    hobbits = [(10, 10)]
    rivendell = (18, 10)  # Due east
    nazgul = [(10, 5)]  # Due north (perpendicular)

    # Move once
    hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Should flee south (away from north threat)
    # X-position might stay same or move toward goal
    assert hobbits[0][1] > 10, "Should flee south from north threat"


@pytest.mark.skip(
    reason="Evasion is not strong enough yet. Hobbit runs into a wall and gets stuck."
)
def test_single_hobbit_escapes_single_nazgul() -> None:
    """Simplest case: 1 hobbit vs 1 Nazgûl, clear path to goal"""
    # Hobbit starts northwest, goal is southeast, Nazgûl starts in between
    hobbits = [(5, 5)]
    rivendell = (15, 15)
    nazgul = [(10, 5)]  # Nazgûl to the NORTH of path
    # This should be a clear path to the goal
    WIDTH, HEIGHT = 20, 20

    # Run simulation (max 50 ticks)
    for tick in range(50):
        print(f"\n--- Tick {tick} ---")
        print(f"Hobbit: {hobbits[0] if hobbits else 'CAUGHT'}")
        print(f"Nazgûl: {nazgul[0]}")
        print(f"Goal: {rivendell}")

        # Check win condition
        if hobbits and hobbits[0] == rivendell:
            print(f"✓ Victory in {tick} ticks!")
            return  # Success!

        # Check lose condition
        if not hobbits:
            pytest.fail(f"Hobbit was caught at tick {tick}")

        # Move entities
        hobbits = update_hobbits(
            hobbits=hobbits,
            rivendell=rivendell,
            nazgul=nazgul,
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )
        nazgul = update_nazgul(
            nazgul=nazgul,
            hobbits=hobbits,
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        if hobbits and hobbits[0] in nazgul:
            hobbits = []

    pytest.fail(f"Simulation timeout after 50 ticks. Hobbit at {hobbits[0]}, Nazgûl at {nazgul[0]}")


@pytest.mark.skip(
    reason="Evasion is not strong enough yet. We need to implement a more robust evasion system."
)
def test_system_three_hobbits_escape_single_rider() -> None:
    """
    System test: Full simulation scenario
    - 3 hobbits start near (0,0)
    - 1 Nazgûl at (18, 12) - far away
    - All hobbits should reach Rivendell (19, 19)
    """
    # Starting positions (match current simulation)
    hobbits = [(1, 0), (0, 1), (1, 1)]
    nazgul = [(18, 12)]
    rivendell = (18, 18)
    WIDTH, HEIGHT = 20, 20

    # Run simulation (max 100 ticks to prevent infinite loop)
    for tick in range(100):
        # Check win condition
        if all(h == rivendell for h in hobbits):
            assert len(hobbits) == 3, "All 3 hobbits should escape"
            return  # Success!

        # Check lose condition
        if not hobbits:
            pytest.fail("All hobbits were caught - simulation failed")

        # Move entities
        hobbits = update_hobbits(
            hobbits=hobbits,
            rivendell=rivendell,
            nazgul=nazgul,
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )
        nazgul = update_nazgul(
            nazgul=nazgul,
            hobbits=hobbits,
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        hobbits_to_remove = [h for h in hobbits if h in nazgul]
        hobbits = [h for h in hobbits if h not in hobbits_to_remove]

    pytest.fail("Simulation didn't complete in 100 ticks")


def test_create_world_returns_valid_state() -> None:
    """World initialization returns all required components"""
    from hobbit_sim import create_world

    world = create_world()

    assert world["width"] == 20
    assert world["height"] == 20
    assert world["rivendell"] == (18, 18)
    assert len(world["hobbits"]) == 3
    assert len(world["nazgul"]) == 1
    assert isinstance(world["terrain"], set)


def test_render_grid_with_hobbits_and_nazgul() -> None:
    """Can we see hobbits and nazgul together?"""
    from hobbit_sim import create_grid, place_entity, render_grid

    grid = create_grid(dimensions=(4, 4))
    place_entity(grid=grid, position=(0, 0), symbol="H")  # Hobbit top-left
    place_entity(grid=grid, position=(3, 3), symbol="N")  # Nazgul bottom-right
    place_entity(grid=grid, position=(1, 2), symbol="H")  # Another hobbit
    result = render_grid(grid=grid)

    expected = "H . . .\n. . . .\n. H . .\n. . . N"
    assert result == expected


def test_render_grid_with_landmarks() -> None:
    """Complete scene: Shire, Rivendell, entities"""
    from hobbit_sim import create_grid, place_entity, render_grid

    grid = create_grid(dimensions=(5, 5))
    place_entity(grid=grid, position=(0, 0), symbol="S")  # Shire
    place_entity(grid=grid, position=(4, 4), symbol="R")  # Rivendell
    place_entity(grid=grid, position=(1, 1), symbol="H")  # Hobbit
    place_entity(grid=grid, position=(3, 2), symbol="N")  # Nazgul
    result = render_grid(grid=grid)

    expected = "S . . . .\n. H . . .\n. . . N .\n. . . . .\n. . . . R"
    assert result == expected


@pytest.mark.skip(reason="Not implemented")
# FUTURE: When we add individual hobbit symbols
def test_render_grid_with_named_hobbits() -> None:
    """RED: This will fail until we implement Phase 3"""
    from hobbit_sim import create_grid, place_entity, render_grid

    grid = create_grid(dimensions=(4, 4))
    place_entity(grid=grid, position=(0, 0), symbol="F")  # Frodo
    place_entity(grid=grid, position=(1, 0), symbol="S")  # Sam
    place_entity(grid=grid, position=(0, 1), symbol="P")  # Pippin
    result = render_grid(grid=grid)

    expected = "F S . .\nP . . .\n. . . .\n. . . ."
    assert result == expected  # Will pass once Phase 3 done!


def test_terrain_creates_borders_with_openings() -> None:
    """Terrain should have border walls except at Shire and Rivendell"""
    from hobbit_sim import create_world

    world = create_world()
    terrain = world["terrain"]

    # Check that borders exist
    assert (5, 0) in terrain, "Top border should exist"
    assert (5, 19) in terrain, "Bottom border should exist"
    assert (0, 5) in terrain, "Left border should exist"
    assert (19, 5) in terrain, "Right border should exist"

    # Check that Shire and Rivendell are NOT blocked
    assert (1, 1) not in terrain, "Shire should be passable"
    assert (18, 18) not in terrain, "Rivendell should be passable"


def test_render_world_shows_terrain() -> None:
    """render_world() should display terrain as # symbols"""
    from hobbit_sim import create_world, render_world

    world = create_world()
    result = render_world(world=world)

    # Check that first row has terrain (borders) and Shire
    # Row 0: S (Shire), # (borders), ..., # (border)
    lines = result.split("\n")
    first_row = lines[0]

    assert "S" in first_row, "Should show Shire"
    assert "#" in first_row, "Should show terrain borders"


def test_hobbit_cannot_move_through_terrain() -> None:
    """Hobbits should be blocked by terrain walls"""
    from hobbit_sim import update_hobbits

    # Place hobbit next to a wall
    hobbits = [(5, 5)]
    rivendell = (10, 10)
    nazgul = [(20, 20)]  # Far away, not in danger

    # Create a wall blocking the path
    terrain = {(6, 5), (6, 6), (5, 6)}  # Wall to the right and diagonal

    # Hobbit wants to move toward (10, 10) but terrain blocks (6, 6)
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
        terrain=terrain,
    )

    # Hobbit should NOT be at (6, 6) because terrain blocks it
    assert new_hobbits[0] != (6, 6), "Hobbit should not move into terrain"
    # Hobbit should still be at original position or moved to a valid adjacent square
    assert new_hobbits[0] in [(5, 5), (6, 5), (5, 6)] or (new_hobbits[0] not in terrain), (
        "Hobbit position should be valid"
    )


def test_nazgul_cannot_move_through_terrain() -> None:
    """Nazgûl should be blocked by terrain walls"""
    from hobbit_sim import update_nazgul

    # Place nazgul next to a wall
    nazgul = [(5, 5)]
    hobbits = [(10, 10)]  # Target

    # Create a wall blocking the path
    terrain = {(6, 5), (6, 6), (5, 6)}  # Wall to the right and diagonal

    # Nazgul wants to move toward (10, 10) but terrain blocks
    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbits=hobbits,
        dimensions=(20, 20),
        tick=0,
        terrain=terrain,
    )

    # Nazgul should NOT be at terrain positions
    assert new_nazgul[0] not in terrain, "Nazgul should not move into terrain"


def test_move_with_speed_stops_at_terrain() -> None:
    """move_with_speed should stop when hitting terrain"""
    from hobbit_sim import move_with_speed

    terrain = {(12, 10)}  # Single wall in the path

    # Try to move from (10, 10) to (15, 10) - should stop at (11, 10)
    result = move_with_speed(
        current=(10, 10),
        target=(15, 10),
        speed=5,
        dimensions=(20, 20),
        tick=0,
        terrain=terrain,
    )

    assert result == (11, 10), f"Should stop before terrain at (12, 10), got {result}"


def test_manhattan_movement_creates_staircase_pattern() -> None:
    """Manhattan movement should create a staircase pattern, not a diagonal line.

    When moving from (0,0) to (5,5), diagonal movement would go:
    (0,0) → (1,1) → (2,2) → (3,3) → (4,4) → (5,5)

    Manhattan movement with distance-priority should alternate axes:
    (0,0) → (0,1) → (1,1) → (1,2) → (2,2) → (2,3) → (3,3) → (3,4) → (4,4) → (4,5) → (5,5)

    This proves:
    1. No diagonal moves (only one coordinate changes per step)
    2. Prioritizes the axis with greater remaining distance
    3. Creates characteristic "staircase" pattern
    """
    path = []
    current = (0, 0)
    target = (5, 5)

    # Simulate 10 moves (enough to reach (5,5))
    for _ in range(11):  # 11 moves needed to go 10 Manhattan-distance
        path.append(current)

        if current == target:
            break

        current = move_toward(current=current, target=target)

    # Verify we reached the target
    assert path[-1] == (5, 5), f"Should reach target, final position: {path[-1]}"

    # Verify Manhattan property: each move changes ONLY one coordinate
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        x_changed = x2 != x1
        y_changed = y2 != y1

        # Exactly one coordinate should change (XOR)
        assert x_changed != y_changed, (
            f"Step {i}: ({x1},{y1}) → ({x2},{y2}) should change exactly one axis. "
            f"x_changed={x_changed}, y_changed={y_changed}"
        )

        # Each move should be exactly 1 square
        manhattan_distance = abs(x2 - x1) + abs(y2 - y1)
        assert manhattan_distance == 1, (
            f"Step {i}: ({x1},{y1}) → ({x2},{y2}) should move exactly 1 square, "
            f"got Manhattan distance {manhattan_distance}"
        )

    # Verify staircase pattern: should NOT be a perfect diagonal
    # A diagonal would be: (0,0), (1,1), (2,2), (3,3), (4,4), (5,5)
    diagonal_path = [(i, i) for i in range(6)]
    assert path != diagonal_path, "Path should be staircase, not diagonal line"

    # Path length should be 11 steps (10 Manhattan distance + starting position)
    assert len(path) == 11, f"Should take 10 moves + start = 11 positions, got {len(path)}"

    print("\n✓ Manhattan path from (0,0) to (5,5):")
    for i, pos in enumerate(path):
        print(f"  Step {i}: {pos}")


def test_move_away_from_without_goal_uses_distance_priority() -> None:
    """When no goal provided, should behave like original move_away_from"""
    # Threat to the east and south (dx=5, dy=2) - larger X distance
    result = move_away_from(current=(10, 10), threat=(15, 12))
    assert result == (9, 10), "Should flee on X axis when dx > dy"

    # Threat to the east and south (dx=2, dy=5) - larger Y distance
    result = move_away_from(current=(10, 10), threat=(12, 15))
    assert result == (10, 9), "Should flee on Y axis when dy > dx"


def test_move_away_from_with_goal_prefers_goal_aligned_direction() -> None:
    """When goal provided, prefer fleeing in direction that also helps reach goal"""
    # Setup: Threat NW, Goal SE
    # Hobbit at (10, 10)
    # Threat at (8, 8) - northwest
    # Goal at (15, 15) - southeast
    # Both fleeing E and fleeing S work, but both also move toward goal!
    result = move_away_from(current=(10, 10), threat=(8, 8), goal=(15, 15))

    # Should flee on one of the axes (both are good)
    assert result in [(11, 10), (10, 11)], f"Should flee toward goal, got {result}"

    # More specific: when distances from threat are equal, should pick one consistently
    # Let's test a clearer case:
    # Threat at (10, 8) - directly north (dy=2, dx=0)
    # Goal at (15, 15) - southeast
    result = move_away_from(current=(10, 10), threat=(10, 8), goal=(15, 15))
    assert result == (10, 11), "Should flee south (away + toward goal)"


def test_move_away_from_flees_even_if_away_from_goal() -> None:
    """Safety first: flee away from threat even if it means moving away from goal"""
    # Setup: Threat and Goal in same direction (southeast)
    # Hobbit at (10, 10)
    # Threat at (11, 11) - SE, close!
    # Goal at (18, 18) - SE, far
    result = move_away_from(current=(10, 10), threat=(11, 11), goal=(18, 18))

    # Should flee NW (away from threat), even though goal is SE
    assert result in [(9, 10), (10, 9)], f"Should flee away from threat, got {result}"
    # Should NOT move toward threat
    assert result not in [(11, 10), (10, 11), (11, 11)]


def test_move_away_from_chooses_goal_aligned_axis_when_both_axes_flee() -> None:
    """When threat is diagonal, choose the flee axis that aligns with goal"""
    # Hobbit at (10, 10)
    # Threat at (8, 12) - northwest (ish)
    # Goal at (18, 10) - directly east

    # Can flee: East (away from threat + toward goal) ✅
    # Can flee: North (away from threat, perpendicular to goal) ⚠️
    result = move_away_from(current=(10, 10), threat=(8, 12), goal=(18, 10))

    # Should prefer fleeing east because it helps with goal
    assert result == (11, 10), f"Should prefer east (toward goal), got {result}"


def test_move_away_from_perpendicular_threat_and_goal() -> None:
    """When threat is on one axis and goal on another"""
    # Hobbit at (10, 10)
    # Threat at (10, 15) - directly south
    # Goal at (15, 10) - directly east

    # Must flee: North (away from threat)
    # Goal says: East
    # These are perpendicular - can't satisfy both with one move
    result = move_away_from(current=(10, 10), threat=(10, 15), goal=(15, 10))

    # Should prioritize safety (flee north)
    assert result == (10, 9), "Should flee from threat even if not toward goal"


def test_move_away_from_when_already_fleeing_correct_direction() -> None:
    """When threat is NW and goal is SE, fleeing SE is optimal"""
    # Hobbit at (10, 10)
    # Threat at (5, 5) - far to the northwest
    # Goal at (18, 18) - far to the southeast

    result = move_away_from(current=(10, 10), threat=(5, 5), goal=(18, 18))

    # Both fleeing E and fleeing S move away from threat AND toward goal
    # Either is fine, but should pick one
    assert result in [(11, 10), (10, 11)], f"Should flee SE quadrant, got {result}"
    # Should definitely not flee back toward threat
    assert result not in [(9, 10), (10, 9)]


def test_move_away_from_backward_compatibility() -> None:
    """Without goal parameters, should match old move_away_from behavior"""
    # This ensures we don't break existing code
    result = move_away_from(current=(10, 10), threat=(11, 11))

    # Should match the test we already have
    assert result in [(9, 10), (10, 9)], "Should behave like original when no goal"
