from sys import exit
import random as r
from pygame.locals import *
import pygame

def main() -> None:

    import time

    # SET CHARECTERS POSITIONS START

    player_x = 400
    player_y = 200

    ghost_1_x = -50
    ghost_1_y = r.randint(1, 400)

    ghost_2_x = r.randint(1, 800)
    ghost_2_y = -50

    ghost_3_x = 850
    ghost_3_y = r.randint(1, 400)

    ghost_4_x = r.randint(1, 800)
    ghost_4_y = 450

    point_x = r.randint(50, 750)
    point_y = r.randint(10, 390)

    # SET CHARECTERS POSITIONS END

    # EXTRA VARIABLES START
    points = .2

    speed = points

    running = True

    size = 20

    # EXTRA VARIABLES END

    # START THE BEGINING OF THE MAIN PYTHON CODE START

    pygame.init()

    # START THE BEGINING OF THE MAIN PYTHON CODE END

    # SET SCREEN SIZE START

    screen = pygame.display.set_mode((800, 400))

    # SET SCREEN SIZE END

    # SET TITLE START

    pygame.display.set_caption('my pac_man')

    # SET TITLE END

    # LOADING THE IMAGES OF THE CHARACTARS START

    player = pygame.image.load('images/pacman.png').convert()

    ghost_1 = pygame.image.load('images/ghost1.png').convert()
    ghost_2 = pygame.image.load('images/ghost2.png').convert()
    ghost_3 = pygame.image.load('images/ghost3.png').convert()
    ghost_4 = pygame.image.load('images/ghost4.png').convert()

    point = pygame.image.load('images/Star.png').convert()

    # LOADING THE IMAGES OF THE CHARECTERS END

    # DEFINING DIRECTIONS START

    up = 1
    down = 2
    left = 3
    right = 4

    # DEFINING DIRECTIONS END

    # DEFINING STARTING DIRECTION VARIABLE START

    direction = up

    # DEFINING STARTING DIRECTION VARIABLE END

    # MAIN GAME LOOP START

    while running:

        # TRANSFORMING THE IMAGES SO THAT THEY FIT ON THE SCREEN START

        player = pygame.transform.scale(player, (size, size))

        ghost_1 = pygame.transform.scale(ghost_1, (size, size))
        ghost_2 = pygame.transform.scale(ghost_2, (size, size))
        ghost_3 = pygame.transform.scale(ghost_1, (size, size))
        ghost_4 = pygame.transform.scale(ghost_2, (size, size))

        point = pygame.transform.scale(point, (size, size))

        # TRANSFORMING THE IMAGES SO THAT THEY FIT ON THE SCREEN END
        # EXTRA VARIABLES NEEDED IN GAME LOOP START

        speed = points

        # EXTRA VARIABLES NEEDED IN GAME LOOP END

        # LOOK FOR EVENTS IN PYGAME START

        for event in pygame.event.get():

            # CHECK IF THE MOUSE HITS THE X START

            if event.type == pygame.QUIT:
                # IF THE MOUSE HITS THE X THEN EXIT START
                run =False
                pygame.display.update()
                pygame.quit()

            # IF THE MOUSE HITS THE X THEN EXIT END

            # CHECK IF THE MOUSE HITS THE X END

            # SENCE A KEY IS PRESSED START

            if event.type == pygame.KEYDOWN:

                # SENCE IF AN ARROW KEY IS PRESSED

                if event.key == pygame.K_LEFT:
                    direction = left

                if event.key == pygame.K_RIGHT:
                    direction = right

                if event.key == pygame.K_UP:
                    direction = up

                if event.key == pygame.K_DOWN:
                    direction = down

        # SENCE IF AN ARROW KEY IS PRESSED END

        # SENCE IF A KEY IS PERSSED END

        # LOOK FOR EVENTS IN PYGAME END

        # PLAYER MOVEMENT START

        if direction == up:
            player_y -= speed

        if direction == down:
            player_y += speed

        if direction == left:
            player_x -= speed

        if direction == right:
            player_x += speed

        # PLAYER MOVEMENT END

        # PLAYER EDGE SENCING START
        """"
        if player_x >= 800:
            running = False

        if player_x <= 0:
            running = False

        if player_y >= 400:
            running = False

        if player_y <= 0:
            running = False
        """
        # PLAYER EDGE SENCING END

        # GHOST 1 MOVEMENT START

        if ghost_1_x <= player_x:
            ghost_1_x += speed / 2

        if ghost_1_x >= player_x:
            ghost_1_x -= speed / 2

        if ghost_1_y <= player_y:
            ghost_1_y += speed / 2

        if ghost_1_y >= player_y:
            ghost_1_y -= speed / 2

        # GHOST 1 MOVEMSNT END

        # GHOST 2 MOVEMENT START

        if ghost_2_x <= player_x:
            ghost_2_x += speed / 2

        if ghost_2_x >= player_x:
            ghost_2_x -= speed / 2

        if ghost_2_y <= player_y:
            ghost_2_y += speed / 2

        if ghost_2_y >= player_y:
            ghost_2_y -= speed / 2

        # GHOST 2 MOVEMSNT END

        # GHOST 3 MOVEMENT START

        if ghost_3_x <= player_x:
            ghost_3_x += speed / 2

        if ghost_3_x >= player_x:
            ghost_3_x -= speed / 2

        if ghost_3_y <= player_y:
            ghost_3_y += speed / 2

        if ghost_3_y >= player_y:
            ghost_3_y -= speed / 2

        # GHOST 3 MOVEMSNT END

        # GHOST 4 MOVEMENT START

        if ghost_4_x <= player_x:
            ghost_4_x += speed / 2

        if ghost_4_x >= player_x:
            ghost_4_x -= speed / 2

        if ghost_4_y <= player_y:
            ghost_4_y += speed / 2

        if ghost_4_y >= player_y:
            ghost_4_y -= speed / 2

        # GHOST 4 MOVEMSNT END

        # BACKGROUND COLOR START

        screen.fill((0, 0, 0))

        # BACKGROUND COLOR END

        # collision sencing format

        # if rect_1 x < rect_2 x + rect_1 width and rect_1 x + rect_2 width > rect_2 x and rect_1 y < rect_2 y + rect_1 height and rect_1 height + rect_1 y > rect_2 y

        # CHECKING FOR COLLISION START
        """
        if player_x < ghost_1_x + size and player_x + size > ghost_1_x and player_y < ghost_1_y + size and size + player_y > ghost_1_y:
            running = False

        if player_x < ghost_2_x + size and player_x + size > ghost_2_x and player_y < ghost_2_y + size and size + player_y > ghost_2_y:
            running = False

        if player_x < ghost_3_x + size and player_x + size > ghost_3_x and player_y < ghost_3_y + size and size + player_y > ghost_3_y:
            running = False

        if player_x < ghost_4_x + size and player_x + size > ghost_4_x and player_y < ghost_4_y + size and size + player_y > ghost_4_y:
            running = False
"""
        if player_x < point_x + size and player_x + size > point_x and player_y < point_y + size and size + player_y > point_y:
            points += 0.1
            size += 5
            point_x = r.randint(50, 750)
            point_y = r.randint(10, 390)

        # CHECKING FOR COLLISION END

        # PLACE CHARACTERS START

        screen.blit(player, (player_x, player_y))

        screen.blit(ghost_1, (ghost_1_x, ghost_1_y))
        screen.blit(ghost_2, (ghost_2_x, ghost_2_y))
        screen.blit(ghost_3, (ghost_3_x, ghost_3_y))
        screen.blit(ghost_4, (ghost_4_x, ghost_4_y))

        screen.blit(point, (point_x, point_y))

        # PLACE CHARECTERS END
        # SHOW SCORE START

        font = pygame.font.Font(None, size)

        if size == 20:
            text = font.render(('20'), 1, (255, 0, 0))

        if size == 25:
            text = font.render(('25'), 1, (255, 0, 255))

        if size == 30:
            text = font.render(('30'), 1, (255, 255, 0))

        if size == 35:
            text = font.render(('35'), 1, (0, 255, 0))

        if size == 40:
            text = font.render(('40'), 1, (0, 0, 255))

        if size == 45:
            text = font.render(('45'), 1, (255, 0, 255))

        if size == 50:
            text = font.render(('50'), 1, (255, 255, 255))

        if size == 55:
            text = font.render(('55'), 1, (255, 255, 255))

        if size == 60:
            text = font.render(('YOU WIN'), 1, (255, 255, 255))

        screen.blit(text, (200, 200))

        # SHOW SCORE END
        # UPDATE CHANGES IN CODE, VARIABLES, PICTURES, ECT... IN PYGAME START

        pygame.display.update()

    # UPDATE CHANGES IN CODE, VARIABLES, PICTURES, ECT... IN PYGAME END

    # MAIN GAME LOOP END
    pass


if __name__ == "__main__":
    main()

"""
pygame.display.set_caption('Reversed Pacman')
image = pygame.image.load('images/Board.png')
image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
"""