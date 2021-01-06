#-------------------------------------------------------------------------------
# Name:        Zombies in your face
# Purpose:
#
# Author:      martinent, oddon, thebaud
#
# Created:     09/02/2015
# Copyright:   (c) thebaud 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

""" Importations """
import time
import sys
import math
import random
# Importations necessaires de la librairie Pygame
import pygame
from pygame.locals import *
""""""

# Initialisation de la librairie Pygame
pygame.init()
# Creation de la fenetre de notre programme et definition de ses parametres (dimensions, titre, icone)
window = pygame.display.set_mode( (900,300) )
pygame.display.set_caption("Zombies in your face")

# Importation et conversion (pour la rendre compatible avec pygame) de l'image
icone = pygame.image.load("Images/icone.png").convert_alpha()
pygame.display.set_icon(icone)

# On desactive l'affichage du curseur pour afficher un curseur personnalise
pygame.mouse.set_visible(False)


""" On recupere les meilleurs scores etablis precedemment"""
try :
    file = open("Files/scores.txt", "r")    # On ouvre le fichier
    high_score_kills = int(file.readline())  # On convertit la chaine de caractere lue en un nombre entier
    high_score_time = [ int(file.readline()), int(file.readline()) ]    # Minutes separees des secondes
    file.close()
except :    # Si le fichier est vide (premier lancement par exemple), les deux lignes precedentes genereraient une erreur, on l'intercepte pour ne pas bloquer le programme
    high_score_kills = 0
    high_score_time = [0,0]
""""""


""" Classes """
class Zombie :  # Chaque zombie cree sera defini selon cette classe
    pos = 0
    i_img = 0
    angle = 0
    health = 0
    alpha = 0
    rank = 0
    speed = 0
    damage = 0

    def __init__(self, rank = 0, pos = 0, speed = 0, health = 0, damage = 0 ) :
        self.rank = rank
        self.pos = pos
        self.speed = speed
        self.health = health
        self.damage = damage
""""""

# Pour le cone de vision, d'un angle de 20 degres, on a sin(20) = 0.34 et cos(20) = 0.94
cos = 0.94
sin = 0.34


""" Constantes """
X = 0
Y = 1   # X et Y serviront de reperes d'indice pour les tableaux, coordonnes (leur seule fonction est de rendre le code plus lisible et intuitif)
MN = 0
SC = 1  # De meme que pour X et Y, ils serviront de reperes d'indice pour gerer le temps
UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3    # Indices correspondant aux directions du personnage
N_IMAGES_HERO = 6
N_IMAGES_ZOMBIE = 8
N_IMAGES_DEAD_ZOMBIE = 10
N_IMAGES_PLAY_BUTTON = 2
N_IMAGES_SHOT = 4   # le nombre d'images de chaque animation pour l'objet concerne
PLAY_BUTTON_CENTER = (450, 95)
PLAY_BUTTON_RADIUS = 25     # Les coordonnees du centre du bouton PLAY ainsi que son rayon permettront de l'afficher a la bonne position mais aussi de verifier la position du curseur par rapport a la sienne
PLAYABLE_AREA = 872     # Taille de la zone jouable de la fenetre (donc en excluant la zone dediee a l'interface). C'est un carre, on ne cree pas de tuple pour cela
INTERFACE_HEIGHT = 97   # Hauteur de l'interface (l'interface epouse la largeur de la fenetre donc inutile de creer un tuple pour cela)
ORBS_SIZE = (85, 122)   # Taille des orbes de vie/experience de l'interface
CHARGER_SIZE = (19, 90) # Taille du chargeur (de l'interface)
HERO_SIZE = (52, 84)    # Taille du personnage (en position de base, c'est a dire avec un angle de rotation de 0 degres)
ZOMBIE_SIZE = (41, 38)  # Taille des zombies (tous les types de zombie ont la meme taille)
HERO_HITBOX_RADIUS = 35
ZOMBIE_HITBOX_RADIUS = 40   # La hitbox permettra de determiner si oui ou non le zombie ou le personnage se fait tirer ou taper dessus (meme principe que pour le bouton play)
CURSOR_RADIUS = 18      # Rayon du curseur, le curseur n'etant pas un seul pixel, il est necessaire de l'avoir pour afficher l'image personnalisee du curseur tout en restant coherent avec les clics
ANIMATION_SPEED_MOVING = 7      # Vitesse de l'animation de mouvement ; concretement, "tous les X tours de boucle, on affiche l'image suivante"
ANIMATION_SPEED_SHOOTING = 3    # Vitesse de l'animation de tir
HIT_ALERT_WIDTH = 5     # Largeur de la bordure rouge affichee quand le personnage subit des degats
HIT_POINTS = ((0,0), (0, PLAYABLE_AREA), (PLAYABLE_AREA, PLAYABLE_AREA), (PLAYABLE_AREA, PLAYABLE_AREA), (PLAYABLE_AREA, 0), (0,0), (HIT_ALERT_WIDTH, HIT_ALERT_WIDTH), \
                        (HIT_ALERT_WIDTH, PLAYABLE_AREA - HIT_ALERT_WIDTH), (PLAYABLE_AREA - HIT_ALERT_WIDTH, PLAYABLE_AREA - HIT_ALERT_WIDTH), (PLAYABLE_AREA - HIT_ALERT_WIDTH, HIT_ALERT_WIDTH), (HIT_ALERT_WIDTH, HIT_ALERT_WIDTH))
                        # Points de la bordure d'alerte
POS_CHRONO = ((153, 938),(184, 938))
POS_KITS = (350, 938)
POS_AMMO = (544, 938)
POS_SCORE = (717, 938)
POS_CHARGER = (428,877)
POS_LVL = (839, 894)    # Coordonnees des elements de l'interface
NUMERALS_WIDTH = 12     # Largeur des chiffres affiches
DELAY_RELOAD_GUN = 63  # Delai de rechargement de l'arme (correspond a une seconde)
MEDIKIT_HEAL = 30       # Nombre de points de vie rendus par l'utilisation d'un kit de soin
ROT_DELAY = 63         # Delai avant que les zombies morts ne commencent a disparaitre
DAMAGE_GUN = 50         # Degats infliges par le pistolet du personnage

ZOMBIES_TYPES = [Zombie(0, 0, 1.5, 50, 0.5), Zombie(1, 0, 0.75, 50, 1)]     # Les differents types de zombie (si on doit rajouter un nouveau type, il suffit de creer un nouvel archetype de zombie dans ce tableau)

IMGS_ZOMBIES = [ [], [] ]   # Tableau contenant toutes les images liees aux zombies

for i in range (2) :   # Chargement des images de zombies (morts et vivants)
    for a in range (len(ZOMBIES_TYPES)) :
        IMGS_ZOMBIES[i].append([])      # Pour chaque type de zombie (premiere "couche du tableau") on y rajoute un tableau dedie aux images du zombie vivant, et un autre pour les images du zombie mort
for i in range(N_IMAGES_ZOMBIE) :
    for a in range(len(ZOMBIES_TYPES)) :    # On ajoute chaque image de l'animation du type de zombie concerne au tableau dedie (ici zombies vivants)
        IMGS_ZOMBIES[0][a].append( pygame.image.load("Images/zombies/zombie_{1}_{0}.png".format(i,a)).convert_alpha() )
for i in range(N_IMAGES_DEAD_ZOMBIE) :
    for a in range(len(ZOMBIES_TYPES)) :    # Ici zombies morts
        IMGS_ZOMBIES[1][a].append( pygame.image.load("Images/zombies/dead_zombie_{1}_{0}.png".format(i,a)).convert_alpha() )


IMGS_HERO = [ [ [], [] ], [] ]  # Tableau contenant toutes les images liees au personnage
IMGS_TIR = []   # Tableau contenant les images liees a l'animation de tir du personnage

for i in range(N_IMAGES_HERO) : # Chargement des images du personnage (arme et a mains nues)
    IMGS_HERO[0][0].append( pygame.image.load("Images/char/char_{0}.png".format(i)).convert_alpha() )
    IMGS_HERO[0][1].append( pygame.image.load("Images/char/char_shot_{0}.png".format(i)).convert_alpha() )
for i in range(2) : # Chargement des images du personnage mort (tombes, en fonction du score obtenu)
    IMGS_HERO[1].append( pygame.image.load("Images/char/char_dead_{0}.png".format(i)).convert_alpha() )
for i in range(N_IMAGES_SHOT) : # Chargement des images de l'animation de tir
    IMGS_TIR.append( pygame.image.load("Images/char/shot_{0}.png".format(i)).convert_alpha() )


FONT = []   # Tableau contenant la police d'ecriture pour les chiffres, on l'utilise car la police que l'on desire n'existe pas dans la librairie, on utilise une methode "artisanale"
for i in range(10) :    # On charge les images de chaque chiffre (donc de 0 a 9)
    FONT.append( pygame.image.load("Images/font/{0}.png".format(i)).convert_alpha() )

IMGS_GAME_OVER = []     # Images game over (en fonction du score obtenu)
for i in range(2) :     # On charge les images correspondantes
    IMGS_GAME_OVER.append( pygame.image.load("Images/interface/end_{0}.png".format(i)).convert_alpha() )


# Differentes images d'interface
IMG_MENU = pygame.image.load("Images/interface/menu.png").convert()     # Menu
IMG_BACKGROUND = pygame.image.load("Images/interface/background.png").convert() # Fond (en jeu)
IMG_INTERFACE = pygame.image.load("Images/interface/interface.png").convert_alpha() # Interface (sur laquelle on va coller les differents elements)
IMG_LIFE_ORB = pygame.image.load("Images/interface/life_orb.png").convert_alpha()   # Orbe de vie
IMG_EXP_ORB = pygame.image.load("Images/interface/exp_orb.png").convert_alpha()     # Orbe d'experience
IMG_CHARGER = pygame.image.load("Images/interface/charger.png").convert_alpha()     # Etat du chargeur

IMG_PAUSE = pygame.image.load("Images/interface/pause.png").convert_alpha() # Image de partie mise en pause
IMGS_PLAY_BUTTON = []   # Images du bouton play du menu
for i in range(N_IMAGES_PLAY_BUTTON) :  # On charge les deux images du bouton (normal ou survole)
    IMGS_PLAY_BUTTON.append( pygame.image.load("Images/interface/play_{0}.png".format(i)).convert_alpha() )
IMG_CURSOR = pygame.image.load("Images/curseur.png").convert_alpha()    # Image personnalisee du curseur
""""""

""" Personnage """
class Hero :    # Le personnage joue sera defini selon cette classe (que l'on reinstanciera lors d'une nouvelle partie)
    pos = 0

    i_img = 0
    img = 0
    pos_bis = 0
    angle = 0

    health = 100
    health_max = 100
    xp = 0
    xp_needed = 10
    medikits = 5
    charger_capacity = 10
    ammo = 50
    charger_heating = 0
    kills = 0
    armed = False
    shot = False
    reloading_gun = False
    time_reload_elapsed = 0
    hit = False
    hit_meter = 0
    pos_shot = 0
    i_img_tir = 0
    img_tir = 0
    lvl = 1
    moving = [False,False,False,False]
    cone_points = [ [], [] ]

    def __init__(self, health_max=100, lvl=1, xp_needed=10, ammo=50, charger_capacity=10) :
        self.health_max = health_max
        self.lvl = lvl
        self.xp_needed = xp_needed
        self.ammo = ammo
        self.charger_capacity = charger_capacity
        for i in range (8) :
            for a in range(2) :
                self.cone_points[a].append(0)
        self.pos = IMGS_HERO[0][self.armed][self.i_img].get_rect()
        self.pos.center = (300,300)
        self.img = IMGS_HERO[0][0][0]
        self.pos_bis = self.pos
        self.pos_shot = self.pos

""""""


""" Fonctions """
# Fonction retournant la valeur absolue du nombre passe en parametre
def val_abs(number) :
    if (number) < 0 :
        number *= -1
    return number

# Rotation d'une image en gardant son centre
def rot_center(image, rect, angle):
	rot_image = pygame.transform.rotate(image, angle)
	w = (rect.width**2 + rect.height**2)**(1/2)
	rot_rect = rot_image.get_rect(center=rect.center, size=(w,w))
	return rot_image,rot_rect

# Calcul du deplacement du zombie concerne vers le personnage
def pathfinding (xZombie, yZombie, xHero, yHero, speed) :
    t = 0
    if(xHero-xZombie != 0 or yHero-yZombie != 0) :
        t = speed / ( ( (xHero-xZombie)**2 + (yHero-yZombie)**2 )**(1/2) )
    x = t * (xHero-xZombie)
    y = t * (yHero-yZombie)
    if(x > 0 and int(x + 0.5) > int(x) ) :
        x += 0.5
    elif(x < 0 and int(x - 0.5) < int(x) ) :
        x -= 0.5
    if(y > 0 and int(y + 0.5) > int(y) ) :
        y += 0.5
    elif(y < 0 and int(y - 0.5) < int(y) ) :
        y -= 0.5
    return x, y

# Decompose un nombre entier (> 10) et renvoie un tableau contenant un chiffre par case
def decompose (number) :
    pas = 1
    while ( int(number/pas) > 9 ) :
        pas *= 10
    chiffres = []
    while(pas > 0 ) :
        chiffres.append(int(number/pas))
        number -= int(number/pas)*pas
        pas = int(pas/10)
    return chiffres

# Calcule l'angle de rotation d'un objet par rapport a un autre (personnage par rapport au curseur / zombie par rapport au personnage)
def angle(pos_1, pos_2) :
    dx = pos_1[X] - pos_2[X]
    dy = pos_1[Y] - pos_2[Y]
    rads = math.atan2(-dy,dx)
    angle = math.degrees(rads) - 90
    return angle

# Calcul des points du cone de vision
def cone(x1, y1, x2, y2) :
    Points = [ [x1,y1], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [x1, y1] ]
    for i in range (3) :
        F = y2 - y1
        E = x2 - x1
        if(i+1 == 1) :
            E = E*cos + F*sin
            F = F*cos - E*sin
        else :
            E = E*cos - F*sin
            F = F*cos + E*sin
        C = [x1, y1]
        Z = [E, F]
        I=0
        J=0
        ebis = 1
        for e in range(2) :
            a = -1
            for h in range (2) :
                P = ( PLAYABLE_AREA * h - C[e] * a ) / ( Z[e] * a )
                if(P > 0) :
                    K = C[ebis] + P * Z[ebis]
                    if(K>=0 and K<= PLAYABLE_AREA) :
                        I = h * PLAYABLE_AREA * ebis + e * int(K)
                        J = (a+1)*PLAYABLE_AREA*e*h/2 + ebis*int(K)
                        break
                a *= -1
            ebis = 0
        Points[i+1] = [I,J]
    Points[6] = Points[2]
    Points[2] = [0,0]
    if(Points[1][X] >= 0 ) :
        if(Points[1][Y] == 0) :
            Points[2] = [0,0]
            Points[3] = [0, PLAYABLE_AREA]
            Points[4] = [PLAYABLE_AREA, PLAYABLE_AREA]
            Points[5] = [PLAYABLE_AREA, 0]
        elif(Points[1][Y] == PLAYABLE_AREA) :
            Points[2] = [PLAYABLE_AREA,PLAYABLE_AREA]
            Points[3] = [PLAYABLE_AREA, 0]
            Points[4] = [0, 0]
            Points[5] = [0, PLAYABLE_AREA]
    if(Points[1][Y] >= 0) :
        if(Points[1][X] == 0) :
            Points[2] = [0,PLAYABLE_AREA]
            Points[3] = [PLAYABLE_AREA, PLAYABLE_AREA]
            Points[4] = [PLAYABLE_AREA, 0]
            Points[5] = [0, 0]
        elif(Points[1][X] == PLAYABLE_AREA) :
            Points[2] = [PLAYABLE_AREA,0]
            Points[3] = [0, 0]
            Points[4] = [0, PLAYABLE_AREA]
            Points[5] = [PLAYABLE_AREA, PLAYABLE_AREA]
    for i in range(len(Points)) :
        Points[i] = tuple(Points[i])
    Points = tuple(Points)
    return Points

""""""

""" Variables """
dark = pygame.Surface((PLAYABLE_AREA,PLAYABLE_AREA), pygame.SRCALPHA)   # Surface qui servira a appliquer le cone de vision (sur laquelle on colle l'obscurite en dehors du cone)
img_hit = pygame.Surface((PLAYABLE_AREA, PLAYABLE_AREA), pygame.SRCALPHA)   # Surface qui servira a alerter le joueur qu'il subit des degats (bordure rouge)

# Etats des differents menus
on_menu=True
in_game=False
paused=False
game_over=False
alpha_game_over = 0 # Variable utilisee pour le fondu lors du game over
boolean = False     # Stockera le resultat du test "le joueur a t-il battu le meilleur score ?"

hero = Hero()   # Le personnage joue

zombies = []    # Tableau contenant tous les zombies

# Variables pour maitriser le temps ecoule
time_elapsed = [0,0]    # Temps ecoule general
time_elapsed_pop = 0    # Temps entre deux apparitions de zombie
pop_delay = 300         # Delai de base entre deux apparitions de zombie (decroissant pour augmenter la difficulte au fil du temps)

i_img_play_button = 0   # Indice permettant de savoir quelle image du bouton play doit etre affichee (normal ou survole)

pos_cursor = (0,0)  # Position du curseur

run = True
while(run) :    # Boucle principale, en sortir signifie quitter le programme (lorsque la variable run vaut "False", cela revient a quitter le programme)

    # Affichage des images dans la fenetre selon quel menu est actif
    if(on_menu) :  # Si on est sur le menu
        window.blit( IMG_MENU, (0,0) )  # On affiche evidemment l'image du menu
        window.blit( IMGS_PLAY_BUTTON[i_img_play_button], ( val_abs(PLAY_BUTTON_CENTER[X]-PLAY_BUTTON_RADIUS) , val_abs(PLAY_BUTTON_CENTER[Y]-PLAY_BUTTON_RADIUS) ) )   # Mais aussi le bouton selon son etat

    elif (in_game or paused or game_over) : # Si on est en jeu
        window.blit( IMG_BACKGROUND, (0,0) )    # On affiche d'abord l'image de fond
        for i in range (len(zombies)) :     # Puis chaque zombie
            if(zombies[i].health > 0) :     # (= "Si le zombie est vivant")
                img, pos = rot_center(IMGS_ZOMBIES[0][zombies[i].rank][int(zombies[i].i_img/ANIMATION_SPEED_MOVING)], zombies[i].pos, zombies[i].angle)    # On oriente chaque zombie vers le personnage
                window.blit( img, pos )     # Et on affiche l'image orientee avec la position correspondante
            else :  # Si le zombie est mort
                if(int((zombies[i].alpha - ROT_DELAY)/10) < N_IMAGES_DEAD_ZOMBIE) :    # On verifie que l'on ne depasse pas le nombre d'images de l'animation
                    if(int((zombies[i].alpha - ROT_DELAY)/10) > 0 ) :   # Si la premiere seconde avant le debut de la disparition du zombie s'est deja ecoulee
                        img = IMGS_ZOMBIES[1][zombies[i].rank][int((zombies[i].alpha-ROT_DELAY)/10)]    # On choisit l'image du zombie avec la transparence associee
                    else :  # Si la seconde ne s'est en revanche pas encore ecoulee
                        img = IMGS_ZOMBIES[1][zombies[i].rank][0]   # On choisit la premiere image (sans transparence) de zombie mort
                    img_bis, pos_bis = rot_center(img, zombies[i].pos, zombies[i].angle)    # On l'oriente selon l'orientation qu'avait le zombie au moment de sa mort
                    window.blit( img_bis, pos_bis )     # Affichage de l'image du zombie, definie selon les conditions precedentes
                    if(in_game) :   # Si la partie est mise en pause, l'animation de disparition des zombies sera egalement mise en pause
                        zombies[i].alpha += 1   # On incremente le compteur pour determiner la transparence a afficher du zombie

        if(game_over) : # Animation de game over
            if(alpha_game_over < 254) : # L'opacite allant de 0 a 255, on verifie que l'on ne depasse pas sa valeur maximale
                alpha_game_over += 2    # On l'incremente pour augmenter l'opacite (effet "fondu")
                dark.fill(Color(0,0,0,alpha_game_over)) # On colle une surface noire selon cette meme opacite
                window.blit(dark, (0,0))    # Et on affiche cette surface sur la fenetre
                window.blit(IMGS_HERO[1][boolean], hero.pos)    # Ainsi que l'image du personnage mort (qui differe selon si le joueur a battu le meilleur score ou non)
            else :  # Une fois le fondu noir fini,
                window.blit(IMGS_GAME_OVER[boolean], (0,0)) # On affiche l'ecran final (qui lui aussi differe selon si le joueur a battu le meilleur score ou non)


        if(in_game or paused) : # Si on est en jeu ou en pause, on affiche le cone de vision (en revanche on ne calcule ses points que lorsque l'on est en jeu)
            dark.fill(Color(0,0,0,0)) # Permet de "reinitialiser" la surface sans devoir la redefinir
            pygame.draw.polygon(dark, Color(0,0,0,250), hero.cone_points)   # On remplit la zone de "non vision" sur la surface, selon les points calcules
            window.blit(dark, (0,0))    # Et on colle cette surface sur la fenetre
            if(hero.hit and int(hero.hit_meter/10) == hero.hit_meter/10) :  # Si le joueur est actuellement en train de subir des degats + on affiche la bordure qu'une image sur 10, pour faire un effet clignotant plus visible
                pygame.draw.polygon(img_hit, Color('red'), HIT_POINTS)  # On colle la bordure rouge
                window.blit(img_hit, (0,0)) # Et on l'affiche sur la fenetre
            window.blit( hero.img, hero.pos_bis )   # Affichage du personnage a ses coordonnees
        window.blit( IMG_INTERFACE, (0,0) ) # On colle ensuite l'interface
        if(hero.health > 0) :   # On affiche une partie seulement de l'orbe selon la vie manquante (Si le joueur possede 10% de sa vie, 10% de l'image en partant du bas seront affiches)
            window.blit( IMG_LIFE_ORB, (0, PLAYABLE_AREA + INTERFACE_HEIGHT - ORBS_SIZE[Y] + ORBS_SIZE[Y] * (hero.health_max - hero.health) * (1/hero.health_max) ), \
                    (0, ORBS_SIZE[Y] * (hero.health_max - hero.health) * (1/hero.health_max) , ORBS_SIZE[X], ORBS_SIZE[Y]) )
        if(hero.xp > 0) :       # Meme principe que pour l'orbe de vie
            window.blit( IMG_EXP_ORB, (PLAYABLE_AREA-ORBS_SIZE[X], PLAYABLE_AREA + INTERFACE_HEIGHT - ORBS_SIZE[Y] + ORBS_SIZE[Y] * (hero.xp_needed - hero.xp) * (1/hero.xp_needed) ), \
                    (0, ORBS_SIZE[Y] * (hero.xp_needed - hero.xp) * (1/hero.xp_needed) , ORBS_SIZE[X], ORBS_SIZE[Y]) )

        # Affichage du score
        numerals = decompose(hero.kills)    # On recupere le nombre de zombies tues dans un tableau (un chiffre par case)
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_SCORE[X] + i * NUMERALS_WIDTH , POS_SCORE[Y] ) )  # Et on affiche ces chiffres un par un, a la suite

        # Affichage du temps ecoule
        numerals = decompose( time_elapsed[SC] )    # On recupere le temps (en secondes) ecoule, avec un chiffre par case
        if(len(numerals) < 2) :
            numerals.append(numerals[0])    # On complete le tableau avec des 0 pour avoir un affichage du type "02 : 09" et non pas "2 :9" (purement esthetique)
            numerals[0] = 0
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_CHRONO[SC][X] + i * NUMERALS_WIDTH, POS_CHRONO[SC][Y] ) ) # Et on affiche ces chiffres

        numerals = decompose( time_elapsed[MN] )    # On recupere le temps (en minutes) ecoule, avec un chiffre par case
        if(len(numerals) < 2) :
            numerals.append(numerals[0])    # Meme operation ici, on complete le tableau
            numerals[0] = 0
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_CHRONO[MN][X] + i * NUMERALS_WIDTH, POS_CHRONO[MN][Y] ) ) # Et on affiche ces chiffres

        # Affichage du nombre de kits de soin
        numerals = decompose(hero.medikits) # Comme precedemment, on recupere les chiffres
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_KITS[X] + i * NUMERALS_WIDTH , POS_KITS[Y] ) )    # Et on les affiche

        # Affichage du nombre de munitions
        numerals = decompose(hero.ammo)     # Idem
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_AMMO[X] + i * NUMERALS_WIDTH , POS_AMMO[Y] ) )    # Et idem

        # Affichage de l'etat du chargeur, comme pour les orbes de vie et d'experience, selon le pourcentage d'echauffement du chargeur (au bout de 10 balles tirees a la suite, le chargeur est vide)
        window.blit( IMG_CHARGER, (POS_CHARGER[X], POS_CHARGER[Y] + CHARGER_SIZE[Y] * hero.charger_heating * 0.1 ), (0, CHARGER_SIZE[Y] * hero.charger_heating * 0.1, CHARGER_SIZE[X], CHARGER_SIZE[Y] ) )

        # Affichage du niveau du personnage (que l'on ecrit sur l'orbe d'experience)
        numerals = decompose(hero.lvl)
        for i in range(len(numerals)) :
            window.blit( FONT[numerals[i]], ( POS_LVL[X] + i * NUMERALS_WIDTH , POS_LVL[Y] ) )

        # Affichage de l'animation de tir
        if(hero.shot) :
            window.blit( hero.img_tir, hero.pos_shot )

        # Affichage de l'image de pause si pause il y a
        if (paused) :
            window.blit( IMG_PAUSE, (0,0) )


    window.blit( IMG_CURSOR, (pos_cursor[X]-CURSOR_RADIUS, pos_cursor[Y]-CURSOR_RADIUS) )    # Affichage du curseur personnalise

    pygame.display.flip()   # Actualisation de l'affichage

    # Interception de tous les evenements (clavier, souris, ...)
    for event in pygame.event.get() :

        # Evenement "Quitter fenetre (croix)"
        if event.type == QUIT :
            run = False     # On quitte le programme

        # Evenement "Clic gauche souris"
        if event.type == MOUSEBUTTONDOWN and event.button == 1 :

            posClic = ( event.pos[X] , event.pos[Y] )   # Recuperation de la position du curseur au moment du clic

            if(on_menu) :  # Gestion de l'evenement "clic" quand on est sur le menu
                # Le joueur a t-il clique sur le bouton play ?
                distance_bouton_play = ( val_abs(PLAY_BUTTON_CENTER[X]-posClic[X]) , val_abs(PLAY_BUTTON_CENTER[Y]-posClic[Y]) )
                if(distance_bouton_play[X]<=PLAY_BUTTON_RADIUS and distance_bouton_play[Y]<=PLAY_BUTTON_RADIUS) :   # Verification de la distance curseur <-> centre du bouton
                    # On lance la partie et readapte la fenetre
                    on_menu=False
                    in_game=True
                    window = pygame.display.set_mode( (PLAYABLE_AREA, PLAYABLE_AREA+INTERFACE_HEIGHT) )
                    # On reinitialise (utile a partir du deuxieme lancement de partie)
                    hero = Hero()
                    zombies = []
                    time_elapsed = [0,0]
                    time_elapsed_pop = 0
                    pop_delay = 300

            elif (in_game) :    # Si l'on est en jeu, le clic signifie "tirer"
                if(hero.reloading_gun == False) :   # On verifie que le personnage ne soit pas en train de recharger
                    if(hero.ammo > 0 and hero.charger_heating < 10) :   # Et que son chargeur n'est pas vide
                        hero.armed = True   # Il passe en mode "arme" (de base, mains nues)
                        hero.shot = True    # Ce booleen permettra de regir l'animation de tir (on la lance a partir de la)
                        hero.ammo -= 1      # Le personnage perd donc une munition
                        hero.charger_heating += 1   # Et son chargeur egalement

                        # Le joueur a t-il clique sur un zombie ?
                        for i in range(len(zombies)) :
                            distance = ( val_abs(zombies[i].pos.center[X]-posClic[X]) , val_abs(zombies[i].pos.center[Y]-posClic[Y]) )
                            if(distance[X] <= ZOMBIE_HITBOX_RADIUS and distance[Y] <= ZOMBIE_HITBOX_RADIUS) :   # Verification de la distance curseur <-> centre de la hitbox du zombie
                                if(zombies[i].health > 0) :     # Si le zombie n'etait pas mort,
                                    zombies[i].health -= DAMAGE_GUN     # il perd un montant de points de vie egal aux degats de l'arme
                                    if(zombies[i].health == 0) :    # Si sa vie arrive a 0, il meurt donc, on recupere l'orientation qu'il avait au moment de mourir
                                        zombies[i].angle_dead = zombies[i].angle
                                    hero.kills += 1     # On incremente le score du joueur
                                    if( hero.xp < hero.xp_needed ) :    # Le personnage gagne de l'experience a chaque zombie tue
                                        hero.xp += 1
                                    if (hero.xp == hero.xp_needed ) :   # Si il atteint les 100% d'experience, on la remet a 0 et le personnage passe au niveau superieur
                                        hero.xp = 0
                                        hero.xp_needed += 5
                                        hero.lvl += 1
                                        hero.health_max += 10           # Pour avantager le joueur, on lui redonne toute sa vie et des munitions
                                        hero.health = hero.health_max
                                        hero.ammo += 3 + hero.lvl * 5
                    elif(hero.charger_heating == 10) :  # Si le joueur clique alors que son chargeur etait vide, on lance le rechargement de l'arme
                        hero.reloading_gun = True


        # Evenement "curseur deplace"
        if event.type == MOUSEMOTION :
            pos_cursor = ( event.pos[X], event.pos[Y] ) # On recupere la position du curseur
            if(on_menu) :   # Sur le menu,
                # On verifie si le curseur se trouve sur le bouton play
                distance_bouton_play = ( val_abs(PLAY_BUTTON_CENTER[X]-pos_cursor[X]) , val_abs(PLAY_BUTTON_CENTER[Y]-pos_cursor[Y]) )
                if(distance_bouton_play[X]<=PLAY_BUTTON_RADIUS and distance_bouton_play[Y]<=PLAY_BUTTON_RADIUS) :
                    # On change l'affichage du bouton
                    i_img_play_button = 1
                else :
                    i_img_play_button = 0

        # Evenement "touche enfoncee"
        if event.type == KEYDOWN :
            key = event.key     # On recupere la touche enfoncee
            # On associe la touche enfoncee au mouvement correspondant
            if(key == pygame.K_w) :
                hero.moving[UP] = True
            if(key == pygame.K_s) :
                hero.moving[DOWN] = True
            if(key == pygame.K_d) :
                hero.moving[RIGHT] = True
            if(key == pygame.K_a) :
                hero.moving[LEFT] = True

            if(key == pygame.K_SPACE) : # Raccourci pour mettre le jeu en pause
                if(in_game) :   # Si on etait en jeu, on passe en pause
                    in_game = False
                    paused = True
                elif(paused) :  # Inversement si on etait en pause, on repasse en jeu
                    paused = False
                    in_game = True
            if(paused) :
                if(key == pygame.K_ESCAPE) :  # Raccourci pour retourner au menu (et interrompre par ailleurs la partie)
                    in_game = False
                    paused = False
                    on_menu = True
                    window = pygame.display.set_mode((900,300)) # On readapte la fenetre
            if(in_game) :
                if(key == pygame.K_1) : # Raccourci pour utiliser un kit de soin
                    if(hero.health < hero.health_max and hero.medikits > 0) :   # On ne l'utilise que si le personnage possede des kits de soin et n'est pas au maximum de sa vie
                        hero.medikits -= 1
                        hero.health += MEDIKIT_HEAL
                        if(hero.health > hero.health_max) :     # Si bien sur le personnage a de la vie en exces, on la ramene a la vie maximale
                            hero.health = hero.health_max
            if(game_over) :
                if(key == pygame.K_ESCAPE) :    # On peut interrompre l'animation de game over en appuyant sur Echap pour revenir au menu
                    game_over = False
                    on_menu = True
                    window = pygame.display.set_mode((900,300))

        # Evenement "touche relachee"
        if event.type == KEYUP :
            key = event.key     # On recupere la touche relachee
            if(key == pygame.K_w) :
                hero.moving[UP] = False
            if(key == pygame.K_s) :
                hero.moving[DOWN] = False
            if(key == pygame.K_d) :
                hero.moving[RIGHT] = False
            if(key == pygame.K_a) :
                hero.moving[LEFT] = False

            if(in_game) :
                if(key == pygame.K_r) : # Raccourci pour recharger l'arme
                    if( hero.charger_capacity - hero.charger_heating < hero.charger_capacity ) :
                        hero.reloading_gun = True

    # Apres l'affichage et le traitement des evenements, c'est ici que seront traites trajectoires, calculs et autres
    if(in_game) :

        # Calcul des points du cone de vision
        hero.cone_points = cone(hero.pos.center[X], hero.pos.center[Y], pos_cursor[X], pos_cursor[Y])

        # Orientation du personnage
        hero.angle = angle(pos_cursor, hero.pos.center) # On calcule l'angle par rapport au curseur
        hero.img, hero.pos_bis = rot_center(IMGS_HERO[0][hero.armed][int(hero.i_img/ANIMATION_SPEED_MOVING)], hero.pos, hero.angle)    # Et on modifie l'image par rapport a cet angle

        # Gestion des deplacements du personnage
        if(hero.moving[UP] or hero.moving[DOWN] or hero.moving[LEFT] or hero.moving[RIGHT]) :
            # Si le joueur se deplace a droite
            if hero.moving[RIGHT] :
                # On verifie qu'il ne depasse pas le bord droit de la fenetre
                if(hero.pos.center[X] < PLAYABLE_AREA - (HERO_SIZE[Y]/2) ) :
                    hero.pos = hero.pos.move(2,0)  # Si il est bien dans la fenetre, on le deplace vers la droite

            # Idem, vers la gauche
            if hero.moving[LEFT] :
                if(hero.pos.center[X] > HERO_SIZE[X]/2) :
                    hero.pos = hero.pos.move(-2,0)

            # Idem, vers le haut
            if hero.moving[UP] :
                if(hero.pos.center[Y] > HERO_SIZE[Y]/2) :
                    hero.pos = hero.pos.move(0,-2)

            # Idem, vers le bas
            if hero.moving[DOWN] :
                if(hero.pos.center[Y] < PLAYABLE_AREA - (HERO_SIZE[Y]/2) ) :
                    hero.pos = hero.pos.move(0,2)

            # On incremente le compteur qui permet de gerer l'animation du personnage (Tous les 10 tours de boucle, on passe a l'image suivante)
            hero.i_img += 1
            if(hero.i_img >= N_IMAGES_HERO*ANIMATION_SPEED_MOVING) :   # Si le compteur atteint sa valeur maximale (nombre d'images * vitesse d'animation), on le remet a 0
                hero.i_img = 0
        else :
            # Si le joueur arrete de bouger, on reinitialise l'animation
            hero.i_img = 0


        # Animation de tir
        if(hero.shot) :
            hero.i_img_tir += 1 # On incremente l'indice d'animation
            if(hero.i_img_tir >= N_IMAGES_SHOT*ANIMATION_SPEED_SHOOTING) : # Meme principe que precedemment
                hero.i_img_tir = 0
                hero.shot = False
            hero.img_tir, hero.pos_shot = rot_center( IMGS_TIR[int(hero.i_img_tir/3)], hero.pos, hero.angle )

        # Gestion du rechargement de l'arme (declenche par clic ou par appui de la touche R)
        if(hero.reloading_gun) :
            hero.time_reload_elapsed += 1   # On incremente le compteur de temps de rechargement
            if(hero.time_reload_elapsed == DELAY_RELOAD_GUN) :  # Apres la seconde de delai, on recharge l'arme
                if(hero.ammo >= hero.charger_capacity) :    # Dans le cas ou il y a plus de munitions que la capacite totale du chargeur
                    hero.charger_heating -= hero.charger_capacity   # On remplit simplement le chargeur
                elif(hero.ammo < hero.charger_capacity and hero.ammo > 0) : # En revanche dans le cas ou il y a moins de munitions que la capacite totale du chargeur
                    hero.charger_heating -= hero.ammo   # On remplit le chargeur seulement d'autant de munitions qu'il reste au personnage
                if(hero.charger_heating < 0) :  # Dans le cas d'un rechargement declenche manuellement (touche R), ces calculs entraineraient l'echauffement en negatif, on le ramene a 0
                    hero.charger_heating = 0
                hero.reloading_gun = False  # Le rechargement est termine
                hero.time_reload_elapsed = 0    # On reinitialise le chronometre de rechargement



        # Gestion de l'apparition aleatoire de zombies aux bords de l'ecran
        if(time_elapsed_pop >= pop_delay) : # On ne fait apparaÃƒÂ®tre un zombie que quand le delai entre deux apparitions est ecoule
            time_elapsed_pop -= pop_delay
            if(pop_delay > 40) :    # On plafonne le delai minimal (pour eviter d'avoir une infinite de zombies qui apparaitraient en meme temps)
                pop_delay -= 10 # Sinon on le reduit pour augmenter la frequence d'apparition
            random_pop = random.randint(1, PLAYABLE_AREA)   # On choisit aleatoirement quelle position (de 1 a la taille de la zone jouable) aura le zombie a son apparition
            random_axe = random.randint(X,Y)    # On choisit aleatoirement sur quel axe sera le zombie (Cote droit/gauche ou haut/bas)
            random_side = random.randint(0,1)   # Puis on determine quelle cote (droit ou gauche si l'axe est X, et haut ou bas si l'axe est Y)

            random_rank = random.randint(0, len(ZOMBIES_TYPES)-1)   # On choisit aleatoirement un type de zombie
            pos = IMGS_ZOMBIES[0][random_rank][0].get_rect()    # On recupere les parametres de l'image associee au type concerne
            # Et on rajoute ce nouveau zombie au tableau de zombies, en l'initialisant selon les parametres du type concerne
            zombies.append( Zombie(random_rank, pos, ZOMBIES_TYPES[random_rank].speed, ZOMBIES_TYPES[random_rank].health, ZOMBIES_TYPES[random_rank].damage) )

            if(random_axe==X) : # Si l'axe X a ete tire
                zombies[len(zombies)-1].pos = zombies[len(zombies)-1].pos.move(random_pop, (random_side*(PLAYABLE_AREA-ZOMBIE_SIZE[Y])) )   # On place le zombie aleatoirement
            elif(random_axe==Y) :   # Si l'axe Y a ete tire
                zombies[len(zombies)-1].pos = zombies[len(zombies)-1].pos.move( (random_side*(PLAYABLE_AREA-ZOMBIE_SIZE[X])) , random_pop)  # On place le zombie aleatoirement

        # On gere le deplacement et l'orientation de chaque zombie vers le personnage
        hero.hit = False    # On reinitialise le booleen "subit des degats"
        for i in range (len(zombies)) : # Pour chaque zombie,
            if(zombies[i].health > 0) : # si celui ci est vivant,
                # on le deplace,
                zombies[i].pos = zombies[i].pos.move((pathfinding(zombies[i].pos[X], zombies[i].pos[Y], hero.pos.center[X], hero.pos.center[Y], zombies[i].speed)))
                # et s'il est au contact du personnage, ce dernier perd de la vie (verification de la distance zombie <-> personnage)
                distance_zombie = ( val_abs(zombies[i].pos.center[X]-hero.pos.center[X]), val_abs(zombies[i].pos.center[Y]-hero.pos.center[Y]) )
                # Si il y a collision avec la hitbox du personnage
                if( distance_zombie[X]-HERO_HITBOX_RADIUS-ZOMBIE_HITBOX_RADIUS <= 0 and distance_zombie[Y]-HERO_HITBOX_RADIUS-ZOMBIE_HITBOX_RADIUS <=0 ) :
                    # Ce dernier subit des degats
                    if(hero.health - zombies[i].damage > 0) :   # Si le coup subit n'acheve pas le personnage,
                        hero.hit = True     # on declenche l'alerte (bordure rouge)
                        hero.hit_meter += 1 # on incremente le compteur d'alerte (utilise pour l'effet clignotant)
                        hero.health -= zombies[i].damage    # On deduit les degats du zombie a la vie du personnage
                    else :      # Mort du personnage -> ecran de 'game over'
                        hero.health = 0
                        alpha_game_over = 0
                        in_game=False
                        game_over=True
                        boolean=bool(time_elapsed[MN] > high_score_time[MN] or (time_elapsed[MN] == high_score_time[MN] and time_elapsed[SC] > high_score_time[SC]))    # On verifie si le joueur a battu le meilleur score
                        if(boolean) :   # Si c'est le cas,
                            high_score_kills = hero.kills
                            high_score_time = time_elapsed  # on met a jour les meilleurs scores
                            file = open("Files/scores.txt", "w")    # On ouvre le fichier du meilleur score
                            file.write(str(high_score_kills) + "\n")
                            file.write(str(high_score_time[MN]) + "\n")
                            file.write(str(int(high_score_time[SC])))   # Et on le met a jour en remplacant par le nouveau score etabli
                            file.close()
                            break;

                zombies[i].i_img += 1   # On incremente l'indice d'animation de deplacement du zombie
                if(zombies[i].i_img >= N_IMAGES_ZOMBIE*ANIMATION_SPEED_MOVING) :    # On verifie qu'il ne depasse pas sa valeur maximale
                    zombies[i].i_img = 0    # Sinon on le reinitialise

                # Orientation du zombie vers le personnage
                zombies[i].angle = angle(hero.pos.center, zombies[i].pos.center)


    # Gestion du temps ecoule en jeu
    if(in_game) :
        time_elapsed[SC] += 0.016   # En prenant compte du temps d'execution d'une boucle, le temps reel ecoule n'est pas le meme que le temps de repos entre deux boucles
        if(time_elapsed[SC] >= 60) :    # Si les secondes atteignent 60, on incremente les minutes et on ramene les secondes a un nombre correct
            time_elapsed[SC] -= 60
            time_elapsed[MN] += 1
        time_elapsed_pop += 1   # On incremente egalement le chronometre d'apparition des zombies

    time.sleep(0.01)    # Temps de repos entre deux boucles


pygame.quit()   # Fin du programme