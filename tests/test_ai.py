import pytest
from game.engine import get_initial_state, actions, terminal_test, utility
from game.state import KalahaState
from ai.minimax import pure_minimax
from ai.alpha_beta import h_minimax_alpha_beta, best_move
from ai.heuristics import eval_1


def test_alpha_beta_equals_minimax():
    """
    Critical test: Alpha-Beta must return IDENTICAL values to pure Minimax.
    Use small near-terminal state to keep computation feasible.
    """
    # Near-terminal state with few seeds
    state = KalahaState(
        pits=((1, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0)),
        stores=(20, 20),
        current_player=0
    )

    mm_value = pure_minimax(state, maximizing_player_id=0)
    ab_value = h_minimax_alpha_beta(
        state, depth=10,
        alpha=float('-inf'), beta=float('inf'),
        maximizing_player_id=0
    )

    assert mm_value == ab_value, f"Minimax={mm_value}, AlphaBeta={ab_value}"


def test_best_move_returns_legal():
    """AI should always return a legal move."""
    state = get_initial_state()
    legal = actions(state)
    move = best_move(state, depth=4)
    assert move in legal, f"AI returned illegal move {move}, legal: {legal}"


def test_terminal_utility():
    """At terminal states, evaluation should match utility."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=(25, 23),
        current_player=0
    )
    assert terminal_test(state)
    assert eval_1(state, 0) == utility(state, 0)


def test_best_move_near_terminal():
    """AI should find winning move in near-terminal state."""
    # Player 0 has only one move left
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 2), (0, 0, 0, 0, 0, 1)),
        stores=(22, 23),
        current_player=0
    )
    move = best_move(state, depth=6)
    legal = actions(state)
    assert move in legal


def test_alpha_beta_equals_minimax_player1():
    """Verify alpha-beta correctness when Player 1 is maximizing."""
    state = KalahaState(
        pits=((0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0)),
        stores=(22, 20),
        current_player=1
    )

    mm_value = pure_minimax(state, maximizing_player_id=1)
    ab_value = h_minimax_alpha_beta(
        state, depth=10,
        alpha=float('-inf'), beta=float('inf'),
        maximizing_player_id=1
    )

    assert mm_value == ab_value, f"Minimax={mm_value}, AlphaBeta={ab_value}"
