"""Implements the core rules of Kalaha: sowing, capture, and end-sweep."""

from game.state import KalahaState
from typing import Tuple, List

STORE = -1  # sentinel value to distinguish the store from pits (0-5)


def opposite_pit(pit_index: int) -> int:
    """Returns the facing pit index (pit 0 faces pit 5, etc.)."""
    return 5 - pit_index


def build_sowing_path(player: int, pit_index: int) -> List[Tuple[int, int]]:
    """Builds the 13-position sowing path: own pits, own store, opponent pits (skipping opponent store)."""
    opponent = 1 - player

    your_pits_after  = [(player, i) for i in range(pit_index + 1, 6)]
    your_store       = [(player, STORE)]
    opponents_pits   = [(opponent, i) for i in range(6)]
    your_pits_before = [(player, i) for i in range(pit_index + 1)]

    return your_pits_after + your_store + opponents_pits + your_pits_before


def sow_seeds(state: KalahaState, pit_index: int) -> Tuple[KalahaState, int, int]:
    """Picks up seeds from the chosen pit and sows them one-by-one; returns (new_state, last_side, last_slot)."""
    player = state.current_player

    pits = [list(state.pits[0]), list(state.pits[1])]
    stores = list(state.stores)

    seeds_in_hand = pits[player][pit_index]
    pits[player][pit_index] = 0

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
        current_player=state.current_player
    )
    return new_state, last_side, last_slot


def check_capture(state: KalahaState, last_side: int, last_slot: int) -> KalahaState:
    """If the last seed landed in an empty own pit with seeds opposite, capture both into your store."""
    player = state.current_player
    opponent = 1 - player

    if last_side != player or last_slot == STORE:
        return state
    if state.pits[player][last_slot] != 1:
        return state

    opp_pit = opposite_pit(last_slot)
    if state.pits[opponent][opp_pit] == 0:
        return state

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


def apply_end_sweep(state: KalahaState) -> KalahaState:
    """When one side is empty, each player collects their remaining pit seeds into their store."""
    stores = list(state.stores)
    stores[0] += sum(state.pits[0])
    stores[1] += sum(state.pits[1])

    return KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=tuple(stores),
        current_player=state.current_player
    )
