import math
from game.engine import player, actions, result, terminal_test, utility
from game.state import KalahaState
from ai.heuristics import eval_3  # Default evaluation function


def h_minimax_alpha_beta(
    state: KalahaState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player_id: int,
    eval_fn=eval_3
) -> float:
    """
    H-Minimax with Alpha-Beta pruning (Lecture 5).

    Args:
        state: Current game state
        depth: Remaining search depth (decremented each level)
        alpha: Best value MAX can guarantee (-inf initially)
        beta: Best value MIN can guarantee (+inf initially)
        maximizing_player_id: The player who called best_move() — always treated as MAX
        eval_fn: Evaluation function to use at cutoff nodes

    Returns:
        Heuristic value of state for maximizing_player_id
    """
    # Cutoff test: terminal state OR depth exhausted
    if terminal_test(state) or depth == 0:
        if terminal_test(state):
            return float(utility(state, maximizing_player_id))
        return eval_fn(state, maximizing_player_id)

    current_player = player(state)
    available_actions = actions(state)

    if current_player == maximizing_player_id:
        # MAX node: maximize value
        value = float('-inf')
        for action in available_actions:
            child_state = result(state, action)
            child_value = h_minimax_alpha_beta(
                child_state, depth - 1, alpha, beta, maximizing_player_id, eval_fn
            )
            value = max(value, child_value)
            alpha = max(alpha, value)
            # Beta-cut: MIN won't allow this path (has better option higher up)
            if value >= beta:
                break
        return value
    else:
        # MIN node: minimize value
        value = float('inf')
        for action in available_actions:
            child_state = result(state, action)
            child_value = h_minimax_alpha_beta(
                child_state, depth - 1, alpha, beta, maximizing_player_id, eval_fn
            )
            value = min(value, child_value)
            beta = min(beta, value)
            # Alpha-cut: MAX has a better option elsewhere
            if value <= alpha:
                break
        return value


def best_move(state: KalahaState, depth: int = 8, eval_fn=eval_3) -> int:
    """
    Returns the best legal action for the current player using H-Minimax.

    Args:
        state: Current game state
        depth: Search depth in plies (default 8)
        eval_fn: Evaluation function to use

    Returns:
        Pit index (0-5) to sow from

    Important: NEVER hardcode player 0 as MAX. The current player is always MAX
    when they call this function. This is critical for AI vs AI mode.
    """
    max_player = player(state)  # Current player is always MAX
    best_action = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for action in actions(state):
        child_state = result(state, action)
        # Evaluate child from MAX's perspective
        child_value = h_minimax_alpha_beta(
            child_state, depth - 1, alpha, beta, max_player, eval_fn
        )
        if child_value > best_value:
            best_value = child_value
            best_action = action
        alpha = max(alpha, best_value)

    return best_action
