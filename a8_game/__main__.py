import pygame
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Reversed Pacman')
image = pygame.image.load('images/Board.png')
image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
run = True
while run:
    screen.blit(image, (0, 0))
    key = pygame.key.get_pressed()
    """
        if key[pygame.K_a] == True
        player.move_ip(-1,0)
    """

    for event in pygame.event.get(): #event handler such as mouse clicks
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()

def main() -> None:
    # TODO: Your implementation here
    pass


if __name__ == "__main__":
    main()
