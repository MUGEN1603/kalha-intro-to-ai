"""Command-line interface for playing Kalaha (human vs AI or AI vs AI)."""

from game.engine import get_initial_state, player, actions, result, terminal_test
from ai.alpha_beta import best_move


def display_board(state):
    """Prints the board as ASCII text with pit labels."""
    p1_pits = list(reversed(state.pits[1]))
    p0_pits = list(state.pits[0])

    print()
    print("=" * 56)
    print(f"  [S2={state.stores[1]:2d}]  [P12={p1_pits[0]}, P11={p1_pits[1]}, P10={p1_pits[2]}, P9={p1_pits[3]}, P8={p1_pits[4]}, P7={p1_pits[5]}]           <- Player 1")
    print(f"           [P1={p0_pits[0]},  P2={p0_pits[1]},  P3={p0_pits[2]},  P4={p0_pits[3]}, P5={p0_pits[4]}, P6={p0_pits[5]}]  [S1={state.stores[0]:2d}]  <- Player 0")
    print("=" * 56)


def human_vs_ai(ai_player=1, depth=8):
    """Runs an interactive game where the human plays against the AI."""
    state = get_initial_state()
    human_player = 1 - ai_player
    print("=== KALAHA: Human vs AI ===")
    print(f"You are Player {human_player + 1}, AI is Player {ai_player + 1}")
    print(f"AI search depth: {depth}")

    while not terminal_test(state):
        display_board(state)
        current = player(state)

        if current != ai_player:
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
            print(f"AI (Player {current + 1}) is thinking...")
            move = best_move(state, depth=depth)
            pit_name = f"P{move + 1 + current * 6}"
            print(f"AI plays {pit_name}")

        state = result(state, move)

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
    """Runs an AI vs AI game silently and returns (winner, total_moves, final_state)."""
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
