import pygame

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

# Texte 

font = pygame.font.Font(None, 40)


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
    screen.fill(WHITE)
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
        pass
    
    elif etat_app == 'jeu_IA':
        pass
    
    pygame.display.flip()
    
pygame.quit()
