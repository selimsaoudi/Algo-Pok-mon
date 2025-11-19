"""
Jeu de combat Pokémon 
Exigences :
- Programmation orientée objet (avec des classes)
- Entrées sécurisées (validation robuste )
- Tour par tour : attaquer, utiliser une potion ou passer
"""

from __future__ import annotations
from enum import Enum
import random
from typing import List, Optional

from term_viz import (
    C, COL, print_banner, format_pokemon_line, afficher_etat_deux,
    announce_attack, announce_potion, announce_pass, announce_ko, resume_final, victory_screen, defeat_screen
)


#######################################################
# Fonctions d'entrée sécurisée (menus, entiers)
#######################################################

def demander_choix(message: str, options: List[str]) -> int:
    
    ### Affiche un menu numéroté pour "options" et lit un choix sécurisé.
    ### Retourne l'indice de l'option choisie.

    while True:
        print(message)
        for i, opt in enumerate(options, start=1):
            print(f"  {i}. {opt}")
        brut = input("> ").strip()
        if not brut:
            print("Veuillez saisir un nombre correspondant à une option")
            continue
        if not brut.isdigit():
            print("Entrée invalide : vous devez saisir un nombre (ex : 1, 2, 3)")
            continue
        n = int(brut)
        if not (1 <= n <= len(options)):
            print(f"Merci de choisir un nombre entre 1 et {len(options)}")
            continue
        return n - 1
#
##
###  On vérifie “vide”, “non numérique”, et “hors bornes”, à chaque fois on refuse et on redemande
################################################################################################################


def demander_entier(message: str, mini: Optional[int] = None, maxi: Optional[int] = None) -> int:
    ### Lit un entier de manière sécurisée, éventuellement borné par [mini, maxi]
    while True:
        brut = input(message).strip()
        if not brut or not (brut[0] == '-' and brut[1:].isdigit() or brut.isdigit()):
            print("Entrée invalide : veuillez saisir un nombre entier")
            continue
        val = int(brut)
        if mini is not None and val < mini:
            print(f"Valeur trop petite (min : {mini})")
            continue
        if maxi is not None and val > maxi:
            print(f"Valeur trop grande (max : {maxi})")
            continue
        return val 
#
##
### Pareil on boucle tant que ce n’est pas correct
######################################################



####################################
# BONUS 2 : ajouter des types
####################################

class TypePoke(Enum):
    FEU = "Feu"
    EAU = "Eau"
    PLANTE = "Plante"
    NORMAL = "Normale"  #neutre

# Attaquant -> Défenseur -> multiplicateur
EFF = {
    TypePoke.FEU:    {TypePoke.PLANTE: 2.0, TypePoke.EAU: 0.5,  TypePoke.FEU: 0.5},
    TypePoke.EAU:    {TypePoke.FEU:    2.0, TypePoke.PLANTE: 0.5, TypePoke.EAU: 0.5},
    TypePoke.PLANTE: {TypePoke.EAU:    2.0, TypePoke.FEU:    0.5, TypePoke.PLANTE: 0.5},
    ## bien sur NORMAL non listé -> 1.0
}

def multiplicateur(att_type: TypePoke, def_type: TypePoke) -> float:
    return EFF.get(att_type, {}).get(def_type, 1.0)


####################################
# Modèle orienté objet du jeu
####################################

class Pokemon:
    def __init__(self, nom, pv_max, attaque, type_p=TypePoke.NORMAL):
        self.nom = nom
        self.pv_max = pv_max
        self.pv = pv_max
        self.attaque = attaque
        self.type = type_p

    def est_ko(self):
        return self.pv <= 0

    def subir_degats(self, quantite):
        if quantite < 0:
            quantite = 0
        avant = self.pv
        self.pv -= quantite
        if self.pv < 0:
            self.pv = 0
        return avant - self.pv

    def soigner(self, quantite):
        if quantite < 0:
            quantite = 0
        avant = self.pv
        self.pv += quantite
        if self.pv > self.pv_max:
            self.pv = self.pv_max
        return self.pv - avant

    def reinitialiser(self):
        self.pv = self.pv_max

    def ligne_info(self):
        return f"{self.nom} [{self.type.value}] — PV : {self.pv}/{self.pv_max}, ATK : {self.attaque}"

class Dresseur:
    def __init__(self, nom: str, equipe: List[Pokemon]):
        self.nom = nom
        self.equipe = equipe
        self.actif = 0

    @property
    def pokemon_actif(self) -> Pokemon:
        return self.equipe[self.actif]

    def a_un_pokemon_disponible(self) -> bool:
        return any(not p.est_ko() for p in self.equipe)

    def soigner_tout(self) -> None:
        for p in self.equipe:
            p.reinitialiser()

    def statut_equipe(self) -> str:
        res = []
        for i, p in enumerate(self.equipe, start=1):
            marqueur = " (Actif)" if i - 1 == self.actif else ""
            res.append(f"{i}. {p.ligne_info()}{marqueur}")
        return "\n".join(res)

class Combat:
    SOIN_POTION = 20

    def __init__(self, joueur: Dresseur, ia: Dresseur):
        self.joueur = joueur
        self.ia = ia
        self.joueur.soigner_tout()
        self.ia.soigner_tout()

    def attaquer(self, attaquant: Pokemon, defenseur: Pokemon):
        mult = multiplicateur(attaquant.type, defenseur.type)
        degats = int(round(attaquant.attaque * mult))
        reels = defenseur.subir_degats(degats)
        return reels, mult

    def tour_joueur(self) -> bool:
        print("\n----- Votre tour -----")
        actions = ["Attaquer", "Utiliser une potion (+20 PV)", "Passer le tour"]
        choix = demander_choix("Que voulez vous faire ?", actions)

        if actions[choix] == "Attaquer":
            degats, mult = self.attaquer(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            note = " (SUPER efficace !)" if mult > 1 else " (PEU efficace !)" if mult < 1 else ""
            degats, mult = self.attaquer(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            announce_attack("Joueur", degats, mult, you_are_player=True)
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            if self.ia.pokemon_actif.est_ko():
                announce_ko(self.ia.pokemon_actif.nom, victory=True)
                return False
            return True


        elif actions[choix] == "Utiliser une potion (+20 PV)":
            soigne = self.joueur.pokemon_actif.soigner(self.SOIN_POTION)
            announce_potion("Joueur", soigne, you_are_player=True)
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            return True


        else:
            announce_pass("Joueur")
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            return True


    def tour_ia(self) -> bool:
        print("\n----- Tour de l'adversaire -----")
        print(f"Pokémon adverse : {self.ia.pokemon_actif.ligne_info()}")
        print(f"Votre Pokémon : {self.joueur.pokemon_actif.ligne_info()}")

        choix = random.choice(["attaque", "potion", "pass"])

        if choix == "attaque":
            degats, mult = self.attaquer(self.ia.pokemon_actif, self.joueur.pokemon_actif)
            announce_attack("IA", degats, mult, you_are_player=False)
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            if self.joueur.pokemon_actif.est_ko():
                announce_ko(self.joueur.pokemon_actif.nom, victory=False)
                return False
            return True


        elif choix == "potion":
            soigne = self.ia.pokemon_actif.soigner(self.SOIN_POTION)
            announce_potion("IA", soigne, you_are_player=False)
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            return True

        else:
            announce_pass("IA")
            afficher_etat_deux(self.joueur.pokemon_actif, self.ia.pokemon_actif)
            return True


    def demarrer(self) -> None:
        print("\n========== COMBAT POKEMON ==========")
        while True:
            if not self.tour_joueur():
                break
            if not self.tour_ia():
                break

        # ----- FIN DU MATCH -----
        victory = (not self.joueur.pokemon_actif.est_ko()) and self.ia.pokemon_actif.est_ko()

        # Résumé + écran final (une seule fois, hors de la boucle)
        resume_final(self.joueur.pokemon_actif, self.ia.pokemon_actif, victory)

        if victory:
            victory_screen()
        else:
            defeat_screen()

        print("====================================")


###########################
# Construction du jeu
###########################

def construire_pokedex() -> List[Pokemon]:
    return [
        Pokemon("Ghazi",    95, 21, TypePoke.EAU),
        Pokemon("Ameur",    88, 23, TypePoke.FEU),
        Pokemon("Haythem",  92, 20, TypePoke.PLANTE),
        Pokemon("Belgacem",100, 19, TypePoke.FEU),
        Pokemon("Smail",    85, 24, TypePoke.EAU),
        Pokemon("Monta",    90, 22, TypePoke.PLANTE),
        Pokemon("Zaineb",   87, 23, TypePoke.FEU),
        Pokemon("Marwa",    93, 21, TypePoke.EAU),
        Pokemon("Sarra",    89, 22, TypePoke.PLANTE),
        Pokemon("Dadou",    97, 20, TypePoke.FEU),
    ]

def choisir_pokemon_joueur(pokedex: List[Pokemon]) -> Pokemon:
    print("\nChoisissez votre Pokémon :")
    for i, p in enumerate(pokedex, start=1):
        print(f"{i}. {p.ligne_info()}")
    idx = demander_entier("Numero : ", 1, len(pokedex)) - 1
    return pokedex[idx]

def main() -> None:
    print_banner()
    random.seed()
    pokedex = construire_pokedex()

    print("Bienvenue dans le jeu Pokémon (CLI) ")
    print("------------------------------------------------")

    p_joueur = choisir_pokemon_joueur(pokedex)
    reste = [p for p in pokedex if p is not p_joueur]
    p_ia = random.choice(reste)

    joueur = Dresseur("Vous", [p_joueur])
    ia = Dresseur("Adversaire", [p_ia])

    print("\nVotre Pokemon :")
    print(joueur.statut_equipe())
    print("\nPokemon adverse :")
    print(ia.statut_equipe())

    combat = Combat(joueur, ia)
    combat.demarrer()

    ##################
    # Rejouer
    ##################
    while True:
        encore = demander_choix("\nREJOUER ?", ["OUI", "NON"])
        if encore == 1:
            print("Merci d'avoir joué ! A bientot !")
            break

        #proposer de re-choisir un Pokemon
        rechoisir = demander_choix("Souhaitez vous re-choisir votre Pokémon ?", ["Oui", "Non"])
        if rechoisir == 0:
            p_joueur = choisir_pokemon_joueur(pokedex)

        #Reset puis tirer un nouvel adversaire différent et relancer
        joueur = Dresseur("Vous", [p_joueur])
        joueur.soigner_tout()
        reste = [p for p in pokedex if p is not p_joueur]
        p_ia = random.choice(reste)
        ia = Dresseur("Adversaire", [p_ia])
        ia.soigner_tout()

        combat = Combat(joueur, ia)
        combat.demarrer()


if __name__ == "__main__":
    main()