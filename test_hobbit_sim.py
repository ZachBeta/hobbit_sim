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


def test_hobbit_evading_at_south_edge_doesnt_get_stuck():
    """
    Scenario: Hobbit at bottom edge (y=19), Nazgûl approaching from north
    Bug: Hobbit tries to move south (away), hits boundary, doesn't move at all
    Expected: Hobbit should move laterally (east or west) along edge to evade
    """
    # Setup: Hobbit at south edge, Nazgûl to the north
    hobbits = [(10, 19)]  # At south edge
    nazgul = [(10, 15)]  # 4 squares north (within danger distance 6)
    rivendell = (19, 19)  # Goal is east along same edge

    # Move hobbits (should evade)
    new_hobbits = update_hobbits(hobbits, rivendell, nazgul, width=20, height=20)

    # Assert: Hobbit should have moved (not stuck at same position)
    assert new_hobbits[0] != (10, 19), "Hobbit should move when evading at edge"

    # Assert: Hobbit moved laterally toward goal (east), not stuck going south
    assert new_hobbits[0][0] > 10, "Hobbit should move east toward goal"
    assert new_hobbits[0][1] == 19, "Hobbit should stay on south edge"


def test_move_toward_moves_diagonally():
    assert move_toward(10, 10, 11, 11) == (11, 11)


def test_move_away_from_moves_opposite_direction():
    assert move_away_from(10, 10, 11, 11) == (9, 9)


def test_find_nearest_nazgul_returns_closest():
    assert find_nearest_nazgul(10, 10, [(11, 11), (9, 10)]) == ((9, 10), 1)


def test_move_with_speed_stops_at_boundary():
    assert move_with_speed(10, 10, 11, 11, 1, 20, 20) == (11, 11)


def test_find_nearest_hobbit_returns_closest():
    assert find_nearest_hobbit(10, 10, [(11, 11), (9, 10)]) == (9, 10)


def test_find_nearest_hobbit_with_no_hobbits():
    assert find_nearest_hobbit(10, 10, []) is None


# skip
@pytest.mark.skip(reason="Not implemented")
def test_hobbits_cannot_stack_on_same_square():
    """Two hobbits trying to move to same square - second one should be blocked"""
    hobbits = [(0, 0), (1, 0)]  # Side by side
    nazgul = [(10, 10)]  # Far away
    rivendell = (2, 0)  # East

    # Both want to move to (2, 0)
    # First hobbit gets there, second should be blocked
    new_hobbits = update_hobbits(hobbits, rivendell, nazgul, width=20, height=20)

    # Should have 2 distinct positions (no stacking)
    assert len(set(new_hobbits)) == 2, "Hobbits should not stack"


@pytest.mark.skip(reason="Not implemented")
def test_nazgul_cannot_stack_on_same_square():
    """Two Nazgûl chasing same hobbit shouldn't stack"""
    hobbits = [(10, 10)]
    nazgul = [(8, 10), (12, 10)]  # Both sides of hobbit

    # Both want to move toward (10, 10)
    new_nazgul = update_nazgul(nazgul, hobbits, width=20, height=20)

    # Should have 2 distinct positions
    assert len(set(new_nazgul)) == 2, "Nazgûl should not stack"


@pytest.mark.skip(reason="Not implemented")
def test_hobbit_can_move_onto_nazgul_square_for_capture():
    """Hobbits and Nazgûl CAN overlap (that's how captures work)"""
    hobbits = [(9, 10)]
    nazgul = [(10, 10)]
    rivendell = (19, 19)

    # Hobbit moving toward Rivendell will pass through Nazgûl
    # This should be ALLOWED (capture detection happens after movement)
    new_hobbits = update_hobbits(hobbits, rivendell, nazgul, width=20, height=20)

    # Movement should happen (even though it leads to capture)
    assert new_hobbits[0] != (9, 10), "Hobbit should be able to move"
