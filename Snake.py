import pygame
from enum import Enum
import random

class Couleur(Enum):
    ROUGE = 1
    VERT = 2
    BLEU = 3


pygame.init()

# Longueur / Hauteur
width = 800
height = 500
screen = pygame.display.set_mode((width, height))

etat_app = 'menu'

# Couleurs
FOND_MENU = (200,200,200)
GRAY = (122, 122, 122)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SERPENT_CORPS_COULEUR = (72, 235, 54)
SERPENT_TETE_COULEUR = (33, 112, 25)
POMME_COULEUR = (179, 20, 20)


# Texte 

font = pygame.font.Font(None, 40)

# Type de case 
class Type_case(Enum):
    VIDE = 0
    POMME = 1
    SERPENT_CORPS = 2
    SERPENT_TETE = 3
    
# Type de direction (case serpent)
class Type_direction(Enum):
    HAUT = 0
    DROITE = 1
    BAS = 2
    GAUCHE = 3


 # ratio 6/5 zone de jeu
 # 18/15, 33.33 par case

taille_case = 33.333
# Creation du tableau de jeu
list_case = []
for i in range(18):
    for j in range(15):
        case = [i,j,Type_case.VIDE.value] 
        # case = [pos_x_longueur, pos_y_hauteur, type de case]
        list_case.append(case)

def coordonnées_case(case):
    return (case[0]*taille_case,case[1]*taille_case)


# Fonction du jeu

jeu_cree = False
def creation_jeu():
    width_game = 600 #longueur du jeu
    """
    for i in range(19): #ligne verticale
       pygame.draw.line(screen, BLACK, (i*taille_case, 0), (i*taille_case, height), 2)   
        
    for i in range(16): #ligne horizontale
        pygame.draw.line(screen, BLACK, (0,i*taille_case), (width,i*taille_case), 2)
    """
    
    # Zone externe au jeu
    pygame.draw.rect(screen, GRAY, (600, 0, 200, 600))
    placement_serpent_pomme_depart()

    
def est_serpent_corps(case):
    if(case[2] == Type_case.SERPENT_CORPS.value): 
        return True
    
def est_serpent_tete(case):
    if(case[2] == Type_case.SERPENT_TETE.value):
        return True
    
def est_pomme(case):
    if(case[2] == Type_case.POMME.value):
        return True
    
def modif_type_case(case, nouveau_type):
    list_case[numeroCaseDans_liste_case(case)][2] = nouveau_type.value
    
def modif_direction_serpent(case,nouvel_direction):
    list_case[numeroCaseDans_liste_case(case)][3] = nouvel_direction.value


def placement_serpent_pomme_depart():
    serpent1 = [4,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    serpent2 = [5,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    serpent3 = [6,7,Type_case.SERPENT_CORPS,Type_direction.DROITE]
    global serpentTete
    serpentTete = [7,7,Type_case.SERPENT_TETE,Type_direction.DROITE]
    pomme = [13,7]
    #placement du serpent
    modif_type_case([serpent1[0],serpent1[1]], Type_case.SERPENT_CORPS)
    modif_type_case([serpent2[0],serpent2[1]], Type_case.SERPENT_CORPS)
    modif_type_case([serpent3[0],serpent3[1]], Type_case.SERPENT_CORPS)
    modif_type_case([serpentTete[0],serpentTete[1]], Type_case.SERPENT_TETE)
    
    #placement de la pomme
    modif_type_case(pomme, Type_case.POMME)
    global list_serpent
    list_serpent = [serpent3,serpent2,serpent1]
    
    pygame.draw.rect(screen, SERPENT_TETE_COULEUR, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1], taille_case, taille_case))
    for i in list_serpent:
        #maj corps serpent dessin
        pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))

def numeroCaseDans_liste_case(coordonnées):
    return coordonnées[0] + coordonnées[1] * 15

def placement_pomme():
    rdm = random.randint(1, 18*15)
    global pomme
    pomme = [rdm % 18, rdm // 18]
    for i in list_serpent:
        if pomme[:2] != i[:2]:
            pygame.draw.rect(screen, RED, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1], taille_case, taille_case))
        else:
            placement_pomme()
            



# Temps 

dernier_mouvement_temps = 0
#intervalle de tick
intervale_temps = 200

cycle = 0

# Application
run = True
while run:
    temps_actuel = pygame.time.get_ticks()
    
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
                
                if bouton_menu_IA.collidepoint(x, y):
                    #MODE IA
                    etat_app = 'jeu_IA'
            
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

                
    # Selection de l'ecran
    if etat_app == 'menu':
        screen.fill(FOND_MENU)
        #Bouton Mode Humain
        bouton_menu_humain = pygame.draw.rect(screen, GRAY, (130, 200, 200, 200))
        text_surface = font.render("Humain", True, BLACK)
        text_rect = text_surface.get_rect(center=(130+200//2, 200+200//2))
        screen.blit(text_surface, text_rect)
        
        #Bouton Mode IA
        bouton_menu_IA = pygame.draw.rect(screen, GRAY, (480, 200, 200, 200))
        text_surface = font.render("IA", True, BLACK)
        text_rect = text_surface.get_rect(center=(480+200//2, 200+200//2))
        screen.blit(text_surface, text_rect)
        
        #Texte Titre
        text_surface = font.render("Selectionner le mode :", True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2, (height//4)-20))
        screen.blit(text_surface, text_rect)
    
    elif etat_app == 'jeu_humain':
        if not jeu_cree:
            screen.fill(WHITE)
            creation_jeu()
            jeu_cree = True
            placement_pomme()


        

        #cycle temps du jeu
        if temps_actuel - dernier_mouvement_temps >= intervale_temps:
            choix_direction = False
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
                    etat_app = 'jeu_perdu'

            if direction == Type_direction.DROITE.value:
                if x < 17:
                    serpentTete[0] += 1
                else:
                    etat_app = 'jeu_perdu'

            if direction == Type_direction.HAUT.value:
                if y > 0:
                    serpentTete[1] -= 1
                else:
                    etat_app = 'jeu_perdu'
                    
            if direction == Type_direction.GAUCHE.value:
                if x > 0:
                    serpentTete[0] -= 1
                else:
                    etat_app = 'jeu_perdu'
                    
            
                
            ancien_serpent_x = list_serpent[-1][0]
            ancien_serpent_y = list_serpent[-1][1]
            ancien_serpent_direction = list_serpent [-1][3]
            #deplacement du corps du serpent
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
                    etat_app = 'jeu_perdu'
                
            if serpentTete[:2] == pomme[:2]:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,Type_case.SERPENT_CORPS,ancien_serpent_direction])
                placement_pomme()
            
            #maj tete serpent dessin
            pygame.draw.rect(screen, SERPENT_TETE_COULEUR, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1], taille_case, taille_case))
            for i in list_serpent:
                #maj corps serpent dessin
                pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))
                
            

           
    elif etat_app == 'jeu_IA':
        pass
    
    elif etat_app == 'jeu_perdu':
        screen.fill(FOND_MENU)
        text_surface = font.render("PERDU", True, BLACK)
        text_rect = text_surface.get_rect(center=(width//2, height//2))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    
pygame.quit()
