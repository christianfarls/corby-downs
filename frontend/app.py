# frontend/app.py

from flask import Flask, render_template, redirect, url_for, request
from horse_race.horse_race import GameState, Suit

app = Flask(__name__)

# We'll define suit names in a list to pass to the templates.
SUIT_NAMES = ["Clubs", "Diamonds", "Hearts", "Spades"]

# One shared GameState for demonstration.
game_state = GameState()

@app.route("/")
def index():
    """ Main page: show positions, deck size, last card flipped, etc. """
    # If the game is finished, go to game_over
    if game_state.is_finished():
        return redirect(url_for("game_over"))

    # Check if next side card is ready to be flipped
    if game_state.check_for_side_card_flip():
        return redirect(url_for("declare_side_card"))

    # Build enumerated suits data: [(0, "Clubs"), (1, "Diamonds"), ...]
    suits_data = list(enumerate(SUIT_NAMES))

    # Also build enumerated data for revealed side cards
    revealed_data = list(enumerate(game_state.revealed_side_cards))

    context = {
        "suits_data": suits_data,  # for listing horse positions
        "revealed_data": revealed_data,
        "positions": game_state.horse_positions,
        "deck_size": len(game_state.deck),
        "last_card": game_state.last_flipped,
    }
    return render_template("index.html", **context)

@app.route("/flip_card")
def flip_card():
    """ Flip the top card from the deck and move that horse forward. """
    game_state.flip_card()
    # Then redirect back to index, which might lead to side-card declaration if needed.
    return redirect(url_for("index"))

@app.route("/declare_side_card", methods=["GET", "POST"])
def declare_side_card():
    """
    Ask the user: "Which suit is this side card?"
    If POST, set that side card's suit and move backward.
    """
    # If the game is finished or no side card to reveal, go back to index
    if game_state.is_finished() or game_state.next_side_card_index >= 5:
        return redirect(url_for("index"))

    # If POST, user picked a suit
    if request.method == "POST":
        chosen_suit = request.form.get("suit")
        if chosen_suit is not None:
            suit_value = int(chosen_suit)
            game_state.declare_side_card(suit_value)
        return redirect(url_for("index"))

    # GET request: show a form with radio buttons for suits
    suits_data = list(enumerate(SUIT_NAMES))  # for the radio inputs
    side_card_index = game_state.next_side_card_index

    return render_template("declare_side_card.html",
                           suits_data=suits_data,
                           side_card_index=side_card_index)

@app.route("/game_over")
def game_over():
    """ Show final positions and revealed side cards. """
    suits_data = list(enumerate(SUIT_NAMES))
    revealed_data = list(enumerate(game_state.revealed_side_cards))

    context = {
        "suits_data": suits_data,
        "revealed_data": revealed_data,
        "positions": game_state.horse_positions,
    }
    return render_template("game_over.html", **context)

if __name__ == "__main__":
    app.run(debug=True)
