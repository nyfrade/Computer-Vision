import pygame, sys, random
import cv2
import numpy as np
from game import Game
from laser import Laser
from OpenCv import cap_main, open_cv_loop, cap_release

pygame.init()

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700
OFFSET = 50

GREY = (29, 29, 27)
YELLOW = (243, 216, 63)

font = pygame.font.Font("Font/monogram.ttf", 40)
level_surface = font.render("LEVEL 01", False, YELLOW)
game_over_surface = font.render("GAME OVER", False, YELLOW)
score_text_surface = font.render("SCORE", False, YELLOW)
highscore_text_surface = font.render("HIGH-SCORE", False, YELLOW)

screen = pygame.display.set_mode((SCREEN_WIDTH + OFFSET, SCREEN_HEIGHT + 2*OFFSET))
pygame.display.set_caption("Python Space Invaders")

clock = pygame.time.Clock()

game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, OFFSET)

SHOOT_LASER = pygame.USEREVENT
pygame.time.set_timer(SHOOT_LASER, 300)

MYSTERYSHIP = pygame.USEREVENT + 1
pygame.time.set_timer(MYSTERYSHIP, random.randint(4000,8000))


# ----- OpenCV -----
cap = cap_main()

#-----OpenCv----
while True:
#-----OpenCv----
    #Checking for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap_release(cap)
            pygame.quit()
            sys.exit()
        if event.type == SHOOT_LASER and game.run:
            game.alien_shoot_laser()

        if event.type == MYSTERYSHIP and game.run:
            game.create_mystery_ship()
            pygame.time.set_timer(MYSTERYSHIP, random.randint(4000,8000))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and game.run == False:
            game.reset()

# ----- Frame da câmara -----
    frame, isMovingLeft, isMovingRight, isShooting = open_cv_loop(cap)
    if frame is None:
        continue

    #Updating
    if game.run:
        #adicionei
        #referência direita à nave para conseguir mexer nas propriedades dela
        spaceship = game.spaceship_group.sprite

        # ----- movimento controlado pela câmara -----
        #Quando o objeto está à esquerda vai substrair spaceship.speed da coordenada X
        if isMovingLeft:
            spaceship.rect.x -= spaceship.speed
        #Quando o objeto está à direita vai somar spaceship.speed da coordenada X
        #o elif vai garantir que a nave não se mexe para os dois lados ao mesmo tempo
        elif isMovingRight:
            spaceship.rect.x += spaceship.speed

        # ----- disparo -----
        #dispara o laser se o objeto estiver na zona superior da câmara e se o laser estiver pronto
        if isShooting and spaceship.laser_ready:
            spaceship.laser_ready = False
            laser = Laser(spaceship.rect.center, 5, spaceship.screen_height)
            spaceship.lasers_group.add(laser)
            spaceship.laser_time = pygame.time.get_ticks()
            spaceship.laser_sound.play()

        spaceship.constrain_movement()
        spaceship.lasers_group.update()
        #acaba aqui

        game.spaceship_group.update()
        game.move_aliens()
        game.alien_lasers_group.update()
        game.mystery_ship_group.update()
        game.check_for_collisions()

    #Drawing
    screen.fill(GREY)

    #UI
    pygame.draw.rect(screen, YELLOW, (10, 10, 780, 780), 2, 0, 60, 60, 60, 60)
    pygame.draw.line(screen, YELLOW, (25, 730), (775, 730), 3)

    if game.run:
        screen.blit(level_surface, (570, 740, 50, 50))
    else:
        screen.blit(game_over_surface, (570, 740, 50, 50))

    x = 50
    for life in range(game.lives):
        screen.blit(game.spaceship_group.sprite.image, (x, 745))
        x += 50

    screen.blit(score_text_surface, (50, 15, 50, 50))
    formatted_score = str(game.score).zfill(5)
    score_surface = font.render(formatted_score, False, YELLOW)
    screen.blit(score_surface, (50, 40, 50, 50))
    screen.blit(highscore_text_surface, (550, 15, 50, 50))
    formatted_highscore = str(game.highscore).zfill(5)
    highscore_surface = font.render(formatted_highscore, False, YELLOW)
    screen.blit(highscore_surface, (625, 40, 50, 50))

    game.spaceship_group.draw(screen)
    game.spaceship_group.sprite.lasers_group.draw(screen)
    for obstacle in game.obstacles:
        obstacle.blocks_group.draw(screen)
    game.aliens_group.draw(screen)
    game.alien_lasers_group.draw(screen)
    game.mystery_ship_group.draw(screen)

    pygame.display.update()
    clock.tick(60)
