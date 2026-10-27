from dopynion.data_model import CardName


def find_card(name: str):
    """Retrouve une carte à partir de son nom ou de sa valeur."""

    normalized_name = name.lower().replace("_", "").replace(" ", "")

    for card in CardName:
        enum_name = card.name.lower().replace("_", "").replace(" ", "")
        enum_value = str(card.value).lower().replace("_", "").replace(" ", "")

        if normalized_name in (enum_name, enum_value):
            return card

    return None


def card_count(cards, name: str) -> int:
    """Renvoie le nombre d'exemplaires d'une carte."""

    card = find_card(name)

    if card is None:
        return 0

    return (
        cards.quantities.get(card, 0)
        if hasattr(cards, "quantities")
        else cards.get(card, 0)
    )


def create_starting_deck() -> dict:
    """Crée le deck de départ d'une partie."""

    return {
        CardName.COPPER: 7,
        CardName.ESTATE: 3,
    }


def record_purchase(deck: dict, decision: str) -> None:

    if decision.startswith('BUY '):
        card = find_card(decision.split(' ', 1)[1])
        if card is not None:
            deck[card] = deck.get(card, 0) + 1


def calculate_money(hand, bonus_money: int = 0) -> int:
    """Calcule l'argent disponible : trésors en main + bonus d'actions."""

    money = 0
    money += hand.quantities.get(CardName.COPPER, 0) * 1
    money += hand.quantities.get(CardName.SILVER, 0) * 2
    money += hand.quantities.get(CardName.GOLD, 0) * 3

    return money + bonus_money


# Base prices for supported kingdom cards. Dynamic price effects are not represented.
CARD_COSTS = {
    'copper': 0, 'silver': 3, 'gold': 6,
    'estate': 2, 'duchy': 5, 'province': 8,
    'village': 3, 'smithy': 4, 'festival': 5,
    'laboratory': 5, 'market': 5, 'woodcutter': 3,
    'bandit': 5, 'witch': 5, 'councilroom': 5,
    'militia': 4, 'bureaucrat': 4, 'farmingvillage': 4,
}


def purchase_cost(decision: str):
    if not decision.startswith('BUY '):
        return None
    card = find_card(decision.split(' ', 1)[1])
    return CARD_COSTS.get(str(card.value).lower()) if card is not None else None



def choose_buy(money: int, stock, deck=None) -> str:
    deck = deck if deck is not None else {}

    def available(name):
        return card_count(stock, name) > 0

    def owned(name):
        return card_count(deck, name)

    def buy(name):
        card = find_card(name)
        return f'BUY {card.value}' if card is not None else 'END_TURN'

    provinces_left = card_count(stock, 'province')
    if money >= 8 and available('province'):
        return buy('province')
    if provinces_left <= 3 and money >= 5 and available('duchy'):
        return buy('duchy')
    if money >= 6 and available('gold'):
        return buy('gold')
    if money >= 5 and available('bandit') and owned('bandit') < 2:
        return buy('bandit')
    if 3 <= money < 5 and available('silver'):
        return buy('silver')
    if money >= 5 and available('witch') and owned('witch') < 2:
        return buy('witch')
    if money >= 5 and available('laboratory') and owned('laboratory') < 2:
        return buy('laboratory')
    if money >= 5 and available('councilroom') and owned('councilroom') < 1:
        return buy('councilroom')
    if money >= 4 and available('militia') and owned('militia') < 2:
        return buy('militia')
    if money >= 4 and available('bureaucrat') and owned('bureaucrat') < 2:
        return buy('bureaucrat')
    if money >= 4 and available('smithy') and owned('smithy') < 2:
        return buy('smithy')
    terminal_actions = sum(owned(name) for name in ('smithy', 'councilroom', 'witch', 'militia', 'bureaucrat', 'bandit', 'woodcutter'))
    if money >= 3 and available('village') and owned('village') < 2 and terminal_actions > owned('village'):
        return buy('village')
    if money >= 5 and available('festival') and owned('festival') < 2:
        return buy('festival')
    if money >= 5 and available('market') and owned('market') < 2:
        return buy('market')
    if money >= 4 and available('farmingvillage') and owned('farmingvillage') < 2:
        return buy('farmingvillage')
    if money >= 3 and available('woodcutter') and owned('woodcutter') < 1:
        return buy('woodcutter')
    if money >= 3 and available('silver'):
        return buy('silver')
    if provinces_left <= 2 and money >= 2 and available('estate'):
        return buy('estate')
    return 'END_TURN'



def card_quantity(hand, name: str) -> int:
    """Nombre d'exemplaires d'une carte dans une main."""
    card = find_card(name)
    if card is None:
        return 0
    return hand.quantities.get(card, 0)



def choose_discard(hand):
    for name in ('curse', 'estate', 'copper', 'woodcutter', 'smithy', 'councilroom', 
                 'distantshore', 'hireling', 'witch', 'farmingvillage', 'village', 
                 'festival', 'market', 'laboratory', 'silver', 'gold', 'province'):
        card = find_card(name)
        if card is not None and card in hand:
            return card
    if not hand:
        raise ValueError('No card available to discard')
    return hand[0]



def choose_trash(hand):
    """
    Choisit la carte à retirer définitivement du deck.
    Retourne un membre de CardName.
    """
    trash_priority = [
        "curse",
        "estate",
        "copper",
        "woodcutter",
    ]
    for name in trash_priority:
        card = find_card(name)
        if card is not None and card_quantity(hand, name) > 0:
            return card

    # Si aucune carte faible n'est présente, éviter de détruire
    # une carte forte : sélectionner la moins utile restante.
    return choose_discard(hand)


def calculate_buys() -> int:
    """Nombre de Buy disponibles au début du tour."""
    return 1


def calculate_actions() -> int:
    """Nombre d'actions disponibles au début du tour."""
    return 1


# (extra actions, extra buys, extra money). Other card effects are resolved by referee.
ACTION_BONUSES = {
    'festival': (2, 1, 2), 'laboratory': (1, 0, 0),
    'market': (1, 1, 1), 'village': (2, 0, 0),
    'woodcutter': (0, 1, 2), 'councilroom': (0, 1, 0),
    'farmingvillage': (2, 0, 0), 'distantshore': (1, 0, 0),
    'smithy': (0, 0, 0), 'witch': (0, 0, 0),
    'hireling': (0, 0, 0), 'militia': (0, 0, 2),
    'bureaucrat': (0, 0, 0), 'bandit': (0, 0, 0),
}


def get_action_bonuses(action: str) -> tuple[int, int, int]:
    if not action.startswith('ACTION '):
        return (0, 0, 0)
    return ACTION_BONUSES.get(action.split(' ', 1)[1].lower(), (0, 0, 0))




def choose_action(hand) -> str | None:
    def count(name):
        return card_count(hand, name)

    def play(name):
        card = find_card(name)
        return f'ACTION {card.value}' if card is not None and count(name) > 0 else None

    terminals = ('witch', 'smithy', 'councilroom', 'militia', 'bureaucrat', 'bandit', 'woodcutter')
    for name in ('laboratory', 'market'):
        if result := play(name):
            return result
    if any(count(name) > 0 for name in terminals):
        for name in ('village', 'farmingvillage', 'festival'):
            if result := play(name):
                return result
    for name in ('witch', 'bandit', 'militia', 'bureaucrat', 'councilroom', 'smithy', 'woodcutter', 'festival', 'village', 'farmingvillage', 'distantshore', 'hireling'):
        if result := play(name):
            return result
    return None