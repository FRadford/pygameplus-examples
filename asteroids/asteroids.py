import sys

import pygame

import pygamesystems.examples.asteroids.extend as extend
import pygamesystems.objects as objects

# Constants
WIDTH = 800
HEIGHT = 400
WINDOW_SIZE = (WIDTH, HEIGHT)

DRAW_BOUNDING_BOXES = False

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    colliders = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    player = extend.Ship(WIDTH / 2, HEIGHT - HEIGHT / 10, {"base": "assets/sprites/ship.png",
                                                           "hurt": "assets/sprites/ship-hurt.png"})
    player.add(colliders, all_sprites)

    asteroids = extend.AsteroidController(1, screen, player, colliders, all_sprites, run_particles=False)

    hearts = extend.HeartContainer(player)
    score_counter = extend.ScoreCounter(24)

    main_cam = objects.Camera(objects.simple_camera, (WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game_over_text = pygame.font.Font(None, 64)

    while True:
        clock.tick(60)
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move(-player.speed, 0, colliders)
        if keys[pygame.K_d]:
            player.move(player.speed, 0, colliders)
        if keys[pygame.K_SPACE]:
            player.attack()

        for sprite in all_sprites:
            if isinstance(sprite, objects.DynamicSprite) and sprite.off_surface(screen):
                sprite.kill()
            if isinstance(sprite, objects.LivingSprite):
                if sprite.health > 0:
                    if sprite is player:
                        for bullet in sprite.projectiles:
                            if bullet.off_surface(screen):
                                bullet.kill()
                            screen.blit(bullet.image, main_cam.apply(bullet))

                            if DRAW_BOUNDING_BOXES:
                                pygame.draw.rect(screen, (255, 0, 0), bullet.rect, 1)
                    screen.blit(sprite.image, main_cam.apply(sprite))
            if DRAW_BOUNDING_BOXES:
                pygame.draw.rect(screen, (255, 0, 0), sprite.rect, 1)

        for heart in hearts:
            screen.blit(heart.image, main_cam.apply(heart))

        if not player.alive():
            for sprite in all_sprites:
                sprite.kill()

            text = game_over_text.render("Game Over", True, (255, 255, 255))
            screen.blit(text, (WIDTH / 2 - text.get_rect().width / 2, HEIGHT / 2 - text.get_rect().height / 2))

        all_sprites.update(colliders, screen, main_cam)
        score, score_multiplier, level_up, score_multiplier_int = score_counter.update_score(
            *asteroids.update(screen, colliders, all_sprites))
        asteroids.asteroid_factor = score_multiplier_int // 10 if score_multiplier_int // 10 != 0 else 1
        screen.blit(score, (WIDTH / 2 - score.get_rect().width / 2, 14))
        screen.blit(score_multiplier, (WIDTH / 2 - score_multiplier.get_rect().width / 2, 28))
        screen.blit(level_up, (WIDTH / 2 - level_up.get_rect().width / 2, 56))
        hearts.update()
        pygame.display.flip()


if __name__ == "__main__":
    main()
