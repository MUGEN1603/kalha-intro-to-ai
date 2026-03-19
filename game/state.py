from dataclasses import dataclass
from typing import Tuple

#Defining the state of the game using a dataclass. We have 12 pits (6 for each player) and 2 stores (1 for each player). The current_player field indicates whose turn it is (0 or 1).
@dataclass(frozen=True)
class KalahaState:
    pits: Tuple[Tuple[int, ...], Tuple[int, ...]]  # pits[player][pit_index]
    stores: Tuple[int, int]                         # stores[player]
    current_player: int                             # 0 or 1


def initial_state() -> KalahaState:
    #rule 1.b "Start with 4 seeds in each of all the pits, and 0 seeds in each store"
    return KalahaState(
        pits=((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4)),
        #Explained: pits=(("P1", "P2", "P3", "P4", "P5", "P6"), ("P7", "P8", "P9", "P10", "P11", "P12")),
        stores=(0, 0),
        #Explained: Stores=("S1", "S2")
        current_player=KalahaState.current_player
    )
