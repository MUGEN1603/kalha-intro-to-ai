from game.state import KalahaState
from typing import Tuple

STORE = -1  # Special marker meaning "store" position


def sow_seeds(state: KalahaState, pit_index: int) -> Tuple[KalahaState, int, int]:
    """
    Sow seeds from pit_index for current_player.

    Returns:
        (new_state_after_sow, last_side, last_slot)
        last_slot == -1 means last seed landed in own store (extra turn trigger).
    """
    p = state.current_player
    opp = 1 - p

    # Create mutable copies (convert back to tuples at the end)
    pits = [list(state.pits[0]), list(state.pits[1])]
    stores = list(state.stores)

    seeds = pits[p][pit_index]
    pits[p][pit_index] = 0  # Pick up all seeds

    # Sowing order: own pits ascending -> own store -> opponent pits 0..5
    # SKIP opponent's store
    positions = (
        [(p, i) for i in range(pit_index + 1, 6)] +   # Own remaining pits
        [(p, STORE)] +                                  # Own store (-1 = store marker)
        [(opp, i) for i in range(6)]                    # Opponent's pits
    )

    # If seeds > positions in one cycle, we need to wrap. Build full cycle:
    # After opponent's pits, we go back to own pits 0..pit_index
    # (then own store, opponent pits, etc.)
    full_cycle = (
        [(p, i) for i in range(pit_index + 1, 6)] +
        [(p, STORE)] +
        [(opp, i) for i in range(6)] +
        [(p, i) for i in range(pit_index + 1)]
    )
    # Use full_cycle for wrapping (13 positions: skip opponent store)

    # Cycle through positions if more seeds than positions
    idx = 0
    last_side, last_slot = p, pit_index
    while seeds > 0:
        side, slot = positions[idx % len(positions)] if idx < len(positions) else full_cycle[idx % len(full_cycle)]
        if slot == STORE:  # Store
            stores[side] += 1
        else:  # Pit
            pits[side][slot] += 1
        last_side, last_slot = side, slot
        seeds -= 1
        idx += 1

    new_state = KalahaState(
        pits=(tuple(pits[0]), tuple(pits[1])),
        stores=tuple(stores),
        current_player=state.current_player  # Not changed yet
    )
    return new_state, last_side, last_slot


def check_capture(state: KalahaState, last_side: int, last_slot: int) -> KalahaState:
    """
    Apply capture rule if all 3 conditions hold:
    1. Last seed landed on current player's own side
    2. That pit now has exactly 1 seed (was empty before landing)
    3. Opposite pit is non-empty
    """
    p = state.current_player

    # Condition 1: Last seed on own side (not opponent's, not store)
    if last_side != p or last_slot == STORE:
        return state

    # Condition 2: Pit now has exactly 1 seed
    if state.pits[p][last_slot] != 1:
        return state

    # Condition 3: Opposite pit non-empty
    opp_pit = 5 - last_slot
    if state.pits[1 - p][opp_pit] == 0:
        return state

    # Perform capture
    pits = [list(state.pits[0]), list(state.pits[1])]
    stores = list(state.stores)

    captured = pits[p][last_slot] + pits[1 - p][opp_pit]
    stores[p] += captured
    pits[p][last_slot] = 0
    pits[1 - p][opp_pit] = 0

    return KalahaState(
        pits=(tuple(pits[0]), tuple(pits[1])),
        stores=tuple(stores),
        current_player=p
    )


def apply_end_sweep(state: KalahaState) -> KalahaState:
    """
    When terminal condition met: each player sweeps all remaining
    seeds on their side into their own store. All pits become 0.
    """
    stores = list(state.stores)
    stores[0] += sum(state.pits[0])
    stores[1] += sum(state.pits[1])

    return KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=tuple(stores),
        current_player=state.current_player
    )
