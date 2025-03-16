# horse_race/simulate.py

import random
from typing import List
from horse_race.game_state import GameState, Suit

def simulate_one_future(initial_state: GameState) -> int:
    """
    Simulate one random future from the given state,
    including side-card threshold flips.
    Any side card that is still None in the real game
    is randomly assigned a suit for the simulation.

    Returns the suit (index 0..3) that finishes LAST.
    """

    # 1) Clone so we don't mutate the real state
    state = initial_state.clone()

    # 2) For each side card that is None, pick a random suit so we can fully simulate
    for i, side_card_suit in enumerate(state.side_cards):
        if side_card_suit is None:
            possible_suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
            state.side_cards[i] = random.choice(possible_suits)

    # 3) Build a local deck from deck_suit_counts
    sim_deck = []
    for suit_id in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES):
        sim_deck.extend([suit_id] * state.deck_suit_counts[suit_id])
    random.shuffle(sim_deck)

    # 4) Flip cards until finished or deck empty
    for suit in sim_deck:
        if state.is_finished():
            break
        state.move_forward(suit)
        state.deck_suit_counts[suit] -= 1

        # Now replicate threshold flips automatically (no user input in simulation)
        # If all horses meet threshold, flip the side card (which is now known in the sim).
        while state.next_side_card_index < 5:
            threshold = state.next_side_card_index + 1
            if all(pos >= threshold for pos in state.horse_positions):
                flipped_suit = state.side_cards[state.next_side_card_index]
                state.move_backward(flipped_suit)
                state.revealed_side_cards[state.next_side_card_index] = flipped_suit
                state.next_side_card_index += 1
            else:
                break

    # 5) Determine last place: lowest final position -> random tie break
    positions = state.horse_positions
    min_pos = min(positions)
    candidates = [i for i, pos in enumerate(positions) if pos == min_pos]
    loser = random.choice(candidates)
    return loser


def simulate_many(initial_state: GameState, num_simulations: int = 10000) -> List[float]:
    """
    Run many simulations from the given state,
    returning a 4-element list of probabilities that each suit is LAST.
    """
    lose_counts = [0, 0, 0, 0]
    for _ in range(num_simulations):
        loser = simulate_one_future(initial_state)
        lose_counts[loser] += 1

    total = sum(lose_counts)
    lose_probs = [c / total for c in lose_counts]
    return lose_probs
