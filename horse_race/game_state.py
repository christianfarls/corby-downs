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

        # Last card flipped (to show in UI or logs)
        self.last_flipped = None

        # Side cards (5 total). Some might be declared by the user; others remain None
        self.side_cards = [None] * 5
        self.revealed_side_cards = [None] * 5
        self.next_side_card_index = 0

        # Probabilities (chance each suit is last)
        self.probabilities = [0.25, 0.25, 0.25, 0.25]

    def _build_deck(self):
        """Constructs the deck from deck_suit_counts, then shuffles."""
        self.deck.clear()
        for suit_id, count in enumerate(self.deck_suit_counts):
            self.deck.extend([Suit(suit_id)] * count)
        random.shuffle(self.deck)

    def clone(self):
        """
        Return a new GameState that is a deep copy of the data
        so we can simulate without mutating the real state.
        """
        new_state = type(self).__new__(type(self))  # create a blank instance
        # Copy all fields manually:
        new_state.horse_positions = self.horse_positions[:]
        new_state.deck_suit_counts = self.deck_suit_counts[:]
        new_state.deck = self.deck[:]
        new_state.last_flipped = self.last_flipped
        new_state.side_cards = self.side_cards[:]
        new_state.revealed_side_cards = self.revealed_side_cards[:]
        new_state.next_side_card_index = self.next_side_card_index
        new_state.probabilities = self.probabilities[:]
        return new_state

    def flip_card(self):
        """
        Draw one card from the deck, move that horse forward.
        Then run a simulation to update probabilities (optional).
        """
        if not self.deck:
            self.last_flipped = None
            return

        card_suit = self.deck.pop()
        self.move_forward(card_suit)
        self.last_flipped = card_suit
        self.deck_suit_counts[card_suit] -= 1

        # Now check if we reached a threshold where a side card might flip
        # If the side card is None, we can prompt the user to declare it in the Flask route
        # If it's known, we can flip automatically
        # (We do only a partial check here; the full logic might be in the Flask route.)

        # Recompute probabilities via simulation
        from horse_race.simulate import simulate_many
        self.probabilities = simulate_many(self.clone(), num_simulations=3000)
        print("Updated probabilities:", self.probabilities)

    def check_for_side_card_flip(self):
        """
        Called after a horse moves forward (in the real game).
        If all horses have reached the threshold for side card # next_side_card_index,
        we see if the side card is known or not.

        - If side_cards[i] is known, we flip automatically (move that suit backward).
        - If side_cards[i] is None, we need user input => we return True
          (meaning "yes, there's a card to declare").
        """
        while self.next_side_card_index < 5:
            threshold = self.next_side_card_index + 1
            if all(pos >= threshold for pos in self.horse_positions):
                card_suit = self.side_cards[self.next_side_card_index]
                if card_suit is None:
                    # We need the user to declare it
                    return True
                else:
                    # We know the suit => flip automatically
                    self.move_backward(card_suit)
                    self.revealed_side_cards[self.next_side_card_index] = card_suit
                    self.next_side_card_index += 1
            else:
                break
        return False

    def declare_side_card(self, suit_value: int):
        """
        The user declares which suit the next side card is.
        We reveal it, move that suit backward, and increment next_side_card_index.
        """
        if self.next_side_card_index >= 5:
            return  # no more side cards to declare

        from horse_race.simulate import Suit
        declared_suit = Suit(suit_value)

        self.side_cards[self.next_side_card_index] = declared_suit
        self.revealed_side_cards[self.next_side_card_index] = declared_suit

        self.move_backward(declared_suit)
        self.next_side_card_index += 1

    def move_forward(self, suit: Suit):
        self.horse_positions[suit] += 1

    def move_backward(self, suit: Suit):
        self.horse_positions[suit] = max(0, self.horse_positions[suit] - 1)

    def is_finished(self) -> bool:
        """Game ends when all horses are >= 6, but you can customize."""
        return all(pos >= 6 for pos in self.horse_positions)
