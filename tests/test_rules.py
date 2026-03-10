import pytest
from game.engine import get_initial_state, result, terminal_test, actions
from game.state import KalahaState


def total_seeds(state):
    """Helper: compute total seed count (should always be 48)."""
    return (sum(state.pits[0]) + sum(state.pits[1]) +
            state.stores[0] + state.stores[1])


def test_seed_conservation():
    """Critical invariant: total seeds = 48 always."""
    state = get_initial_state()
    assert total_seeds(state) == 48

    # Simulate 50 moves
    for _ in range(50):
        legal = actions(state)
        if not legal or terminal_test(state):
            break
        state = result(state, legal[0])
        assert total_seeds(state) == 48, f"Conservation violated: {total_seeds(state)}"


def test_initial_state():
    """Verify standard starting position."""
    s = get_initial_state()
    assert s.pits == ((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4))
    assert s.stores == (0, 0)
    assert s.current_player == 0


def test_extra_turn():
    """
    Test Rule 2: Last seed in own store -> extra turn.
    Pit 5 has 1 seed at distance 1 -> sowing lands in store.
    """
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 1), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0),
        current_player=0
    )
    new_state = result(state, 5)
    # Player 0 should move again (extra turn)
    assert new_state.current_player == 0
    assert new_state.stores[0] == 1


def test_capture():
    """
    Test Rule 3: Capture when landing in empty pit opposite non-empty pit.
    P0 pit 2 has 1 seed, will land in pit 3 (currently empty)
    P1 pit 2 (opposite of P0 pit 3 = 5-3) has 5 seeds
    """
    state = KalahaState(
        pits=((0, 0, 1, 0, 0, 0), (4, 4, 5, 4, 4, 4)),
        stores=(0, 0),
        current_player=0
    )
    new_state = result(state, 2)
    # Capture should occur: 1 (landed) + 5 (opposite) = 6 to store
    assert new_state.stores[0] == 6
    assert new_state.pits[0][3] == 0  # Captured pit now empty
    assert new_state.pits[1][2] == 0  # Opposite pit now empty


def test_terminal_detection():
    """Game ends when one player's side is empty."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (4, 4, 4, 4, 4, 4)),
        stores=(20, 4),
        current_player=1
    )
    assert terminal_test(state) == True


def test_seed_conservation_multiple_moves():
    """Extended seed conservation: play many random-ish moves."""
    state = get_initial_state()
    move_count = 0
    while not terminal_test(state) and move_count < 200:
        legal = actions(state)
        if not legal:
            break
        # Pick different moves to explore more states
        move = legal[move_count % len(legal)]
        state = result(state, move)
        assert total_seeds(state) == 48, \
            f"Seed conservation violated at move {move_count}: {total_seeds(state)} seeds"
        move_count += 1


def test_no_legal_moves_on_empty_side():
    """When a player's side is empty, they have no legal moves."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (1, 2, 3, 4, 5, 6)),
        stores=(10, 17),
        current_player=0
    )
    assert actions(state) == []
