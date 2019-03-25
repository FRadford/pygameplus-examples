import itertools
import math
import random

import pygame

import pygamesystems.objects as objects


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class ScoreCounter(pygame.font.Font):
    def __init__(self, size):
        super(ScoreCounter, self).__init__(None, size)
        self.score = 0
        self.secondary = pygame.font.Font(None, size * 2)
        self.level = pygame.font.Font(None, size)

    def update_score(self, increment, multiplier):
        self.score += increment * multiplier

        colour = pygame.Color("white")
        colour.hsva = (multiplier % 360, 100, 100, 100)

        return self.render(f"{self.score:011}", True, (255, 255, 255)), \
               self.secondary.render("x" + str(multiplier), True, colour), \
               self.level.render(f"Level {multiplier // 10}", True, colour), \
               multiplier


class HeartContainer(pygame.sprite.AbstractGroup):
    def __init__(self, player):
        super(HeartContainer, self).__init__()
        self.player = player

        self.add(*[Heart(x) for x in range(player.health)])

    def update(self, *args):
        while len(self.spritedict) != self.player.health:
            self.remove(self.sprites()[-1])


class Heart(objects.StaticSprite):
    def __init__(self, index):
        super(Heart, self).__init__(36 * index + 14, 14, {"base": "assets/sprites/heart.png"}, scale=2.0)


class Ship(objects.Player):
    def __init__(self, x, y, sprites):
        super(Ship, self).__init__(x, y, sprites, scale=2.0)
        self.attack_type = self.shoot
        self.attack_strength = 1
        self.base_cool_down = 30
        self.cool_down = self.base_cool_down

        self.max_health = 3
        self.health = self.max_health
        self.base_hurt_time = 50

        self.speed = 3
        self.shoot_speed = 8

        self.hurt_sound = pygame.mixer.Sound("assets/sfx/hurt.wav")
        self.death_sound = pygame.mixer.Sound("assets/sfx/death.wav")

    def attack(self):
        if self.cool_down <= 0:
            self.cool_down = self.base_cool_down
            return self.attack_type(self.angle)
        else:
            return itertools.repeat(0, 0)

    def update(self, colliders, surface, cam):
        objects.Player.update(self, colliders, surface, cam)
        self.projectiles.update(colliders)
        if self.cool_down >= 0:
            self.cool_down -= 1

    def shoot(self, angle):
        self.projectiles.add(
            Bullet(self.rect.centerx - 4, self.rect.centery - self.rect.size[1], angle, self.shoot_speed,
                   self.attack_strength))
        return self.shake_screen()

    def damage(self, value, *groups):
        self.hurt_sound.play()
        super(Ship, self).damage(value, *groups)

    def kill(self):
        self.death_sound.play()
        self.health = 0
        super(Ship, self).kill()


class Bullet(objects.DynamicSprite):
    def __init__(self, x, y, angle, speed, strength):
        super(Bullet, self).__init__(x, y, {"base": "assets/sprites/laser.png"}, scale=2.0)
        self.speed = speed
        self.strength = strength
        self.dx, self.dy = self.parse_directions(math.radians(-angle - 90), speed)

        pygame.mixer.Sound("assets/sfx/laser.wav").play()

    @staticmethod
    def parse_directions(angle, speed):
        return [speed * math.cos(angle), speed * math.sin(angle)]

    def update(self, colliders):
        self.move(self.dx, self.dy, colliders)

    def move_single_axis(self, dx, dy, colliders):
        self.rect.x += dx
        self.rect.y += dy

        for other in colliders:
            if len(self.groups()) > 0:
                if self is other:
                    pass
                elif self.check_collision(other):
                    if not isinstance(other, Ship):
                        self.kill()
                        if hasattr(other, "damage"):
                            other.damage(self.strength, colliders, shot=True)
                            other.explosion.play()


class AsteroidController(pygame.sprite.AbstractGroup):
    def __init__(self, asteroid_factor, surface, player, *groups, run_particles=True):
        super(AsteroidController, self).__init__()
        self.asteroid_factor = asteroid_factor
        self.run_particles = run_particles
        self.cool_down = 10
        self.multiplier = 1
        self.player = player
        self.player_max_health = self.player.health
        self.removed_sprites = []

        self.update(surface, *groups)

    def update(self, surface, *groups):
        width, height = surface.get_size()
        if self.cool_down <= 0:
            self.cool_down = 10

            asteroids = [Asteroid(random.randint(0, width), -(height / 2), random.random() * self.asteroid_factor,
                                  random.random() * random.choice((-1, 1)), run_particles=self.run_particles)
                         for _ in range(self.asteroid_factor)]
            self.add(*asteroids)

            for group in groups:
                group.add(*asteroids)
        else:
            self.cool_down -= 1

        score = 0
        for sprite in self.removed_sprites:
            if sprite.shot:
                score += sprite.size
                self.multiplier += 1
            self.removed_sprites.remove(sprite)

        if self.player_max_health > self.player.health:
            self.player_max_health = self.player.health
            self.multiplier = 1

        return score, self.multiplier

    def remove_internal(self, sprite):
        self.removed_sprites.append(sprite)
        super(AsteroidController, self).remove_internal(sprite)


class Asteroid(objects.LivingSprite):
    def __init__(self, x, y, speed, rot_speed, run_particles=True):
        self.explosion = pygame.mixer.Sound("assets/sfx/explosion.wav")

        self.possible_sprites = ["assets/sprites/asteroid1.png", "assets/sprites/asteroid2.png",
                                 "assets/sprites/asteroid3.png"]
        self.size = random.randint(1, len(self.possible_sprites))

        super(Asteroid, self).__init__(x, y, {"base": self.possible_sprites[self.size - 1]}, scale=2.0,
                                       run_particles=run_particles)

        self.particle_rgb = (130, 120, 80)
        self.particle_duration = 100
        self.particle_variation = 20

        self.blood = self.size * 15

        self.health = self.size
        self.speed = speed
        self.rot_speed = rot_speed
        self.strength = 1
        self.shot = False

    def update(self, colliders, surface, cam):
        if colliders.has(self):
            self.rotate(self.angle + self.rot_speed)
            self.move(0, self.speed, colliders)

        super(Asteroid, self).update(colliders, surface, cam)

    def move_single_axis(self, dx, dy, colliders):
        self.rect.x += dx
        self.rect.y += dy

        for other in colliders:

            if self is other:
                pass
            elif self.check_collision(other):
                self.kill()
                if hasattr(other, "damage"):
                    other.damage(self.strength, colliders)

    def off_surface(self, surface):
        """
        Does the same as the overriden method except that this method ignores the top side of the surface as
        asteroids are created above the top of the window.
        """
        if self.rect.right < 0 or \
                        self.rect.left > surface.get_rect().width or \
                        self.rect.top > surface.get_rect().height:
            return True
        return False

    def damage(self, value, *groups, **kwargs):
        if "shot" in kwargs.keys():
            self.shot = kwargs["shot"]
        super(Asteroid, self).damage(value, *groups)

    # def kill(self):
    #     self.explosion.play()
    #     super(Asteroid, self).kill()
