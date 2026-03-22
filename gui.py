"""Tkinter GUI for playing Kalaha against the AI. Run with: python gui.py"""

import tkinter as tk
from tkinter import font as tkfont
import threading

from game.engine import get_initial_state, player, actions, result, terminal_test
from game.state import KalahaState
from ai.alpha_beta import best_move

# Layout constants
W, H         = 820, 380
PIT_R        = 38
STORE_W      = 80
STORE_H      = 160
PAD          = 30
PIT_Y_TOP    = 100
PIT_Y_BOT    = 260
STORE_Y      = 170
PIT_SPACING  = 100

# Colour palette
BG           = "#1e1e2e"
PIT_FILL     = "#313244"
PIT_HOVER    = "#45475a"
PIT_ACTIVE   = "#89b4fa"
STORE_FILL   = "#45475a"
TEXT_PRIMARY = "#cdd6f4"
TEXT_DIM     = "#6c7086"
SEED_TEXT    = "#cdd6f4"
P0_COLOR     = "#a6e3a1"
P1_COLOR     = "#f38ba8"
OUTLINE      = "#585b70"
WIN_COLOR    = "#f9e2af"


def pit_x(pit_index: int) -> int:
    """Returns the x-centre of a pit on the canvas."""
    left_edge = STORE_W + PAD * 2 + 20
    return left_edge + pit_index * PIT_SPACING


class KalahaGUI:
    def __init__(self, root: tk.Tk, ai_depth: int = 8):
        self.root = root
        self.root.title("Kalaha")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.ai_depth = ai_depth
        self.state: KalahaState = get_initial_state()
        self.ai_player = 1
        self.ai_thinking = False
        self.hover_pit = None

        self.font_big   = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.font_med   = tkfont.Font(family="Helvetica", size=13)
        self.font_small = tkfont.Font(family="Helvetica", size=10)

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.status_var = tk.StringVar(value="Your turn — click a green pit")
        status = tk.Label(root, textvariable=self.status_var,
                          bg=BG, fg=TEXT_PRIMARY, font=self.font_med, pady=6)
        status.pack(fill=tk.X)

        btn = tk.Button(root, text="New game", command=self.restart,
                        bg="#313244", fg=TEXT_PRIMARY, activebackground=PIT_HOVER,
                        activeforeground=TEXT_PRIMARY, relief=tk.FLAT,
                        font=self.font_med, padx=16, pady=4, cursor="hand2")
        btn.pack(pady=(0, 10))

        self.canvas.bind("<Motion>",    self._on_mouse_move)
        self.canvas.bind("<Leave>",     self._on_mouse_leave)
        self.canvas.bind("<Button-1>",  self._on_click)

        self.draw()

    def draw(self):
        """Redraws the entire board."""
        self.canvas.delete("all")
        self._draw_stores()
        self._draw_pits()
        self._draw_labels()

    def _draw_stores(self):
        self._draw_store(PAD, STORE_Y - STORE_H // 2,
                         self.state.stores[0], P0_COLOR)
        x1 = W - PAD - STORE_W
        self._draw_store(x1, STORE_Y - STORE_H // 2,
                         self.state.stores[1], P1_COLOR)

    def _draw_store(self, x, y, seeds, color):
        self.canvas.create_rectangle(x, y, x + STORE_W, y + STORE_H,
                                     fill=STORE_FILL, outline=color, width=2)
        self.canvas.create_text(x + STORE_W // 2, y + STORE_H // 2,
                                text=str(seeds), fill=color, font=self.font_big)

    def _draw_pits(self):
        legal = actions(self.state) if not self.ai_thinking else []
        current = player(self.state)
        is_human_turn = (current != self.ai_player) and not terminal_test(self.state)

        for i in range(6):
            cx = pit_x(i)

            # Player 0 pits (bottom)
            seeds0 = self.state.pits[0][i]
            can_click = (i in legal) and is_human_turn
            is_hover  = (self.hover_pit == i) and can_click

            fill0 = PIT_ACTIVE if can_click else PIT_FILL
            if is_hover:
                fill0 = PIT_HOVER
            outline0 = P0_COLOR if can_click else OUTLINE

            self.canvas.create_oval(cx - PIT_R, PIT_Y_BOT - PIT_R,
                                    cx + PIT_R, PIT_Y_BOT + PIT_R,
                                    fill=fill0, outline=outline0, width=2)
            self.canvas.create_text(cx, PIT_Y_BOT, text=str(seeds0),
                                    fill=SEED_TEXT, font=self.font_big)
            if can_click:
                self.canvas.create_text(cx, PIT_Y_BOT + PIT_R + 14,
                                        text=str(i), fill=P0_COLOR,
                                        font=self.font_small)

            # Player 1 pits (top, mirrored)
            mirror = 5 - i
            seeds1 = self.state.pits[1][mirror]
            self.canvas.create_oval(cx - PIT_R, PIT_Y_TOP - PIT_R,
                                    cx + PIT_R, PIT_Y_TOP + PIT_R,
                                    fill=PIT_FILL, outline=OUTLINE, width=1)
            self.canvas.create_text(cx, PIT_Y_TOP, text=str(seeds1),
                                    fill=SEED_TEXT, font=self.font_big)

    def _draw_labels(self):
        self.canvas.create_text(PAD + STORE_W // 2, STORE_Y - STORE_H // 2 - 14,
                                text="You (P0)", fill=P0_COLOR, font=self.font_small)
        self.canvas.create_text(W - PAD - STORE_W // 2,
                                STORE_Y - STORE_H // 2 - 14,
                                text="AI (P1)", fill=P1_COLOR, font=self.font_small)
        self.canvas.create_text(pit_x(0) - 10, PIT_Y_TOP,
                                text="AI →", fill=TEXT_DIM,
                                font=self.font_small, anchor=tk.E)
        self.canvas.create_text(pit_x(0) - 10, PIT_Y_BOT,
                                text="You →", fill=TEXT_DIM,
                                font=self.font_small, anchor=tk.E)

        if terminal_test(self.state):
            s0, s1 = self.state.stores
            if s0 > s1:
                msg, col = "You win! 🎉", P0_COLOR
            elif s1 > s0:
                msg, col = "AI wins!", P1_COLOR
            else:
                msg, col = "Draw!", WIN_COLOR
            self.canvas.create_text(W // 2, H // 2, text=msg,
                                    fill=col, font=self.font_big)

    def _pit_at(self, x, y) -> int | None:
        """Returns pit index if click is inside a Player-0 pit circle, else None."""
        for i in range(6):
            cx = pit_x(i)
            if (x - cx) ** 2 + (y - PIT_Y_BOT) ** 2 <= PIT_R ** 2:
                return i
        return None

    def _on_mouse_move(self, event):
        pit = self._pit_at(event.x, event.y)
        if pit != self.hover_pit:
            self.hover_pit = pit
            self.draw()
            if pit is not None and pit in actions(self.state):
                self.canvas.configure(cursor="hand2")
            else:
                self.canvas.configure(cursor="")

    def _on_mouse_leave(self, event):
        self.hover_pit = None
        self.canvas.configure(cursor="")
        self.draw()

    def _on_click(self, event):
        if self.ai_thinking or terminal_test(self.state):
            return
        if player(self.state) == self.ai_player:
            return
        pit = self._pit_at(event.x, event.y)
        if pit is None or pit not in actions(self.state):
            return
        self._apply_move(pit)

    def _apply_move(self, action: int):
        self.state = result(self.state, action)
        self.draw()
        if terminal_test(self.state):
            self._show_result()
            return
        if player(self.state) == self.ai_player:
            self._ai_turn()
        else:
            self.status_var.set("Your turn — click a green pit")

    def _ai_turn(self):
        self.ai_thinking = True
        self.status_var.set("AI is thinking…")
        self.draw()
        threading.Thread(target=self._run_ai, daemon=True).start()

    def _run_ai(self):
        move = best_move(self.state, depth=self.ai_depth)
        self.root.after(0, lambda: self._ai_done(move))

    def _ai_done(self, move: int):
        self.ai_thinking = False
        self.status_var.set(f"AI played pit {move}")
        self._apply_move(move)

    def _show_result(self):
        s0, s1 = self.state.stores
        if s0 > s1:
            msg = f"You win!  {s0} – {s1}"
        elif s1 > s0:
            msg = f"AI wins!  {s0} – {s1}"
        else:
            msg = f"Draw!  {s0} – {s1}"
        self.status_var.set(msg)
        self.draw()

    def restart(self):
        self.state = get_initial_state()
        self.ai_thinking = False
        self.hover_pit = None
        self.status_var.set("Your turn — click a green pit")
        self.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = KalahaGUI(root, ai_depth=8)
    root.mainloop()
