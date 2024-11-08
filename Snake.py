import pygame
from enum import Enum

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
        
    for i in range(19): #ligne verticale
        pygame.draw.line(screen, BLACK, (i*taille_case, 0), (i*taille_case, height), 2)   
        
    for i in range(16): #ligne horizontale
        pygame.draw.line(screen, BLACK, (0,i*taille_case), (width,i*taille_case), 2)
        
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
    index = case[1] + case[0] * 15
    list_case[index][2] = nouveau_type.value


def placement_serpent_pomme_depart():
    modif_type_case([4, 7], Type_case.SERPENT_CORPS)
    modif_type_case([5, 7], Type_case.SERPENT_CORPS)
    modif_type_case([6, 7], Type_case.SERPENT_CORPS)
    modif_type_case([7, 7], Type_case.SERPENT_TETE)
    modif_type_case([13, 7], Type_case.POMME)




# Application

run = True
while run:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            #MENU
            if etat_app == 'menu':
                if bouton_menu_humain.collidepoint(x, y):
                    #MODE HUMAIN
                    etat_app = 'jeu_humain'
                
                if bouton_menu_IA.collidepoint(x, y):
                    #MODE IA
                    etat_app = 'jeu_IA'
    
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

            
        

            
        for i in list_case:
            if est_serpent_corps(i):
                pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))
            if est_serpent_tete(i):
                pygame.draw.rect(screen, SERPENT_TETE_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))
            if est_pomme(i):
                pygame.draw.rect(screen, POMME_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))


    elif etat_app == 'jeu_IA':
        pass    
    pygame.display.flip()
    
pygame.quit()
