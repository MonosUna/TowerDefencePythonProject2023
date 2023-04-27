import constants
import obj
import pygame
import assist_func


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
        self.end = False
        self.slowed = False
        self.max_HP = health_points

    def in_center(self):
        """Checks whether the object is in the center of the cell."""
        x = int(int(self.x) - (constants.CELL_SIZE / 2)) % constants.CELL_SIZE
        y = int(int(self.y) - (constants.CELL_SIZE / 2)) % constants.CELL_SIZE
        if x == 0 and y == 0:
            return True
        return False

    def set_speed(self):
        """Change direction of enemy."""
        if self.in_center:
            current_cell = (
                int((self.x - constants.CELL_SIZE // 2) // constants.CELL_SIZE),
                int((self.y - constants.CELL_SIZE // 2) // constants.CELL_SIZE),
            )
            if (
                current_cell[0] == constants.enemy_finish[0]
                and current_cell[1] == constants.enemy_finish[1]
            ):
                self.end = True
            if not self.end:
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

    def draw_health_bar(self):
        length = 50
        height = 20
        start_x = self.x - 25
        start_y = self.y - 50
        pygame.draw.rect(
            obj.screen, constants.red, (start_x, start_y, length, height), 1
        )
        pygame.draw.rect(
            obj.screen,
            constants.green,
            (start_x, start_y, length * self.health_points / self.max_HP, height),
        )

    def draw(self):
        self.set_speed()
        self.move()
        self.draw_health_bar()
        pygame.draw.circle(obj.screen, self.color, [self.x, self.y], self.size)

    def check_for_death(self):
        if self.health_points <= 0:
            obj.enemies.remove(self)
            return True
        return False


class Tower:
    def __init__(
        self,
        x,
        y,
        color,
        size,
        attack_distance,
        damage,
        price,
        attack_speed,
        bullet_type,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.attack_distance = attack_distance
        self.damage = damage
        self.price = price
        self.bullet_type = bullet_type
        self.attack_speed = attack_speed

    def create_tower(self, selected_cell: tuple):
        self.x = assist_func.get_x(selected_cell)
        self.y = assist_func.get_y(selected_cell)

    def draw(self):
        pygame.draw.circle(obj.screen, self.color, [self.x, self.y], self.size)

    def place_tower(self, selected_cell):
        """If cell is free and enough balance, place tower here."""
        if (
            self.price <= obj.balance
            and constants.field[selected_cell[0]][selected_cell[1]] == 0
        ):
            obj.balance -= self.price
            constants.field[selected_cell[0]][selected_cell[1]] = 2
            self.create_tower(selected_cell)
            obj.towers.append(self)
            pygame.draw.circle(obj.screen, self.color, [self.x, self.y], self.size)

    def attack_with_bullets(self):
        min_distance = self.attack_distance + 1
        nearest_enemy = None
        for enemy in obj.enemies:
            distance = ((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2) ** 0.5
            if min_distance > distance:
                nearest_enemy = enemy
                min_distance = distance
        if nearest_enemy is not None:
            color = (0, 0, 0)
            if self.bullet_type == "7.62":
                color = constants.green
            if self.bullet_type == "Slow":
                color = constants.orange
            if self.bullet_type == "Explode":
                color = constants.white
            bullet = Bullet(
                self.x, self.y, color, 3, 10, self, nearest_enemy, self.bullet_type
            )
            obj.bullets.append(bullet)

    def try_to_attack(self, time):
        already_attacked = False
        if self.bullet_type == "None":
            for enemy in obj.enemies:
                if not already_attacked:
                    distance = (
                        (self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2
                    ) ** 0.5
                    if self.attack_distance >= distance:
                        attack(enemy, self.damage)
                        pygame.draw.line(
                            obj.screen,
                            constants.red,
                            (self.x, self.y),
                            (enemy.x, enemy.y),
                        )
                        if enemy.check_for_death():
                            obj.balance += enemy.reward
                            obj.score += enemy.reward
                        already_attacked = True
        if self.bullet_type != "None" and time % self.attack_speed == 0:
            self.attack_with_bullets()


def attack(enemy: Enemy, damage):
    enemy.health_points -= damage


class Bullet:
    def __init__(
        self, x, y, color, size, speed, owner: Tower, target: Enemy, bullet_type
    ):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.owner = owner
        self.target = target
        self.bullet_type = bullet_type

    def bullet_attack_for_different_types(self):
        if self.bullet_type == "7.62":
            attack(self.target, self.owner.damage)
        if self.bullet_type == "Slow":
            attack(self.target, self.owner.damage)
            if self.target.slowed is False:
                self.target.speed *= 0.5
                self.target.slowed = True
        if self.target.check_for_death():
            obj.balance += self.target.reward
            obj.score += self.target.reward
        if self.bullet_type == "Explode":
            radius = 200
            erased = []
            for opponent in obj.enemies:
                distance = (
                    (self.x - opponent.x) ** 2 + (self.y - opponent.y) ** 2
                ) ** 0.5
                if distance <= radius:
                    attack(opponent, self.owner.damage)
                    if opponent.health_points <= 0:
                        erased.append(opponent)
            for opponent in erased:
                opponent.check_for_death()
            pygame.draw.circle(obj.screen, constants.pink, (self.x, self.y), 200, 5)
        obj.bullets.remove(self)

    def move(self):
        """Move bullet and check for hit."""
        if self.target not in obj.enemies:
            obj.bullets.remove(self)
            return
        vector = (self.target.x - self.x, self.target.y - self.y)
        distance = (
            (self.target.x - self.x) ** 2 + (self.y - self.target.y) ** 2
        ) ** 0.5
        if distance < 10:
            self.bullet_attack_for_different_types()
            return
        self.x += (self.speed * vector[0]) / distance
        self.y += (self.speed * vector[1]) / distance

    def draw(self):
        pygame.draw.circle(obj.screen, self.color, [self.x, self.y], self.size)
