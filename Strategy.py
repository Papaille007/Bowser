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
    """Ajoute au deck la carte correspondant à un achat."""

    if not decision.startswith("BUY "):
        return

    card_name = decision.split(" ", 1)[1]

    for card in CardName:
        if card.value == card_name:
            deck[card] = deck.get(card, 0) + 1
            return


def calculate_money(hand) -> int:
    """Calcule l'argent disponible dans la main."""

    money = 0

    money += hand.quantities.get(CardName.COPPER, 0) * 1
    money += hand.quantities.get(CardName.SILVER, 0) * 2
    money += hand.quantities.get(CardName.GOLD, 0) * 3

    return money


def choose_buy(money: int, stock, deck=None) -> str:
    """Choisit quoi acheter selon l'argent, le stock et le deck."""

    if deck is None:
        deck = {}

    # --------------------------------------------------
    # 1. Vérification du stock disponible
    # --------------------------------------------------

    province_available = card_count(stock, "province") > 0
    duchy_available = card_count(stock, "duchy") > 0

    gold_available = card_count(stock, "gold") > 0
    silver_available = card_count(stock, "silver") > 0

    witch_available = card_count(stock, "witch") > 0
    councilroom_available = card_count(stock, "councilroom") > 0
    laboratory_available = card_count(stock, "laboratory") > 0
    smithy_available = card_count(stock, "smithy") > 0
    village_available = card_count(stock, "village") > 0
    festival_available = card_count(stock, "festival") > 0
    market_available = card_count(stock, "market") > 0
    farmingvillage_available = card_count(stock, "farmingvillage") > 0
    woodcutter_available = card_count(stock, "woodcutter") > 0

    provinces_left = card_count(stock, "province")

    # --------------------------------------------------
    # 2. Quantités déjà possédées
    # --------------------------------------------------

    def owned(name: str) -> int:
        card = find_card(name)

        if card is None:
            return 0

        return deck.get(card, 0)

    def buy(name: str) -> str:
        card = find_card(name)
        return f"BUY {card.value}"

    # --------------------------------------------------
    # 3. Acheter les points de victoire
    # --------------------------------------------------

    if money >= 8 and province_available:
        return buy("province")

    # --------------------------------------------------
    # 4. Fin de partie : Duchés
    # --------------------------------------------------

    if provinces_left <= 4 and money >= 5 and duchy_available:
        return buy("duchy")

    # --------------------------------------------------
    # 5. Renforcer l'économie
    # --------------------------------------------------

    if money >= 6 and gold_available:
        return buy("gold")

    # --------------------------------------------------
    # 6. Attaque et pioche : Sorcière
    # --------------------------------------------------

    if money >= 5 and witch_available and owned("witch") < 2:
        return buy("witch")

    # --------------------------------------------------
    # 7. Développer la pioche
    # --------------------------------------------------

    if money >= 5 and laboratory_available and owned("laboratory") < 2:
        return buy("laboratory")

    if money >= 5 and councilroom_available and owned("councilroom") < 2:
        return buy("councilroom")

    if money >= 4 and smithy_available and owned("smithy") < 2:
        return buy("smithy")

    # --------------------------------------------------
    # 8. Améliorer le moteur d'actions et d'achats
    # --------------------------------------------------

    if money >= 3 and village_available and owned("village") < 2:
        return buy("village")

    if money >= 5 and festival_available and owned("festival") < 2:
        return buy("festival")

    if money >= 5 and market_available and owned("market") < 2:
        return buy("market")

    if money >= 4 and farmingvillage_available and owned("farmingvillage") < 2:
        return buy("farmingvillage")

    if money >= 3 and woodcutter_available and owned("woodcutter") < 2:
        return buy("woodcutter")

    # --------------------------------------------------
    # 9. Argent : achat économique par défaut
    # --------------------------------------------------

    if money >= 3 and silver_available:
        return buy("silver")

    # --------------------------------------------------
    # 10. Duché de secours en fin de partie
    # --------------------------------------------------

    if money >= 5 and duchy_available and provinces_left <= 2:
        return buy("duchy")

    # Ne pas acheter de Cuivre par défaut
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


def get_action_bonuses(action: str) -> tuple[int, int]:
    """
    Renvoie les bonus de la carte jouée :
    (actions supplémentaires, achats supplémentaires).
    """

    bonuses = {
        "festival": (2, 1),
        "laboratory": (1, 0),
        "market": (1, 1),
        "village": (2, 0),
        "woodcutter": (0, 1),
        "councilroom": (0, 1),
        "farmingvillage": (2, 0),
        "distantshore": (1, 0),
        "smithy": (0, 0),
        "witch": (0, 0),
        "hireling": (0, 0),
    }

    if not action.startswith("ACTION "):
        return 0, 0

    card_name = action.split(" ", 1)[1].lower()

    return bonuses.get(card_name, (0, 0))


def choose_action(hand) -> str | None:
    """Choisit une carte Action à jouer."""

    # 1. Cartes qui permettent de jouer plus d'actions
    action_cards = [
        "village",
        "farmingvillage",
        "festival",
        "laboratory",
        "market",
    ]

    for name in action_cards:
        card = find_card(name)

        if card is not None and hand.quantities.get(card, 0) > 0:
            return f"ACTION {card.value}"

    # 2. Cartes qui font piocher des cartes
    draw_cards = [
        "councilroom",
        "witch",
        "smithy",
        "distantshore",
    ]

    for name in draw_cards:
        card = find_card(name)

        if card is not None and hand.quantities.get(card, 0) > 0:
            return f"ACTION {card.value}"

    # 3. Autres cartes Action
    card = find_card("hireling")

    if card is not None and hand.quantities.get(card, 0) > 0:
        return f"ACTION {card.value}"

    card = find_card("woodcutter")

    if card is not None and hand.quantities.get(card, 0) > 0:
        return f"ACTION {card.value}"

    return None
