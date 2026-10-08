from dopynion.data_model import CardName


def calculate_money(hand: list[CardName]) -> int:
    """Calcule l'argent disponible dans une main."""

    money = 0

    for card in hand:
        if card == CardName.COPPER:
            money += 1

        elif card == CardName.SILVER:
            money += 2

        elif card == CardName.GOLD:
            money += 3

    return money


def choose_buy(money: int, stock) -> str:
    """Choisit quoi acheter selon l'argent et le stock disponible."""

    province_available = stock.quantities.get(CardName.PROVINCE, 0) > 0
    gold_available = stock.quantities.get(CardName.GOLD, 0) > 0
    silver_available = stock.quantities.get(CardName.SILVER, 0) > 0
    copper_available = stock.quantities.get(CardName.COPPER, 0) > 0

    if money >= 8 and province_available:
        return f"BUY {CardName.PROVINCE.value}"

    if money >= 6 and gold_available:
        return f"BUY {CardName.GOLD.value}"

    if money >= 3 and silver_available:
        return f"BUY {CardName.SILVER.value}"

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
