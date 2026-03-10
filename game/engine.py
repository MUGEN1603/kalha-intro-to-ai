from game.state import KalahaState, initial_state
from game.rules import STORE, sow_seeds, check_capture, apply_end_sweep
from typing import List


def player(state: KalahaState) -> int:
    """Returns the player whose turn it is (0 or 1)."""
    return state.current_player


def actions(state: KalahaState) -> List[int]:
    """Returns list of legal moves: indices of non-empty pits on current player's side."""
    p = state.current_player
    return [i for i in range(6) if state.pits[p][i] > 0]


def result(state: KalahaState, action: int) -> KalahaState:
    """
    Apply action and return next state.
    Pipeline order is CRITICAL:
    1. Sow seeds
    2. Turn logic:
       - If last seed in own store -> extra turn (keep current_player)
       - Else -> check capture, then switch current_player
    3. Terminal check -> apply end sweep if needed
    """
    new_state, last_side, last_slot = sow_seeds(state, action)

    if last_slot == STORE:  # Last seed in own store
        # Extra turn: keep current player, no capture check to be completed
        final_state = KalahaState(
            pits=new_state.pits,
            stores=new_state.stores,
            current_player=state.current_player  # SAME player moves again
        )
    else:
        # Normal turn: check capture first, then switch player
        captured_state = check_capture(new_state, last_side, last_slot)
        final_state = KalahaState(
            pits=captured_state.pits,
            stores=captured_state.stores,
            current_player=1 - state.current_player  # SWITCH player
        )

    # Terminal check after every move
    if terminal_test(final_state):
        return apply_end_sweep(final_state)

    return final_state


def terminal_test(state: KalahaState) -> bool:
    """Game ends when either player has no seeds left on their side."""
    return sum(state.pits[0]) == 0 or sum(state.pits[1]) == 0


def utility(state: KalahaState, p: int) -> int:
    """
    Zero-sum utility: player p's advantage over opponent.
    Utility(s,0) + Utility(s,1) = 0 always holds.
    """
    return state.stores[p] - state.stores[1 - p]


def get_initial_state() -> KalahaState:
    """Returns the standard starting position."""
    return initial_state()
