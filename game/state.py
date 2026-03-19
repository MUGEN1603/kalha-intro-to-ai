from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class KalahaState:
    """
    Immutable game state representation.
    frozen=True makes states hashable (useful for transposition tables).
    """
    pits: Tuple[Tuple[int, ...], Tuple[int, ...]]  # pits[player][pit_index]
    stores: Tuple[int, int]                         # stores[player]
    current_player: int                             # 0 or 1


def initial_state() -> KalahaState:
    """Returns the standard starting position for Kalaha."""
    return KalahaState(
        pits=((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4)),
        #Explained: pits=(("P1", "P2", "P3", "P4", "P5", "P6"), ("P7", "P8", "P9", "P10", "P11", "P12")),
        stores=(0, 0),
        #Explained: Stores=("S1", "S2")
        current_player=0
    )
