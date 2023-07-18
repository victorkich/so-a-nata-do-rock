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

DIRECTIONS_ANN = [[0, 0], [0, 1], [1, 0], [1, 1]]

# Define o tamanho do tabuleiro e dos quadrados
BOARD_SIZE = 7
SQUARE_SIZE = 100
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

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


def close_position_and_facing(p1, p2, direction):
    if (np.abs(p1[0] - p2[0]) + np.abs(p1[1] - p2[1])) == 1:
        if p1[1] < p2[1] and direction == UP:
            return True
        if p1[1] > p2[1] and direction == DOWN:
            return True
        if p1[0] > p2[0] and direction == RIGHT:
            return True
        if p1[0] < p2[0] and direction == LEFT:
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
        pygame.draw.circle(screen, self.color,
                           (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                           SQUARE_SIZE // 2 - 5)
        if self.direction == UP:
            pygame.draw.line(screen, self.color, (
            self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                             (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE), 6)
        elif self.direction == RIGHT:
            pygame.draw.line(screen, self.color, (
            self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                             (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2), 6)
        elif self.direction == DOWN:
            pygame.draw.line(screen, self.color, (
            self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                             (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE), 6)
        elif self.direction == LEFT:
            pygame.draw.line(screen, self.color, (
            self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                             (self.pos[0] * SQUARE_SIZE, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2), 6)

    def move_forward(self, other_robot):
        new_pos = self.pos.copy()
        if self.direction == UP:
            new_pos[1] -= 1
        elif self.direction == RIGHT:
            new_pos[0] += 1
        elif self.direction == DOWN:
            new_pos[1] += 1
        elif self.direction == LEFT:
            new_pos[0] -= 1
        if map_matrix[new_pos[1], new_pos[0]] == 1 and new_pos != other_robot.pos:
            self.pos = new_pos
        else:
            collided = True
            return collided

    def turn_right(self):
        self.direction = (self.direction + 1) % 4

    def turn_left(self):
        self.direction = (self.direction - 1) % 4


class Target:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                           SQUARE_SIZE // 2 - 5)

    def check_facing(self, robot):
        if close_position_and_facing(self.pos, robot.pos, robot.direction):
            if not robot.ordered:
                robot.ordered = True
                self.color = (self.color[0] - self.color[0] / 10, self.color[1] - self.color[1] / 10,
                              self.color[2] - self.color[2] / 10)
                return True
            elif robot.ordered and robot.spot and not robot.delivered:
                robot.delivered = True
                self.color = (self.color[0] - self.color[0] / 10, self.color[1] - self.color[1] / 10,
                              self.color[2] - self.color[2] / 10)
                return True


class Spot:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.touched = False

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (self.pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2, self.pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2),
                           SQUARE_SIZE // 2 - 5)

    def check_facing(self, robot):
        if not self.touched and not robot.spot:
            if close_position_and_facing(self.pos, robot.pos, robot.direction):
                if robot.ordered:
                    self.touched = True
                    robot.spot = True
                    self.color = (self.color[0] - self.color[0] / 10, self.color[1] - self.color[1] / 10,
                                  self.color[2] - self.color[2] / 10)
                    return True


class Environment:
    def __init__(self):
        # Cria os robôs, o alvo e os pontos
        self.robot1 = Robot(self.get_random_position(1, BOARD_SIZE - 2), RED, RIGHT)
        self.r2_pos = self.get_random_position(1, BOARD_SIZE - 2)
        # in order to not start at same position
        while self.r2_pos == self.robot1.pos:
            self.r2_pos = self.get_random_position(1, BOARD_SIZE - 2)
        self.robot2 = Robot(self.r2_pos, BLUE, LEFT)
        self.spot1 = Spot(self.get_random_position(2, BOARD_SIZE - 4), YELLOW)
        self.spot2 = Spot(self.get_random_position(2, BOARD_SIZE - 4), YELLOW)
        self.target = Target(self.get_random_position(0, BOARD_SIZE), GREEN)

        self.s_r1 = []
        self.s_r2 = []
        self.update_states()
        self.display_gamescreen()

    def step(self, action, robot_id):
        collided = False
        if robot_id == 1:
            if action == 0:
                collided = self.robot1.move_forward(self.robot2)
            elif action == 1:
                self.robot1.turn_right()
            elif action == 2:
                self.robot1.turn_left()
        elif robot_id == 2:
            if action == 0:
                collided = self.robot2.move_forward(self.robot1)
            elif action == 1:
                self.robot2.turn_right()
            elif action == 2:
                self.robot2.turn_left()

        self.update_states()

        #print("printing both states")
        #print("Robot 1 state")
        #print(self.s_r1)
        #print("Robot 2 state")
        #print(self.s_r2)

        done = self.check_end()
        reward = -1
        # se conseguir completar tudo
        if done:
            reward = 100
        # se bateu na parede ou no amiguinho
        elif collided:
            #done = True
            reward = -1
        else:
            if robot_id == 1:
                if self.check_facings(self.robot1):
                    reward = 100
            elif robot_id == 2:
                if self.check_facings(self.robot2):
                    reward = 100

        self.display_gamescreen()

        if robot_id == 1:
            return self.s_r1, reward, done
        elif robot_id == 2:
            return self.s_r2, reward, done

    def update_states(self):
        # updating states
        self.s_r1 = map_matrix.copy()
        self.s_r1[self.spot1.pos[0]][self.spot1.pos[1]] = 2
        self.s_r1[self.spot2.pos[0]][self.spot2.pos[1]] = 2
        self.s_r2 = self.s_r1.copy()


        self.ordered = False
        self.spot = False
        self.delivered = False

        if not self.robot1.ordered:
            self.s_r1[self.target.pos[0]][self.target.pos[1]] = 3
        elif not self.robot1.spot:
            self.s_r1[self.target.pos[0]][self.target.pos[1]] = 4
        elif not self.robot1.delivered:
            self.s_r1[self.target.pos[0]][self.target.pos[1]] = 5
        else:
            self.s_r1[self.target.pos[0]][self.target.pos[1]] = 6

        self.s_r1[self.robot1.pos[0]][self.robot1.pos[1]] = 7
        self.s_r1[self.robot2.pos[0]][self.robot2.pos[1]] = 8

        if not self.robot2.ordered:
            self.s_r2[self.target.pos[0]][self.target.pos[1]] = 3
        elif not self.robot2.spot:
            self.s_r2[self.target.pos[0]][self.target.pos[1]] = 4
        elif not self.robot2.delivered:
            self.s_r2[self.target.pos[0]][self.target.pos[1]] = 5
        else:
            self.s_r2[self.target.pos[0]][self.target.pos[1]] = 6

        self.s_r2[self.robot1.pos[0]][self.robot1.pos[1]] = 8
        self.s_r2[self.robot2.pos[0]][self.robot2.pos[1]] = 7

        self.s_r1 = self.s_r1.flatten()
        self.s_r1 = np.append(self.s_r1, DIRECTIONS_ANN[self.robot1.direction])
        self.s_r1 = np.append(self.s_r1, DIRECTIONS_ANN[self.robot2.direction])

        self.s_r2 = self.s_r2.flatten()
        self.s_r2 = np.append(self.s_r2, DIRECTIONS_ANN[self.robot2.direction])
        self.s_r2 = np.append(self.s_r2, DIRECTIONS_ANN[self.robot1.direction])

    def check_facings(self, robot):
        c1 = self.target.check_facing(robot)
        c2 = self.spot1.check_facing(robot)
        c3 = self.spot2.check_facing(robot)
        if c1 or c2 or c3:
            print("ECOSTO AQUI")
            return True
        else:
            return False


    def reset(self):
        # Cria os robôs, o alvo e os pontos
        self.robot1 = Robot(self.get_random_position(1, BOARD_SIZE - 2), RED, RIGHT)
        r2_pos = self.get_random_position(1, BOARD_SIZE - 2)
        # in order to not start at same position
        while r2_pos == self.robot1.pos:
            r2_pos = self.get_random_position(1, BOARD_SIZE - 2)
        self.robot2 = Robot(self.r2_pos, BLUE, LEFT)

        self.spot1 = Spot(self.spot1.pos, YELLOW)
        self.spot2 = Spot(self.spot2.pos, YELLOW)
        self.target = Target(self.target.pos, GREEN)
        
        #self.spot1 = Spot(self.get_random_position(2, BOARD_SIZE - 4), YELLOW)
        #self.spot2 = Spot(self.get_random_position(2, BOARD_SIZE - 4), YELLOW)
        #self.target = Target(self.get_random_position(0, BOARD_SIZE), GREEN)
        self.update_states()

    def get_state(self, robot_id):
        if robot_id == 1:
            return self.s_r1
        elif robot_id == 2:
            return self.s_r2

    # Função para desenhar o tabuleiro
    def draw_board(self):
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                color = WHITE if map_matrix[y, x] == 1 else DARK_GRAY
                pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def get_random_position(self, starting, size):
        if size == BOARD_SIZE:
            h = np.random.randint(1, size - 2)
        else:
            h = np.random.randint(size - 1)
        vertical = np.random.choice([True, False])
        top = np.random.choice([True, False])
        if vertical:
            if top:
                return [starting, starting + h]
            else:
                return [BOARD_SIZE - 1 - starting, starting + h]
        else:
            if top:
                return [starting + h, starting]
            else:
                return [starting + h, BOARD_SIZE - 1 - starting]

    def check_end(self):
        if self.robot1.ordered and self.robot1.spot and self.robot1.delivered:
            if self.robot2.ordered and self.robot2.spot and self.robot2.delivered:
                print("GAME FINISHED")
                return True
        return False

    def display_gamescreen(self):

        screen.fill(BLACK)
        self.draw_board()
        self.robot1.draw()
        self.robot2.draw()
        self.target.draw()
        self.spot1.draw()
        self.spot2.draw()

        pygame.display.flip()
