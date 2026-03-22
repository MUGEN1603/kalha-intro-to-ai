from dataclasses import dataclass
from typing import Tuple

# Immutable game state: 6 pits per player, 1 store each, and whose turn it is.
@dataclass(frozen=True)
class KalahaState:
    pits: Tuple[Tuple[int, ...], Tuple[int, ...]]
    stores: Tuple[int, int]
    current_player: int


def initial_state() -> KalahaState:
    """Returns the standard starting position: 4 seeds per pit, empty stores, P0 first."""
    return KalahaState(
        pits=((4, 4, 4, 4, 4, 4), (4, 4, 4, 4, 4, 4)),
        stores=(0, 0),
        current_player=0
    )
