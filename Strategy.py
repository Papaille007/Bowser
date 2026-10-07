from collections import Counter


# ============================================================
# Valeur des cartes
# ============================================================

CARD_VALUE = {
    "copper": 0,
    "silver": 1,
    "gold": 2,
    "estate": 1,
    "duchy": 3,
    "province": 6,
}


# ============================================================
# OUTILS
# ============================================================


def get_card_count(hand, card_name):
    """Retourne le nombre d'exemplaires d'une carte dans une main."""
    if hand is None:
        return 0

    return hand.quantities.get(card_name, 0)


def get_hand_cards(hand):
    """Transforme une main en liste de cartes."""
    if hand is None:
        return []

    cards = []

    for card, quantity in hand.quantities.items():
        cards.extend([card] * quantity)

    return cards


# ============================================================
# STRATÉGIE D'ACHAT
# ============================================================


def choose_buy(possible_cards):
    """
    Choisit une carte parmi les cartes proposées à l'achat.

    Stratégie actuelle :
    Province > Duché > Or > Argent > Domaine > Cuivre
    """

    priority = {
        "province": 100,
        "duchy": 80,
        "gold": 70,
        "silver": 50,
        "estate": 20,
        "copper": 10,
    }

    best_card = None
    best_score = -1

    for card in possible_cards:
        score = priority.get(str(card), 0)

        if score > best_score:
            best_score = score
            best_card = card

    return best_card


# ============================================================
# STRATÉGIE DE DÉFAUSSE
# ============================================================


def choose_discard(hand):
    """
    Choisit une carte à défausser.

    On préfère se débarrasser des cartes peu intéressantes
    pour améliorer progressivement le deck.
    """

    cards = get_hand_cards(hand)

    if not cards:
        return None

    priority = {
        "copper": 0,
        "estate": 1,
        "silver": 2,
        "duchy": 3,
        "gold": 4,
        "province": 5,
    }

    return min(cards, key=lambda card: priority.get(str(card), 1))


# ============================================================
# STRATÉGIE DE REBUT
# ============================================================


def choose_trash(hand):
    """
    Choisit une carte à envoyer au rebut.

    Pour commencer :
    Cuivre > Domaine > autres cartes.
    """

    cards = get_hand_cards(hand)

    if not cards:
        return None

    priority = {
        "copper": 0,
        "estate": 1,
        "silver": 2,
        "duchy": 3,
        "gold": 4,
        "province": 5,
    }

    return min(cards, key=lambda card: priority.get(str(card), 1))


# ============================================================
# CARTES À RECEVOIR
# ============================================================


def choose_best_card(possible_cards):
    """
    Choisit la meilleure carte parmi plusieurs possibilités.
    """

    priority = {
        "province": 100,
        "duchy": 80,
        "gold": 70,
        "silver": 50,
        "estate": 20,
        "copper": 10,
    }

    if not possible_cards:
        return None

    return max(possible_cards, key=lambda card: priority.get(str(card), 0))
