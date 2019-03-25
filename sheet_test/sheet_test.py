import sys

import pygame

import pygamesystems.helpers as helpers

pygame.init()
screen = pygame.display.set_mode((400, 300))
FPS = 120
frames = FPS / 6

strip = helpers.SpriteSheetAnimator("assets/gradient.png", (0, 0, 16, 16), 7, True, frames)

clock = pygame.time.Clock()
image = strip.next()
n = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                strip.iter()

    screen.blit(image, (200, 150))
    pygame.display.flip()
    image = strip.next()
    clock.tick(FPS)
