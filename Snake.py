import pygame
from enum import Enum
import random
import numpy as np

pygame.init()

# Type de case
class Type_case(Enum):
    VIDE = 0
    POMME = 1
    SERPENT_CORPS = 2
    SERPENT_TETE = 3
    
# Type de direction (case serpent / serpentTete)
class Type_direction(Enum):
    HAUT = 1
    DROITE = 2
    BAS = -1
    GAUCHE = -2

# Longueur / Hauteur de l'application
width = 800
height = 495
screen = pygame.display.set_mode((width, height))
 
# Taille des cases
taille_case = 33 # 18 cases par ligne / 15 cases par colonne --- 33 pixel par case
 
# Etat du jeu au lancement de l'app
etat_app = 'menu'

# Modif taille IA fenetre 
global tailleAjoutFenetre
tailleAjoutFenetre = 200 #taille sumplémentaire de la fenetre IA pour ajout d'informations

# Nombre de partie (pour l'IA)
nombrePartie = 0

# Couleurs
FOND = (200,200,200)
GRAY = (122, 122, 122)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SERPENT_CORPS_COULEUR = (72, 235, 54)

# Image
image_tete_serpent_bas = pygame.image.load("ressources/tete_serpent.png")
image_tete_serpent_bas = pygame.transform.scale(image_tete_serpent_bas, (taille_case, taille_case))
image_tete_serpent_droite = pygame.transform.rotate(image_tete_serpent_bas, 90)
image_tete_serpent_haut = pygame.transform.rotate(image_tete_serpent_bas, 180)
image_tete_serpent_gauche = pygame.transform.rotate(image_tete_serpent_bas, 270)

image_pomme = pygame.image.load("ressources/pomme.png")
image_pomme = pygame.transform.scale(image_pomme, (taille_case,taille_case))

# Texte 
font40 = pygame.font.Font(None, 40)
font50 = pygame.font.Font(None, 50)
font60 = pygame.font.Font(None, 60)
font80 = pygame.font.Font(None, 80)



# Fonction du jeu
def coordonnées_case(case):
    return (case[0]*taille_case,case[1]*taille_case)

    # Creation du jeu humain
global jeu_cree
jeu_cree = False
def creation_jeu_humain():
    global bouton_restart_jeu_humain, bouton_menu_jeu_humain, score, cycle
    score = 0
    cycle = 0
    width_game = 594 #longueur du jeu
    
    # Zone externe au jeu
    pygame.draw.rect(screen, FOND, (width_game, 0, 200+6, 600))
    pygame.draw.line(screen, BLACK, (width_game, 0), (width_game, height), 2)   

    bouton_menu_jeu_humain = pygame.draw.rect(screen, GRAY, (635, 410, 130, 60))
    text_surface = font40.render("Menu", True, BLACK)
    text_rect = text_surface.get_rect(center=(700, 440))
    screen.blit(text_surface, text_rect)

    bouton_restart_jeu_humain = pygame.draw.rect(screen, GRAY, (635, 330, 130, 60))
    text_surface = font40.render("Restart", True, BLACK)
    text_rect = text_surface.get_rect(center=(700, 360))
    screen.blit(text_surface, text_rect)
    
    text_surface = font40.render("Score : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(680,50))
    screen.blit(text_surface, text_rect)
    
    text_surface = font40.render("Cycle : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(670,110))
    screen.blit(text_surface, text_rect)
    
    placement_serpent_depart()
    maj_affichage_score(0)
    maj_affichage_cycle(0)
    placement_pomme()

def creation_jeu_ia():
    global bouton_restart_jeu_ia, bouton_menu_jeu_ia, score, cycle
    score = 0
    cycle = 0
    width_game = 594 #longueur du jeu
    
    # Zone externe au jeu
    pygame.draw.rect(screen, FOND, (width_game, 0, 200+6, 600))
    pygame.draw.line(screen, BLACK, (width_game, 0), (width_game, height), 2)   

    
    bouton_menu_jeu_ia = pygame.draw.rect(screen, GRAY, (635, 410, 130, 60))
    text_surface = font40.render("Menu", True, BLACK)
    text_rect = text_surface.get_rect(center=(700, 440))
    screen.blit(text_surface, text_rect)
    
    text_surface = font40.render("Score : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(680,50))
    screen.blit(text_surface, text_rect)
    
    text_surface = font40.render("Cycle : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(680,110))
    screen.blit(text_surface, text_rect)
    
    placement_serpent_depart()
    maj_affichage_score(0)
    maj_affichage_cycle(0)
    
    placement_pomme()
    



def placement_serpent_depart():
    global serpentTete, list_serpent
    serpent1 = [4,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    serpent2 = [5,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    serpent3 = [6,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    serpentTete = [7,7,Type_case.SERPENT_TETE,Type_direction.DROITE]
    
    # placement du serpent
    list_serpent = [serpent3,serpent2,serpent1]
    
    screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
    for i in list_serpent:
        #maj corps serpent dessin
        pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))

def placement_pomme():
    pomme_placée = False
    while not pomme_placée:
        rdm_x = random.randint(0, 17)
        rdm_y = random.randint(0, 14)
        if all(segment[:2] != [rdm_x, rdm_y] for segment in list_serpent):
            global pomme
            pomme = [rdm_x, rdm_y]
            screen.blit(image_pomme, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1]))
            pomme_placée = True
            
def maj_affichage_score(score):
    pygame.draw.rect(screen, FOND, (730, 27, 50, 50))
    text_surface = font40.render(str(score), True, BLACK)
    text_rect = text_surface.get_rect(center=(755,52))
    screen.blit(text_surface, text_rect)
    
def maj_affichage_cycle(cycle):
    pygame.draw.rect(screen, FOND, (730, 87, 50, 50))
    text_surface = font40.render(str(cycle), True, BLACK)
    text_rect = text_surface.get_rect(center=(755,112))
    screen.blit(text_surface, text_rect)
    
def joue_aléatoirement():
    rdm = random.randint(1, 4)
    if rdm == 1:
        return Type_direction.HAUT
    elif rdm == 2:
        return Type_direction.GAUCHE
    elif rdm == 3:
        return Type_direction.BAS
    elif rdm == 4:
        return Type_direction.DROITE


#IA
TAILLE_GRILLE_VISIBLE = 5
list_actions_ia = (Type_direction.DROITE,Type_direction.BAS,Type_direction.GAUCHE,Type_direction.HAUT)

def etat():
    return (tuple(list_serpent), serpentTete, pomme)

# Q-table dictionnaire
Q_table = {}

# renvoie les valeurs de Q pour un état
def get_q_table(q_table_actuel, etat):
    if etat not in q_table_actuel:
        q_table_actuel[etat] = {action: 0 for action in list_actions_ia} # Si l'état n'était pas dans la table, il est ajouté avec toutes les actions mise à 1 de valeur
    return q_table_actuel[etat]

# met à jour la valeur de Q pour un état-action donné
def update_q_table(q_table, etat, action, valeur):
    if etat not in q_table:
        q_table[etat] = {a: 0 for a in list_actions_ia} # Si l'état n'était pas dans la table, il est ajouté avec toutes les actions mise à 1 de valeur
    # maj table
    q_table[etat][action] = valeur

# choisir action (epsilon-greedy)
def choisir_action(q_table, etat, epsilon=0.1):
    if random.uniform(0, 1) < epsilon:
        # Choix aléatoire pour explorer
        return random.choice(list_actions_ia)
    else:
        # Choix de l'action ayant la valeur Q maximale
        q_values = get_q_table(q_table, etat,None)
        return max(q_values, key=q_values.get)
    
def generer_etat(serpentTete, list_serpent, pomme):
    # Création d'une zone 5x5 autour de la tête du serpent
    etatGrilleVisible = np.zeros((TAILLE_GRILLE_VISIBLE, TAILLE_GRILLE_VISIBLE), dtype=int)

    # Position du serpent tête
    x, y = serpentTete[0], serpentTete[1]

    for seg in list_serpent:
        dx = seg[0] - x + 2
        dy = seg[1] - y + 2
        if 0 <= dx < TAILLE_GRILLE_VISIBLE and 0 <= dy < TAILLE_GRILLE_VISIBLE:
            etatGrilleVisible[dx][dy] = 1
    return (serpentTete, pomme, etatGrilleVisible)


def calcul_récompense():
    if pomme == serpentTete[:2]:
        return 20
    for segment in list_serpent:
        if serpentTete[:2] == segment[:2]:        
            return -20
    if serpentTete[0] < 0 or serpentTete[0] > 17 or serpentTete [1] < 0 or serpentTete[1] > 14:
        return -20
    else: 
        return -1


# A FAIRE
def entrainer(q_table, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    for _ in range(episodes):
        # Réinitialiser l'état du jeu
        jeu_cree = False
        etat_actuel = generer_etat(serpentTete, list_serpent, pomme)
        
        while True:  # Jusqu'à la fin de l'épisode
            # Choisir une action
            action = choisir_action(q_table, etat_actuel, epsilon)
            
            # Calculer le nouvel état après l'action
            nouvel_etat, reward, done = simuler_action(serpentTete, list_serpent, action, pomme)
            
            # Mise à jour de la Q-table
            mise_a_jour_q_learning(q_table, etat_actuel, action, reward, nouvel_etat, alpha, gamma)
            
            # Passer à l'état suivant
            etat_actuel = nouvel_etat
            
            if done:  # Si le jeu est terminé, on passe à l'épisode suivant
                break


# Application
run = True
while run:
    temps_actuel = pygame.time.get_ticks()
    # test IA
    
    if etat_app == 'jeu_perdu_ia':
            
            if score < 3:
                nombrePartie += 1
                jeu_cree = False
                etat_app = 'jeu_ia'
            else:
                print("Nombre de partie pour atteindre 4 : " + str(nombrePartie))
                nombrePartie = 0
                break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            #MENU
            if etat_app == 'menu':
                if bouton_menu_humain.collidepoint(x, y):
                    #MODE HUMAIN
                    etat_app = 'jeu_humain'
                    dernier_mouvement_temps = 0
                    intervale_temps = 1000
                    screen = pygame.display.set_mode((width, height))
                if bouton_menu_IA.collidepoint(x, y):
                    #MODE IA
                    etat_app = 'jeu_ia'
                    dernier_mouvement_temps = 0
                    intervale_temps = 1
                    screen = pygame.display.set_mode((width + tailleAjoutFenetre, height))
                
            #JEU_HUMAIN
            elif etat_app == 'jeu_humain':
                if bouton_restart_jeu_humain.collidepoint(x, y):
                    # Réinitialisation du jeu
                    jeu_cree = False
                    etat_app = 'jeu_humain'
                    
                if bouton_menu_jeu_humain.collidepoint(x,y):
                    jeu_cree = False
                    etat_app = 'menu'
            
            #JEU_IA
            elif etat_app == 'jeu_ia':
                if bouton_menu_jeu_ia.collidepoint(x,y):
                    jeu_cree = False
                    etat_app = 'menu'
                    
            #PERDU_HUMAIN
            elif etat_app == 'jeu_perdu_humain':
                if bouton_restart_perdu_humain.collidepoint(x, y):
                    jeu_cree = False
                    etat_app = 'jeu_humain'
                    
                if bouton_menu_perdu_humain.collidepoint(x, y):
                    jeu_cree = False
                    etat_app = 'menu'
                    
            #PERDU_IA
            elif etat_app == 'jeu_perdu_ia':
                if bouton_restart_perdu_ia.collidepoint(x, y):
                    jeu_cree = False
                    etat_app = 'jeu_ia'
                    
                if bouton_menu_jeu_ia.collidepoint(x, y):
                    jeu_cree = False
                    etat_app = 'menu'

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_UP or event.key == pygame.K_z) and serpentTete[3] != Type_direction.BAS and not choix_direction:  # aller en haut
                serpentTete[3] = Type_direction.HAUT
                choix_direction = True
            elif (event.key == pygame.K_DOWN  or event.key == pygame.K_s) and serpentTete[3] != Type_direction.HAUT and not choix_direction:  # aller en bas
                serpentTete[3] = Type_direction.BAS
                choix_direction = True
            elif (event.key == pygame.K_LEFT  or event.key == pygame.K_q) and serpentTete[3] != Type_direction.DROITE and not choix_direction:  # aller a gauche
                serpentTete[3] = Type_direction.GAUCHE
                choix_direction = True
            elif (event.key == pygame.K_RIGHT  or event.key == pygame.K_d) and serpentTete[3] != Type_direction.GAUCHE and not choix_direction:  # aller a droite
                serpentTete[3] = Type_direction.DROITE
                choix_direction = True
            #cheat
            elif event.key == pygame.K_y:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,Type_case.SERPENT_CORPS,ancien_serpent_direction])
                score += 1
                maj_affichage_score(score)
                
    # Selection de l'ecran
    if etat_app == 'menu':
        screen.fill(FOND)
        #Bouton Mode Humain
        bouton_menu_humain = pygame.draw.rect(screen, GRAY, (130, 200, 200, 200))
        text_surface = font50.render("Humain", True, BLACK)
        text_rect = text_surface.get_rect(center=(130+200//2, 200+200//2))
        screen.blit(text_surface, text_rect)
        
        #Bouton Mode IA
        bouton_menu_IA = pygame.draw.rect(screen, GRAY, (480, 200, 200, 200))
        text_surface = font60.render("IA", True, BLACK)
        text_rect = text_surface.get_rect(center=(480+200//2, 200+200//2))
        screen.blit(text_surface, text_rect)
        
        #Texte Titre
        text_surface = font60.render("Selectionnez le mode :", True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2, (height//4)-20))
        screen.blit(text_surface, text_rect)
    
    elif etat_app == 'jeu_humain':
        if not jeu_cree:
            screen.fill(WHITE)
            creation_jeu_humain()
            jeu_cree = True
        
        #cycle temps du jeu
        if temps_actuel - dernier_mouvement_temps >= intervale_temps:
            choix_direction = False
            cycle += 1
            maj_affichage_cycle(cycle)
            print(generer_etat(serpentTete,list_serpent,pomme))
            print("-------------------------------")
            dernier_mouvement_temps = temps_actuel            
            direction = serpentTete[3].value
            x,y = serpentTete[0],serpentTete[1]
            
            ancienne_position_tete = serpentTete[:2]
            ancienne_direction_tete = serpentTete[3]
            
            #déplacement avec check colision murs
            
            if direction == Type_direction.BAS.value:
                if y < 14:
                    serpentTete[1] += 1
                else:
                    etat_app = 'jeu_perdu_humain'

            if direction == Type_direction.DROITE.value:
                if x < 17:
                    serpentTete[0] += 1
                else:
                    etat_app = 'jeu_perdu_humain'

            if direction == Type_direction.HAUT.value:
                if y > 0:
                    serpentTete[1] -= 1
                else:
                    etat_app = 'jeu_perdu_humain'
                    
            if direction == Type_direction.GAUCHE.value:
                if x > 0:
                    serpentTete[0] -= 1
                else:
                    etat_app = 'jeu_perdu_humain'
                
            #deplacement du corps du serpent
            
            ancien_serpent_x = list_serpent[-1][0]
            ancien_serpent_y = list_serpent[-1][1]
            ancien_serpent_direction = list_serpent [-1][3]
            
            for i in range(len(list_serpent)):
                ancienne_position_segment = list_serpent[i][:2]
                ancienne_direction_segment = list_serpent[i][3]
        
                pygame.draw.rect(screen, WHITE, (coordonnées_case(ancienne_position_segment)[0], coordonnées_case(ancienne_position_segment)[1], taille_case, taille_case))

                list_serpent[i][0], list_serpent[i][1] = ancienne_position_tete
                list_serpent[i][3] = ancienne_direction_tete
            
                ancienne_position_tete = ancienne_position_segment
                ancienne_direction_tete = ancienne_direction_segment
            
            # Collision avec son propre corps
            for i in list_serpent:
                if serpentTete[:2] == i[:2]:
                    etat_app = 'jeu_perdu_humain'
                
            # Collision avec une pomme
            if serpentTete[:2] == pomme[:2]:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,Type_case.SERPENT_CORPS,ancien_serpent_direction])
                score += 1
                maj_affichage_score(score)
                placement_pomme()
            
            #maj tete serpent dessin
            if serpentTete[3] == Type_direction.BAS:
                screen.blit(image_tete_serpent_bas, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.HAUT:
                screen.blit(image_tete_serpent_haut, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.DROITE:
                screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.GAUCHE:
                screen.blit(image_tete_serpent_gauche, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))

            for i in list_serpent:
                #maj corps serpent dessin
                pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))
           
    elif etat_app == 'jeu_ia':
        if not jeu_cree:
            screen.fill(WHITE)
            pygame.draw.rect(screen, FOND, (width, 0, tailleAjoutFenetre, height)) # Ajout parti supplémentaire pour les informations de l'IA
            creation_jeu_ia()
            jeu_cree = True
        
        #cycle temps du jeu
        if temps_actuel - dernier_mouvement_temps >= intervale_temps:
            cycle += 1
            maj_affichage_cycle(cycle)
            choix_direction = False
            dernier_mouvement_temps = temps_actuel            
            direction = serpentTete[3].value
            x,y = serpentTete[0],serpentTete[1]               
            # Test
            print(generer_etat(serpentTete,list_serpent,pomme))
            print("-------------------------------")
            #joue aléatoirement
            direction_aleatoire = joue_aléatoirement()
            if direction_aleatoire.value != direction*-1:
                serpentTete[3] = direction_aleatoire
                choix_direction = True
            
            ancienne_position_tete = serpentTete[:2]
            ancienne_direction_tete = serpentTete[3]
        
            #déplacement avec check colision murs
            
            if direction == Type_direction.BAS.value:
                if y < 14:
                    serpentTete[1] += 1
                else:
                    etat_app = 'jeu_perdu_ia'

            if direction == Type_direction.DROITE.value:
                if x < 17:
                    serpentTete[0] += 1
                else:
                    etat_app = 'jeu_perdu_ia'

            if direction == Type_direction.HAUT.value:
                if y > 0:
                    serpentTete[1] -= 1
                else:
                    etat_app = 'jeu_perdu_ia'
                    
            if direction == Type_direction.GAUCHE.value:
                if x > 0:
                    serpentTete[0] -= 1
                else:
                    etat_app = 'jeu_perdu_ia'
                    
            #deplacement du corps du serpent
            ancien_serpent_x = list_serpent[-1][0]
            ancien_serpent_y = list_serpent[-1][1]
            ancien_serpent_direction = list_serpent [-1][3]
            
            for i in range(len(list_serpent)):
                
                ancienne_position_segment = list_serpent[i][:2]
                ancienne_direction_segment = list_serpent[i][3]
        
                pygame.draw.rect(screen, WHITE, (coordonnées_case(ancienne_position_segment)[0], coordonnées_case(ancienne_position_segment)[1], taille_case, taille_case))

                list_serpent[i][0], list_serpent[i][1] = ancienne_position_tete
                list_serpent[i][3] = ancienne_direction_tete
            
                ancienne_position_tete = ancienne_position_segment
                ancienne_direction_tete = ancienne_direction_segment
            
            # colision avec son propre corps
            for i in list_serpent:
                if serpentTete[:2] == i[:2]:
                    etat_app = 'jeu_perdu_ia'
                
            # colistion avec une pomme
            if serpentTete[:2] == pomme[:2]:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,Type_case.SERPENT_CORPS,ancien_serpent_direction])
                score += 1
                maj_affichage_score(score)
                placement_pomme()
            
            #maj tete serpent dessin
            if serpentTete[3] == Type_direction.BAS:
                screen.blit(image_tete_serpent_bas, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.HAUT:
                screen.blit(image_tete_serpent_haut, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.DROITE:
                screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[3] == Type_direction.GAUCHE:
                screen.blit(image_tete_serpent_gauche, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))

            for i in list_serpent:
                #maj corps serpent dessin
                pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))

    
    elif etat_app == 'jeu_perdu_humain':
        screen.fill(FOND)
        
        bouton_menu_perdu_humain = pygame.draw.rect(screen, GRAY, (180, 350, 180, 100))
        text_surface = font60.render("Menu", True, BLACK)
        text_rect = text_surface.get_rect(center=(270, 400))
        screen.blit(text_surface, text_rect)
        
        bouton_restart_perdu_humain = pygame.draw.rect(screen, GRAY, (420, 350, 180, 100))
        text_surface = font60.render("Restart", True, BLACK)
        text_rect = text_surface.get_rect(center=(510, 400))
        screen.blit(text_surface, text_rect)
    
        text_surface = font80.render("PERDU", True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2, height//2 - 30))
        screen.blit(text_surface, text_rect)
        
        text_surface = font50.render("Score : " + str(score), True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2,height//4-65))
        screen.blit(text_surface, text_rect)
        
        text_surface = font50.render("Cycle : " + str(cycle), True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2,height//4-20))
        screen.blit(text_surface, text_rect)
        
    elif etat_app == 'jeu_perdu_ia':
        screen.fill(FOND)
        
        bouton_menu_jeu_ia = pygame.draw.rect(screen, GRAY, (180, 350, 180, 100))
        text_surface = font60.render("Menu", True, BLACK)
        text_rect = text_surface.get_rect(center=(270, 400))
        screen.blit(text_surface, text_rect)
        
        bouton_restart_perdu_ia = pygame.draw.rect(screen, GRAY, (420, 350, 180, 100))
        text_surface = font60.render("Restart", True, BLACK)
        text_rect = text_surface.get_rect(center=(510, 400))
        screen.blit(text_surface, text_rect)
    
        text_surface = font80.render("PERDU", True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2, height//2 - 30))
        screen.blit(text_surface, text_rect)
        
        text_surface = font50.render("Score : " + str(score), True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2,height//4-65))
        screen.blit(text_surface, text_rect)
        
        text_surface = font50.render("Cycle : " + str(cycle), True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2,height//4-20))
        screen.blit(text_surface, text_rect)
        
        
    pygame.display.flip()
    
pygame.quit()