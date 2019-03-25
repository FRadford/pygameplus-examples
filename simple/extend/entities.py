import itertools
import math

import pygamesystems.objects as objects


class TopDownPlayer(objects.Player):
    def __init__(self, x, y, sprites):
        super(TopDownPlayer, self).__init__(x, y, sprites)
        self.attack_type = self.shoot
        self.attack_strength = 5
        self.cool_down = 10

        self.max_health = 100
        self.health = self.max_health
        self.base_hurt_time = 50

    def attack(self):
        if self.cool_down <= 0:
            self.cool_down = 10
            return self.attack_type(self.angle)
        else:
            return itertools.repeat(0, 0)

    def update(self, colliders, surface, cam):
        objects.Player.update(self, colliders, surface, cam)
        for bullet in self.projectiles:
            bullet.move(bullet.dx, bullet.dy, colliders)
        if self.cool_down >= 0:
            self.cool_down -= 1

    def shoot(self, angle):
        self.projectiles.add(Bullet(self.rect.centerx, self.rect.centery, angle, self.speed + 1, self.attack_strength))
        return self.shake_screen()


class Bullet(objects.DynamicSprite):
    def __init__(self, x, y, angle, speed, strength):
        super(Bullet, self).__init__(x, y, {"base": "assets/bullet.png"}, scale=0.5)
        self.speed = speed
        self.strength = strength
        self.dx, self.dy = self.parse_directions(math.radians(-angle - 90), speed)

    @staticmethod
    def parse_directions(angle, speed):
        return [speed * math.cos(angle), speed * math.sin(angle)]

    def move_single_axis(self, dx, dy, colliders):
        self.rect.x += dx
        self.rect.y += dy

        for other in colliders:
            if len(self.groups()) > 0:
                if self is other:
                    pass
                elif self.check_collision(other):
                    if not isinstance(other, TopDownPlayer):
                        self.kill()
                        if hasattr(other, "damage"):
                            other.damage(self.strength)


class Follower(objects.Enemy, objects.AIMixin):
    def __init__(self, x, y, sprites, target):
        super(Follower, self).__init__(x, y, sprites)
        self.speed = 0.75
        self.attack_strength = 1
        self.target = target
        self.health = 10

        self.move_towards = self.move_to_target_simple

    def update(self, colliders, surface, cam):
        objects.Enemy.update(self, colliders, surface, cam)
        if self.health > 0:
            self.move_towards(self.target, colliders)

    @objects.basic_movement
    def move_single_axis(self, dx, dy, colliders):
        for other in colliders:
            if self is other:
                pass
            elif self.check_collision(other):
                if other is self.target:
                    self.target.damage(self.attack_strength)


class Floor(objects.StaticSprite):
    def __init__(self, x, y):
        super(Floor, self).__init__(x, y, {"base": "assets/floor.png"})


class Wall(objects.StaticSprite):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y, {"base": "assets/wall.png"}, scale=2)
