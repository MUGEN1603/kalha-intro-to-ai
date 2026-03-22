"""Tests for AI: alpha-beta correctness, best_move behaviour, eval functions, and move ordering."""

import pytest
from game.engine import get_initial_state, actions, result, terminal_test, utility
from game.state import KalahaState
from ai.minimax import pure_minimax
from ai.alpha_beta import h_minimax_alpha_beta, best_move, _order_moves
from ai.heuristics import eval_1, eval_2, eval_3


def test_alpha_beta_equals_minimax():
    """Alpha-beta must return the same value as pure minimax on a small state."""
    state = KalahaState(
        pits=((1, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0)),
        stores=(20, 20), current_player=0
    )
    mm = pure_minimax(state, maximizing_player_id=0)
    ab = h_minimax_alpha_beta(state, depth=10, alpha=float('-inf'), beta=float('inf'), maximizing_player_id=0)
    assert mm == ab


def test_alpha_beta_equals_minimax_player1():
    """Alpha-beta correctness when Player 1 is the maximizer."""
    state = KalahaState(
        pits=((0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0)),
        stores=(22, 20), current_player=1
    )
    mm = pure_minimax(state, maximizing_player_id=1)
    ab = h_minimax_alpha_beta(state, depth=10, alpha=float('-inf'), beta=float('inf'), maximizing_player_id=1)
    assert mm == ab


def test_alpha_beta_equals_minimax_more_seeds():
    """Alpha-beta correctness on a slightly larger near-terminal state."""
    state = KalahaState(
        pits=((2, 1, 0, 0, 0, 0), (0, 1, 1, 0, 0, 0)),
        stores=(20, 23), current_player=0
    )
    mm = pure_minimax(state, maximizing_player_id=0)
    ab = h_minimax_alpha_beta(state, depth=15, alpha=float('-inf'), beta=float('inf'), maximizing_player_id=0)
    assert mm == ab


def test_best_move_returns_legal():
    """best_move must always return a legal pit index."""
    state = get_initial_state()
    assert best_move(state, depth=4) in actions(state)


def test_best_move_near_terminal():
    """AI returns a legal move in a near-terminal position."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 2), (0, 0, 0, 0, 0, 1)),
        stores=(22, 23), current_player=0
    )
    assert best_move(state, depth=6) in actions(state)


def test_best_move_takes_winning_capture():
    """AI should pick the capture move that wins the game."""
    state = KalahaState(
        pits=((0, 0, 1, 0, 0, 0), (0, 0, 5, 0, 0, 0)),
        stores=(20, 22), current_player=0
    )
    assert best_move(state, depth=6) == 2


def test_best_move_player1():
    """AI works correctly when playing as Player 1."""
    state = KalahaState(
        pits=((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=1
    )
    assert best_move(state, depth=4) in actions(state)


def test_terminal_utility():
    """eval_1 matches utility at terminal states."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=(25, 23), current_player=0
    )
    assert terminal_test(state)
    assert eval_1(state, 0) == utility(state, 0)


def test_eval_symmetry():
    """eval_1 is antisymmetric: eval_1(s,0) == -eval_1(s,1)."""
    state = KalahaState(
        pits=((3, 2, 1, 0, 4, 5), (1, 2, 3, 4, 5, 0)),
        stores=(10, 13), current_player=0
    )
    assert eval_1(state, 0) == -eval_1(state, 1)


def test_eval_functions_agree_terminal():
    """All eval functions agree on terminal states (up to their scaling)."""
    state = KalahaState(
        pits=((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
        stores=(30, 18), current_player=0
    )
    assert eval_1(state, 0) == 12.0
    assert eval_2(state, 0) == 120.0
    assert eval_3(state, 0) == 120.0


def test_move_ordering_prioritises_extra_turn():
    """Move ordering puts extra-turn moves before regular moves."""
    state = KalahaState(
        pits=((4, 0, 0, 0, 0, 1), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0), current_player=0
    )
    assert _order_moves(state, [0, 5])[0] == 5


def test_move_ordering_preserves_set():
    """Move ordering does not add or remove any legal moves."""
    state = get_initial_state()
    legal = actions(state)
    ordered = _order_moves(state, legal)
    assert set(ordered) == set(legal)
    assert len(ordered) == len(legal)


def test_ai_vs_ai_completes():
    """Two AIs can play a full game to completion with correct final scores."""
    state = get_initial_state()
    moves = 0
    while not terminal_test(state) and moves < 200:
        move = best_move(state, depth=4)
        assert move is not None
        state = result(state, move)
        moves += 1
    assert terminal_test(state)
    assert state.stores[0] + state.stores[1] == 48
