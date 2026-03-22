"""Public API for the Kalaha game — ties together state.py and rules.py."""

from game.state import KalahaState, initial_state
from game.rules import STORE, sow_seeds, check_capture, apply_end_sweep
from typing import List


def get_initial_state() -> KalahaState:
    """Returns the starting game state: 4 seeds per pit, empty stores, P0 goes first."""
    return initial_state()


def player(state: KalahaState) -> int:
    """Returns whose turn it is (0 or 1)."""
    return state.current_player


def actions(state: KalahaState) -> List[int]:
    """Returns list of legal pit indices (0-5) that contain seeds."""
    p = state.current_player
    return [i for i in range(6) if state.pits[p][i] > 0]


def result(state: KalahaState, action: int) -> KalahaState:
    """Applies one move and returns the resulting state, handling sowing, extra turns, captures, and end-sweep."""
    # Sow the seeds
    new_state, last_side, last_slot = sow_seeds(state, action)

    if last_slot == STORE:
        # Last seed in own store → extra turn
        final_state = KalahaState(
            pits=new_state.pits,
            stores=new_state.stores,
            current_player=state.current_player
        )
    else:
        # Check capture, then switch player
        captured_state = check_capture(new_state, last_side, last_slot)
        final_state = KalahaState(
            pits=captured_state.pits,
            stores=captured_state.stores,
            current_player=1 - state.current_player
        )

    # If one side is now empty, sweep remaining seeds
    if terminal_test(final_state):
        return apply_end_sweep(final_state)

    return final_state


def terminal_test(state: KalahaState) -> bool:
    """Returns True if either player's side has no seeds left."""
    return sum(state.pits[0]) == 0 or sum(state.pits[1]) == 0


def utility(state: KalahaState, p: int) -> int:
    """Returns the score difference from player p's perspective (zero-sum)."""
    return state.stores[p] - state.stores[1 - p]
