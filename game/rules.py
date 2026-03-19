"""
rules.py - Implements the 5 rules of Kalaha in the order the game is played.
"""

from game.state import KalahaState
from typing import Tuple, List

STORE = -1  # pits are 0-5, so -1 marks the store


def opposite_pit(pit_index: int) -> int:
    """Pit 0 faces pit 5, pit 1 faces pit 4, pit 2 faces pit 3."""
    return 5 - pit_index


def build_sowing_path(player: int, pit_index: int) -> List[Tuple[int, int]]:
    """
    Builds the ordered list of positions seeds travel through.
    Goes: your pits → your store → opponent's pits → wraps back.
    Skips the opponent's store. Always 13 positions total.
    """
    opponent = 1 - player

    your_pits_after  = [(player, i) for i in range(pit_index + 1, 6)]
    your_store       = [(player, STORE)]
    opponents_pits   = [(opponent, i) for i in range(6)]
    your_pits_before = [(player, i) for i in range(pit_index + 1)]

    return your_pits_after + your_store + opponents_pits + your_pits_before


# ── Rule 1 & 2: Pick up seeds and sow them ──────────────────────────────────

def sow_seeds(state: KalahaState, pit_index: int) -> Tuple[KalahaState, int, int]:
    """
    Rule 1: Pick up all seeds from the chosen pit.
    Rule 2: Drop them one-by-one counter-clockwise around the board.
    Returns (new_state, last_side, last_slot) so engine.py can check rules 3/4.
    """
    player = state.current_player

    # make mutable copies so we can update pits and stores
    pits = [list(state.pits[0]), list(state.pits[1])]
    stores = list(state.stores)

    # pick up seeds
    seeds_in_hand = pits[player][pit_index]
    pits[player][pit_index] = 0

    # drop them one by one
    path = build_sowing_path(player, pit_index)
    last_side, last_slot = player, pit_index

    for i in range(seeds_in_hand):
        side, slot = path[i % len(path)]
        if slot == STORE:
            stores[side] += 1
        else:
            pits[side][slot] += 1
        last_side, last_slot = side, slot

    new_state = KalahaState(
        pits=(tuple(pits[0]), tuple(pits[1])),
        stores=tuple(stores),
        current_player=state.current_player  # engine decides who goes next
    )
    return new_state, last_side, last_slot


# ── Rule 3: Extra turn (handled in engine.py) ───────────────────────────────
# If the last seed lands in your own store, you go again.


# ── Rule 4: Capture ─────────────────────────────────────────────────────────

def check_capture(state: KalahaState, last_side: int, last_slot: int) -> KalahaState:
    """
    Rule 4: If your last seed lands in an empty pit on your side,
    and the opposite pit has seeds, you capture both into your store.
    Three conditions must all be true for capture to happen.
    """
    player = state.current_player
    opponent = 1 - player

    # condition 1: landed on your own side, not in a store
    if last_side != player or last_slot == STORE:
        return state

    # condition 2: that pit was empty before (now has exactly 1)
    if state.pits[player][last_slot] != 1:
        return state

    # condition 3: opposite pit is not empty
    opp_pit = opposite_pit(last_slot)
    if state.pits[opponent][opp_pit] == 0:
        return state

    # all conditions met — do the capture
    pits = [list(state.pits[0]), list(state.pits[1])]
    stores = list(state.stores)

    captured = pits[player][last_slot] + pits[opponent][opp_pit]
    stores[player] += captured
    pits[player][last_slot] = 0
    pits[opponent][opp_pit] = 0

    return KalahaState(
        pits=(tuple(pits[0]), tuple(pits[1])),
        stores=tuple(stores),
        current_player=player
    )


# ── Rule 5: End sweep ─--

def apply_end_sweep(state: KalahaState) -> KalahaState:
    """
    Rule 5: When one side is empty, each player collects
    whatever seeds remain on their side into their own store.
    """
    stores = list(state.stores)
    stores[0] += sum(state.pits[0])
    stores[1] += sum(state.pits[1])

    return KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=tuple(stores),
        current_player=state.current_player
    )
