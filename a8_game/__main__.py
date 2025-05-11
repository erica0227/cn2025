import pygame
import random as r

def main() -> None:

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    player = pygame.Rect((300, 250, 40, 40))

    CELL_SIZE = 40
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    grid = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    GRID_WIDTH = len(grid[0])
    GRID_HEIGHT = len(grid)

    run = True
    while run:

        screen.fill((0, 0, 0))

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE))
                elif grid[y][x] == 0:
                    pygame.draw.circle(screen, YELLOW,
                                       (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2 + 50), 3)

        pygame.draw.rect(screen, (255, 0, 0), player)

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            player.move_ip(-1, 0)
        elif key[pygame.K_RIGHT]:
            player.move_ip(1, 0)
        elif key[pygame.K_UP]:
            player.move_ip(0, -1)
        elif key[pygame.K_DOWN]:
            player.move_ip(0, 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
