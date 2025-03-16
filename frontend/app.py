# frontend/app.py

from flask import Flask, render_template, redirect, url_for, request
from horse_race.game_state import GameState, Suit

app = Flask(__name__)

SUIT_NAMES = ["Clubs", "Diamonds", "Hearts", "Spades"]

# Single shared game state for demo
game_state = GameState()

@app.route("/")
def index():
    """ Main page: show positions, deck size, last card flipped, etc. """
    # If the game is finished, show game_over
    if game_state.is_finished():
        return redirect(url_for("game_over"))

    # Check if we need to reveal a side card
    if game_state.check_for_side_card_flip():
        # That means side_cards[next_side_card_index] is None => user must pick
        return redirect(url_for("declare_side_card"))

    # Build enumerated suits data (for template loops)
    suits_data = list(enumerate(SUIT_NAMES))
    revealed_data = list(enumerate(game_state.revealed_side_cards))

    context = {
        "suits_data": suits_data,
        "revealed_data": revealed_data,
        "positions": game_state.horse_positions,
        "deck_size": len(game_state.deck),
        "last_card": game_state.last_flipped,
        "probabilities": game_state.probabilities,  # if you want to display them
    }
    return render_template("index.html", **context)

@app.route("/flip_card")
def flip_card():
    """ Flip the top card from the deck, move that horse, recalc probabilities. """
    game_state.flip_card()
    return redirect(url_for("index"))

@app.route("/declare_side_card", methods=["GET", "POST"])
def declare_side_card():
    """
    If POST, user picks which suit the side card is.
    If GET, show a form to pick from 4 suits.
    """
    if game_state.is_finished() or game_state.next_side_card_index >= 5:
        return redirect(url_for("index"))

    if request.method == "POST":
        chosen_suit_str = request.form.get("suit")
        if chosen_suit_str is not None:
            suit_value = int(chosen_suit_str)
            game_state.declare_side_card(suit_value)
        return redirect(url_for("index"))
    else:
        suits_data = list(enumerate(SUIT_NAMES))
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
        "probabilities": game_state.probabilities,
    }
    return render_template("game_over.html", **context)

@app.route("/new_game")
def new_game():
    global game_state
    game_state = GameState()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
