# Kalaha AI — DTU 02180 Spring 2026

AI player for Kalaha (Mancala) using H-Minimax with Alpha-Beta Pruning.

## Installation

Requires Python 3.11 or higher.

```bash
cd kalaha-ai
python3 -m venv venv
source venv/bin/activate   # On Mac/Linux
pip install -r requirements.txt
```

## Usage

### Play Against AI

```bash
python -m interface.cli
```

Default: You are Player 0 (bottom), AI is Player 1 (top) with depth 8 search.

### Run Benchmarks

```python
from benchmarks.experiments import depth_comparison, eval_comparison

# Compare search depths
depth_comparison(depths=[4, 6, 8], games_per_pair=10)

# Compare evaluation functions
eval_comparison(games_per_pair=10)
```

Or run directly:

```bash
python -m benchmarks.experiments
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_rules.py -v
pytest tests/test_ai.py -v

# With coverage report
pytest tests/ --cov=game --cov=ai
```

## Project Structure

```
kalaha-ai/
├── game/           # Game engine (state, rules, public API)
│   ├── state.py    # KalahaState dataclass, initial_state()
│   ├── rules.py    # sow_seeds(), check_capture(), apply_end_sweep()
│   └── engine.py   # PUBLIC API: player(), actions(), result(), etc.
├── ai/             # AI algorithms
│   ├── heuristics.py  # eval_1, eval_2, eval_3
│   ├── minimax.py     # pure_minimax() (testing reference)
│   └── alpha_beta.py  # h_minimax_alpha_beta(), best_move()
├── interface/      # CLI for human play and silent benchmarking
│   └── cli.py
├── benchmarks/     # Experimental evaluation
│   └── experiments.py
├── tests/          # Unit and integration tests
│   ├── test_rules.py
│   └── test_ai.py
├── requirements.txt
└── README.md
```

## Algorithm

**H-Minimax with Alpha-Beta Pruning** (Lecture 5):
- Default search depth: 8 plies
- Default evaluation: eval_3 (weighted store + positional features)
- Guaranteed optimal play within search horizon

### Evaluation Functions

| Function | Formula | Description |
|----------|---------|-------------|
| eval_1 | `stores[p] - stores[1-p]` | Pure store difference |
| eval_2 | `10·S_diff + P_diff` | Weighted store + pit seeds |
| eval_3 | `10·S_diff + P_diff + 5·T + 0.3·C` | Full positional evaluation |

## Game Rules

Standard Kalaha (Mancala):
- 6 pits per player, 4 seeds per pit initially (48 seeds total)
- Sow counter-clockwise, skip opponent's store
- **Extra turn** if last seed lands in own store
- **Capture** when landing in empty pit opposite non-empty pit
- Game ends when one player's side is empty
- Winner has most seeds in store (need ≥25 to win)
