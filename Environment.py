import pygame
import sys
import numpy as np

# Inicializa o Pygame
pygame.init()

# Define as cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (220, 255, 0)
DARK_GRAY = (50, 50, 50)

# Define as direções
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIRECTIONS_ANN = [[0,0], [0,1], [1,0], [1,1]]

# Define o tamanho do tabuleiro e dos quadrados
BOARD_SIZE = 7
SQUARE_SIZE = 100
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

# Define as posições dos robôs e do alvo
"""ROBOT1_POS = (1, 1)
ROBOT2_POS = (8, 8)
TARGET_POS = (1, 5)"""

# Cria a tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define the size of the map
size = 7

# Create a matrix filled with 1s
map_matrix = np.zeros((size, size))

# Set the outer border to 0s
map_matrix[1, 1:-1] = 1
map_matrix[1:-1, 1] = 1
map_matrix[-2, 1:-1] = 1
map_matrix[1:-1, -2] = 1
"""map_matrix[0, 5] = 5
map_matrix[3, 8] = 6
map_matrix[6, 8] = 6"""
print(map_matrix)

def get_random_position(starting, size):
    if size == BOARD_SIZE:
        h = np.random.randint(1, size - 2)
    else:
        h = np.random.randint(size-1)
    vertical = np.random.choice([True, False])
    top = np.random.choice([True, False])
    if vertical:
        if top:
            return [starting, starting+h]
        else:
            return [BOARD_SIZE-1-starting, starting+h]
    else:
        if top:
            return [starting+h, starting]
        else:
            return [starting+h, BOARD_SIZE-1-starting]
def close_position_and_facing(p1,p2,direction):
    if (np.abs(p1[0]-p2[0])+np.abs(p1[1]-p2[1])) == 1:
        if p1[1] < p2[1] and direction == UP:
            return True
        if p1[1] > p2[1] and direction == DOWN:
            return True
        if p1[0] > p2[0] and direction == RIGHT:
            return True
        if p1[0] < p2[0] and direction == LEFT:
            return True
    return False

def check_end(r1, r2):
    if r1.ordered and r1.spot and r1.delivered:
        if r2.ordered and r2.spot and r2.delivered:
            print("GAME FINISHED")
            return True
    return False

class Robot:
    def __init__(self, pos, color, direction):
        self.pos = list(pos)
        self.color = color
        self.direction = direction
        self.ordered = False
        self.spot = False
        self.delivered = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), SQUARE_SIZE//2 - 5)
        if self.direction == UP:
            pygame.draw.line(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE), 6)
        elif self.direction == RIGHT:
            pygame.draw.line(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), 6)
        elif self.direction == DOWN:
            pygame.draw.line(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE), 6)
        elif self.direction == LEFT:
            pygame.draw.line(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), (self.pos[0]*SQUARE_SIZE, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), 6)

    def move_forward(self):
        new_pos = self.pos.copy()
        if self.direction == UP:
            new_pos[1] -= 1
        elif self.direction == RIGHT:
            new_pos[0] += 1
        elif self.direction == DOWN:
            new_pos[1] += 1
        elif self.direction == LEFT:
            new_pos[0] -= 1
        if map_matrix[new_pos[1], new_pos[0]] == 1 and new_pos != robot1.pos and new_pos != robot2.pos:
            self.pos = new_pos

    def turn_right(self):
        self.direction = (self.direction + 1) % 4

    def turn_left(self):
        self.direction = (self.direction - 1) % 4

class Target:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), SQUARE_SIZE//2 - 5)

    def check_collision(self, robot):
        if close_position_and_facing(self.pos, robot.pos, robot.direction):
            if not robot.ordered:
                robot.ordered = True
                self.color = (self.color[0]-self.color[0]/10, self.color[1]-self.color[1]/10, self.color[2]-self.color[2]/10)
            elif robot.ordered and robot.spot:
                robot.delivered = True
                self.color = (self.color[0]-self.color[0]/10, self.color[1]-self.color[1]/10, self.color[2]-self.color[2]/10)


class Spot:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.touched = False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.pos[0]*SQUARE_SIZE + SQUARE_SIZE//2, self.pos[1]*SQUARE_SIZE + SQUARE_SIZE//2), SQUARE_SIZE//2 - 5)

    def check_collision(self, robot):
        if not self.touched and not robot.spot:
            if close_position_and_facing(self.pos, robot.pos, robot.direction):
                if robot.ordered:
                    self.touched = True
                    robot.spot = True
                    self.color = (self.color[0]-self.color[0]/10, self.color[1]-self.color[1]/10, self.color[2]-self.color[2]/10)

class Environment:
    def __init__(self, pos, color):
        self.
        self.color = color
        self.touched = False






# Função para desenhar o tabuleiro
def draw_board():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            color = WHITE if map_matrix[y, x] == 1 else DARK_GRAY
            pygame.draw.rect(screen, color, (x*SQUARE_SIZE, y*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


while True:
    # Cria os robôs, o alvo e os pontos
    robot1 = Robot(get_random_position(1,BOARD_SIZE-2), RED, RIGHT)
    r2_pos = get_random_position(1, BOARD_SIZE - 2)
    while r2_pos == robot1.pos:
        print("Tentando again")
        r2_pos = get_random_position(1,BOARD_SIZE-2)
    robot2 = Robot(r2_pos, BLUE, LEFT)
    spot1 = Spot(get_random_position(2,BOARD_SIZE-4), YELLOW)
    spot2 = Spot(get_random_position(2,BOARD_SIZE-4), YELLOW)
    """robot1 = Robot([1, 1], RED, RIGHT)
    robot2 = Robot([9, 1], BLUE, LEFT)"""
    target = Target(get_random_position(0,BOARD_SIZE), GREEN)
    """spot1 = Spot([7, 2], YELLOW)
    spot2 = Spot([8, 3], YELLOW)"""

    # Loop principal do jogo
    while True:
        restart = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    robot1.move_forward()
                elif event.key == pygame.K_RIGHT:
                    robot1.turn_right()
                elif event.key == pygame.K_LEFT:
                    robot1.turn_left()
                elif event.key == pygame.K_w:
                    robot2.move_forward()
                elif event.key == pygame.K_d:
                    robot2.turn_right()
                elif event.key == pygame.K_a:
                    robot2.turn_left()
                elif event.key == pygame.K_r:
                    restart = True

                s_r1 = map_matrix.copy()
                s_r1[spot1.pos[0]][spot1.pos[1]] = 3
                s_r1[spot2.pos[0]][spot2.pos[1]] = 3
                s_r2 = s_r1.copy()

                if not (robot1.ordered and not robot1.spot):
                    s_r1[target.pos[0]][target.pos[1]] = 2
                s_r1[robot1.pos[0]][robot1.pos[1]] = 7
                s_r1[robot2.pos[0]][robot2.pos[1]] = 8

                if not (robot2.ordered and not robot2.spot):
                    s_r2[target.pos[0]][target.pos[1]] = 2
                s_r2[robot1.pos[0]][robot1.pos[1]] = 8
                s_r2[robot2.pos[0]][robot2.pos[1]] = 7


                f_s1 = s_r1.flatten()
                f_s1 = np.append(f_s1, DIRECTIONS_ANN[robot1.direction])
                f_s1 = np.append(f_s1, DIRECTIONS_ANN[robot2.direction])

                f_s2 = s_r2.flatten()
                f_s2 = np.append(f_s2, DIRECTIONS_ANN[robot2.direction])
                f_s2 = np.append(f_s2, DIRECTIONS_ANN[robot1.direction])

                print("printing both states")
                print("Robot 1 state")
                print(s_r1)
                print("Robot 2 state")
                print(s_r2)

                print("Robot 1 state")
                print(f_s1)
                print("Robot 2 state")
                print(f_s2)


        screen.fill(BLACK)
        draw_board()
        robot1.draw()
        robot2.draw()
        target.draw()
        spot1.draw()
        spot2.draw()
        target.check_collision(robot1)
        target.check_collision(robot2)
        spot1.check_collision(robot1)
        spot1.check_collision(robot2)
        spot2.check_collision(robot1)
        spot2.check_collision(robot2)

        pygame.display.flip()

        if check_end(robot1, robot2) or restart == True:
            break

