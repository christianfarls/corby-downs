# horse_race/main.py

import random
from horse_race import GameState, Suit
from simulate import simulate_many

def main():
    # For reproducibility (optional)
    random.seed(42)

    # 1) Initialize the game state
    # Example: all horses at 0, 12 unseen cards of each suit, 5 unknown side cards
    game_state = GameState()

    # 2) Suppose we've already flipped 3 cards in real life:
    #    hearts, clubs, spades.
    #    So we must update the real game_state accordingly:
    game_state.move_forward(Suit.HEARTS)
    game_state.deck_suit_counts[Suit.HEARTS] -= 1

    game_state.move_forward(Suit.CLUBS)
    game_state.deck_suit_counts[Suit.CLUBS] -= 1

    game_state.move_forward(Suit.SPADES)
    game_state.deck_suit_counts[Suit.SPADES] -= 1

    # 3) Now we want the probability that each suit eventually ends last
    #    from this point forward. So we run many simulations:
    lose_probs = simulate_many(game_state, num_simulations=10000)

    # 4) Print or plot results
    suit_names = ["Clubs", "Diamonds", "Hearts", "Spades"]
    for suit_idx, p_loss in enumerate(lose_probs):
        print(f"{suit_names[suit_idx]} has a {p_loss*100:.2f}% chance to lose.")
        print(f" -> So a {(1 - p_loss)*100:.2f}% chance to *not* lose (i.e. potentially win).")

if __name__ == "__main__":
    main()
