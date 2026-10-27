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
    """Renvoie le nombre d'exemplaires d'une carte dans une main ou la réserve."""
    card = find_card(name)
    if card is None:
        return 0

    quantities = cards.quantities if hasattr(cards, "quantities") else cards
    return quantities.get(card, 0)


def create_starting_deck() -> dict:
    """Deck de départ Dominion : 7 Cuivres et 3 Domaines."""
    return {CardName.COPPER: 7, CardName.ESTATE: 3}


def record_purchase(deck: dict, decision: str) -> None:
    """Mémorise les achats pour estimer la composition du deck."""
    if not decision.startswith("BUY "):
        return

    card_name = decision.split(" ", 1)[1]
    for card in CardName:
        if str(card.value) == card_name:
            deck[card] = deck.get(card, 0) + 1
            return


def calculate_money(hand, bonus_money: int = 0) -> int:
    """Argent des Trésors en main + bonus d'argent déjà gagnés ce tour."""
    money = (
        card_count(hand, "copper")
        + 2 * card_count(hand, "silver")
        + 3 * card_count(hand, "gold")
    )
    return money + bonus_money


def choose_buy(money: int, stock, deck=None, player_count: int = 2) -> str:
    """
    Stratégie d'achat générale pour 2 à 4 joueurs.

    La priorité exacte dépend toujours des 10 cartes Royaume disponibles.
    player_count sert notamment à pondérer les attaques et Conseil des Bouleversements.
    """
    if deck is None:
        deck = {}

    player_count = max(2, min(4, player_count))

    def available(name: str) -> bool:
        return card_count(stock, name) > 0

    def owned(name: str) -> int:
        card = find_card(name)
        return deck.get(card, 0) if card is not None else 0

    def buy(name: str) -> str:
        card = find_card(name)
        return f"BUY {card.value}" if card is not None else "END_TURN"

    provinces_left = card_count(stock, "province")
    duchies_left = card_count(stock, "duchy")
    deck_size = sum(deck.values())

    # 1. Victoire immédiate : une Province vaut 6 points.
    if money >= 8 and available("province"):
        return buy("province")

    # 2. Fin de partie : prendre des points plutôt que continuer à construire
    # son moteur. Le seuil tient compte de la quantité initiale habituelle.
    province_endgame_threshold = 2 if player_count == 2 else 4
    if provinces_left <= province_endgame_threshold:
        if money >= 5 and available("duchy"):
            return buy("duchy")
        if money >= 4 and available("gardens") and deck_size >= 30:
            return buy("gardens")
        if money >= 2 and available("estate") and provinces_left <= 1:
            return buy("estate")

    # 3. Hireling : investissement durable, particulièrement rentable tôt.
    # On en évite trop pour ne pas remplir le deck d'actions terminales.
    if (
        money >= 6
        and available("hireling")
        and owned("hireling") < 2
        and provinces_left > province_endgame_threshold
    ):
        return buy("hireling")

    # 4. Attaques puissantes : leur valeur augmente quand il y a plus d'adversaires.
    # Witch fait piocher 2 cartes et donne une Malédiction à chaque adversaire
    # encore en mesure d'en recevoir une.
    if money >= 5 and available("witch") and owned("witch") < 2:
        return buy("witch")

    # Bandit améliore l'économie en faisant gagner un Or et peut gêner les adversaires.
    if money >= 5 and available("bandit") and owned("bandit") < 2:
        return buy("bandit")

    # Militia est particulièrement intéressante tôt et à plusieurs joueurs.
    if (
        money >= 4
        and available("militia")
        and owned("militia") < (2 if player_count >= 3 else 1)
    ):
        return buy("militia")

    # 5. Moteur économique. L'Or est fiable, mais ne doit pas empêcher d'acheter
    # une carte moteur très forte au bon moment.
    if money >= 6 and available("gold"):
        return buy("gold")

    # Laboratoire est une excellente action : +2 cartes et +1 action.
    if money >= 5 and available("laboratory") and owned("laboratory") < 2:
        return buy("laboratory")

    # Festival donne +2 actions, +1 achat et +2 pièces.
    if money >= 5 and available("festival") and owned("festival") < 2:
        return buy("festival")

    if money >= 5 and available("market") and owned("market") < 2:
        return buy("market")

    # Conseil des Bouleversements fait piocher les adversaires : moins séduisant
    # à 3-4 joueurs. On le limite fortement dans ces parties.
    if money >= 5 and available("councilroom"):
        max_council_rooms = 1 if player_count == 2 else 0
        if owned("councilroom") < max_council_rooms:
            return buy("councilroom")

    # Bureaucrate fournit un Argent, mais son attaque est souvent moins décisive
    # qu'une Sorcière ou une Milice. Une seule copie suffit généralement.
    if money >= 4 and available("bureaucrat") and owned("bureaucrat") < 1:
        return buy("bureaucrat")

    if money >= 4 and available("smithy") and owned("smithy") < 2:
        return buy("smithy")

    # 6. Ajouter des actions uniquement si le deck a des actions terminales à jouer.
    terminal_actions = sum(
        owned(name)
        for name in (
            "hireling",
            "witch",
            "bandit",
            "militia",
            "bureaucrat",
            "smithy",
            "councilroom",
            "chancellor",
        )
    )
    villages = owned("village") + owned("farmingvillage")

    if (
        money >= 3
        and available("village")
        and villages < terminal_actions
        and owned("village") < 3
    ):
        return buy("village")

    if (
        money >= 4
        and available("farmingvillage")
        and villages < terminal_actions
        and owned("farmingvillage") < 2
    ):
        return buy("farmingvillage")

    # 7. Jardins : uniquement si le deck est déjà grand et l'achat a un bon rapport
    # coût/points. Le compteur du deck reste une estimation si les gains spéciaux
    # (par exemple Bandit/Bureaucrate) ne sont pas suivis dans Main.py.
    if money >= 4 and available("gardens") and deck_size >= 30 and owned("gardens") < 3:
        return buy("gardens")

    # Le Chancelier n'est pas un achat automatique : +2 pièces ne compensent pas
    # toujours la perte de contrôle sur la pioche. Ne l'acheter qu'en repli.
    if (
        money >= 3
        and available("chancellor")
        and owned("chancellor") < 1
        and not available("silver")
        and not available("village")
    ):
        return buy("chancellor")

    # Argent : achat stable pour améliorer la production de pièces.
    if money >= 3 and available("silver"):
        return buy("silver")

    # Le Duché devient intéressant lorsque la fin approche.
    if (
        provinces_left <= province_endgame_threshold
        and money >= 5
        and available("duchy")
    ):
        return buy("duchy")

    if provinces_left <= 1 and money >= 2 and available("estate"):
        return buy("estate")

    # Ne pas acheter de Cuivre par défaut : il encombre le deck.
    return "END_TURN"


def card_quantity(hand, name: str) -> int:
    return card_count(hand, name)


def choose_discard(hand):
    """Choisit une carte faible à défausser, en préservant les cartes fortes."""
    discard_priority = [
        "curse",
        "estate",
        "copper",
        "chancellor",
        "woodcutter",
        "councilroom",
        "smithy",
        "bureaucrat",
        "bandit",
        "militia",
        "witch",
        "distantshore",
        "market",
        "laboratory",
        "festival",
        "farmingvillage",
        "village",
        "silver",
        "gold",
        "hireling",
        "province",
    ]

    for name in discard_priority:
        card = find_card(name)
        if card is not None and card_quantity(hand, name) > 0:
            return card

    for card, quantity in hand.quantities.items():
        if quantity > 0:
            return card

    raise ValueError("Impossible de défausser : la main est vide.")


def choose_trash(hand):
    """Retire en priorité les cartes qui affaiblissent le deck."""
    for name in ("curse", "estate", "copper"):
        card = find_card(name)
        if card is not None and card_quantity(hand, name) > 0:
            return card

    # Ne pas détruire une carte utile si aucune carte faible n'est présente.
    return choose_discard(hand)


def calculate_buys() -> int:
    return 1


def calculate_actions() -> int:
    return 1


def get_action_bonuses(action: str) -> tuple[int, int, int]:
    """
    Renvoie (actions supplémentaires, achats supplémentaires, pièces immédiates).
    Les effets qui font gagner des cartes ou affectent les adversaires sont gérés
    par le moteur du jeu, pas par cette table.
    """
    bonuses = {
        "festival": (2, 1, 2),
        "laboratory": (1, 0, 0),
        "market": (1, 1, 1),
        "village": (2, 0, 0),
        "woodcutter": (0, 1, 2),
        "councilroom": (0, 1, 0),
        "farmingvillage": (2, 0, 0),
        "distantshore": (
            1,
            0,
            0,
        ),  # À confirmer avec le texte exact de la carte Dopynion.
        "smithy": (0, 0, 0),
        "witch": (0, 0, 0),
        "hireling": (0, 0, 0),
        "militia": (0, 0, 2),
        "bureaucrat": (0, 0, 0),
        "bandit": (0, 0, 0),
        "chancellor": (0, 0, 2),
    }

    if not action.startswith("ACTION "):
        return 0, 0, 0

    card_name = action.split(" ", 1)[1].lower().replace("_", "").replace(" ", "")
    return bonuses.get(card_name, (0, 0, 0))


def choose_action(hand) -> str | None:
    """Choisit l'action à jouer en limitant les actions terminales inutiles."""

    def count(name: str) -> int:
        return card_quantity(hand, name)

    def play(name: str) -> str | None:
        card = find_card(name)
        if card is not None and count(name) > 0:
            return f"ACTION {card.value}"
        return None

    terminal_actions = (
        "hireling",
        "witch",
        "bandit",
        "militia",
        "bureaucrat",
        "smithy",
        "councilroom",
        "chancellor",
        "distantshore",
    )
    has_terminal_action = any(count(name) > 0 for name in terminal_actions)

    # 1. Festival : argent, achat supplémentaire et actions pour la suite.
    action = play("festival")
    if action is not None:
        return action

    # 2. Jouer les générateurs d'actions avant les cartes terminales.
    if has_terminal_action:
        action = play("village")
        if action is not None:
            return action
        action = play("farmingvillage")
        if action is not None:
            return action

    # 3. Les cartes qui piochent et rendent une action sont jouées tôt.
    action = play("laboratory")
    if action is not None:
        return action
    action = play("market")
    if action is not None:
        return action

    # 4. Hireling tôt dans le tour : son effet persistant aide tous les tours suivants.
    action = play("hireling")
    if action is not None:
        return action

    # 5. Attaques et bonus d'argent.
    for name in ("witch", "bandit", "militia", "bureaucrat"):
        action = play(name)
        if action is not None:
            return action

    # 6. Pioche sans action supplémentaire, puis actions de rendement plus faible.
    action = play("smithy")
    if action is not None:
        return action
    action = play("councilroom")
    if action is not None:
        return action
    action = play("chancellor")
    if action is not None:
        return action
    action = play("woodcutter")
    if action is not None:
        return action
    action = play("distantshore")
    if action is not None:
        return action

    return None
