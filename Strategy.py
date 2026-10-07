from dopynion.data_model import CardName


def choose_discard(hand: list[CardName]) -> CardName:
    """Choisit une carte à défausser."""

    # Priorité : défausser un Estate
    if CardName.ESTATE in hand:
        return CardName.ESTATE

    # Sinon : défausser un Copper
    if CardName.COPPER in hand:
        return CardName.COPPER

    # Sinon : première carte disponible
    return hand[0]


def choose_trash(hand: list[CardName]) -> CardName:
    """Choisit une carte à supprimer du deck."""

    # Priorité : supprimer un Estate
    if CardName.ESTATE in hand:
        return CardName.ESTATE

    # Sinon : supprimer un Copper
    if CardName.COPPER in hand:
        return CardName.COPPER

    # Sinon : première carte disponible
    return hand[0]
