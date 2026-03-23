# Kalaha AI — DTU 02180 Spring 2026

AI player for Kalaha (Mancala) using H-Minimax with Alpha-Beta Pruning. This guide provides step-by-step instructions on how to set up the project, run the game via CLI, and execute tests and benchmarks on both Mac and Windows.

## 🚀 Prerequisites

Before you begin, ensure you have Python installed on your system. This project requires **Python 3.11** or higher.
- Verify your installation by running `python --version` or `python3 --version` in your terminal or command prompt.

---

## 🛠️ Installation & Setup

First, navigate to the project directory in your terminal/command prompt:
```bash
cd kalaha-ai
```

### For Mac/Linux

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```
2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### For Windows

1. **Create a virtual environment:**
   ```cmd
   python -m venv venv
   ```
2. **Activate the virtual environment:**
   - Command Prompt (cmd):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

---

## 🎮 Playing the Game (CLI)
## if just python does not run try python3 then your command (mac issues ) 

You can play a game of Kalaha against the implementation of the AI directly from your terminal.

To start the game, run:
```bash
python -m interface.cli
```

- **Player 0** (You): Located at the bottom of the board.
- **Player 1** (AI): Located at the top of the board. The AI uses H-Minimax with Alpha-Beta Pruning (default search depth is 8).

Follow the on-screen prompts to input the number of the pit you wish to sow from.

---

## 📊 Running Benchmarks

Benchmarks are used to evaluate the AI's performance, comparing different search depths and evaluation functions.

To run the predefined benchmark experiments, execute:
```bash
python -m benchmarks.experiments
```

### Custom Benchmarks (Python Script)
If you wish to run specific comparisons manually, you can import and use the functions in your own scripts:
```python
from benchmarks.experiments import depth_comparison, eval_comparison

# Compare how the AI performs at different search depths
depth_comparison(depths=[4, 6, 8], games_per_pair=10)

# Compare the performance of different evaluation functions
eval_comparison(games_per_pair=10)
```

---

## 🧪 Running Tests

The project uses `pytest` for unit and integration testing. Ensure your virtual environment is activated before running these commands.

1. **Run all tests:**
   ```bash
   pytest tests/ -v
   ```

2. **Run specific test files:**
   ```bash
   # Test only game rules
   pytest tests/test_rules.py -v
   
   # Test only AI logic
   pytest tests/test_ai.py -v
   ```

3. **Run tests with coverage report:**
   To see how much of the code is covered by tests:
   ```bash
   pytest tests/ --cov=game --cov=ai
   ```

---

## 📁 Project Structure

```text
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

---

## 🤖 Algorithm

**H-Minimax with Alpha-Beta Pruning**:
- Default search depth: 8 plies
- Default evaluation: eval_3 (weighted store + positional features)
- Guaranteed optimal play within search horizon

### Evaluation Functions

| Function | Formula | Description |
|----------|---------|-------------|
| eval_1 | `stores[p] - stores[1-p]` | Pure store difference |
| eval_2 | `10·S_diff + P_diff` | Weighted store + pit seeds |
| eval_3 | `10·S_diff + P_diff + 5·T + 0.3·C` | Full positional evaluation |

---

## 📜 Game Rules

Standard Kalaha (Mancala):
- 6 pits per player, 4 seeds per pit initially (48 seeds total)
- Sow counter-clockwise, skip opponent's store
- **Extra turn** if last seed lands in own store
- **Capture** when landing in empty pit opposite non-empty pit
- Game ends when one player's side is empty
- Winner has most seeds in store (need ≥25 to win)
