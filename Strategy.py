"""
Stratégie du royaume Koopa Dominion.
"""

from dopynion.data_model import CardName


def choose_discard(hand: list[CardName]) -> CardName:
    """Choisit une carte à défausser."""

    # On privilégie la défausse d'un Estate
    if CardName.Estate in hand:
        return CardName.Estate

    # Sinon, on défausse un Copper
    if CardName.Copper in hand:
        return CardName.Copper

    # Sinon, on prend la première carte disponible
    return hand[0]
