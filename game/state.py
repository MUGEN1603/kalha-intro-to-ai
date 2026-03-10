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
        stores=(0, 0),
        current_player=0
    )
