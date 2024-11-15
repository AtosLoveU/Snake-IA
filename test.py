import numpy as np
import random

# Configuration de la grille
TAILLE_GRILLE_X = 18
TAILLE_GRILLE_Y = 15
TAILLE_VISION = 5
list_actions_ia = ('haut', 'droite', 'bas', 'gauche')

# Q-table dictionnaire
Q_table = {}

# Choisir une action (epsilon-greedy)
def choisir_action(q_table, etat, epsilon=0.1):
    if random.uniform(0, 1) < epsilon:
        # Choix aléatoire pour explorer
        return random.choice(list_actions_ia)
    else:
        # Choix de l'action ayant la valeur Q maximale
        q_values = get_q_table(q_table, etat)
        if (q_values.get('haut') == q_values.get('droite') and
            q_values.get('droite') == q_values.get('bas') and
            q_values.get('bas') == q_values.get('gauche')):
            return random.choice(list_actions_ia)
        else:
            return max(q_values, key=q_values.get)
            

def generer_etat(serpentTete, list_serpent, pomme):
    # Création d'une zone de vision autour de la tête du serpent
    etatGrille = np.zeros((TAILLE_VISION, TAILLE_VISION), dtype=int)
    x, y = serpentTete

    for seg in list_serpent:
        dx = seg[0] - x + 2
        dy = seg[1] - y + 2
        if 0 <= dx < TAILLE_VISION and 0 <= dy < TAILLE_VISION:
            etatGrille[dx][dy] = 1

    return (tuple(serpentTete), tuple(pomme), tuple(map(tuple, etatGrille)))

# Récupérer les valeurs de Q pour un état donné
def get_q_table(q_table, etat):
    if etat not in q_table:
        q_table[etat] = {action: 0 for action in list_actions_ia}
    return q_table[etat]

# Mettre à jour la Q-table
def update_q_table(q_table, etat, action, valeur):
    if etat not in q_table:
        q_table[etat] = {a: 0 for a in list_actions_ia}
    q_table[etat][action] = valeur

# Mettre à jour la Q-table (formule de Bellman)
def mise_a_jour_q_learning(q_table, etat, action, reward, etat_suivant, alpha=0.1, gamma=0.9):
    max_q_suivant = max(get_q_table(q_table, etat_suivant).values())
    valeur_actuelle = get_q_table(q_table, etat)[action]
    nouvelle_valeur = valeur_actuelle + alpha * (reward + gamma * max_q_suivant - valeur_actuelle)
    update_q_table(q_table, etat, action, nouvelle_valeur)

# Générer une nouvelle pomme
def generer_nouvelle_pomme(list_serpent):
    while True:
        rdm_x = random.randint(0, TAILLE_GRILLE_X - 1)
        rdm_y = random.randint(0, TAILLE_GRILLE_Y - 1)
        if all(segment != [rdm_x, rdm_y] for segment in list_serpent):
            return [rdm_x, rdm_y]

# Simuler une action
def simuler_action(serpentTete, list_serpent, action, pomme):
    x, y = serpentTete
    if action == 'haut':
        y -= 1
    elif action == 'bas':
        y += 1
    elif action == 'gauche':
        x -= 1
    elif action == 'droite':
        x += 1

    nouvelle_tete = [x, y]
    done = False

    # Vérifier conditions de fin et récompenses
    if nouvelle_tete == pomme:
        reward = 20
        pomme = generer_nouvelle_pomme(list_serpent + [nouvelle_tete])
    elif nouvelle_tete in list_serpent or not (0 <= x < TAILLE_GRILLE_X and 0 <= y < TAILLE_GRILLE_Y):
        reward = -20
        done = True
    else:
        reward = -1

    # Mettre à jour le serpent
    nouveau_serpent = list_serpent + [nouvelle_tete]
    if nouvelle_tete != pomme:
        nouveau_serpent.pop(0)  # Enlever la queue si pas de pomme mangée

    # Générer le nouvel état
    nouvel_etat = generer_etat(nouvelle_tete, nouveau_serpent, pomme)
    return nouvel_etat, reward, done, nouveau_serpent, pomme

# Entraîner l'agent
def entrainer(q_table, episodes=10, alpha=0.1, gamma=0.9, epsilon=0.1, max_steps=100):
    for episode in range(episodes):
        print(f"--- Épisode {episode + 1} ---")
        # Initialiser l'état
        serpentTete = [6, 4]
        list_serpent = [[5,4]]
        pomme = [7, 5]
        etat_actuel = generer_etat(serpentTete, list_serpent, pomme)

        for step in range(max_steps):
            # Choisir une action
            action = choisir_action(q_table, etat_actuel, epsilon)
            # Simuler l'action
            nouvel_etat, reward, done, list_serpent, pomme = simuler_action(serpentTete, list_serpent, action, pomme)
            # Mise à jour de la Q-table
            mise_a_jour_q_learning(q_table, etat_actuel, action, reward, nouvel_etat, alpha, gamma)
            # Passer au nouvel état
            etat_actuel = nouvel_etat
            serpentTete = list_serpent[-1]

            print(f"Étape {step + 1}, Action : {action}, Reward : {reward}, Tête : {serpentTete}, Pomme : {pomme}")

            if done:
                print(f"Fin de l'épisode à l'étape {step + 1}")
                break

# Tester l'entraînement
entrainer(Q_table, episodes=5)
print(Q_table)
print(len(Q_table))
