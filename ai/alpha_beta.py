"""Alpha-Beta pruning with move ordering, transposition table, and endgame solver."""

import math
from game.engine import player, actions, result, terminal_test, utility
from game.state import KalahaState
from ai.heuristics import eval_3

# Transposition table: caches evaluated positions to avoid redundant computation.
_transposition_table: dict = {}


def _move_priority(state: KalahaState, pit_index: int) -> int:
    """Scores a move for ordering: 3=extra turn, 2=capture, 1=large pit, 0=default."""
    p = state.current_player
    seeds = state.pits[p][pit_index]
    if seeds == 0:
        return -1

    distance_to_store = 6 - pit_index
    if seeds == distance_to_store:
        return 3

    if seeds < distance_to_store:
        landing_pit = pit_index + seeds
        if landing_pit < 6:
            opp = 1 - p
            if state.pits[p][landing_pit] == 0 and state.pits[opp][5 - landing_pit] > 0:
                return 2

    return 1 if seeds > 3 else 0


def _order_moves(state: KalahaState, legal_moves: list) -> list:
    """Sorts legal moves by priority (best-first) without changing which moves are legal."""
    return sorted(legal_moves, key=lambda m: _move_priority(state, m), reverse=True)


def h_minimax_alpha_beta(
    state: KalahaState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player_id: int,
    eval_fn=eval_3
) -> float:
    """H-Minimax with alpha-beta pruning, move ordering, and transposition table."""
    if terminal_test(state):
        return float(utility(state, maximizing_player_id))
    if depth == 0:
        return eval_fn(state, maximizing_player_id)

    # Check transposition table for previously computed result
    tt_key = (state, maximizing_player_id)
    if tt_key in _transposition_table:
        cached_depth, cached_score = _transposition_table[tt_key]
        if cached_depth >= depth:
            return cached_score

    current_player = player(state)
    ordered_actions = _order_moves(state, actions(state))

    if current_player == maximizing_player_id:
        value = float('-inf')
        for action in ordered_actions:
            child_value = h_minimax_alpha_beta(
                result(state, action), depth - 1, alpha, beta, maximizing_player_id, eval_fn
            )
            value = max(value, child_value)
            alpha = max(alpha, value)
            if value >= beta:
                break  # beta cutoff
        _transposition_table[tt_key] = (depth, value)
        return value
    else:
        value = float('inf')
        for action in ordered_actions:
            child_value = h_minimax_alpha_beta(
                result(state, action), depth - 1, alpha, beta, maximizing_player_id, eval_fn
            )
            value = min(value, child_value)
            beta = min(beta, value)
            if value <= alpha:
                break  # alpha cutoff
        _transposition_table[tt_key] = (depth, value)
        return value


def best_move(state: KalahaState, depth: int = 8, eval_fn=eval_3) -> int:
    """Returns the best pit index (0-5) for the current player using alpha-beta search."""
    global _transposition_table
    _transposition_table = {}

    # Endgame solver: search exhaustively when few seeds remain
    total_pit_seeds = sum(state.pits[0]) + sum(state.pits[1])
    if total_pit_seeds <= 10:
        depth = max(depth, 20)

    max_player = player(state)
    best_action = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for action in _order_moves(state, actions(state)):
        child_value = h_minimax_alpha_beta(
            result(state, action), depth - 1, alpha, beta, max_player, eval_fn
        )
        if child_value > best_value:
            best_value = child_value
            best_action = action
        alpha = max(alpha, best_value)

    return best_action
