from dopynion.data_model import CardName


def choose_discard(hand: list[CardName]) -> CardName:
    """Choisit une carte à défausser."""

    if CardName.Estate in hand:
        return CardName.Estate

    if CardName.Copper in hand:
        return CardName.Copper

    return hand[0]


def choose_trash(hand: list[CardName]) -> CardName:
    """Choisit une carte à supprimer du deck."""

    if CardName.Estate in hand:
        return CardName.Estate

    if CardName.Copper in hand:
        return CardName.Copper

    return hand[0]
