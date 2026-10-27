import html
import logging
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Annotated

from dopynion.data_model import (
    CardName, CardNameAndHand, Game, Hand, MoneyCardsInHand, PossibleCards,
)
from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from Strategy import (
    choose_discard, choose_trash, calculate_money, choose_buy, choose_action,
    calculate_buys, calculate_actions, get_action_bonuses,
    create_starting_deck, record_purchase, purchase_cost, find_card,
)

app = FastAPI()
logger = logging.getLogger('koopa')
state_lock = RLock()


@dataclass
class GameState:
    deck: dict = field(default_factory=create_starting_deck)
    actions_remaining: int = 1
    buys_remaining: int = 1
    bonus_money: int = 0
    spent_money: int = 0
    phase: str = 'ACTION'


states_by_game: dict[str, GameState] = {}


class DopynionResponseBool(BaseModel):
    game_id: str
    decision: bool


class DopynionResponseCardName(BaseModel):
    game_id: str
    decision: CardName


class DopynionResponseStr(BaseModel):
    game_id: str
    decision: str


def get_game_id(x_game_id: str = Header(description='ID of the game')) -> str:
    return x_game_id


GameIdDependency = Annotated[str, Depends(get_game_id)]


def response(game_id: str, decision: str) -> DopynionResponseStr:
    return DopynionResponseStr(game_id=game_id, decision=decision)


@app.exception_handler(Exception)
def unknown_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception('Unexpected error: %s', exc)
    return JSONResponse(status_code=500, content={
        'message': 'Oops!', 'detail': str(exc), 'name': exc.__class__.__name__,
    })


@app.get('/', response_class=HTMLResponse)
def root() -> str:
    header = ('<html><head><title>Koopa Dominion</title></head><body>'
              '<h1>Koopa Dominion</h1><a href="/docs">API documentation</a><pre>')
    return header + html.escape(Path(__file__).read_text(encoding='utf-8')) + '</pre></body></html>'


@app.get('/name')
def name() -> str:
    return 'KOOPA DOMINION test'


@app.get('/start_game')
def start_game(game_id: GameIdDependency) -> DopynionResponseStr:
    with state_lock:
        states_by_game[game_id] = GameState()
    logger.info('START GAME %s', game_id)
    return response(game_id, 'OK')


@app.get('/start_turn')
def start_turn(game_id: GameIdDependency) -> DopynionResponseStr:
    with state_lock:
        state = states_by_game.setdefault(game_id, GameState())
        state.actions_remaining = calculate_actions()
        state.buys_remaining = calculate_buys()
        state.bonus_money = 0
        state.spent_money = 0
        state.phase = 'ACTION'
    logger.info('START TURN %s', game_id)
    return response(game_id, 'OK')


@app.post('/play')
def play(game: Game, game_id: GameIdDependency) -> DopynionResponseStr:
    with state_lock:
        # The referee exposes only our hand; never rely on a player name.
        visible_players = [p for p in game.players if p.hand is not None]
        if len(visible_players) != 1:
            logger.error('Expected one visible hand, got %s in %s', len(visible_players), game_id)
            return response(game_id, 'END_TURN')
        player = visible_players[0]
        state = states_by_game.setdefault(game_id, GameState())
        hand = player.hand

        if state.phase == 'ACTION' and state.actions_remaining > 0:
            action = choose_action(hand)
            if action is not None and action.startswith('ACTION '):
                card = find_card(action.split(' ', 1)[1])
                if card is not None and hand.quantities.get(card, 0) > 0:
                    extra_actions, extra_buys, extra_money = get_action_bonuses(action)
                    state.actions_remaining += extra_actions - 1
                    state.buys_remaining += extra_buys
                    state.bonus_money += extra_money
                    logger.info('%s %s -> actions=%s buys=%s bonus=%s', game_id, action,
                                state.actions_remaining, state.buys_remaining, state.bonus_money)
                    return response(game_id, action)

        state.phase = 'BUY'
        money = max(0, calculate_money(hand, state.bonus_money) - state.spent_money)
        if state.buys_remaining > 0:
            decision = choose_buy(money, game.stock, state.deck)
            if decision.startswith('BUY '):
                cost = purchase_cost(decision)
                card = find_card(decision.split(' ', 1)[1])
                if (cost is not None and cost <= money and card is not None
                        and game.stock.quantities.get(card, 0) > 0):
                    state.spent_money += cost
                    state.buys_remaining -= 1
                    record_purchase(state.deck, decision)
                    logger.info('%s %s -> money=%s buys=%s', game_id, decision,
                                money - cost, state.buys_remaining)
                    return response(game_id, decision)
                logger.warning('%s unsafe buy %s cost=%s money=%s', game_id, decision, cost, money)
        logger.info('%s END_TURN', game_id)
        return response(game_id, 'END_TURN')


@app.get('/end_game')
def end_game(game_id: GameIdDependency) -> DopynionResponseStr:
    with state_lock:
        states_by_game.pop(game_id, None)
    return response(game_id, 'OK')


@app.post('/confirm_discard_card_from_hand')
async def confirm_discard_card_from_hand(game_id: GameIdDependency, _decision_input: CardNameAndHand) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post('/discard_card_from_hand')
async def discard_card_from_hand(game_id: GameIdDependency, decision_input: Hand) -> DopynionResponseCardName:
    return DopynionResponseCardName(game_id=game_id, decision=choose_discard(decision_input.hand))


@app.post('/confirm_trash_card_from_hand')
async def confirm_trash_card_from_hand(game_id: GameIdDependency, _decision_input: CardNameAndHand) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post('/trash_card_from_hand')
async def trash_card_from_hand(game_id: GameIdDependency, decision_input: Hand) -> DopynionResponseCardName:
    card = choose_trash(decision_input.hand)
    # The referee executes the trash; we update the estimated deck for future buys.
    with state_lock:
        state = states_by_game.get(game_id)
        if state is not None and state.deck.get(card, 0) > 0:
            state.deck[card] -= 1
    return DopynionResponseCardName(game_id=game_id, decision=card)


@app.post('/confirm_discard_deck')
async def confirm_discard_deck(game_id: GameIdDependency) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post('/choose_card_to_receive_in_discard')
async def choose_card_to_receive_in_discard(game_id: GameIdDependency, decision_input: PossibleCards) -> DopynionResponseCardName:
    card = decision_input.possible_cards[0]
    with state_lock:
        state = states_by_game.get(game_id)
        if state is not None:
            state.deck[card] = state.deck.get(card, 0) + 1
    return DopynionResponseCardName(game_id=game_id, decision=card)


@app.post('/choose_card_to_receive_in_deck')
async def choose_card_to_receive_in_deck(game_id: GameIdDependency, decision_input: PossibleCards) -> DopynionResponseCardName:
    card = decision_input.possible_cards[0]
    with state_lock:
        state = states_by_game.get(game_id)
        if state is not None:
            state.deck[card] = state.deck.get(card, 0) + 1
    return DopynionResponseCardName(game_id=game_id, decision=card)


@app.post('/skip_card_reception_in_hand')
async def skip_card_reception_in_hand(game_id: GameIdDependency, _decision_input: CardNameAndHand) -> DopynionResponseBool:
    return DopynionResponseBool(game_id=game_id, decision=True)


@app.post('/trash_money_card_for_better_money_card')
async def trash_money_card_for_better_money_card(game_id: GameIdDependency, decision_input: MoneyCardsInHand) -> DopynionResponseCardName:
    return DopynionResponseCardName(game_id=game_id, decision=decision_input.money_in_hand[0])
