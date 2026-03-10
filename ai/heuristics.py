from game.state import KalahaState


def eval_1(state: KalahaState, player_id: int) -> float:
    """
    Evaluation Function 1: Pure store difference.
    Mathematical notation:
        E₁(s, p) = stores[p] - stores[1-p]
    Rationale: Identical to Utility at terminal states. Good baseline.
    Ignores positional advantages and future capture potential.
    """
    return float(state.stores[player_id] - state.stores[1 - player_id])


def eval_2(state: KalahaState, player_id: int) -> float:
    """
    Evaluation Function 2: Weighted store + pit seeds.
    Mathematical notation:
        E₂(s, p) = 10·(stores[p] - stores[1-p]) + (Σpits[p] - Σpits[1-p])
    Rationale: Seeds in pits will eventually reach the store (through sowing),
    but are worth less than already-stored seeds because they can be captured.
    Weight ratio 10:1 reflects that stored seeds are secure while pit seeds are vulnerable.
    """
    opp = 1 - player_id
    store_diff = state.stores[player_id] - state.stores[opp]
    pit_diff = sum(state.pits[player_id]) - sum(state.pits[opp])
    return 10.0 * store_diff + pit_diff


def eval_3(state: KalahaState, player_id: int) -> float:
    """
    Evaluation Function 3: Full positional evaluation with tactical features.
    Mathematical notation:
        E₃(s, p) = 10·S_diff + P_diff + 5·T_p + 0.3·C_p
    where:
        - S_diff = stores[p] - stores[1-p]
        - P_diff = Σpits[p] - Σpits[1-p]
        - T_p = extra turn potential (count of pits at correct distance)
        - C_p = capture potential (opponent seeds opposite empty pits)
    Rationale:
        - Store difference (weight 10): Most important — secured points
        - Pit difference (weight 1): Future potential
        - Extra turn bonus (weight 5): Tactical advantage of consecutive moves
        - Capture potential (weight 0.3): Structural weakness, not immediate
    """
    opp = 1 - player_id

    # Core material evaluation
    store_diff = state.stores[player_id] - state.stores[opp]
    pit_diff = sum(state.pits[player_id]) - sum(state.pits[opp])

    # Extra turn bonus: count pits that would land last seed in own store
    extra_turn_bonus = 0
    if state.current_player == player_id:
        for i in range(6):
            seeds = state.pits[player_id][i]
            distance_to_store = 6 - i
            if seeds > 0 and seeds == distance_to_store:
                extra_turn_bonus += 1

    # Capture potential: opponent seeds exposed opposite your empty pits
    # This is a structural weakness indicator, not an immediate threat
    capture_potential = sum(
        state.pits[opp][5 - i]
        for i in range(6)
        if state.pits[player_id][i] == 0 and state.pits[opp][5 - i] > 0
    )

    return 10.0 * store_diff + pit_diff + 5.0 * extra_turn_bonus + 0.3 * capture_potential


# Registry of evaluation functions for easy selection
EVAL_FUNCTIONS = {
    "eval_1": eval_1,
    "eval_2": eval_2,
    "eval_3": eval_3,
}
