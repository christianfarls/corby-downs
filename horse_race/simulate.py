# horse_race/simulate.py

import random
from typing import List
from horse_race import GameState, Suit

def simulate_one_future(initial_state: GameState) -> int:
    """
    Simulate one random future outcome from the given initial state.
    Returns the suit (integer 0–3) that finishes LAST (the loser).
    """

    # 1. Clone the state so we don't mutate the original
    state = initial_state.clone()

    # 2. We must decide how to handle side cards that are still unknown.
    #    For each unknown side card, pick a random suit from among the deck suits
    #    or from the entire set {0,1,2,3}, depending on your game rules.
    #    For simplicity, let's pick from {CLUBS, DIAMONDS, HEARTS, SPADES} uniformly:
    for i, side_card_suit in enumerate(state.side_cards):
        if side_card_suit is None:
            possible_suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
            choice = random.choice(possible_suits)
            state.side_cards[i] = choice

    # 3. Create a list (deck) of the remaining unseen suits (based on state.deck_suit_counts).
    deck = []
    for suit in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES):
        deck.extend([suit] * state.deck_suit_counts[suit])

    # 4. Shuffle the deck
    random.shuffle(deck)

    # 5. Simulate flipping all cards until all horses have finished
    for suit in deck:
        if state.all_finished():
            break

        # Move the horse corresponding to 'suit'
        state.move_forward(suit)
        # We've "used" this card, so decrement deck count
        state.decrement_deck_count(suit)

    # If some horses still haven't finished after running out of deck, they remain where they are
    # Now determine who is the last to cross 6
    # We'll keep flipping "empty" until all finish, though typically you'd end if the deck is done

    # Determine finishing times by order
    # "Time" in a simple sense: how many total steps did it take each horse to reach 6?
    # We can store those as the deck is processed. Or we can just see who is behind at the end.
    # We'll define "last horse" as the one with the minimum position. If there's a tie, pick one tie at random:
    positions = state.horse_positions
    min_pos = min(positions)
    # If multiple suits are tied for last, pick one at random for this simulation:
    candidates = [s for s, pos in enumerate(positions) if pos == min_pos]
    loser = random.choice(candidates)
    return loser

def simulate_many(initial_state: GameState, num_simulations: int = 10000) -> List[float]:
    """
    Perform many simulations from the given state.
    Returns a list of size 4, where result[suit] = probability that suit ends up LAST.
    """
    lose_counts = [0, 0, 0, 0]

    for _ in range(num_simulations):
        loser = simulate_one_future(initial_state)
        lose_counts[loser] += 1

    # Convert to probabilities
    total = sum(lose_counts)
    lose_probabilities = [count / total for count in lose_counts]
    return lose_probabilities
