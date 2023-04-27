import constants
import pygame
import pygame_menu
import obj
import classes
import assist_func
import time
import random

pygame.init()


def finish_game():
    """A function that ends the game and returns you to the menu."""
    obj.screen.fill((0, 0, 0))
    font1 = pygame.font.Font(None, 100)
    text1 = font1.render("GAME OVER", True, constants.green)
    text2 = font1.render("YOUR SCORE:" + str(obj.score), True, constants.green)
    obj.screen.blit(
        text1, (constants.WINDOW_SIZE[0] / 2 - 210, constants.WINDOW_SIZE[1] / 2 - 50)
    )
    obj.screen.blit(
        text2, (constants.WINDOW_SIZE[0] / 2 - 250, constants.WINDOW_SIZE[1] / 2 + 10)
    )
    obj.records.append(obj.score)
    obj.records.sort(reverse=True)
    obj.update_records()
    records.clear()
    records.add.label(obj.records_str, max_char=-1, font_size=50)
    pygame.display.flip()
    time.sleep(2)
    menu.mainloop(obj.screen)


def spawn_wave(cur_time: int):
    """Generates enemies every tick"""
    if cur_time % 60 == 0 and cur_time < 5000:
        if cur_time < 1000:
            enemy = classes.Enemy(
                assist_func.get_x(constants.enemy_start),
                assist_func.get_y(constants.enemy_start),
                1,
                constants.white,
                15,
                500,
                5,
            )
            obj.enemies.append(enemy)
        elif cur_time < 3000:
            enemy = classes.Enemy(
                assist_func.get_x(constants.enemy_start),
                assist_func.get_y(constants.enemy_start),
                2,
                constants.marine,
                15,
                2000,
                10,
            )
            obj.enemies.append(enemy)
        elif cur_time < 5000:
            enemy = classes.Enemy(
                assist_func.get_x(constants.enemy_start),
                assist_func.get_y(constants.enemy_start),
                5,
                constants.purple,
                15,
                2000,
                20,
            )
            obj.enemies.append(enemy)
    boost = random.randint(-4, 5)
    if cur_time % max(20 - boost, 10) == 0 and cur_time > 5000:
        enemy = classes.Enemy(
            assist_func.get_x(constants.enemy_start),
            assist_func.get_y(constants.enemy_start),
            5 + boost // 2,
            ((boost * 231) % 255, (boost * 103) % 255, (boost * 83) % 255),
            15,
            2000 + (boost * 100),
            20 + boost,
        )
        obj.enemies.append(enemy)


def redraw_screen(selected_cell):
    """Redraw grid every tick"""
    for row in range(constants.NUM_ROWS):
        for col in range(constants.NUM_COLS):
            if selected_cell == (row, col):
                pygame.draw.rect(
                    obj.screen, constants.yellow, constants.grid[row][col], 1
                )
            else:
                if constants.field[row][col] == 0:
                    pygame.draw.rect(
                        obj.screen, constants.marine, constants.grid[row][col], 1
                    )
                else:
                    pygame.draw.rect(
                        obj.screen, constants.red, constants.grid[row][col], 1
                    )


def press_key(selected_cell):
    """Place tower or finish the game"""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        finish_game()
    if selected_cell is not None:
        if keys[pygame.K_1]:
            """Default tower.

            Cheap and useful tower attacking at close range.

            Damage: 🌟
          Distance: 🌟
             Speed: 🌟🌟🌟🌟🌟   
             Price: 🌟🌟🌟🌟   
            """

            tower = classes.Tower(0, 0, constants.red, 20, 100, 3, 10, 0, "None")
            tower.place_tower(selected_cell)
        if keys[pygame.K_2]:
            """Sniper tower.

            Long range tower with good damage.

              Damage: 🌟🌟🌟🌟
            Distance: 🌟🌟🌟🌟🌟
               Speed: 🌟🌟   
               Price: 🌟🌟🌟   
               """

            tower = classes.Tower(0, 0, constants.yellow, 20, 1000, 500, 20, 200, "7.62")
            tower.place_tower(selected_cell)
        if keys[pygame.K_3]:
            """Freezer.

            Close range tower that slows down opponents.

              Damage: 🌟🌟
            Distance: 🌟
               Speed: 🌟🌟🌟   
               Price: 🌟🌟  
                Cold: 🥶🥶🥶🥶🥶
               """

            tower = classes.Tower(
                0, 0, constants.blue, 20, 100, 100, 30, 100, "Slow"
            )
            tower.place_tower(selected_cell)
        if keys[pygame.K_4]:
            """Mortar.

            Formidable weapons that blow up enemies.

              Damage: 🌟🌟🌟🌟
            Distance: 🌟🌟🌟
               Speed: 🌟🌟   
               Price: 🌟 
                 Hot: 🥵🥵🥵🥵🥵
               """

            tower = classes.Tower(
                0, 0, constants.brown, 20, 500, 500, 50, 200, "Explode"
            )
            tower.place_tower(selected_cell)


records = pygame_menu.Menu("Records", 1250, 800, theme=pygame_menu.themes.THEME_ORANGE)
records.add.label(obj.records_str, max_char=-1, font_size=40)
records.clear()


def main():
    """Start infinity cycle"""
    obj.clear()
    selected_cell = None
    running = True
    current_time = 0
    while running:
        current_time += 1
        spawn_wave(current_time)
        obj.clock.tick(constants.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for row in range(constants.NUM_ROWS):
                    for col in range(constants.NUM_COLS):
                        if constants.grid[row][col].collidepoint(mouse_pos):
                            selected_cell = (row, col)
                            pygame.draw.rect(
                                obj.screen,
                                constants.yellow,
                                constants.grid[row][col],
                                1,
                            )
                        else:
                            if constants.field[row][col] == 0:
                                pygame.draw.rect(
                                    obj.screen,
                                    constants.marine,
                                    constants.grid[row][col],
                                    1,
                                )
                            else:
                                pygame.draw.rect(
                                    obj.screen,
                                    constants.red,
                                    constants.grid[row][col],
                                    1,
                                )
        redraw_screen(selected_cell)
        for tower in obj.towers:
            tower.draw()
            tower.try_to_attack(current_time)
        for bullet in obj.bullets:
            bullet.move()
            bullet.draw()
        for enemy in obj.enemies:
            enemy.draw()
            if enemy.end:
                finish_game()
        press_key(selected_cell)
        font1 = pygame.font.Font(None, 36)
        text1 = font1.render("balance: " + str(obj.balance), True, constants.green)
        obj.screen.blit(text1, (10, 50))
        pygame.display.flip()
        obj.screen.fill((0, 0, 0))

    pygame.quit()


menu = pygame_menu.Menu(
    "Welcome to tower defence game", 1250, 800, theme=pygame_menu.themes.THEME_BLUE
)

menu.add.button("Play", main)
menu.add.button("Records", records)
menu.add.button("Quit", pygame_menu.events.EXIT)

menu.mainloop(obj.screen)
