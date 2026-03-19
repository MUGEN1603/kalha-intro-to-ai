"""
engine.py — Kalaha Game Engine
================================
This file is the public API of the game. The AI and interface layers
call ONLY these functions. It ties together state.py and rules.py.

Game flow for one move:
    Step 1: Player picks a pit       → actions() gives legal choices
    Step 2: Sow seeds                → rules.sow_seeds()
    Step 3: Check for extra turn     → Rule 3: last seed in store?
    Step 4: Check for capture        → Rule 4: last seed in empty pit?
    Step 5: Switch player            → unless extra turn
    Step 6: Check if game is over    → Rule 5: end sweep if needed
"""

from game.state import KalahaState, initial_state
from game.rules import STORE, sow_seeds, check_capture, apply_end_sweep
from typing import List


def get_initial_state() -> KalahaState:
    """
    Rule 1: The game starts with 4 seeds in each pit, 0 in each store.
    Player 0 goes first.
    """
    return initial_state()


def player(state: KalahaState) -> int:
    """Returns whose turn it is: 0 or 1."""
    return state.current_player


def actions(state: KalahaState) -> List[int]:
    """
    A player can only pick a pit that has seeds in it.
    Returns a list of pit indices (0-5) that are non-empty.
    Example: [0, 1, 3, 5] means pits 2 and 4 are empty.
    """
    p = state.current_player
    return [i for i in range(6) if state.pits[p][i] > 0]


def result(state: KalahaState, action: int) -> KalahaState:
    """
    Apply one move and return the next game state.
    This follows the game rules in order:

        Step 1: Sow the seeds (Rule 1 + Rule 2)
        Step 2: Did the last seed land in your store?
                YES → Rule 3: Extra turn (same player goes again)
                NO  → Rule 4: Check capture, then switch player
        Step 3: Is the game over?
                YES → Rule 5: End sweep (collect remaining seeds)
                NO  → Continue playing
    """
    # Step 1: Sow seeds from the chosen pit
    new_state, last_side, last_slot = sow_seeds(state, action)

    # Step 2: Determine what happens after sowing
    if last_slot == STORE:
        # Rule 3: Last seed landed in own store → EXTRA TURN
        # The same player gets to move again
        final_state = KalahaState(
            pits=new_state.pits,
            stores=new_state.stores,
            current_player=state.current_player    # keep same player
        )
    else:
        # Rule 4: Check if capture applies
        captured_state = check_capture(new_state, last_side, last_slot)

        # Normal turn ends: switch to the other player
        final_state = KalahaState(
            pits=captured_state.pits,
            stores=captured_state.stores,
            current_player=1 - state.current_player   # switch player
        )

    # Step 3: Check if the game just ended
    if terminal_test(final_state):
        # Rule 5: One side is empty → sweep remaining seeds
        return apply_end_sweep(final_state)

    return final_state


def terminal_test(state: KalahaState) -> bool:
    """
    The game ends when EITHER player's side has no seeds left.
    Example: if all of Player 0's pits are [0,0,0,0,0,0] → game over.
    """
    return sum(state.pits[0]) == 0 or sum(state.pits[1]) == 0


def utility(state: KalahaState, p: int) -> int:
    """
    The final score from player p's perspective.
    Score = my store − opponent's store.

    Positive = winning, negative = losing, zero = draw.
    This is zero-sum: utility(s,0) + utility(s,1) = 0 always.
    """
    return state.stores[p] - state.stores[1 - p]
