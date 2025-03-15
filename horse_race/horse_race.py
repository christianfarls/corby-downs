# horse_race/game_state.py

import random
from enum import IntEnum

class Suit(IntEnum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

class GameState:
    def __init__(self):
        # Positions of the 4 horses
        self.horse_positions = [0, 0, 0, 0]

        # A simple deck: 12 clubs, 12 diamonds, 12 hearts, 12 spades
        self.deck_suit_counts = [12, 12, 12, 12]
        self.deck = []
        self._build_deck()

        # Last card flipped
        self.last_flipped = None

        # Side cards (5 total), all initially unknown
        self.side_cards = [None]*5
        self.revealed_side_cards = [None]*5
        self.next_side_card_index = 0

    def _build_deck(self):
        """Constructs the deck from deck_suit_counts, then shuffles."""
        self.deck.clear()
        for suit_id, count in enumerate(self.deck_suit_counts):
            self.deck.extend([Suit(suit_id)] * count)
        random.shuffle(self.deck)

    def flip_card(self):
        """
        Draw one card from the deck, move that horse forward.
        We'll check afterwards if it's time to reveal a side card.
        But we do NOT auto-assign the side card's suit here.
        """
        if not self.deck:
            self.last_flipped = None
            return

        card_suit = self.deck.pop()
        self.move_forward(card_suit)
        self.last_flipped = card_suit
        self.deck_suit_counts[card_suit] -= 1

    def check_for_side_card_flip(self):
        """
        Checks if all horses have reached the threshold for the next side card:
        threshold = next_side_card_index + 1
        If it's time to reveal the next side card, return True so the front-end
        can prompt the user to pick its suit. Otherwise return False.
        """
        if self.next_side_card_index >= 5:
            return False  # no more side cards

        threshold = self.next_side_card_index + 1
        if all(pos >= threshold for pos in self.horse_positions):
            # It's time to reveal the side card with index `self.next_side_card_index`
            return True
        return False

    def declare_side_card(self, suit_value: int):
        """
        The user declares which suit the next side card is.
        We reveal it, move that suit backward, and increment next_side_card_index.
        """
        if self.next_side_card_index >= 5:
            return  # no side card to declare

        declared_suit = Suit(suit_value)
        idx = self.next_side_card_index

        self.side_cards[idx] = declared_suit
        self.revealed_side_cards[idx] = declared_suit

        self.move_backward(declared_suit)
        self.next_side_card_index += 1

    def move_forward(self, suit: Suit):
        self.horse_positions[suit] += 1

    def move_backward(self, suit: Suit):
        self.horse_positions[suit] = max(0, self.horse_positions[suit] - 1)

    def is_finished(self) -> bool:
        """Example: game ends when all horses reach position >= 6."""
        return all(pos >= 6 for pos in self.horse_positions)
