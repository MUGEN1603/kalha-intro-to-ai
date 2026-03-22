"""Three evaluation functions of increasing sophistication for Kalaha."""

from game.state import KalahaState


def eval_1(state: KalahaState, player_id: int) -> float:
    """E1(s,p) = stores[p] - stores[1-p]. Simple store difference."""
    return float(state.stores[player_id] - state.stores[1 - player_id])


def eval_2(state: KalahaState, player_id: int) -> float:
    """E2(s,p) = 10*(store diff) + (pit diff). Weighs stored seeds higher than pit seeds."""
    opp = 1 - player_id
    store_diff = state.stores[player_id] - state.stores[opp]
    pit_diff = sum(state.pits[player_id]) - sum(state.pits[opp])
    return 10.0 * store_diff + pit_diff


def eval_3(state: KalahaState, player_id: int) -> float:
    """E3(s,p) = 10*S_diff + P_diff + 5*extra_turn_bonus + 0.3*capture_potential."""
    opp = 1 - player_id

    store_diff = state.stores[player_id] - state.stores[opp]
    pit_diff = sum(state.pits[player_id]) - sum(state.pits[opp])

    # Count pits whose seed count exactly reaches the store
    extra_turn_bonus = 0
    if state.current_player == player_id:
        for i in range(6):
            seeds = state.pits[player_id][i]
            if seeds > 0 and seeds == 6 - i:
                extra_turn_bonus += 1

    # Sum of opponent seeds sitting opposite our empty pits
    capture_potential = sum(
        state.pits[opp][5 - i]
        for i in range(6)
        if state.pits[player_id][i] == 0 and state.pits[opp][5 - i] > 0
    )

    return 10.0 * store_diff + pit_diff + 5.0 * extra_turn_bonus + 0.3 * capture_potential


EVAL_FUNCTIONS = {
    "eval_1": eval_1,
    "eval_2": eval_2,
    "eval_3": eval_3,
}
