"""Tests for game rules: seed conservation, extra turns, captures, end-sweep, and edge cases."""

import pytest
from game.engine import get_initial_state, result, terminal_test, actions, utility
from game.state import KalahaState


def total_seeds(state):
    """Returns total seed count across all pits and stores."""
    return sum(state.pits[0]) + sum(state.pits[1]) + state.stores[0] + state.stores[1]


def test_seed_conservation():
    """Total seeds must stay at 48 across 50 moves."""
    state = get_initial_state()
    assert total_seeds(state) == 48
    for _ in range(50):
        legal = actions(state)
        if not legal or terminal_test(state):
            break
        state = result(state, legal[0])
        assert total_seeds(state) == 48


def test_seed_conservation_multiple_moves():
    """Seed conservation holds over many moves with varying move choices."""
    state = get_initial_state()
    move_count = 0
    while not terminal_test(state) and move_count < 200:
        legal = actions(state)
        if not legal:
            break
        state = result(state, legal[move_count % len(legal)])
        assert total_seeds(state) == 48
        move_count += 1


def test_zero_sum_invariant():
    """utility(s,0) + utility(s,1) must equal 0 at any terminal state."""
    state = get_initial_state()
    move_count = 0
    while not terminal_test(state) and move_count < 200:
        legal = actions(state)
        if not legal:
            break
        state = result(state, legal[move_count % len(legal)])
        move_count += 1
    if terminal_test(state):
        assert utility(state, 0) + utility(state, 1) == 0


def test_initial_state():
    """Starting position has 4 seeds per pit, empty stores, and P0's turn."""
    s = get_initial_state()
    assert s.pits == ((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4))
    assert s.stores == (0, 0)
    assert s.current_player == 0


def test_initial_state_all_moves_legal():
    """All 6 pits are non-empty at start so all moves are legal."""
    s = get_initial_state()
    assert actions(s) == [0, 1, 2, 3, 4, 5]


def test_extra_turn():
    """Sowing pit 5 with 1 seed lands in store, giving an extra turn."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 1), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    new_state = result(state, 5)
    assert new_state.current_player == 0
    assert new_state.stores[0] == 1


def test_extra_turn_from_various_pits():
    """Extra turn works from pit 0 (6 seeds) and pit 3 (3 seeds)."""
    state = KalahaState(
        pits=((6, 0, 0, 0, 0, 0), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    assert result(state, 0).current_player == 0

    state2 = KalahaState(
        pits=((0, 0, 0, 3, 0, 0), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    assert result(state2, 3).current_player == 0


def test_no_extra_turn_when_not_landing_in_store():
    """3 seeds from pit 4 overshoots the store, so the turn switches."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 3, 0), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    assert result(state, 4).current_player == 1


def test_capture():
    """Landing in empty pit 3 captures it and the 5 seeds opposite."""
    state = KalahaState(
        pits=((0, 0, 1, 0, 0, 0), (4, 4, 5, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    new_state = result(state, 2)
    assert new_state.stores[0] == 6
    assert new_state.pits[0][3] == 0
    assert new_state.pits[1][2] == 0


def test_no_capture_on_opponent_side():
    """Capture does not happen when the last seed lands on the opponent's side."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 3, 0), (0, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    new_state = result(state, 4)
    assert new_state.stores[0] == 1


def test_no_capture_when_opposite_empty():
    """No capture when the opposite pit has 0 seeds."""
    state = KalahaState(
        pits=((0, 1, 0, 0, 0, 0), (5, 0, 0, 0, 0, 0)),
        stores=(20, 20), current_player=0
    )
    new_state = result(state, 1)
    assert new_state.stores[0] == 20
    assert new_state.current_player == 1


def test_no_capture_when_landing_pit_not_empty():
    """No capture when the landing pit already had seeds (count > 1 after sowing)."""
    state = KalahaState(
        pits=((0, 1, 3, 0, 0, 0), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    new_state = result(state, 1)
    assert new_state.pits[0][2] == 4
    assert new_state.stores[0] == 0


def test_terminal_detection():
    """Game is terminal when one side has no seeds."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (4, 4, 4, 4, 4, 4)),
        stores=(20, 4), current_player=1
    )
    assert terminal_test(state) == True


def test_not_terminal_when_both_sides_have_seeds():
    """Game is not over when both sides still have seeds."""
    state = KalahaState(
        pits=((1, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1)),
        stores=(23, 23), current_player=0
    )
    assert terminal_test(state) == False


def test_end_sweep_scores():
    """End-sweep correctly adds remaining seeds to each player's store."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 1), (0, 0, 0, 0, 0, 5)),
        stores=(21, 21), current_player=0
    )
    new_state = result(state, 5)
    assert terminal_test(new_state)
    assert new_state.stores[0] == 22
    assert new_state.stores[1] == 26
    assert total_seeds(new_state) == 48


def test_wrap_around_sowing():
    """14 seeds from pit 0 wrap around the board and seed conservation holds."""
    state = KalahaState(
        pits=((14, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=(17, 17), current_player=0
    )
    assert total_seeds(result(state, 0)) == 48


def test_no_legal_moves_on_empty_side():
    """A player with all empty pits has no legal moves."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (1, 2, 3, 4, 5, 6)),
        stores=(10, 17), current_player=0
    )
    assert actions(state) == []


def test_partial_legal_moves():
    """Only pits with seeds are returned as legal moves."""
    state = KalahaState(
        pits=((0, 3, 0, 2, 0, 1), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    assert actions(state) == [1, 3, 5]


def test_player1_extra_turn():
    """Extra turn works the same way for Player 1."""
    state = KalahaState(
        pits=((4, 4, 4, 4, 4, 4), (0, 0, 0, 0, 0, 1)),
        stores=(0, 0), current_player=1
    )
    new_state = result(state, 5)
    assert new_state.current_player == 1
    assert new_state.stores[1] == 1


def test_player1_capture():
    """Capture works the same way for Player 1."""
    state = KalahaState(
        pits=((4, 4, 5, 4, 4, 4), (0, 0, 1, 0, 0, 0)),
        stores=(0, 0), current_player=1
    )
    new_state = result(state, 2)
    assert new_state.stores[1] == 6
    assert new_state.pits[1][3] == 0
    assert new_state.pits[0][2] == 0
