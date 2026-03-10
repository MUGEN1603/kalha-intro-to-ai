from game.engine import player, actions, result, terminal_test, utility
from game.state import KalahaState


def pure_minimax(state: KalahaState, maximizing_player_id: int) -> float:
    """
    Pure (unbounded) Minimax for testing purposes.
    WARNING: Exponentially expensive. Use only on small game trees
    (near-terminal states) to verify alpha-beta correctness.

    Returns:
        Exact minimax value of state for maximizing_player_id
    """
    if terminal_test(state):
        return float(utility(state, maximizing_player_id))

    current_player = player(state)

    child_values = [
        pure_minimax(result(state, action), maximizing_player_id)
        for action in actions(state)
    ]

    if current_player == maximizing_player_id:
        return max(child_values) if child_values else float('-inf')
    else:
        return min(child_values) if child_values else float('inf')
