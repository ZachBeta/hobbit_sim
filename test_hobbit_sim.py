# test_hobbit_sim.py
from hobbit_sim import move_away_from, move_with_speed, update_hobbits

def test_hobbit_evading_at_south_edge_doesnt_get_stuck():
    """
    Scenario: Hobbit at bottom edge (y=19), Nazgûl approaching from north
    Bug: Hobbit tries to move south (away), hits boundary, doesn't move at all
    Expected: Hobbit should move laterally (east or west) along edge to evade
    """
    # Setup: Hobbit at south edge, Nazgûl to the north
    hobbits = [(10, 19)]  # At south edge
    nazgul = [(10, 15)]   # 4 squares north (within danger distance 6)
    rivendell = (19, 19)  # Goal is east along same edge

    # Move hobbits (should evade)
    new_hobbits = update_hobbits(hobbits, rivendell, nazgul, width=20, height=20)

    # Assert: Hobbit should have moved (not stuck at same position)
    assert new_hobbits[0] != (10, 19), "Hobbit should move when evading at edge"

    # Assert: Hobbit moved laterally toward goal (east), not stuck going south
    assert new_hobbits[0][0] > 10, "Hobbit should move east toward goal"
    assert new_hobbits[0][1] == 19, "Hobbit should stay on south edge"