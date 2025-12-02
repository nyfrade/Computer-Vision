import pygame
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from entities.Mario import Mario


import codigo_opencv


windowSize = 640, 480

#----- variável para a câmara
cap = None

def main():




    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    max_frame_rate = 60
    dashboard = Dashboard("./img/font.png", 8, screen)
    sound = Sound()
    level = Level(screen, sound, dashboard)
    menu = Menu(screen, dashboard, level, sound)

    # ---------- CHAMADA OPENCV
    global cap
    cap= codigo_opencv.cap_main()


    while not menu.start:
        menu.update()

    mario = Mario(0, 0, level, screen, dashboard, sound)
    clock = pygame.time.Clock()

    while not mario.restart:
        pygame.display.set_caption("Super Mario running with {:d} FPS".format(int(clock.get_fps())))
        if mario.pause:
            mario.pauseObj.update()
        else:
            level.drawLevel(mario.camera)
            dashboard.update()
            mario.update()

            # ---------- CHAMADA OPENCV
            codigo_opencv.open_cv_loop(cap)

            print(mario.getPos())

        pygame.display.update()
        clock.tick(max_frame_rate)


    return 'restart'

if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = main()

        #---------- CHAMADA OPENCV
        codigo_opencv.cap_release(cap)