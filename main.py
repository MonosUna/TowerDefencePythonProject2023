import sys
import time
import constants
import pygame
import pygame_menu

pygame.init()
clock = pygame.time.Clock()
balance = 10

screen = pygame.display.set_mode(constants.WINDOW_SIZE)
pygame.display.set_caption("Tower Defense Project")

towers = []
enemies = []
bullets = []


def get_x(selected_cell: tuple):
    x = selected_cell[1] * constants.CELL_SIZE + (constants.CELL_SIZE / 2)
    return x


def get_y(selected_cell: tuple):
    y = selected_cell[0] * constants.CELL_SIZE + (constants.CELL_SIZE / 2)
    return y


def finish_game():
    screen.fill((0, 0, 0))
    font1 = pygame.font.Font(None, 100)
    text1 = font1.render('YOU LOSE', True, constants.green)
    screen.blit(text1, (constants.WINDOW_SIZE[0] / 2 - 150, constants.WINDOW_SIZE[1] / 2 - 50))
    pygame.display.flip()
    time.sleep(2)
    sys.exit()


class Enemy:
    def __init__(self, x, y, speed, color, size, health_points, reward):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.x_speed = 0
        self.y_speed = 0
        self.reward = reward
        self.health_points = health_points

    def in_center(self):
        x = int(int(self.x) - (constants.CELL_SIZE / 2)) % constants.CELL_SIZE
        y = int(int(self.y) - (constants.CELL_SIZE / 2)) % constants.CELL_SIZE
        if x == 0 and y == 0:
            return True
        return False

    def set_speed(self):
        if self.in_center:
            current_cell = (
                int((self.x - constants.CELL_SIZE // 2) // constants.CELL_SIZE),
                int((self.y - constants.CELL_SIZE // 2) // constants.CELL_SIZE),
            )
            if current_cell[0] == constants.enemy_finish[0] and current_cell[1] == constants.enemy_finish[1]:
                finish_game()
            if constants.field[current_cell[1]][current_cell[0] + 1] == 1:
                self.x_speed = self.speed
                self.y_speed = 0
                return
            if (
                    constants.field[current_cell[1] - 1][current_cell[0]] == 1
                    and constants.field[current_cell[1] + 1][current_cell[0]] != 1
            ):
                self.x_speed = 0
                self.y_speed = -self.speed
                return
            if (
                    constants.field[current_cell[1] + 1][current_cell[0]] == 1
                    and constants.field[current_cell[1] - 1][current_cell[0]] != 1
            ):
                self.x_speed = 0
                self.y_speed = self.speed
                return
        return

    def move(self):
        self.x += self.x_speed
        self.y += self.y_speed

    def draw(self):
        self.set_speed()
        self.move()
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.size)

    def check_for_death(self):
        if self.health_points <= 0:
            enemies.remove(self)
            return True
        return False


class Tower:
    def __init__(self, x, y, color, size, attack_distance, damage, price, type):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.attack_distance = attack_distance
        self.damage = damage
        self.price = price
        self.type = type
        if self.type == 2:
            self.attack_speed = 200

    def create_tower(self, selected_cell: tuple):
        self.x = get_x(selected_cell)
        self.y = get_y(selected_cell)

    def draw(self):
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.size)

    def place_tower(self, selected_cell):
        global balance
        if self.price <= balance and constants.field[selected_cell[0]][selected_cell[1]] == 0:
            balance -= self.price
            constants.field[selected_cell[0]][selected_cell[1]] = 2
            self.create_tower(selected_cell)
            towers.append(self)
            pygame.draw.circle(screen, self.color, [self.x, self.y], self.size)

    def try_to_attack(self, time):
        already_attacked = False
        global balance
        if self.type == 1:
            for enemy in enemies:
                if not already_attacked:
                    distance = (
                                       (self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2
                               ) ** 0.5
                    if self.attack_distance >= distance:
                        attack(enemy, self.damage)
                        pygame.draw.line(
                            screen, constants.red, (self.x, self.y), (enemy.x, enemy.y)
                        )
                        if enemy.check_for_death():
                            balance += enemy.reward
                        already_attacked = True
        if self.type == 2 and time % self.attack_speed == 0:
            min_distance = self.attack_distance + 1
            nearest_enemy = None
            for enemy in enemies:
                distance = ((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2) ** 0.5
                if min_distance > distance:
                    nearest_enemy = enemy
                    min_distance = distance
            if nearest_enemy is not None:
                bullet = Bullet(self.x, self.y, constants.green, 3, 10, self, nearest_enemy)
                bullets.append(bullet)


def attack(enemy: Enemy, damage):
    enemy.health_points -= damage


class Bullet:
    def __init__(self, x, y, color, size, speed, owner: Tower, target: Enemy):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.owner = owner
        self.target = target

    def move(self):
        global balance
        if self.target not in enemies:
            bullets.remove(self)
            return
        vector = (self.target.x - self.x, self.target.y - self.y)
        distance = (
                           (self.target.x - self.x) ** 2 + (self.y - self.target.y) ** 2
                   ) ** 0.5
        if distance < 10:
            attack(self.target, self.owner.damage)
            if self.target.check_for_death():
                balance += self.target.reward
            bullets.remove(self)
            return
        self.x += (self.speed * vector[0]) / distance
        self.y += (self.speed * vector[1]) / distance

    def draw(self):
        pygame.draw.circle(screen, self.color, [self.x, self.y], self.size)


def spawn_wave(time: int):
    boost = time // 2000
    if time % 60 == 0 and time < 5000:
        if time < 1000:
            enemy = Enemy(get_x(constants.enemy_start), get_y(constants.enemy_start), 1, constants.white, 15, 500, 5)
            enemies.append(enemy)
        elif time < 3000:
            enemy = Enemy(get_x(constants.enemy_start), get_y(constants.enemy_start), 2, constants.marine, 15, 2000, 10)
            enemies.append(enemy)
        elif time < 5000:
            enemy = Enemy(get_x(constants.enemy_start), get_y(constants.enemy_start), 5, constants.purple, 15, 2000, 20)
            enemies.append(enemy)
    if time % max(40 - boost, 20) == 0 and time > 5000:
        enemy = Enemy(get_x(constants.enemy_start), get_y(constants.enemy_start),
                      5 + boost, constants.purple, 15, 2000 + (boost * 100), 20)
        enemies.append(enemy)


def redraw_screen(selected_cell):
    for row in range(constants.NUM_ROWS):
        for col in range(constants.NUM_COLS):
            if selected_cell == (row, col):
                pygame.draw.rect(screen, constants.yellow, constants.grid[row][col], 1)
            else:
                if constants.field[row][col] == 0:
                    pygame.draw.rect(screen, constants.marine, constants.grid[row][col], 1)
                else:
                    pygame.draw.rect(screen, constants.red, constants.grid[row][col], 1)


def press_key(selected_cell):
    if selected_cell is not None:
        global balance
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            tower = Tower(0, 0, constants.red, 20, 100, 5, 10, 1)
            tower.place_tower(selected_cell)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_2]:
            tower = Tower(0, 0, constants.blue, 20, 1000, 500, 30, 2)
            tower.place_tower(selected_cell)


def main():
    global balance
    selected_cell = None
    running = True
    time = 0
    while running:
        time += 1
        spawn_wave(time)
        clock.tick(constants.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for row in range(constants.NUM_ROWS):
                    for col in range(constants.NUM_COLS):
                        if constants.grid[row][col].collidepoint(mouse_pos):
                            selected_cell = (row, col)
                            pygame.draw.rect(screen, constants.yellow, constants.grid[row][col], 1)
                        else:
                            if constants.field[row][col] == 0:
                                pygame.draw.rect(screen, constants.marine, constants.grid[row][col], 1)
                            else:
                                pygame.draw.rect(screen, constants.red, constants.grid[row][col], 1)
        redraw_screen(selected_cell)
        for enemy in enemies:
            enemy.draw()
        for tower in towers:
            tower.draw()
            tower.try_to_attack(time)
        for bullet in bullets:
            bullet.move()
            bullet.draw()
        press_key(selected_cell)
        font1 = pygame.font.Font(None, 36)
        text1 = font1.render('balance: ' + str(balance), True, constants.green)
        screen.blit(text1, (10, 50))
        pygame.display.flip()
        screen.fill((0, 0, 0))

    pygame.quit()


menu = pygame_menu.Menu('Welcome to tower defence game', 1250, 800, theme=pygame_menu.themes.THEME_BLUE)

menu.add.button('Play', main)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)
