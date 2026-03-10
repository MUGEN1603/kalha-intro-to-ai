from interface.cli import run_silent_game
from ai.heuristics import eval_1, eval_2, eval_3


def depth_comparison(depths=[4, 6, 8], games_per_pair=10):
    """
    Benchmark: Does deeper search win more often?
    Tests depth d vs depth (d-2) over multiple games.
    Returns win rate for higher depth player.
    """
    print("=== DEPTH COMPARISON EXPERIMENT ===\n")
    results = {}

    for d_high in depths[1:]:
        d_low = d_high - 2
        wins_high = 0

        for game_num in range(games_per_pair):
            # High depth plays as Player 0
            winner, moves, _ = run_silent_game(depth0=d_high, depth1=d_low)
            if winner == 0:
                wins_high += 1

        win_rate = wins_high / games_per_pair
        results[f"d{d_high}_vs_d{d_low}"] = win_rate
        print(f"Depth {d_high} vs Depth {d_low}: {wins_high}/{games_per_pair} wins ({win_rate:.1%})")

    print()
    return results


def eval_comparison(games_per_pair=10):
    """
    Benchmark: Which evaluation function performs best?
    Tests eval functions head-to-head over multiple games.
    """
    print("=== EVALUATION FUNCTION COMPARISON ===\n")

    pairs = [
        ("eval_3_vs_eval_1", eval_3, eval_1),
        ("eval_3_vs_eval_2", eval_3, eval_2),
        ("eval_2_vs_eval_1", eval_2, eval_1),
    ]

    results = {}

    for label, ev0, ev1 in pairs:
        wins = 0

        for game_num in range(games_per_pair):
            winner, _, _ = run_silent_game(
                depth0=8, depth1=8,
                eval_fn0=ev0, eval_fn1=ev1
            )
            if winner == 0:
                wins += 1

        win_rate = wins / games_per_pair
        results[label] = win_rate
        print(f"{label}: {wins}/{games_per_pair} wins ({win_rate:.1%})")

    print()
    return results


if __name__ == "__main__":
    print("Running all benchmarks...\n")
    depth_results = depth_comparison()
    eval_results = eval_comparison()
    print("=== ALL BENCHMARKS COMPLETE ===")
    print(f"Depth results: {depth_results}")
    print(f"Eval results: {eval_results}")
