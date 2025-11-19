#for terminal (colors, bars, banner, nice messages)

# ---- COULEURS ----
try:
    from colorama import init as colorama_init, Fore, Style
    # Initialiser Colorama dès l'import
    colorama_init(autoreset=True)

    def C(txt, col=""):  # colorize
        return f"{col}{txt}{Style.RESET_ALL}" if col else txt

    COL = {
        "RED": Fore.RED,
        "GREEN": Fore.GREEN,
        "YELLOW": Fore.YELLOW,
        "BLUE": Fore.BLUE,
        "CYAN": Fore.CYAN,
        "MAGENTA": Fore.MAGENTA,
        "WHITE": Fore.WHITE,
    }

except Exception:
    # fallback sans couleur
    def C(txt, col=""): return txt
    COL = {
        "RED": "",
        "GREEN": "",
        "YELLOW": "",
        "BLUE": "",
        "CYAN": "",
        "MAGENTA": "",
        "WHITE": "",
    }

# ---- barres en ASCII ----
def barre_vie(pv: int, pv_max: int, longueur: int = 22) -> str:
    pv = max(0, min(pv, pv_max))
    rempli = int(round((pv / pv_max) * longueur)) if pv_max > 0 else 0
    return "[" + "█" * rempli + "-" * (longueur - rempli) + f"] {pv}/{pv_max}"

# ---- Slow print (typewriter) qui préserve les séquences ANSI ----
import sys, time, re

# Séquences ANSI de type \x1b[ ... m
_ANSI = re.compile(r'\x1b\[[0-9;]*m')

def slow_print(txt: str, vitesse: float = 0.02):
    pos = 0
    # Parcourt les séquences ANSI pour ne jamais les découper caractère par caractère
    for m in _ANSI.finditer(txt):
        # 1) animer la partie "texte normal" avant la séquence ANSI
        segment = txt[pos:m.start()]
        for ch in segment:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(vitesse)
        # 2) écrire la séquence ANSI d’un seul coup (pas d’attente)
        sys.stdout.write(m.group())
        sys.stdout.flush()
        pos = m.end()
    # 3) animer le reste (après la dernière séquence ANSI)
    segment = txt[pos:]
    for ch in segment:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(vitesse)
    print()

# ---- (ASCII POKEMON) ----
BANNER = r"""
██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║
██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""

def print_banner():
    print(C(BANNER, COL["CYAN"]))

# ---- AFFICHAGE ----
def format_pokemon_line(p):
    return f"{p.nom} [{p.type.value}] — {barre_vie(p.pv, p.pv_max)}  ATK: {p.attaque}"

def afficher_etat_deux(joueur_poke, ia_poke):
    print("\n" + "─" * 52)
    print("ÉTAT DES PV")
    print("Vous :", C(barre_vie(joueur_poke.pv, joueur_poke.pv_max), COL["GREEN"]))
    print("IA   :", C(barre_vie(ia_poke.pv, ia_poke.pv_max), COL["YELLOW"]))
    print("─" * 52)

# ---- COMBAT ----
def announce_attack(auteur: str, degats: int, mult: float, you_are_player: bool = True):
    note = " (SUPER efficace !)" if mult > 1 else " (peu efficace...)" if mult < 1 else ""
    icon = "⚔️ "
    col  = COL["BLUE"] if you_are_player and auteur == "Joueur" else COL["MAGENTA"]
    slow_print(C(f"{icon} {auteur} attaque et inflige {degats} dégâts{note}.", col))

def announce_potion(auteur: str, healed: int, you_are_player: bool = True):
    icon = "💊"
    col  = COL["GREEN"] if (you_are_player and auteur == "Joueur") else COL["YELLOW"]
    slow_print(C(f"{icon} {auteur} utilise une potion : +{healed} PV.", col))

def announce_pass(auteur: str):
    slow_print(C(f"⏭️  {auteur} passe son tour.", COL["WHITE"]))

def announce_ko(nom_poke: str, victory: bool):
    if victory:
        slow_print(C(f"🏆 {nom_poke} est KO ! Vous gagnez le combat !", COL["GREEN"]))
    else:
        slow_print(C(f"💀 Votre Pokémon {nom_poke} est KO ! Vous avez perdu…", COL["RED"]))

def resume_final(joueur_poke, ia_poke, victory: bool):
    cadre = "═" * 50
    print("\n" + cadre)
    titre = "🏆 VICTOIRE !" if victory else ""
    print(C(titre, COL["GREEN"] if victory else COL["RED"]))

def victory_screen():
    print(C(r"""
    ██╗    ██╗██╗███╗   ██╗
    ██║    ██║██║████╗  ██║
    ██║ █╗ ██║██║██╔██╗ ██║
    ██║███╗██║██║██║╚██╗██║
    ╚███╔███╔╝██║██║ ╚████║
    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝
    """, COL["GREEN"]))
    slow_print(C("🏆 Félicitations, vous avez gagné le combat !", COL["GREEN"]), 0.02)


def defeat_screen():
    print(C(r"""
   ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ 
  ██╔═══  ╗██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
  ██║     ║███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║██║   ██║██╔══╝  ██╔══██╗
  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝╚██████╔╝███████╗██║  ██║
   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
    """, COL["RED"]))
    slow_print(C("A Bientot looser !", COL["RED"]), 0.05)
