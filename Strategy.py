from dopynion.data_model import CardName


def calculate_money(hand) -> int:
    """Calcule l'argent disponible dans la main."""

    money = 0

    money += hand.quantities.get(CardName.COPPER, 0) * 1
    money += hand.quantities.get(CardName.SILVER, 0) * 2
    money += hand.quantities.get(CardName.GOLD, 0) * 3

    return money


def choose_buy(money: int, stock) -> str:
    """Choisit quoi acheter selon l'argent et le stock disponible."""

    # Vérification de la disponibilité des cartes
    province_available = stock.quantities.get(CardName.PROVINCE, 0) > 0
    duchy_available = stock.quantities.get(CardName.DUCHY, 0) > 0
    estate_available = stock.quantities.get(CardName.ESTATE, 0) > 0

    gold_available = stock.quantities.get(CardName.GOLD, 0) > 0
    silver_available = stock.quantities.get(CardName.SILVER, 0) > 0
    copper_available = stock.quantities.get(CardName.COPPER, 0) > 0

    festival_available = stock.quantities.get(CardName.FESTIVAL, 0) > 0
    laboratory_available = stock.quantities.get(CardName.LABORATORY, 0) > 0
    market_available = stock.quantities.get(CardName.MARKET, 0) > 0
    smithy_available = stock.quantities.get(CardName.SMITHY, 0) > 0
    village_available = stock.quantities.get(CardName.VILLAGE, 0) > 0
    woodcutter_available = stock.quantities.get(CardName.WOODCUTTER, 0) > 0

    # Stratégie d'achat
    if money >= 8 and province_available:
        return f"BUY {CardName.PROVINCE.value}"

    if money >= 6 and gold_available:
        return f"BUY {CardName.GOLD.value}"

    if money >= 5 and duchy_available:
        return f"BUY {CardName.DUCHY.value}"

    if money >= 5 and festival_available:
        return f"BUY {CardName.FESTIVAL.value}"

    if money >= 5 and laboratory_available:
        return f"BUY {CardName.LABORATORY.value}"

    if money >= 5 and market_available:
        return f"BUY {CardName.MARKET.value}"

    if money >= 4 and smithy_available:
        return f"BUY {CardName.SMITHY.value}"

    if money >= 3 and silver_available:
        return f"BUY {CardName.SILVER.value}"

    if money >= 3 and village_available:
        return f"BUY {CardName.VILLAGE.value}"

    if money >= 3 and woodcutter_available:
        return f"BUY {CardName.WOODCUTTER.value}"

    if money >= 2 and estate_available:
        return f"BUY {CardName.ESTATE.value}"

    if copper_available:
        return f"BUY {CardName.COPPER.value}"

    return "END_TURN"


def choose_discard(hand: list[CardName]) -> CardName:
    """Choisit une carte à défausser."""

    if CardName.ESTATE in hand:
        return CardName.ESTATE

    if CardName.COPPER in hand:
        return CardName.COPPER

    return hand[0]


def choose_trash(hand: list[CardName]) -> CardName:
    """Choisit une carte à supprimer du deck."""

    if CardName.ESTATE in hand:
        return CardName.ESTATE

    if CardName.COPPER in hand:
        return CardName.COPPER

    return hand[0]


def calculate_buys() -> int:
    """Nombre de Buy disponibles au début du tour."""
    return 1


def calculate_actions() -> int:
    """Nombre d'actions disponibles au début du tour."""
    return 1


def choose_action(hand) -> str:
    """Choisit une carte Action à jouer."""
    if hand.quantities.get(CardName.SMITHY, 0) > 0:
        return f"ACTION {CardName.SMITHY.value}"

    if hand.quantities.get(CardName.VILLAGE, 0) > 0:
        return f"ACTION {CardName.VILLAGE.value}"

    if hand.quantities.get(CardName.MARKET, 0) > 0:
        return f"ACTION {CardName.MARKET.value}"

    if hand.quantities.get(CardName.WOODCUTTER, 0) > 0:
        return f"ACTION {CardName.WOODCUTTER.value}"

    if hand.quantities.get(CardName.FESTIVAL, 0) > 0:
        return f"ACTION {CardName.FESTIVAL.value}"

    if hand.quantities.get(CardName.LABORATORY, 0) > 0:
        return f"ACTION {CardName.LABORATORY.value}"

    return None
