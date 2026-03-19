from game.engine import get_initial_state, player, actions, result, terminal_test
from ai.alpha_beta import best_move


def display_board(state):
    """
    ASCII board visualization.
    Player 1 on top (reversed order), Player 0 on bottom.

    Board Layout:
        [S1]  [p5][p4][p3][p2][p1][p0]        <- Player 1's side
              [p0][p1][p2][p3][p4][p5]  [S0]  <- Player 0's side
    """
    p1_pits = list(reversed(state.pits[1]))
    p0_pits = list(state.pits[0])

    print()
    print("=" * 56)
    print(f"  [S2={state.stores[1]:2d}]  [P12={p1_pits[0]}, P11={p1_pits[1]}, P10={p1_pits[2]}, P9={p1_pits[3]}, P8={p1_pits[4]}, P7={p1_pits[5]}]           <- Player 1")
    print(f"           [P1={p0_pits[0]},  P2={p0_pits[1]},  P3={p0_pits[2]},  P4={p0_pits[3]}, P5={p0_pits[4]}, P6={p0_pits[5]}]  [S1={state.stores[0]:2d}]  <- Player 0")
    print("=" * 56)


def human_vs_ai(ai_player=1, depth=8):
    """
    Interactive human vs AI game.

    Args:
        ai_player: Which player is the AI (0 or 1)
        depth: AI search depth
    """
    state = get_initial_state()
    human_player = 1 - ai_player
    print("=== KALAHA: Human vs AI ===")
    print(f"You are Player {human_player + 1}, AI is Player {ai_player + 1}")
    print(f"AI search depth: {depth}")

    while not terminal_test(state):
        display_board(state)
        current = player(state)

        if current != ai_player:
            # Human turn
            legal = actions(state)
            pit_names = [f"P{i + 1 + current * 6}" for i in legal]
            print(f"Your turn (Player {current + 1}). Legal pits: {pit_names}")
            while True:
                try:
                    pit_input = int(input(f"Choose pit (P{1 + current * 6}-P{6 + current * 6}): "))
                    move = pit_input - 1 - current * 6
                    if move in legal:
                        break
                    print("Illegal move. Try again.")
                except ValueError:
                    print(f"Please enter a number between {1 + current * 6} and {6 + current * 6}.")
        else:
            # AI turn
            print(f"AI (Player {current + 1}) is thinking...")
            move = best_move(state, depth=depth)
            pit_name = f"P{move + 1 + current * 6}"
            print(f"AI plays {pit_name}")

        state = result(state, move)

    # Game over
    display_board(state)
    if state.stores[0] > state.stores[1]:
        winner = 0
    elif state.stores[1] > state.stores[0]:
        winner = 1
    else:
        winner = -1

    print(f"\nFinal Score -- Player 1: {state.stores[0]}, Player 2: {state.stores[1]}")
    print("Draw!" if winner == -1 else f"Player {winner + 1} wins!")


def run_silent_game(depth0=8, depth1=8, eval_fn0=None, eval_fn1=None):
    """
    AI vs AI game without output (for benchmarking).

    Args:
        depth0: Search depth for Player 0
        depth1: Search depth for Player 1
        eval_fn0: Evaluation function for Player 0
        eval_fn1: Evaluation function for Player 1

    Returns:
        (winner, total_moves, final_state) where winner is 0, 1, or -1 (draw)
    """
    from ai.heuristics import eval_3

    eval0 = eval_fn0 or eval_3
    eval1 = eval_fn1 or eval_3

    state = get_initial_state()
    moves = 0

    while not terminal_test(state):
        current = player(state)
        depth = depth0 if current == 0 else depth1
        eval_fn = eval0 if current == 0 else eval1
        move = best_move(state, depth=depth, eval_fn=eval_fn)
        state = result(state, move)
        moves += 1

    if state.stores[0] > state.stores[1]:
        winner = 0
    elif state.stores[1] > state.stores[0]:
        winner = 1
    else:
        winner = -1

    return winner, moves, state


if __name__ == "__main__":
    print("=== KALAHA AI ===")
    print("You are Player 1 (bottom)")
    print("AI is Player 2 (top)")
    print()
    human_vs_ai()
