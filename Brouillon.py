def choose_card(possible_cards):
    """
    Choisit une carte parmi les cartes proposées.

    Pour l'instant, on conserve une stratégie simple :
    on choisit la première carte disponible.

    Cette fonction sera améliorée progressivement.
    """
    if not possible_cards:
        return None

    return possible_cards[0]


def choose_trash(hand):
    """
    Choisit une carte à envoyer au rebut.

    Pour l'instant :
    Cuivre > Domaine > autre carte.
    """
    if not hand:
        return None

    if "copper" in hand:
        return "copper"

    if "estate" in hand:
        return "estate"

    return hand[0]


def choose_money_card(money_cards):
    """
    Choisit une carte Trésor à améliorer/remplacer.

    Pour l'instant, on privilégie le Cuivre.
    """
    if not money_cards:
        return None

    if "copper" in money_cards:
        return "copper"

    return money_cards[0]
