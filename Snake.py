import pygame
from enum import Enum
import random
import pickle
from multiprocessing import Pool, cpu_count
import os

# Type de direction (case serpent / serpentTete)
class Type_direction(Enum):
    HAUT = 1
    DROITE = 2
    BAS = -1
    GAUCHE = -2

# Taille des cases
taille_case = 33 # 18 cases par ligne / 15 cases par colonne --- 33 pixel par case
 
# Fonction du jeu
def coordonnées_case(case):
    return (case[0]*taille_case,case[1]*taille_case)

    # Creation du jeu humain
global jeu_cree
jeu_cree = False
def creation_jeu_humain():
    global score, cycle
    score = 0
    cycle = 0
    placement_serpent_depart()
    pomme = placement_pomme(serpentTete,list_serpent,None)
    return pomme


def creation_jeu_ia():
    global score, cycle
    score = 0
    cycle = 0
    placement_serpent_depart()
    pomme = placement_pomme(serpentTete,list_serpent)
    #debug / pomme = m['positions_pomme'][0]
    return pomme

def placement_serpent_depart():
    global serpentTete, list_serpent
    serpentTete = [7, 7, Type_direction.GAUCHE]
    serpent1 = [10, 7, Type_direction.GAUCHE]
    serpent2 = [9, 7, Type_direction.GAUCHE]
    serpent3 = [8, 7, Type_direction.GAUCHE]
    list_serpent = [serpent3, serpent2, serpent1]
    return serpentTete, list_serpent


def placement_pomme(serpentTete,list_serpent):
    #Positionne une pomme hors du serpent.
    while True:
        nouvelle_pomme = [random.randint(0, 17), random.randint(0, 14)]
        if nouvelle_pomme not in [serpentTete[:2]] + [segment[:2] for segment in list_serpent]:
            return nouvelle_pomme

def placement_pomme_m(m,cycle):
    nouvelle_pomme = m['positions_pomme'][cycle]  
    return nouvelle_pomme

def verifier_collision(serpentTete, list_serpent):
    """Vérifie les collisions avec les murs et le corps du serpent."""
    x_c, y_c = serpentTete[:2]
    
    # Vérification mur
    if x_c < 0 or x_c > 17 or y_c < 0 or y_c > 14:
        return True
    # Vérification corps
    if [x_c, y_c] in [segment[:2] for segment in list_serpent]:
        return True
    return False

def deplacer_serpent(serpentTete, list_serpent):
    """Effectue le déplacement du serpent."""
    # Stocker les anciennes positions pour déplacer le corps
    ancienne_position_tete = serpentTete[:2]
    ancienne_direction_tete = serpentTete[2]
    
    x, y = serpentTete[:2]
    direction = serpentTete[2]
    
    # Mise à jour de la position de la tête
    mouvements = {
        Type_direction.HAUT: (x, y - 1),
        Type_direction.BAS: (x, y + 1),
        Type_direction.GAUCHE: (x - 1, y),
        Type_direction.DROITE: (x + 1, y),
    }
    serpentTete[0], serpentTete[1] = mouvements[direction]
    
    # Déplacement du corps
    for i in range(len(list_serpent)):
        ancienne_position_segment = list_serpent[i][:2]
        ancienne_direction_segment = list_serpent[i][2]
        # pygame.draw.rect(screen, WHITE, (coordonnées_case(ancienne_position_segment)[0], coordonnées_case(ancienne_position_segment)[1], taille_case, taille_case))

        list_serpent[i][0], list_serpent[i][1] = ancienne_position_tete
        list_serpent[i][2] = ancienne_direction_tete
        
        ancienne_position_tete = ancienne_position_segment
        ancienne_direction_tete = ancienne_direction_segment

REWARD_POMME = 10
def calculer_reward(serpentTete, pomme, collision):
    if collision:
        return -20
    elif serpentTete[:2] == pomme[:2]:
        return REWARD_POMME
    else:
        # Récompense basée sur la distance à la pomme
        distance_actuelle = abs(serpentTete[0] - pomme[0]) + abs(serpentTete[1] - pomme[1])
        return -0.1 * distance_actuelle


"""
                                                #########
                                                PARTIE IA
                                                #########
"""

ALPHA = 0.5
GAMMA = 0.2
EPSILON = 0.2

list_actions_ia = (Type_direction.BAS,Type_direction.GAUCHE,Type_direction.HAUT,Type_direction.DROITE)

# renvoie les valeurs de Q pour un état
def get_q_table(q_table, etat):
    direction_actuelle = etat[-1]  # La direction actuelle est stockée dans le dernier élément de `etat`
    
    def action_opposée(direction, action):
        oppositions = {
            Type_direction.HAUT: Type_direction.BAS,
            Type_direction.BAS: Type_direction.HAUT,
            Type_direction.GAUCHE: Type_direction.DROITE,
            Type_direction.DROITE: Type_direction.GAUCHE,
        }
        return oppositions.get(direction) == action

    if etat not in q_table:
        action_disponibles = {
            action: 0
            for action in list_actions_ia
            if not action_opposée(direction_actuelle, action)
        }
        q_table[etat] = action_disponibles

    return q_table[etat]

# met à jour la valeur de Q pour un état-action donné
def update_q_table(q_table, etat, action, valeur):
    if etat not in q_table:
        q_table[etat] = {a: 0 for a in list_actions_ia} # Si l'état n'était pas dans la table, il est ajouté avec toutes les actions mise à 1 de valeur
    # maj table
    q_table[etat][action] = valeur

# Choisir une action (epsilon-greedy)
def choisir_action_ia(q_table, etat, epsilon=EPSILON):
    # Récupération des valeurs Q et des dangers
    q_values = get_q_table(q_table, etat)
    actions_sans_danger = [action for action, is_danger in dangers.items() if not is_danger]

    # Si toutes les actions sont dangereuses, on doit continuer (éviter une erreur)
    if not actions_sans_danger:
        actions_sans_danger = list(q_values.keys())

    # Exploration ou exploitation
    if random.uniform(0, 1) < epsilon:
        # Exploration : Choisir une action sans danger au hasard
        return random.choice(actions_sans_danger)
    else:
        # Exploitation : Choisir la meilleure action parmi celles sans danger
        meilleures_actions = [
            action for action in actions_sans_danger
            if q_values[action] == max(q_values[a] for a in actions_sans_danger)
        ]
        return random.choice(meilleures_actions)

# Mettre à jour la Q-table pour inclure la direction de la tête
def generer_etat(serpentTete, list_serpent, pomme):
    global dangers
    x, y = serpentTete[:2]
    pomme_x, pomme_y = pomme
    directions = {
        Type_direction.HAUT: (x, y - 1),
        Type_direction.BAS: (x, y + 1),
        Type_direction.GAUCHE: (x - 1, y),
        Type_direction.DROITE: (x + 1, y),
    }
    
    # Distances relatives à la pomme
    dx = pomme_x - x
    dy = pomme_y - y
    
    # Danger dans chaque direction
    dangers = {
        dir_: verifier_collision([nx, ny, dir_], list_serpent)
        for dir_, (nx, ny) in directions.items()
    }
    
    # Encode l'état
    etat = (dx, dy, tuple(dangers.values()),serpentTete[2])
    return etat

# Mettre à jour la Q-table (formule de Bellman)
def mise_a_jour_q_learning(q_table, etat, action, reward, etat_suivant, alpha=ALPHA, gamma=GAMMA):
    max_q_suivant = max(get_q_table(q_table, etat_suivant).values())
    valeur_actuelle = get_q_table(q_table, etat)[action]
    nouvelle_valeur = valeur_actuelle + alpha * (reward + gamma * max_q_suivant - valeur_actuelle)
    update_q_table(q_table, etat, action, nouvelle_valeur)

# Simuler une action
def simuler_action(serpentTete, list_serpent, action, pomme):
    x, y = serpentTete[:2]
    if action == Type_direction.HAUT:
        y -= 1
    elif action == Type_direction.BAS:
        y += 1
    elif action == Type_direction.GAUCHE:
        x -= 1
    elif action == Type_direction.DROITE:
        x += 1

    nouvelle_tete = [x, y,action]
    done = False

    # Vérifier conditions de fin et récompenses
    collision = verifier_collision(nouvelle_tete, list_serpent)
    reward = calculer_reward(nouvelle_tete, pomme, collision)

    if reward == REWARD_POMME:  # Le serpent mange la pomme
        pomme = placement_pomme(serpentTete, list_serpent)
    elif collision:  # Collision détectée
        done = True
    # Mettre à jour le serpent
    nouveau_serpent = list_serpent + [serpentTete]
    if nouvelle_tete != pomme:
        nouveau_serpent.pop(0)  # Enlever la queue si pas de pomme mangée

    # Générer le nouvel état
    nouvel_etat = generer_etat(nouvelle_tete, nouveau_serpent, pomme)
    return nouvel_etat, reward, done, nouveau_serpent, pomme, nouvelle_tete

# Entraîner l'agent
def entrainer(q_table, episodes, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON, max_steps=1000):
    for episode in range(episodes):
        # Initialiser l'état
        #if episode % (episodes/100) == 0:
            #print(str((episode / episodes)*100) + "%")
            
        serpentTete,list_serpent = placement_serpent_depart()
        nouvelle_pomme = placement_pomme(serpentTete,list_serpent)
        serpentTeteEntrainement = serpentTete
        list_serpentEntrainement = [segment[:2] for segment in list_serpent]
        pommeEntrainement = nouvelle_pomme[:2]
        etat_actuel = generer_etat(serpentTeteEntrainement, list_serpentEntrainement, pommeEntrainement)
        for step in range(max_steps):
            # Choisir une action
            action = choisir_action_ia(q_table, etat_actuel, epsilon)
            # Simuler l'action
            nouvel_etat, reward, done, list_serpentEntrainement, pommeEntrainement, serpentTeteEntrainement = simuler_action(serpentTeteEntrainement, list_serpentEntrainement, action, pommeEntrainement)
            # Mise à jour de la Q-table
            mise_a_jour_q_learning(q_table, etat_actuel, action, reward, nouvel_etat, alpha, gamma)
            # Passer au nouvel état
            etat_actuel = nouvel_etat


            if done:
                break
    print("Entraintement fini")


def choisir_action_jeu(q_table, etat):
    q_values = get_q_table(q_table, etat)
    actions_sans_danger = [action for action, is_danger in dangers.items() if not is_danger]

    # Si toutes les actions sont dangereuses, on doit continuer (éviter une erreur)
    if not actions_sans_danger:
        actions_sans_danger = list(q_values.keys())

    # Exploitation : Choisir la meilleure action parmi celles sans danger
    meilleures_actions = [
        action for action in actions_sans_danger
        if q_values[action] == max(q_values[a] for a in actions_sans_danger)
    ]
    return random.choice(meilleures_actions)



def simuler_parties(q_table, nombre_parties, max_steps=500, interval_enregistrement=1):
    total_score = 0
    score_max = 0
    meilleures_donnees = None  # Contiendra les données de la meilleure partie

    for partie in range(nombre_parties):
        # Initialisation des variables pour une nouvelle partie
        serpentTete, list_serpent = placement_serpent_depart()
        super_pomme = placement_pomme(serpentTete, list_serpent)
        etat_actuel = generer_etat(serpentTete, list_serpent, super_pomme)
        score = 0
        done = False

        # Initialisation pour enregistrer les données de la partie
        donnees_partie = {"positions_pomme": [], "actions": [], "score": 0}

        for step in range(max_steps):
            if done:
                break
            
            # Choix de l'action et simulation
            action = choisir_action_jeu(q_table, etat_actuel)
            nouvel_etat, reward, done, list_serpent, super_pomme, serpentTete = simuler_action(
                serpentTete, list_serpent, action, super_pomme
            )
            etat_actuel = nouvel_etat
            
            # Enregistrement des données à intervalle donné
            if step % interval_enregistrement == 0:
                donnees_partie["positions_pomme"].append(super_pomme)
                donnees_partie["actions"].append(action)
            
            # Mise à jour du score
            if reward == REWARD_POMME:
                score += 1
        
        # Sauvegarde du score et des données de la partie
        donnees_partie["score"] = score
        if score > score_max:
            score_max = score
            meilleures_donnees = donnees_partie

        print(f"Partie {partie + 1} : Score = {score}")
        total_score += score

    print(f"Score total : {total_score}")
    print(f"Score maximum atteint : {score_max}")
    return meilleures_donnees


# Sauvegarde des Q_table
def save_qtable(q_table, q_number):  
    with open("ressources/q-table"+str(q_number)+".pkl", "wb") as fichier:
        pickle.dump(q_table, fichier)

#Chargement de la QTable
def load_qtable(q_number):
    with open("ressources/q-table"+str(q_number)+".pkl", "rb") as fichier:
        Q_table = pickle.load(fichier)
        return Q_table

"""   
#--------------------------------------------------------------------------------------------------------------------
   

# Fonction d'entraînement pour un processus
def entrainer_process(args):
    id_proces, episodes = args  # Chaque processus reçoit un ID et un nombre d'épisodes
    print(f"Process {id_proces} started on PID {os.getpid()}")
    
    # Initialisation de la Q-table et entraînement
    q_table = {}
    entrainer(q_table, episodes=episodes)
    
    # Sauvegarder la Q-table de ce processus
    save_qtable(q_table, id_proces)
    print(f"Process {id_proces} finished")
    return q_table

# Distribution des épisodes sur plusieurs cœurs
def entrainer_parallele(nb_episodes, nb_process):
    # Diviser les épisodes par processus
    episodes_par_process = nb_episodes // nb_process
    args = [(i, episodes_par_process) for i in range(nb_process)]
    
    # Utiliser un pool de processus
    with Pool(nb_process) as pool:
        q_tables = pool.map(entrainer_process, args)
    
    print("Entraînement parallèle terminé")
    return q_tables

# Fusionner les Q-tables (optionnel)
def fusionner_qtables(q_tables):
    q_table_finale = {}
    for q_table in q_tables:
        for etat, actions in q_table.items():
            if etat not in q_table_finale:
                q_table_finale[etat] = actions
            else:
                for action, valeur in actions.items():
                    if action not in q_table_finale[etat]:
                        q_table_finale[etat][action] = valeur
                    else:
                        q_table_finale[etat][action] = max(q_table_finale[etat][action], valeur)
    return q_table_finale

# Contrôle principal
if __name__ == "__main__":
    NB_EPISODES = 100000  # Total des épisodes
    NB_PROCESS = cpu_count()  # Utiliser le nombre de cœurs disponibles

    # Entraînement en parallèle
    q_tables = entrainer_parallele(NB_EPISODES, NB_PROCESS)

    # Option : Fusionner toutes les Q-tables
    q_table_finale = fusionner_qtables(q_tables)
    
    # Sauvegarder la Q-table fusionnée
    save_qtable(q_table_finale, 9999)
    print(simuler_parties(q_table_finale, 1000))

   """


        
       
   
    

"""
                                                        ###################
                                                        TABLEAU DE CONTROLE
                                                        ###################
"""

LANCER_APP = True
Q_table = load_qtable(522)
#debug / m = simuler_parties(Q_table,1)
#debug / print(m)
#save_qtable(Q_table,522)
print("#########################")



""" 
                                                        ###############
                                                        PARTIE VISUELLE
                                                        ############### 
""" 

pygame.init()

# Longueur / Hauteur de l'application
width = 800
height = 495
screen = pygame.display.set_mode((width, height))

# Etat du jeu au lancement de l'app
etat_app = 'menu'

# Modif taille IA fenetre 
global tailleAjoutFenetre
tailleAjoutFenetre = 200 #taille sumplémentaire de la fenetre IA pour ajout d'informations

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

        # Fonction visuelles 
def creation_jeu_humain_visuel():
    global bouton_restart_jeu_humain, bouton_menu_jeu_humain
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
    
    placement_serpent_depart_visuel()
    maj_affichage_score(0)
    maj_affichage_cycle(0)
    
def creation_jeu_ia_visuel():
    global bouton_jeu_plus_rapide, bouton_jeu_moins_rapide, bouton_menu_jeu_ia, bouton_montrer_simulation
    width_game = 594 #longueur du jeu
    
    # Zone externe au jeu
    pygame.draw.rect(screen, FOND, (width_game, 0, 200+6, 600))
    pygame.draw.line(screen, BLACK, (width_game, 0), (width_game, height), 2)   

    
    bouton_menu_jeu_ia = pygame.draw.rect(screen, GRAY, (635, 410, 130, 60))
    text_surface = font40.render("Menu", True, BLACK)
    text_rect = text_surface.get_rect(center=(700, 440))
    screen.blit(text_surface, text_rect)
    
    bouton_jeu_plus_rapide = pygame.draw.rect(screen, GRAY, (825, 130, 130, 60))
    text_surface = font40.render("+ SPEED", True, BLACK)
    text_rect = text_surface.get_rect(center=(890, 160))
    screen.blit(text_surface, text_rect)
    
    bouton_jeu_moins_rapide = pygame.draw.rect(screen, GRAY, (825, 230, 130, 60))
    text_surface = font40.render("- SPEED", True, BLACK)
    text_rect = text_surface.get_rect(center=(890, 260))
    screen.blit(text_surface, text_rect)
    
    """
    bouton_montrer_simulation = pygame.draw.rect(screen, GRAY, (825, 30, 130, 60))
    text_surface = font40.render("Montrer simu", True, BLACK)
    text_rect = text_surface.get_rect(center=(890, 60))
    screen.blit(text_surface, text_rect)
    """
    
    text_surface = font40.render("Score : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(680,50))
    screen.blit(text_surface, text_rect)
    
    text_surface = font40.render("Cycle : ", True, BLACK)
    text_rect = text_surface.get_rect(center=(680,110))
    screen.blit(text_surface, text_rect)
    
    placement_serpent_depart_visuel()
    maj_affichage_score(0)
    maj_affichage_cycle(0)

def placement_serpent_depart_visuel():
    screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
    for i in list_serpent:
        pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))

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

    """
                                                    ##########
                                                    PARTIE APP
                                                    ##########
    """ 


while LANCER_APP:
    temps_actuel = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            LANCER_APP = False
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            #MENU
            if etat_app == 'menu':
                if bouton_menu_humain.collidepoint(x, y):
                    #MODE HUMAIN
                    etat_app = 'jeu_humain'
                    dernier_mouvement_temps = 0
                    intervale_temps = 200
                    screen = pygame.display.set_mode((width, height))
                if bouton_menu_IA.collidepoint(x, y):
                    #MODE IA
                    etat_app = 'jeu_ia'
                    dernier_mouvement_temps = 0
                    intervale_temps = 200
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
                    screen = pygame.display.set_mode((width, height))
                
                if bouton_jeu_plus_rapide.collidepoint(x,y):
                    if intervale_temps <= 100:
                        if intervale_temps <= 10:
                            print("Intervalle de coups maximum atteinte : " + str(intervale_temps))
                        else:
                            intervale_temps -= 10                            
                            print("nouvelle intervale : " + str(intervale_temps))

                    else:
                        intervale_temps -= 100
                        print("nouvelle intervale : " + str(intervale_temps))
                
                if bouton_jeu_moins_rapide.collidepoint(x,y):
                    if intervale_temps >= 5000:
                        print("Intervalle de coups minimum atteinte : " + str(intervale_temps))
                    else:
                        if intervale_temps <= 100:
                            intervale_temps += 10
                            print("nouvelle intervale : " + str(intervale_temps))

                        else:
                            intervale_temps += 100
                            print("nouvelle intervale : " + str(intervale_temps))
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
                    screen = pygame.display.set_mode((width, height))

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_UP or event.key == pygame.K_z) and serpentTete[2] != Type_direction.BAS and not choix_direction:  # aller en haut
                serpentTete[2] = Type_direction.HAUT
                choix_direction = True
            elif (event.key == pygame.K_DOWN  or event.key == pygame.K_s) and serpentTete[2] != Type_direction.HAUT and not choix_direction:  # aller en bas
                serpentTete[2] = Type_direction.BAS
                choix_direction = True
            elif (event.key == pygame.K_LEFT  or event.key == pygame.K_q) and serpentTete[2] != Type_direction.DROITE and not choix_direction:  # aller a gauche
                serpentTete[2] = Type_direction.GAUCHE
                choix_direction = True
            elif (event.key == pygame.K_RIGHT  or event.key == pygame.K_d) and serpentTete[2] != Type_direction.GAUCHE and not choix_direction:  # aller a droite
                serpentTete[2] = Type_direction.DROITE
                choix_direction = True
            #cheat
            elif event.key == pygame.K_y:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,ancien_serpent_direction])
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
            pomme = creation_jeu_humain()
            screen.blit(image_pomme, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1]))

            creation_jeu_humain_visuel()
            jeu_cree = True
        
        #cycle temps du jeu
        if temps_actuel - dernier_mouvement_temps >= intervale_temps:
            
            choix_direction = False
            cycle += 1
            maj_affichage_cycle(cycle)
            dernier_mouvement_temps = temps_actuel            
            direction = serpentTete[2].value
            x,y = serpentTete[0],serpentTete[1]
            
            ancienne_position_tete = serpentTete[:2]
            ancienne_direction_tete = serpentTete[2]
            for i in range(len(list_serpent)):
                ancienne_position_segment = list_serpent[i][:2]
                ancienne_direction_segment = list_serpent[i][2]
                pygame.draw.rect(screen, WHITE, (coordonnées_case(ancienne_position_segment)[0], coordonnées_case(ancienne_position_segment)[1], taille_case, taille_case))
            #déplacement avec check colision murs
            
            
            deplacer_serpent(serpentTete,list_serpent)
            if verifier_collision(serpentTete,list_serpent):
                etat_app = 'jeu_perdu_humain'
            
            ancien_serpent_x = list_serpent[-1][0]
            ancien_serpent_y = list_serpent[-1][1]
            ancien_serpent_direction = list_serpent [-1][2]
            
            if serpentTete[:2] == pomme[:2]:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,ancien_serpent_direction])
                score += 1
                maj_affichage_score(score)
                pomme = placement_pomme(serpentTete,list_serpent)
                screen.blit(image_pomme, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1]))
            
            #maj tete serpent dessin
            if serpentTete[2] == Type_direction.BAS:
                screen.blit(image_tete_serpent_bas, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[2] == Type_direction.HAUT:
                screen.blit(image_tete_serpent_haut, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[2] == Type_direction.DROITE:
                screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if serpentTete[2] == Type_direction.GAUCHE:
                screen.blit(image_tete_serpent_gauche, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))

            for i in list_serpent:
                #maj corps serpent dessin
                pygame.draw.rect(screen, SERPENT_CORPS_COULEUR, (coordonnées_case(i)[0], coordonnées_case(i)[1], taille_case, taille_case))
           
    elif etat_app == 'jeu_ia':
        if not jeu_cree:
            screen.fill(WHITE)
            pygame.draw.rect(screen, FOND, (width, 0, tailleAjoutFenetre, height)) # Ajout parti supplémentaire pour les informations de l'IA
            pomme = creation_jeu_ia()
            screen.blit(image_pomme, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1]))
            creation_jeu_ia_visuel()
            jeu_cree = True
        
        #cycle temps du jeu
        if temps_actuel - dernier_mouvement_temps >= intervale_temps:
            cycle += 1
            maj_affichage_cycle(cycle)
            choix_direction = False
            dernier_mouvement_temps = temps_actuel            
            #direction = serpentTete[2].value
            x,y = serpentTete[0],serpentTete[1]               
            
            #joue IA
            etat_jeu_ia = generer_etat(serpentTete,list_serpent,pomme)
            
            direction = choisir_action_jeu(Q_table,etat_jeu_ia)
            #debug / direction = m['actions'][cycle-1]
            
            
            
            #déplacement avec check colision murs
            serpentTete[2] = direction

            ancienne_position_tete = serpentTete[:2]
            ancienne_direction_tete = serpentTete[2]
        
            if direction == Type_direction.BAS:
                if y < 14:
                    serpentTete[1] += 1
                else:
                    etat_app = 'jeu_perdu_ia'

            if direction == Type_direction.DROITE:
                if x < 17:
                    serpentTete[0] += 1
                else:
                    etat_app = 'jeu_perdu_ia'

            if direction == Type_direction.HAUT:
                if y > 0:
                    serpentTete[1] -= 1
                else:
                    etat_app = 'jeu_perdu_ia'
                    
            if direction == Type_direction.GAUCHE:
                if x > 0:
                    serpentTete[0] -= 1
                else:
                    etat_app = 'jeu_perdu_ia'
                    
            #deplacement du corps du serpent
            ancien_serpent_x = list_serpent[-1][0]
            ancien_serpent_y = list_serpent[-1][1]
            ancien_serpent_direction = list_serpent [-1][2]
            
            for i in range(len(list_serpent)):
                
                ancienne_position_segment = list_serpent[i][:2]
                ancienne_direction_segment = list_serpent[i][2]
        
                pygame.draw.rect(screen, WHITE, (coordonnées_case(ancienne_position_segment)[0], coordonnées_case(ancienne_position_segment)[1], taille_case, taille_case))

                list_serpent[i][0], list_serpent[i][1] = ancienne_position_tete
                list_serpent[i][2] = ancienne_direction_tete
            
                ancienne_position_tete = ancienne_position_segment
                ancienne_direction_tete = ancienne_direction_segment
            
            # colision avec son propre corps
            for i in list_serpent:
                if serpentTete[:2] == i[:2]:
                    etat_app = 'jeu_perdu_ia'
                
            # collision avec une pomme
            if serpentTete[:2] == pomme[:2]:
                list_serpent.append([ancien_serpent_x,ancien_serpent_y,ancien_serpent_direction])
                score += 1
                maj_affichage_score(score)
                pomme = placement_pomme(serpentTete,list_serpent)
                #debug/ pomme = placement_pomme_m(m,cycle)
                screen.blit(image_pomme, (coordonnées_case(pomme)[0], coordonnées_case(pomme)[1]))
 
            #maj tete serpent dessin
            if direction == Type_direction.BAS:
                screen.blit(image_tete_serpent_bas, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if direction == Type_direction.HAUT:
                screen.blit(image_tete_serpent_haut, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if direction == Type_direction.DROITE:
                screen.blit(image_tete_serpent_droite, (coordonnées_case(serpentTete)[0], coordonnées_case(serpentTete)[1]))
            if direction == Type_direction.GAUCHE:
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