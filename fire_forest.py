import random
import sys
import time
import numpy as np
import pygame

WIDTH, HEIGHT = 40, 24  # Wysokość i szerokość tablicy numpy
TILE_SIZE = 30 # Wielkość pojedynczego pola w którym wyświetlany jest obiekt
TREE_DENSITY = 0.9  # Gęstość lasu
GROW_CHANCE = 0.001  # Szansa na wyrośnięcie drzewa w pustym miejscu
BOLT_STRIKING_CHANCE = 0.0001  # Szansa na uderzenie pioruna w drzewo
FIRE_SPREAD_CHANCE = 0.5  # Szansa na rozprzestrzenienie się ognia na drzewo
LAKES_DENSITY = 0.1  # Gęstość jezior
TREE_REGENERATION_TIME = 5  # Ilość iteracji po których drzewo odnawia się
TREE_REGENERATION_CHANCE = 0.2  # Szansa na odnowę drzewa
PAUSE_LENGTH = 0.2 # Długość pauzy pomiędzy iteracjami w sekundach

pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption("Forest Fire Simulation")

Tree = pygame.image.load('./Images/drzewo.png')
Tree = pygame.transform.scale(Tree, (TILE_SIZE, TILE_SIZE))
SmallTree = pygame.image.load('./Images/male_drzewo.png')
SmallTree = pygame.transform.scale(SmallTree, (TILE_SIZE, TILE_SIZE))
MediumTree = pygame.image.load('./Images/srednie_drzewo.png')
MediumTree = pygame.transform.scale(MediumTree, (TILE_SIZE, TILE_SIZE))
Tree2 = pygame.image.load('./Images/plonace_drzewo1.png')
Tree2 = pygame.transform.scale(Tree2, (TILE_SIZE, TILE_SIZE))
Tree3 = pygame.image.load('./Images/plonace_drzewo2.png')
Tree3 = pygame.transform.scale(Tree3, (TILE_SIZE, TILE_SIZE))
BurnedTree = pygame.image.load('./Images/spalone_drzewo.png')
BurnedTree = pygame.transform.scale(BurnedTree, (TILE_SIZE, TILE_SIZE))
Fire = pygame.image.load('./Images/ogien.png')
Fire = pygame.transform.scale(Fire, (TILE_SIZE, TILE_SIZE))
Bolt = pygame.image.load('./Images/piorun.png')
Bolt = pygame.transform.scale(Bolt, (TILE_SIZE, TILE_SIZE))
Lake = pygame.image.load('./Images/jezioro.png')
Lake = pygame.transform.scale(Lake, (TILE_SIZE, TILE_SIZE))

def check_parameters():
    params = {
        "GROW_CHANCE": GROW_CHANCE,
        "BOLT_STRIKING_CHANCE": BOLT_STRIKING_CHANCE,
        "FIRE_SPREAD_CHANCE": FIRE_SPREAD_CHANCE,
        "TREE_REGENERATION_CHANCE": TREE_REGENERATION_CHANCE,
        'TREE_DENSITY': TREE_DENSITY,
        'LAKES_DENSITY': LAKES_DENSITY
    }
    for name, var in params.items():
        if not 0 <= var <= 1:
            raise ValueError(f"{name} musi być wartością od 0 do 1.")

def fireForestSim():
    forest = createNewForest()
    regeneration_time = np.zeros((WIDTH, HEIGHT))
    iteration = 0
    not_burned_trees = [1, 8, 9]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        screen.fill('green')
        next_forest = np.zeros((WIDTH, HEIGHT))
        displayForest(forest)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                # Jeżeli w tej komórce w poprzedniej iteracji przypisano już jakiś stan pomiń tą komórkę
                if next_forest[x][y] != 0:
                    continue
                # Jeżeli w tej komórce w poprzedniej iteracji drzewo nie podpaliło się to pozostaje drzewem
                elif next_forest[x][y] != 5:
                    next_forest[x][y] = 1

                if (forest[x][y] == 0) and (random.random() <= GROW_CHANCE):  # Jeżeli komórka jest pusta i wylosowana liczba jest mniejsza lub równa szansie na wyrośnięcie drzewa
                    next_forest[x][y] = 8  # Wyrasta małe drzewo
                elif (forest[x][y] == 1) and (random.random() <= BOLT_STRIKING_CHANCE):  # Jeżeli w tej komórce jest drzewo i wylosowana liczba jest mniejsza lub równa szansie na uderzenie pioruna
                    next_forest[x][y] = 2  # Piorun uderza w drzewo
                elif forest[x][y] == 3:  # Jeżeli w tej komórce jest ogień
                    next_forest[x][y] = 7  # Zastąp ogień spalonym drzewem
                    regeneration_time[x][y] = TREE_REGENERATION_TIME  # Rozpocznij odliczanie do odnowienia drzewa
                elif forest[x][y] == 2:  # Jeżeli w tej komórce w drzewo uderzył piorun
                    next_forest[x][y] = 5  # Zamień piorun na 1 stopień spalania drzewa
                elif forest[x][y] == 5:
                    next_forest[x][y] = 6  # 2 stopień spalania drzewa
                elif forest[x][y] == 6:
                    next_forest[x][y] = 3  # Ogień
                elif forest[x][y] == 7: # Jeżeli w tej komórce jest spalone drzewo
                    if regeneration_time[x][y] > 0: # Jeżeli odliczenie do reneracji nie skończyło się
                        regeneration_time[x][y] -= 1 # Zmniejsz czas regeneracji o 1
                        if regeneration_time[x][y] == 0: # Jeżeli odliczanie do regenracji skończyło się
                            if random.random() <= TREE_REGENERATION_CHANCE:  # Jeżeli wylosowana liczba jest mniejsza lub równa szansie na regenrację drzewa
                                next_forest[x][y] = 8  # Drzewa zaczyna się odnawiać
                            else:
                                next_forest[x][y] = 0  # W przeciwnym wypadku komórka zmienia się na pustą
                        else:
                            next_forest[x][y] = 7
                elif forest[x][y] == 8:
                    next_forest[x][y] = 9  # Średnie drzewo
                elif forest[x][y] == 9:
                    next_forest[x][y] = 1  # Duże drzewo
                elif forest[x][y] == 1:
                    # Sprawdzenie 8 sąsiadów drzewa
                    for ix in range(-1, 2):
                        for iy in range(-1, 2):
                            # Pomiń sprawdzanie komórki w której znajduję się drzewo
                            if ix == 0 and iy == 0:
                                continue
                            # Sprawdzenie czy nie wyszliśmy poza ekran
                            if (x + ix) >= 0 and (y + iy) >= 0:
                                if (x + ix) <= WIDTH - 1 and (y + iy) <= HEIGHT - 1:
                                    # Jeżeli w komórce sąsiada jest ogień i wylosowana liczba jest mniejsza lub równa szansie na rozprzestenienie ognia
                                    if (forest[x + ix][y + iy] == 3) and (random.random() <= FIRE_SPREAD_CHANCE):
                                        next_forest[x][y] = 5 # Podpal drzewo
                else:
                    next_forest[x][y] = forest[x][y]

        if not np.any(np.isin(forest, not_burned_trees)):
            print("Wszystkie drzewa spłonęły.")
            pygame.quit()
            sys.exit()

        forest = next_forest
        iteration += 1
        pygame.display.set_caption(f"Forest Fire Simulation - Iteration: {iteration}")

        time.sleep(PAUSE_LENGTH)
        pygame.display.update()


def createNewForest():
    forestlist = np.zeros((WIDTH, HEIGHT))

    # Generowanie drzew
    TREES_NUMBER = int(TREE_DENSITY * (WIDTH * HEIGHT))
    if TREES_NUMBER < 1:
        TREES_NUMBER = 1
    while TREES_NUMBER > 0:
        x, y = [random.randint(0, WIDTH - 1)], [random.randint(0, HEIGHT - 1)]
        if forestlist[x, y] == 0:
            forestlist[x, y] = 1
            TREES_NUMBER -= 1

    # Generowanie jezior
    LAKES_NUMBER = int(LAKES_DENSITY * (WIDTH * HEIGHT))
    if LAKES_DENSITY + TREE_DENSITY > 1:
        raise ValueError("Suma LAKES_DENSITY i TREE_DENSITY musi być mniejsza bądz równa 1")
    if LAKES_NUMBER < 1:
        LAKES_NUMBER = 1
    while LAKES_NUMBER > 0:
        x, y = [random.randint(0, WIDTH - 1)], [random.randint(0, HEIGHT - 1)]
        if forestlist[x, y] == 0:
            forestlist[x, y] = 4
            LAKES_NUMBER -= 1

    # Generowanie pożaru
    x, y = [random.randint(0, WIDTH - 1)], [random.randint(0, HEIGHT - 1)]
    while forestlist[x, y] != 1:
        x, y = [random.randint(0, WIDTH - 1)], [random.randint(0, HEIGHT - 1)]
    forestlist[x, y] = 3

    return forestlist


def displayForest(forest):
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if forest[x][y] == 1:
                screen.blit(Tree, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 2:
                screen.blit(Bolt, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 3:
                screen.blit(Fire, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 4:
                screen.blit(Lake, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 5:
                screen.blit(Tree2, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 6:
                screen.blit(Tree3, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 7:
                screen.blit(BurnedTree, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 8:
                screen.blit(SmallTree, (x * TILE_SIZE, y * TILE_SIZE))
            elif forest[x][y] == 9:
                screen.blit(MediumTree, (x * TILE_SIZE, y * TILE_SIZE))


if __name__ == "__main__":
    check_parameters()
    fireForestSim()
