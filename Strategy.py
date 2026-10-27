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


def calculate_money(hand, bonus_money: int = 0) -> int:
    """Calcule l'argent disponible : trésors en main + bonus d'actions."""

    money = 0
    money += hand.quantities.get(CardName.COPPER, 0) * 1
    money += hand.quantities.get(CardName.SILVER, 0) * 2
    money += hand.quantities.get(CardName.GOLD, 0) * 3

    return money + bonus_money


def choose_buy(money: int, stock, deck=None) -> str:
    """Stratégie d'achat : économie, puis moteur, puis points."""

    if deck is None:
        deck = {}

    def available(name: str) -> bool:
        return card_count(stock, name) > 0

    def owned(name: str) -> int:
        card = find_card(name)
        if card is None:
            return 0
        return deck.get(card, 0)

    def buy(name: str) -> str:
        card = find_card(name)
        if card is None:
            return "END_TURN"
        return f"BUY {card.value}"

    provinces_left = card_count(stock, "province")
    duchies_left = card_count(stock, "duchy")

    # 1. Les points avant tout dès que possible
    if money >= 8 and available("province"):
        return buy("province")

    # 2. Quand les Provinces commencent à manquer,
    # les Duchés deviennent une priorité
    if duchies_left <= 4 and money >= 5 and available("duchy"):
        return buy("duchy")

    # Hireling : priorité élevée en début de partie
    if (
        money >= 6
        and available("hireling")
        and owned("hireling") < 3
        and provinces_left > 4
    ):
        return buy("hireling")

    deck_size = sum(deck.values())

    # Gardens devient intéressant quand le deck est volumineux
    if money >= 4 and available("gardens") and deck_size >= 30 and owned("gardens") < 2:
        return buy("gardens")

    # 3. Renforcer rapidement l'économie
    if money >= 6 and available("gold"):
        return buy("gold")

    # Chancelier : coûte 3 pièces
    if money >= 3 and available("chancellor") and owned("chancellor") < 2:
        return buy("chancellor")

    # Bandit : améliore l'économie et attaque les adversaires
    if money >= 5 and available("bandit") and owned("bandit") < 2:
        return buy("bandit")

    if money >= 3 and available("silver") and money < 5:
        return buy("silver")

    # 4. Cartes d'action fortes : éviter d'en acheter trop
    if money >= 5 and available("witch") and owned("witch") < 2:
        return buy("witch")

    if money >= 5 and available("laboratory") and owned("laboratory") < 2:
        return buy("laboratory")

    if money >= 5 and available("councilroom") and owned("councilroom") < 1:
        return buy("councilroom")

    # Milice : +2 pièces et attaque les adversaires
    if money >= 4 and available("militia") and owned("militia") < 2:
        return buy("militia")

    # Bureaucrate : gagne un Argent et gêne les adversaires
    if money >= 4 and available("bureaucrat") and owned("bureaucrat") < 2:
        return buy("bureaucrat")

    if money >= 4 and available("smithy") and owned("smithy") < 2:
        return buy("smithy")

    # 5. Village seulement si le deck possède déjà
    # assez de cartes d'action à jouer
    terminal_actions = (
        owned("smithy") + owned("laboratory") + owned("councilroom") + owned("witch")
    )

    if (
        money >= 3
        and available("village")
        and owned("village") < 2
        and terminal_actions > owned("village")
    ):
        return buy("village")

    if money >= 5 and available("festival") and owned("festival") < 2:
        return buy("festival")

    if money >= 5 and available("market") and owned("market") < 2:
        return buy("market")

    if money >= 4 and available("farmingvillage") and owned("farmingvillage") < 2:
        return buy("farmingvillage")

    if money >= 3 and available("woodcutter") and owned("woodcutter") < 1:
        return buy("woodcutter")

    # 6. Repli économique
    if money >= 3 and available("silver"):
        return buy("silver")

    # Duché de secours si la fin de partie est proche
    if provinces_left <= 2 and money >= 5 and available("duchy"):
        return buy("duchy")

    # Estate uniquement en toute fin de partie
    if provinces_left <= 2 and money >= 2 and available("estate"):
        return buy("estate")

    # Surtout pas de Cuivre acheté automatiquement
    return "END_TURN"


def card_quantity(hand, name: str) -> int:
    """Nombre d'exemplaires d'une carte dans une main."""
    card = find_card(name)
    if card is None:
        return 0
    return hand.quantities.get(card, 0)


def choose_discard(hand):
    """
    Choisit la carte la moins utile à conserver dans la main.
    Retourne un membre de CardName.
    """
    # Ordre initial : cartes généralement les moins utiles

    discard_priority = [
        "curse",
        "estate",
        "copper",
        "woodcutter",
        "smithy",
        "councilroom",
        "distantshore",
        "hireling",
        "witch",
        "farmingvillage",
        "village",
        "festival",
        "market",
        "laboratory",
        "silver",
        "gold",
        "province",
    ]

    for name in discard_priority:
        card = find_card(name)
        if card is not None and card_quantity(hand, name) > 0:
            return card

    # Repli : première carte présente dans la main
    for card, quantity in hand.quantities.items():
        if quantity > 0:
            return card

    # Une main vide ne devrait pas arriver sur cette route.
    raise ValueError("Impossible de défausser : la main est vide.")


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


def get_action_bonuses(action: str) -> tuple[int, int, int]:
    """
    Renvoie les bonus de la carte jouée :
    (actions supplémentaires, achats supplémentaires, argent).
    """

    bonuses = {
        "festival": (2, 1, 2),
        "laboratory": (1, 0, 0),
        "market": (1, 1, 1),
        "village": (2, 0, 0),
        "woodcutter": (0, 1, 2),
        "councilroom": (0, 1, 0),
        "farmingvillage": (2, 0, 0),
        "distantshore": (1, 0, 0),
        "smithy": (0, 0, 0),
        "witch": (0, 0, 0),
        "hireling": (0, 0, 0),
        "militia": (0, 0, 2),
        "bureaucrat": (0, 0, 0),
        "bandit": (0, 0, 0),
        "gardens": (0, 0, 0),
        "chancellor": (0, 0, 2),
    }

    if not action.startswith("ACTION "):
        return 0, 0, 0

    card_name = action.split(" ", 1)[1].lower()

    return bonuses.get(card_name, (0, 0, 0))


def choose_action(hand) -> str | None:
    """Choisit l'action à jouer selon les cartes en main."""

    def count(name: str) -> int:
        card = find_card(name)
        if card is None:
            return 0
        return hand.quantities.get(card, 0)

    def play(name: str) -> str | None:
        card = find_card(name)
        if card is not None and count(name) > 0:
            return f"ACTION {card.value}"
        return None

    # Cartes qui consomment une action sans en rendre
    terminal_actions = (
        "witch",
        "smithy",
        "councilroom",
        "distantshore",
        "hireling",
        "militia",
        "bureaucrat",
        "bandit",
    )

    has_other_action = any(count(name) > 0 for name in terminal_actions)

    # 1. Festival : bonus d'actions, d'achat et d'argent
    action = play("festival")
    if action is not None:
        return action

    # 2. Débloquer les autres cartes Action
    if has_other_action:
        action = play("village")
        if action is not None:
            return action

        action = play("farmingvillage")
        if action is not None:
            return action

    # 3. Pioche qui permet généralement de continuer à jouer
    action = play("hireling")
    if action is not None:
        return action

    action = play("laboratory")
    if action is not None:
        return action

    action = play("market")
    if action is not None:
        return action

    # 4. Attaque et pioche
    action = play("witch")
    if action is not None:
        return action
    # Bandit : attaque et gain d'Or
    action = play("bandit")
    if action is not None:
        return action

    # Milice : attaque et +2 pièces
    action = play("militia")
    if action is not None:
        return action

    # Bureaucrate : gain d'Argent et gêne les adversaires
    action = play("bureaucrat")
    if action is not None:
        return action

    # 5. Pioche de cartes
    action = play("councilroom")
    if action is not None:
        return action

    action = play("smithy")
    if action is not None:
        return action

    action = play("chancellor")
    if action is not None:
        return action

    # 6. Autres cartes utiles
    action = play("woodcutter")
    if action is not None:
        return action

    # À conserver seulement si ces cartes sont bien jouables
    # comme des actions dans la version de Dopynion utilisée.
    action = play("distantshore")
    if action is not None:
        return action

    return None
