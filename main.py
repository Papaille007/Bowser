import html
import json
from pathlib import Path
from typing import Annotated

from dopynion.data_model import (
    CardName,
    CardNameAndHand,
    Game,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)
from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from Strategy import (
    choose_discard,
    choose_trash,
    calculate_money,
    choose_buy,
    choose_action,
    calculate_buys,
    calculate_actions,
)

app = FastAPI()

#####################################################
# Data model for responses
#####################################################


class DopynionResponseBool(BaseModel):
    game_id: str
    decision: bool


class DopynionResponseCardName(BaseModel):
    game_id: str
    decision: CardName


class DopynionResponseStr(BaseModel):
    game_id: str
    decision: str


#####################################################
# Getter for the game identifier
#####################################################


def get_game_id(x_game_id: str = Header(description="ID of the game")) -> str:
    return x_game_id


GameIdDependency = Annotated[str, Depends(get_game_id)]


#####################################################
# Error management
#####################################################


@app.exception_handler(Exception)
def unknown_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    print(exc.__class__.__name__, str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "message": "Oops!",
            "detail": str(exc),
            "name": exc.__class__.__name__,
        },
    )


#####################################################
# Template extra bonus
#####################################################


# The root of the website shows the code of the website
@app.get("/", response_class=HTMLResponse)
def root() -> str:
    header = (
        "<html><head><title>Dopynion template</title></head><body>"
        "<h1>Dopynion documentation</h1>"
        "<h2>API documentation</h2>"
        '<p><a href="/docs">Read the documentation.</a></p>'
        "<h2>Code template</h2>"
        "<p>The code of this website is:</p>"
        "<pre>"
    )
    footer = "</pre></body></html>"
    return header + html.escape(Path(__file__).read_text(encoding="utf-8")) + footer


#####################################################
# The code of the strategy
#####################################################


@app.get("/name")
def name() -> str:
    return "Koopa Dominion"


@app.get("/start_game")
def start_game(game_id: GameIdDependency) -> DopynionResponseStr:
    return DopynionResponseStr(game_id=game_id, decision="OK")


@app.get("/start_turn")
def start_turn(game_id: GameIdDependency) -> DopynionResponseStr:
    return DopynionResponseStr(game_id=game_id, decision="OK")


@app.post("/play")
def play(game: Game, game_id: GameIdDependency) -> DopynionResponseStr:
    # Notre royaume est identifié par le game_id.
    print("GAME :", game)
    # Le premier joueur correspond à notre royaume.
    player = next(player for player in game.players if "Koopa Dominion" in player.name)
    print("PLAYER :", player, flush=True)
    print("HAND :", player.hand, flush=True)

    # Sécurité
    if player.hand is None:
        return DopynionResponseStr(
            game_id=game_id,
            decision="END_TURN",
        )

    # -----------------------------------------
    # 1. PHASE ACTION
    # -----------------------------------------

    actions_remaining = calculate_actions()

    print("ACTIONS :", actions_remaining, flush=True)

    if actions_remaining > 0:
        action = choose_action(player.hand)

        if action.startswith("ACTION"):
            actions_remaining -= 1

        print("ACTION :", action, flush=True)
        print("ACTIONS RESTANTES :", actions_remaining, flush=True)

        return DopynionResponseStr(
            game_id=game_id,
            decision=action,
        )

    # -----------------------------------------
    # 2. PHASE ACHAT
    # -----------------------------------------

    money = calculate_money(player.hand)

    print("MONEY :", money, flush=True)

    buys_remaining = calculate_buys()

    print("BUYS :", buys_remaining, flush=True)

    if buys_remaining > 0:
        decision = choose_buy(money, game.stock)

        if decision.startswith("BUY"):
            buys_remaining -= 1

        print("BUY :", decision, flush=True)
        print("BUYS RESTANTS :", buys_remaining, flush=True)

        return DopynionResponseStr(
            game_id=game_id,
            decision=decision,
        )

    # -----------------------------------------
    # 3. FIN DU TOUR
    # -----------------------------------------

    print("END TURN", flush=True)

    return DopynionResponseStr(
        game_id=game_id,
        decision="END_TURN",
    )


@app.get("/end_game")
def end_game(game_id: GameIdDependency) -> DopynionResponseStr:
    return DopynionResponseStr(game_id=game_id, decision="OK")


@app.post("/confirm_discard_card_from_hand")
async def confirm_discard_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/discard_card_from_hand")
async def discard_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:
    card = choose_discard(decision_input.hand)

    return DopynionResponseCardName(
        game_id=game_id,
        decision=card,
    )


@app.post("/confirm_trash_card_from_hand")
async def confirm_trash_card_from_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/trash_card_from_hand")
async def trash_card_from_hand(
    game_id: GameIdDependency,
    decision_input: Hand,
) -> DopynionResponseCardName:
    card = choose_trash(decision_input.hand)

    return DopynionResponseCardName(game_id=game_id, decision=card)


@app.post("/confirm_discard_deck")
async def confirm_discard_deck(
    game_id: GameIdDependency,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/choose_card_to_receive_in_discard")
async def choose_card_to_receive_in_discard(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post("/choose_card_to_receive_in_deck")
async def choose_card_to_receive_in_deck(
    game_id: GameIdDependency,
    decision_input: PossibleCards,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.possible_cards[0],
    )


@app.post("/skip_card_reception_in_hand")
async def skip_card_reception_in_hand(
    game_id: GameIdDependency,
    _decision_input: CardNameAndHand,
) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post("/trash_money_card_for_better_money_card")
async def trash_money_card_for_better_money_card(
    game_id: GameIdDependency,
    decision_input: MoneyCardsInHand,
) -> DopynionResponseCardName:
    return DopynionResponseCardName(
        game_id=game_id,
        decision=decision_input.money_in_hand[0],
    )
