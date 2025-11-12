# test_hobbit_sim.py
import pytest

from hobbit_sim import (
    EntityPositions,
    Position,
    _run_simulation_loop,
    create_world,
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
    hobbits = {0: (10, 19)}  # At south edge
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
    hobbits = {0: (10, 18)}  # At south edge
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


def test_calculate_perpendicular_moves_when_threat_is_east() -> None:
    """When threat is east (on X axis), perpendicular moves are north/south"""
    from hobbit_sim import calculate_perpendicular_moves

    options = calculate_perpendicular_moves(
        current=(10, 10),
        threat=(15, 10),  # 5 squares east
    )

    assert (10, 11) in options, "Should include south"
    assert (10, 9) in options, "Should include north"
    assert len(options) == 2, "Should return exactly 2 options"


def test_calculate_perpendicular_moves_when_threat_is_north() -> None:
    """When threat is north (on Y axis), perpendicular moves are east/west"""
    from hobbit_sim import calculate_perpendicular_moves

    options = calculate_perpendicular_moves(
        current=(10, 10),
        threat=(10, 5),  # 5 squares north
    )

    assert (11, 10) in options, "Should include east"
    assert (9, 10) in options, "Should include west"
    assert len(options) == 2, "Should return exactly 2 options"


def test_calculate_perpendicular_moves_when_threat_is_diagonal() -> None:
    """When threat is diagonal, use larger axis distance as tiebreaker"""
    from hobbit_sim import calculate_perpendicular_moves

    # Threat northeast: dx=3, dy=2 → larger X distance
    options = calculate_perpendicular_moves(
        current=(10, 10),
        threat=(13, 8),
    )

    # Should treat as X-axis threat → perpendicular is Y-axis
    assert (10, 11) in options, "Should include south"
    assert (10, 9) in options, "Should include north"


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
    assert find_nearest_hobbit(nazgul=(10, 10), hobbit_positions=[(11, 11), (9, 10)]) == (
        (9, 10),
        1,
    )


def test_find_nearest_hobbit_with_no_hobbits() -> None:
    assert find_nearest_hobbit(nazgul=(10, 10), hobbit_positions=[]) == (None, 999_999_999)


def test_distance_calculations_use_manhattan_distance() -> None:
    """
    Distance calculations match movement system (Manhattan distance).

    Both find_nearest_* functions return integer Manhattan distances,
    not float Euclidean distances.

    Example: point (0,0) to (3,4)
    - Manhattan: |3| + |4| = 7 (int)
    - Euclidean: sqrt(3² + 4²) = 5.0 (float)

    This test verifies the return type is int and distances are calculated correctly.
    """
    # Test find_nearest_hobbit returns integer Manhattan distance
    hobbits: EntityPositions = [(3, 4), (5, 5)]
    nazgul_pos: Position = (0, 0)

    nearest_hobbit, distance = find_nearest_hobbit(nazgul=nazgul_pos, hobbit_positions=hobbits)

    assert nearest_hobbit == (3, 4), "Should find closest hobbit"
    assert distance == 7, "Manhattan distance from (0,0) to (3,4) is |3| + |4| = 7"
    assert isinstance(distance, int), "Distance should be int, not float (Manhattan not Euclidean)"

    # Test find_nearest_nazgul returns integer Manhattan distance
    nazguls: EntityPositions = [(2, 1), (6, 8)]
    hobbit_pos: Position = (0, 0)

    nearest_naz, distance = find_nearest_nazgul(hobbit=hobbit_pos, nazgul=nazguls)

    assert nearest_naz == (2, 1), "Should find closest Nazgûl"
    assert distance == 3, "Manhattan distance from (0,0) to (2,1) is |2| + |1| = 3"
    assert isinstance(distance, int), "Distance should be int, not float (Manhattan not Euclidean)"


def test_hobbits_at_rivendell_represent_exited_state() -> None:
    """
    Hobbits reaching Rivendell are considered 'exited' (current simplification).

    In the current implementation, hobbits "stack" at the Rivendell position
    to represent having successfully exited the map. This is a simplification
    of the ideal behavior where escaped hobbits would be tracked in a separate
    buffer off the board.

    See: test_escaped_hobbits_tracked_separately_from_active (skipped) for
    the desired future behavior.
    """
    hobbits = {0: (0, 0), 1: (1, 0)}  # Side by side
    nazgul = [(10, 10)]  # Far away
    rivendell = (2, 0)  # East - the exit

    # Both hobbits move toward Rivendell (the exit)
    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Both hobbits at Rivendell (currently represented as "stacking")
    assert len(set(new_hobbits.values())) == 1, "Both hobbits should reach the exit"
    assert new_hobbits[0] == (2, 0), "Exit position should be Rivendell"


@pytest.mark.skip(
    reason="Exit buffer not implemented - hobbits currently 'stack' at Rivendell "
    "to represent exited state"
)
def test_escaped_hobbits_tracked_separately_from_active() -> None:
    """
    Escaped hobbits should be tracked in separate buffer, not as board positions.

    When a hobbit reaches Rivendell, they should be:
    - Removed from active board positions
    - Added to escaped/exited buffer
    - Not vulnerable to capture
    - Counted toward victory condition

    This separates the concept of 'exiting' (state transition) from
    'stacking' (collision problem). Similar to roguelike level transitions
    or Diablo's town portal - you're off the combat map.

    Future implementation might return:
    - (active_hobbits, escaped_hobbits) tuple
    - Or WorldState dataclass with separate tracking
    - Or Game object with exit buffer
    """
    # Test will be written when exit buffer is implemented
    pass


def test_nazgul_cannot_stack_on_same_square() -> None:
    """Two Nazgûl chasing same hobbit shouldn't stack"""
    hobbits = {0: (10, 10)}
    nazgul = [(9, 10), (11, 10)]  # Both sides of hobbit

    # Both want to move toward (10, 10)
    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbit_positions=list(hobbits.values()),  # Convert dict to positions list
        dimensions=(20, 20),
        tick=0,
        terrain=set(),
    )

    # Should have 2 distinct positions
    assert len(set(new_nazgul)) == 2, "Nazgûl should not stack"
    assert new_nazgul[0] == (10, 10)
    assert new_nazgul[1] == (11, 10)


def test_hobbits_fleeing_to_corner_cannot_stack() -> None:
    """
    Hobbits avoid colliding when fleeing from danger (collision avoidance).

    When multiple hobbits panic and flee in the same direction, they should
    spread out to avoid stacking on the same square. This is about collision
    avoidance during movement, not exiting behavior.

    This is different from reaching Rivendell (exiting), where multiple hobbits
    CAN occupy the same square because they're transitioning off the map.
    See: test_hobbits_at_rivendell_represent_exited_state
    """
    # Setup: Two hobbits in a line, Nazgûl chasing from behind
    hobbits = {0: (1, 1), 1: (1, 2)}  # Vertical line
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
    assert len(set(new_hobbits.values())) == 2, f"Hobbits stacked! {new_hobbits}"

    # Verify they actually moved to different positions (collision avoidance working)
    # Note: Specific positions depend on movement priority logic, which may change.
    # The core requirement is: no two hobbits on the same square.
    assert new_hobbits[0] != new_hobbits[1], "Hobbits must be at different positions"


# TODO: test a race where a hobbit makes it to safety while another is en route,
# the nazgul should not be able to capture the one that made it to safety
def test_nazgul_can_move_onto_hobbit_square_for_capture() -> None:
    """Nazgûl can move onto a hobbit square for capture"""
    hobbits = {0: (10, 10)}
    nazgul = [(9, 10)]

    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbit_positions=list(hobbits.values()),  # Convert dict to positions
        dimensions=(20, 20),
        tick=0,
        terrain=set(),
    )

    assert new_nazgul[0] == (10, 10)


@pytest.mark.skip(
    reason="Hobbits don't yet detect Nazgûl positions when choosing movement. "
    "Need to add collision awareness to prevent walking into capture."
)
def test_hobbit_routes_around_nazgul_to_avoid_capture() -> None:
    """
    Hobbit detects Nazgûl in path and routes around to avoid capture.

    When a hobbit's direct path to Rivendell passes through a Nazgûl position,
    the hobbit should detect this and choose an alternative route that avoids
    the threat while still making progress toward the goal.
    Open question - if a hobbit decides to pass thru a nazgul space does that
    count as a capture, or is it effectively running just past them
    attack of opportunity? or can a nazgul only capture on their own turn
    """
    hobbits = {0: (9, 10)}
    nazgul = [(10, 10)]  # Directly east of hobbit
    rivendell = (19, 19)  # Southeast - direct path goes through Nazgûl

    new_hobbits = update_hobbits(
        hobbits=hobbits,
        rivendell=rivendell,
        nazgul=nazgul,
        dimensions=(20, 20),
        tick=0,
    )

    # Hobbit should move (not stay stuck)
    assert new_hobbits[0] != (9, 10), "Hobbit should move, not stay stuck"

    # Hobbit should NOT walk into the Nazgûl
    assert new_hobbits[0] != (10, 10), "Hobbit should not walk onto Nazgûl square"

    # Hobbit should make progress by routing around
    # Could be (9, 11) going north, or (10, 11) going diagonal northeast
    assert new_hobbits[0] in [(9, 11), (10, 11)], (
        f"Hobbit should route around Nazgûl, got {new_hobbits[0]}"
    )


def test_hobbit_reaches_goal_when_no_threat() -> None:
    """Baseline: Hobbit should reach Rivendell when Nazgûl is far away"""
    hobbits = {0: (5, 5)}
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
    hobbits = {0: (10, 10)}
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
    hobbits = {0: (10, 10)}
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


def test_hobbit_with_threats_on_two_axes_doesnt_flee_into_trap() -> None:
    """
    Scenario: Hobbit cornered with Nazgûl on two perpendicular axes.

    Setup:
        H . . . . N    Hobbit at (5, 5)
        . . . . . .    Nazgûl A at (10, 5) - east, distance 5
        . . . . . .    Nazgûl B at (5, 10) - south, distance 5
        . . . . . .
        . . . . . .    Goal at (0, 0) - northwest (safe direction)
        N . . . . .

    Current behavior might try:
    - flee from Nazgûl A (east) → go WEST (good!) or perpendicular N/S (bad if south!)

    Expected: Hobbit should flee NORTHWEST (away from both threats, toward goal)
    Bug: Hobbit might flee SOUTH (perpendicular from A, but toward B)
    """
    hobbits = {0: (5, 5)}
    nazgul = [
        (10, 5),  # East - distance 5
        (5, 10),  # South - distance 5
    ]
    rivendell = (0, 0)  # Northwest - safe direction
    WIDTH, HEIGHT = 20, 20

    # Run simulation
    for tick in range(50):
        print(f"\n--- Tick {tick} ---")
        print(f"Hobbit: {hobbits.get(0, 'CAUGHT')}")
        print(f"Nazgûl: {nazgul}")
        print(f"Goal: {rivendell}")

        # Win condition
        if hobbits and hobbits.get(0) == rivendell:
            print(f"✓ Victory in {tick} ticks!")
            return

        # Lose condition
        if not hobbits:
            pytest.fail(f"Hobbit caught at tick {tick}")

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
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        if hobbits and hobbits.get(0) in nazgul:
            hobbits = {}

    pytest.fail(f"Timeout after 50 ticks. Hobbit at {hobbits.get(0, 'caught')}")


def test_hobbit_threads_between_two_nazgul_to_reach_goal() -> None:
    """
    Scenario: Hobbit must navigate BETWEEN two Nazgûl to reach goal.

    Setup:
              N₁ (10,3)
              |
    H (5,5) -----> Goal (15,5)
              |
              N₂ (10,7)

    Hobbit at (5, 5)
    Nazgûl A at (10, 3) - northeast, distance 7
    Nazgûl B at (10, 7) - southeast, distance 7
    Goal at (15, 5) - due east (through the gap!)

    Challenge: Hobbit must move EAST toward goal, threading the needle
    between two threats. Simple "flee away" won't work here.

    Expected: Hobbit stays on y=5 (middle line), speeds through the gap
    Bug: Hobbit might flee north/south away from goal
    """
    hobbits = {0: (5, 5)}
    nazgul = [
        (10, 3),  # Northeast - distance 7
        (10, 7),  # Southeast - distance 7
    ]
    rivendell = (15, 5)  # Due east - through the gap!
    WIDTH, HEIGHT = 20, 20

    # Run simulation
    for tick in range(50):
        print(f"\n--- Tick {tick} ---")
        print(f"Hobbit: {hobbits.get(0, 'CAUGHT')}")
        print(f"Nazgûl: {nazgul}")
        print(f"Goal: {rivendell}")

        # Win condition
        if hobbits and hobbits.get(0) == rivendell:
            print(f"✓ Victory in {tick} ticks!")
            return

        # Lose condition
        if not hobbits:
            pytest.fail(f"Hobbit caught at tick {tick}")

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
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        if hobbits and hobbits.get(0) in nazgul:
            hobbits = {}

    pytest.fail(f"Timeout after 50 ticks. Hobbit at {hobbits.get(0, 'caught')}")


def test_hobbit_navigates_through_three_nazgul_blockade() -> None:
    """
    Scenario: Three Nazgûl form a blockade between hobbit and goal.

    Setup:
           N₁ (9,3)
           |
    H ---- N₂ (10,5) -----> Goal (18,5)
           |
           N₃ (9,7)

    Hobbit at (5, 5)
    Nazgûl A at (9, 3) - northeast, distance 6
    Nazgûl B at (10, 5) - due east, distance 5
    Nazgûl C at (9, 7) - southeast, distance 6
    Goal at (18, 5) - due east beyond blockade

    Challenge: Three Nazgûl block the direct path. Hobbit must find a gap
    or go around. This tests if hobbit can path around a blockade.

    Expected: Hobbit routes around (north or south of blockade)
    Bug: Hobbit might get stuck or flee backward away from goal
    """
    hobbits = {0: (5, 5)}
    nazgul = [
        (9, 3),  # North guard - distance 6
        (10, 5),  # Center guard - distance 5
        (9, 7),  # South guard - distance 6
    ]
    rivendell = (18, 5)  # Due east beyond blockade
    WIDTH, HEIGHT = 20, 20

    # Run simulation
    for tick in range(50):
        print(f"\n--- Tick {tick} ---")
        print(f"Hobbit: {hobbits.get(0, 'CAUGHT')}")
        print(f"Nazgûl: {nazgul}")
        print(f"Goal: {rivendell}")

        # Win condition
        if hobbits and hobbits.get(0) == rivendell:
            print(f"✓ Victory in {tick} ticks!")
            return

        # Lose condition
        if not hobbits:
            pytest.fail(f"Hobbit caught at tick {tick}")

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
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        if hobbits and hobbits.get(0) in nazgul:
            hobbits = {}

    pytest.fail(f"Timeout after 50 ticks. Hobbit at {hobbits.get(0, 'caught')}")


def test_single_hobbit_escapes_single_nazgul() -> None:
    """Simplest case: 1 hobbit vs 1 Nazgûl, clear path to goal, no terrain complexity"""
    # Hobbit starts northwest, goal is southeast, Nazgûl starts in between
    hobbits = {0: (5, 5)}
    rivendell = (15, 15)
    nazgul = [(10, 5)]  # Nazgûl to the NORTH of path
    # This should be a clear path to the goal
    WIDTH, HEIGHT = 20, 20

    # Run simulation (max 50 ticks)
    for tick in range(50):
        print(f"\n--- Tick {tick} ---")
        print(f"Hobbit: {hobbits.get(0, 'CAUGHT')}")
        print(f"Nazgûl: {nazgul[0]}")
        print(f"Goal: {rivendell}")

        # Check win condition
        if hobbits and hobbits.get(0) == rivendell:
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
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        if hobbits and hobbits.get(0) in nazgul:
            hobbits = {}

    pytest.fail(
        f"Simulation timeout after 50 ticks. "
        f"Hobbit at {hobbits.get(0, 'caught')}, Nazgûl at {nazgul[0]}"
    )


def test_baseline_three_hobbits_can_reach_rivendell() -> None:
    """
    Baseline system test: 3 hobbits escape 1 Nazgûl and reach Rivendell.

    This test locks in the current working behavior - the basic FOTR scenario
    of hobbits fleeing from a Black Rider and reaching safety.

    Setup (matching current create_world()):
    - 3 hobbits start in southwest corner
    - 1 Nazgûl starts far east
    - Rivendell in northeast corner
    - 20x20 grid with border walls

    Success: ALL 3 hobbits reach Rivendell (current sim achieves this in ~16 ticks)
    """
    # Hardcoded setup matching current create_world()
    hobbits = {0: (1, 2), 1: (2, 1), 2: (2, 2)}  # Southwest corner
    nazgul = [(18, 5)]  # Far east
    rivendell = (18, 18)  # Northeast corner
    WIDTH, HEIGHT = 20, 20

    # Create terrain - border walls
    terrain = set()
    for x in range(WIDTH):
        terrain.add((x, 0))  # Top border
        terrain.add((x, HEIGHT - 1))  # Bottom border
    for y in range(HEIGHT):
        terrain.add((0, y))  # Left border
        terrain.add((WIDTH - 1, y))  # Right border

    starting_hobbit_count = len(hobbits)

    # Run simulation
    for tick in range(50):  # Current sim finishes in ~16 ticks
        # Check victory: all hobbits at Rivendell
        if all(pos == rivendell for pos in hobbits.values()):
            assert len(hobbits) == starting_hobbit_count, (
                f"Only {len(hobbits)}/{starting_hobbit_count} hobbits escaped"
            )
            return  # Success!

        # Check loss: all captured
        if not hobbits:
            pytest.fail(f"All hobbits were caught at tick {tick}")

        # Update entities
        hobbits = update_hobbits(
            hobbits=hobbits,
            rivendell=rivendell,
            nazgul=nazgul,
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
            terrain=terrain,
        )
        nazgul = update_nazgul(
            nazgul=nazgul,
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
            terrain=terrain,
        )

        # Remove captured hobbits
        hobbits = {hid: pos for hid, pos in hobbits.items() if pos not in nazgul}

    pytest.fail(
        f"Simulation timeout after 50 ticks. "
        f"{len(hobbits)}/{starting_hobbit_count} hobbits reached Rivendell"
    )


def test_current_simulation_configuration_completes() -> None:
    """
    Surface-level test: Whatever create_world() returns completes successfully.

    This test wraps the current simulation configuration. As we evolve the
    simulation setup in create_world(), this test evolves with it, ensuring
    the configured scenario always works.

    This is different from test_baseline_three_hobbits_can_reach_rivendell
    which has hardcoded values and stays stable.
    """
    world = create_world()
    hobbits = world.hobbits
    nazgul = world.nazgul
    rivendell = world.rivendell
    terrain = world.terrain
    dimensions = world.dimensions
    starting_hobbit_count = world.starting_hobbit_count

    # Run simulation
    for tick in range(100):  # Generous limit for future configs
        # Check victory: all hobbits at Rivendell
        if all(pos == rivendell for pos in hobbits.values()):
            assert len(hobbits) == starting_hobbit_count, (
                f"Only {len(hobbits)}/{starting_hobbit_count} hobbits escaped"
            )
            return  # Success!

        # Check loss: all captured
        if not hobbits:
            pytest.fail(f"All hobbits were caught at tick {tick}")

        # Update entities
        hobbits = update_hobbits(
            hobbits=hobbits,
            rivendell=rivendell,
            nazgul=nazgul,
            dimensions=dimensions,
            tick=tick,
            terrain=terrain,
        )
        nazgul = update_nazgul(
            nazgul=nazgul,
            hobbit_positions=list(hobbits.values()),
            dimensions=dimensions,
            tick=tick,
            terrain=terrain,
        )

        # Remove captured hobbits
        hobbits = {hid: pos for hid, pos in hobbits.items() if pos not in nazgul}

    pytest.fail(
        f"Simulation timeout after 100 ticks. "
        f"{len(hobbits)}/{starting_hobbit_count} hobbits reached Rivendell"
    )


def test_acceptance_full_simulation_succeeds() -> None:
    """
    Acceptance test: Full simulation path from create_world() to victory.

    This tests the complete simulation stack including _run_simulation_loop(),
    which is what run_simulation() calls internally. Tests the full path:
    - World creation
    - Victory/defeat detection
    - Entity updates
    - Capture detection
    - Grid rendering (headless, no display callback)

    This is the most realistic test - it exercises the exact same code path
    as the interactive simulation, just without display/pacing.
    """
    result = _run_simulation_loop(max_ticks=100)

    # Assert successful completion
    assert result["outcome"] == "victory", (
        f"Expected victory but got {result['outcome']} after {result['ticks']} ticks. "
        f"Escaped: {result['hobbits_escaped']}, Captured: {result['hobbits_captured']}"
    )

    # Assert all hobbits escaped
    assert result["hobbits_escaped"] == 3, (
        f"Expected all 3 hobbits to escape, but only {result['hobbits_escaped']} made it"
    )

    # Assert no captures
    assert result["hobbits_captured"] == 0, (
        f"Expected no captures, but {result['hobbits_captured']} hobbits were caught"
    )

    # Assert reasonable completion time (current sim finishes in ~16 ticks)
    assert result["ticks"] < 50, (
        f"Simulation took {result['ticks']} ticks, expected < 50 (current baseline is ~16)"
    )


def test_system_three_hobbits_escape_single_rider() -> None:
    """
    System test: Full simulation scenario
    - 3 hobbits start near (0,0)
    - 1 Nazgûl at (18, 12) - far away
    - All hobbits should reach Rivendell (19, 19)
    """
    # Starting positions (match current simulation)
    hobbits = {0: (1, 0), 1: (0, 1), 2: (1, 1)}
    nazgul = [(18, 12)]
    rivendell = (18, 18)
    WIDTH, HEIGHT = 20, 20

    # Run simulation (max 100 ticks to prevent infinite loop)
    for tick in range(100):
        # Check win condition
        if all(pos == rivendell for pos in hobbits.values()):
            assert len(hobbits) == 3, "All 3 hobbits should escape"
            return  # Success!

        # Check lose condition
        if len(hobbits) != 3:
            pytest.fail("Hobbits were captured - simulation failed")

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
            hobbit_positions=list(hobbits.values()),  # Convert dict to positions
            dimensions=(WIDTH, HEIGHT),
            tick=tick,
        )

        # Check captures
        hobbits = {hid: pos for hid, pos in hobbits.items() if pos not in nazgul}

    pytest.fail("Simulation didn't complete in 100 ticks")


def test_create_world_returns_valid_state() -> None:
    """World initialization returns all required components"""
    from hobbit_sim import create_world

    world = create_world()

    assert world.width == 20
    assert world.height == 20
    assert world.rivendell == (18, 18)
    assert len(world.hobbits) == 3
    assert len(world.nazgul) == 1
    assert isinstance(world.terrain, set)


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


def test_render_grid_with_named_hobbits() -> None:
    """place_entity() can render individual hobbit symbols F, S, P, M"""
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
    terrain = world.terrain

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

    # Check that rendering shows terrain borders and exit marker
    lines = result.split("\n")
    first_row = lines[0]

    assert "#" in first_row, "Should show terrain borders"
    assert "X" in result, "Should show exit marker (X) somewhere in grid"


def test_render_world_shows_hobbit_names() -> None:
    """render_world() can show hobbit names as F, S, P, M"""
    from hobbit_sim import WorldState, render_world

    # Create simple world with 4 hobbits at known positions
    world = WorldState(
        width=6,
        height=6,
        map_id=0,
        rivendell=(5, 5),
        exit_position=(5, 5),
        entry_symbol="S",
        exit_symbol="R",
        terrain=set(),
        starting_hobbit_count=4,
        starting_nazgul_count=0,
        hobbits={0: (1, 1), 1: (2, 2), 2: (3, 3), 3: (4, 4)},  # Frodo, Sam, Pippin, Merry
        nazgul=[],
    )

    # Render without IDs (default) - should show generic 'H'
    result_default = render_world(world=world)
    assert result_default.count("H") == 4, "Should show 4 generic 'H' symbols by default"

    # Render with IDs enabled - should show F, S, P, M
    result_with_ids = render_world(world=world, show_hobbit_ids=True)
    assert "F" in result_with_ids, "Should show Frodo as 'F'"
    assert "S" in result_with_ids, "Should show Sam as 'S'"
    assert "P" in result_with_ids, "Should show Pippin as 'P'"
    assert "M" in result_with_ids, "Should show Merry as 'M'"


def test_hobbit_cannot_move_through_terrain() -> None:
    """Hobbits should be blocked by terrain walls"""
    from hobbit_sim import update_hobbits

    # Place hobbit next to a wall
    hobbits = {0: (5, 5)}
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
    hobbits = {0: (10, 10)}  # Target

    # Create a wall blocking the path
    terrain = {(6, 5), (6, 6), (5, 6)}  # Wall to the right and diagonal

    # Nazgul wants to move toward (10, 10) but terrain blocks
    new_nazgul = update_nazgul(
        nazgul=nazgul,
        hobbit_positions=list(hobbits.values()),  # Convert dict to positions
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


def test_dict_based_hobbit_movement() -> None:
    """Proof of concept: hobbits as dict with explicit IDs works end-to-end"""
    from hobbit_sim import WorldState, render_world

    # Create world with dict-based hobbits (explicit identity)
    world = WorldState(
        width=10,
        height=10,
        map_id=0,
        rivendell=(9, 9),
        exit_position=(9, 9),
        entry_symbol="S",
        exit_symbol="R",
        terrain=set(),
        starting_hobbit_count=3,
        starting_nazgul_count=0,
        hobbits={
            0: (1, 1),  # Frodo
            1: (2, 2),  # Sam
            2: (3, 3),  # Pippin
        },
        nazgul=[],
        tick=0,
    )

    # Verify initial state
    assert isinstance(world.hobbits, dict)
    assert len(world.hobbits) == 3
    assert world.hobbits[0] == (1, 1)
    assert world.hobbits[1] == (2, 2)
    assert world.hobbits[2] == (3, 3)

    # Move hobbits toward rivendell
    result = update_hobbits(
        hobbits=world.hobbits,
        rivendell=world.rivendell,
        nazgul=world.nazgul,
        dimensions=world.dimensions,
        tick=0,
        terrain=world.terrain,
    )

    # update_hobbits now returns dict for identity tracking
    assert isinstance(result, dict)
    assert len(result) == 3

    # All hobbits should have moved via Manhattan movement toward (9,9)
    # Frodo from (1,1) -> (1,2) -> (2,2)
    # Sam from (2,2) -> (2,3) -> (3,3)
    # Pippin from (3,3) -> (3,4) -> (4,4)
    assert (2, 2) in result.values()
    assert (3, 3) in result.values()
    assert (4, 4) in result.values()

    # Test rendering with dict hobbits
    rendered = render_world(world=world, show_hobbit_ids=True)
    assert "F" in rendered  # Frodo
    assert "S" in rendered  # Sam
    assert "P" in rendered  # Pippin


def test_map_config_defines_three_maps() -> None:
    """Verify MAP_DEFINITIONS contains correct 3-map journey configuration."""
    from hobbit_sim import MAP_DEFINITIONS

    # Verify we have exactly 3 maps
    assert len(MAP_DEFINITIONS) == 3
    assert 0 in MAP_DEFINITIONS
    assert 1 in MAP_DEFINITIONS
    assert 2 in MAP_DEFINITIONS

    # Map 0: Bag End
    bag_end = MAP_DEFINITIONS[0]
    assert bag_end.map_id == 0
    assert bag_end.name == "Bag End"
    assert bag_end.entry_symbol == "B"
    assert bag_end.exit_symbol == "X"
    assert bag_end.hobbit_spawns == (1, 1)
    assert len(bag_end.nazgul_spawns) == 1  # One Nazgûl

    # Map 1: Shire Forest
    forest = MAP_DEFINITIONS[1]
    assert forest.map_id == 1
    assert forest.name == "Shire Forest"
    assert forest.entry_symbol == "F"
    assert forest.exit_symbol == "X"
    assert forest.hobbit_spawns == (1, 1)
    assert len(forest.nazgul_spawns) == 2  # Two Nazgûl

    # Map 2: Crickhollow
    crickhollow = MAP_DEFINITIONS[2]
    assert crickhollow.map_id == 2
    assert crickhollow.name == "Crickhollow"
    assert crickhollow.entry_symbol == "C"
    assert crickhollow.exit_symbol == "X"
    assert crickhollow.hobbit_spawns == (1, 1)
    assert len(crickhollow.nazgul_spawns) == 3  # Three Nazgûl


def test_all_hobbits_at_exit_returns_true_when_grouped() -> None:
    """all_hobbits_at_exit() returns True when all hobbits reach the exit."""
    from hobbit_sim import all_hobbits_at_exit

    exit_pos = (18, 18)

    # All hobbits at exit
    hobbits_at_exit = {
        0: (18, 18),  # Frodo at exit
        1: (18, 18),  # Sam at exit
        2: (18, 18),  # Pippin at exit
    }
    assert all_hobbits_at_exit(hobbits=hobbits_at_exit, exit_position=exit_pos) is True

    # Some hobbits not at exit
    hobbits_mixed = {
        0: (18, 18),  # Frodo at exit
        1: (17, 18),  # Sam not at exit
        2: (18, 18),  # Pippin at exit
    }
    assert all_hobbits_at_exit(hobbits=hobbits_mixed, exit_position=exit_pos) is False

    # No hobbits at exit
    hobbits_away = {
        0: (1, 1),  # Frodo far away
        1: (2, 2),  # Sam far away
        2: (3, 3),  # Pippin far away
    }
    assert all_hobbits_at_exit(hobbits=hobbits_away, exit_position=exit_pos) is False

    # Empty hobbits dict
    assert all_hobbits_at_exit(hobbits={}, exit_position=exit_pos) is False


def test_transition_preserves_hobbit_ids() -> None:
    """Transition to next map preserves hobbit IDs."""
    from hobbit_sim import create_map, transition_to_next_map

    # Start on Map 0
    map0 = create_map(map_id=0)
    original_hobbit_ids = set(map0.hobbits.keys())

    # Transition to Map 1
    map1 = transition_to_next_map(current_state=map0)
    assert map1 is not None
    assert map1.map_id == 1
    assert set(map1.hobbits.keys()) == original_hobbit_ids  # Same IDs


def test_transition_spawns_new_nazgul() -> None:
    """Transition to next map spawns fresh Nazgûl from config."""
    from hobbit_sim import MAP_DEFINITIONS, create_map, transition_to_next_map

    # Start on Map 0
    map0 = create_map(map_id=0)
    assert len(map0.nazgul) == 1  # Map 0 has 1 Nazgûl

    # Transition to Map 1
    map1 = transition_to_next_map(current_state=map0)
    assert map1 is not None
    assert len(map1.nazgul) == 2  # Map 1 has 2 Nazgûl
    assert map1.nazgul == list(MAP_DEFINITIONS[1].nazgul_spawns)


def test_exiting_final_map_triggers_victory() -> None:
    """Exiting Map 2 (final map) returns None (victory condition)."""
    from hobbit_sim import create_map, transition_to_next_map

    # Start on Map 2 (final map)
    map2 = create_map(map_id=2)

    # Try to transition beyond final map
    result = transition_to_next_map(current_state=map2)
    assert result is None  # No more maps - victory!
