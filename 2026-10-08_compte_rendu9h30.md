[COMPTE RENDU.md](https://github.com/user-attachments/files/33196254/COMPTE.RENDU.md)
Bonjour à tous,

Vous trouverez ci-dessous le compte rendu de la réunion du mercredi 08 octobre à 09h30 :

&nbsp;**Groupe :** 3
**Personnes présentes :**

- Client : Vincent POULAILLEAU
- Équipe de développement : Alexandre, Jean-Eudes, Pauline, Matteo
- Absents : Younes

**1\. Mécaniques de jeu & Nouvelles actions (verbes)**

- Écarter : Mise au rebut d'une carte (de la main vers la défausse).
- Recevoir : Prendre une carte de la réserve et la placer directement dans la défausse.

Phase d'achat : Limité à 1 achat par tour. Les cartes trésor sont mises automatiquement en défausse (= monnaie).

&nbsp;

**2\. Communication avec l'arbitre & Gestion des parties**

- Gestion multi-parties : Possibilité de jouer plusieurs parties en simultané, avec plusieurs ID par partie et par joueur.
- Identifiant (game Id) : Un nouvel ID est attribué par partie. Il est obligatoire pour transmettre le moindre ordre à l'arbitre.
- Identification d'équipe : Format root / name - > nom de l'équipe.

**3\. Commandes & Déroulement du jeu**

Contrôle du flux :

Start_game (en début de partie, il fournit l'ID de la partie + java script jason ok)

Start_turn

/play (get pour prendre une décision)

**Actions de jeu :**

Buy "Card Name" : acheter une carte.

Action "Card Name" : jouer une carte action.

&nbsp;

&nbsp;

Bonne journée,
