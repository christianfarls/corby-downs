# horse_race/__init__.py

from .horse_race import GameState, Suit
from .simulate import simulate_many, simulate_one_future

__all__ = [
    "GameState",
    "Suit",
    "simulate_many",
    "simulate_one_future",
]
