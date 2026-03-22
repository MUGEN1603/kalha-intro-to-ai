"""Benchmarking suite: depth comparison, eval comparison, AI vs random, symmetry, and timing."""

import time
import random
from interface.cli import run_silent_game
from game.engine import get_initial_state, player, actions, result, terminal_test
from ai.alpha_beta import best_move
from ai.heuristics import eval_1, eval_2, eval_3


def depth_comparison(depths=[4, 6, 8], games_per_pair=10):
    """Tests whether deeper search depth consistently wins against shallower depth."""
    print("=" * 60)
    print("EXPERIMENT 1: DEPTH COMPARISON")
    print("=" * 60)
    print(f"{'Matchup':<20} {'Wins (deep)':<12} {'Draws':<8} {'Win Rate':<10}")
    print("-" * 50)

    results = {}
    for d_high in depths[1:]:
        d_low = d_high - 2
        wins_high = 0
        draws = 0

        for _ in range(games_per_pair):
            winner, moves, _ = run_silent_game(depth0=d_high, depth1=d_low)
            if winner == 0:
                wins_high += 1
            elif winner == -1:
                draws += 1

        win_rate = wins_high / games_per_pair
        results[f"d{d_high}_vs_d{d_low}"] = win_rate
        print(f"d{d_high} vs d{d_low}          {wins_high}/{games_per_pair}          {draws:<8} {win_rate:.0%}")

    print()
    return results


def eval_comparison(games_per_pair=10):
    """Compares evaluation functions head-to-head at the same search depth."""
    print("=" * 60)
    print("EXPERIMENT 2: EVALUATION FUNCTION COMPARISON (depth=8)")
    print("=" * 60)
    print(f"{'Matchup':<25} {'P0 Wins':<10} {'Draws':<8} {'P0 Win Rate':<12}")
    print("-" * 55)

    pairs = [
        ("eval_3 vs eval_1", eval_3, eval_1),
        ("eval_3 vs eval_2", eval_3, eval_2),
        ("eval_2 vs eval_1", eval_2, eval_1),
    ]

    results = {}
    for label, ev0, ev1 in pairs:
        wins = 0
        draws = 0

        for _ in range(games_per_pair):
            winner, _, _ = run_silent_game(depth0=8, depth1=8, eval_fn0=ev0, eval_fn1=ev1)
            if winner == 0:
                wins += 1
            elif winner == -1:
                draws += 1

        win_rate = wins / games_per_pair
        results[label] = win_rate
        print(f"{label:<25} {wins}/{games_per_pair}        {draws:<8} {win_rate:.0%}")

    print()
    return results


def ai_vs_random(games=20, ai_depth=8):
    """Measures the AI's win rate against a random player, alternating sides for fairness."""
    print("=" * 60)
    print(f"EXPERIMENT 3: AI (depth={ai_depth}) vs RANDOM PLAYER")
    print("=" * 60)

    ai_wins = 0
    random_wins = 0
    draws = 0
    total_score_diff = 0

    for g in range(games):
        state = get_initial_state()
        ai_player = g % 2

        while not terminal_test(state):
            current = player(state)
            legal = actions(state)
            if not legal:
                break
            if current == ai_player:
                move = best_move(state, depth=ai_depth)
            else:
                move = random.choice(legal)
            state = result(state, move)

        score_diff = state.stores[ai_player] - state.stores[1 - ai_player]
        total_score_diff += score_diff
        if score_diff > 0:
            ai_wins += 1
        elif score_diff < 0:
            random_wins += 1
        else:
            draws += 1

    print(f"  AI wins:     {ai_wins}/{games} ({ai_wins/games:.0%})")
    print(f"  Random wins: {random_wins}/{games} ({random_wins/games:.0%})")
    print(f"  Draws:       {draws}/{games}")
    print(f"  Avg score diff (AI perspective): {total_score_diff/games:+.1f}")
    print()
    return {"ai_win_rate": ai_wins / games, "avg_score_diff": total_score_diff / games}


def symmetry_test(games=10, depth=8):
    """Checks whether going first (P0) gives a significant advantage."""
    print("=" * 60)
    print(f"EXPERIMENT 4: FIRST-PLAYER ADVANTAGE (depth={depth})")
    print("=" * 60)

    p0_wins = 0
    p1_wins = 0
    draws = 0

    for _ in range(games):
        winner, _, _ = run_silent_game(depth0=depth, depth1=depth)
        if winner == 0:
            p0_wins += 1
        elif winner == 1:
            p1_wins += 1
        else:
            draws += 1

    print(f"  Player 0 (first) wins: {p0_wins}/{games}")
    print(f"  Player 1 (second) wins: {p1_wins}/{games}")
    print(f"  Draws: {draws}/{games}")
    print()
    return {"p0_win_rate": p0_wins / games, "p1_win_rate": p1_wins / games}


def timing_benchmark(depths=[4, 6, 8]):
    """Measures average and max per-move computation time at different depths."""
    print("=" * 60)
    print("EXPERIMENT 5: PER-MOVE TIMING")
    print("=" * 60)
    print(f"{'Depth':<10} {'Avg (ms)':<12} {'Max (ms)':<12} {'Moves measured':<16}")
    print("-" * 50)

    for depth in depths:
        state = get_initial_state()
        times = []
        moves_done = 0

        while not terminal_test(state) and moves_done < 20:
            legal = actions(state)
            if not legal:
                break
            start = time.time()
            move = best_move(state, depth=depth)
            elapsed = time.time() - start
            times.append(elapsed)
            state = result(state, move)
            moves_done += 1

        avg_ms = (sum(times) / len(times)) * 1000 if times else 0
        max_ms = max(times) * 1000 if times else 0
        print(f"d={depth:<7} {avg_ms:<12.1f} {max_ms:<12.1f} {len(times)}")

    print()


if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║           KALAHA AI — BENCHMARK SUITE                   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    depth_results = depth_comparison()
    eval_results = eval_comparison()
    random_results = ai_vs_random(games=20)
    sym_results = symmetry_test(games=10)
    timing_benchmark()

    print("=" * 60)
    print("ALL BENCHMARKS COMPLETE")
    print("=" * 60)
    print(f"  Depth results:    {depth_results}")
    print(f"  Eval results:     {eval_results}")
    print(f"  AI vs Random:     {random_results}")
    print(f"  Symmetry:         {sym_results}")
