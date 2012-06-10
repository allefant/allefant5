from picture import Picture
from orb import Orb, SpatialHash, InverseOrb
import sprites
from sprites import Ball1, Allefant, Block1, RoundBlock1, Cogwheel, Spring
from sprites import Python, Rider, Spikes, Lever, Coin, Leprechaun, Laser, Wall
from sprites import Portal

from OpenGL.GL import *
import data, math
import run

class View:
    pass

class Game:
    def __init__(self, vw, vh):
        self.vw = vw
        self.vh = vh
        self.level = 0

        self.background1 = Picture("clock.jpg")

    def restart(game):
        game.spatialhash = SpatialHash(64, 64, 64, 64)
        game.orbs = []

        game.decohash = SpatialHash(64, 64, 64, 64)
        game.deco = []

        game.active = []
        game.lasers = {}

        game.dragged = None
        game.drag = (0, 0)
        game.selected = None
        game.new_size = 10

        game.twist = 0

        cx = 64 * 32
        cy = 64 * 32
        game.x = cx
        game.y = cy
        game.radius = 1000

        game.view = View()
        game.view.x = 0
        game.view.y = 0
        game.view.angle = 0

        game.coins = 0
        game.rider = None

    def script1(game):

        game.player = Allefant(game.x, game.y + game.radius - 50, 20)
        game.player.spawn(game.spatialhash)
        game.orbs.append(game.player)

        game.active.append(game.player)

        outside = InverseOrb(game.x, game.y, game.radius)
        outside.spawn(game.spatialhash)
        game.orbs.append(outside)

    def script2(game):
        # ai = 360 / n
        # ao = 180 - ai = 180 - 360 / n
        # h*h + s2*s2 = r*r
        # s = 2 * r * sin(ai / 2)
        # h = 2 * r * cos(ai / 2)
        # c = n * s
        game.place(game.x, game.y, 30, 0, RoundBlock1)
        outerr = game.radius - 80
        vdist = 220
        a = 0
        while 1:
            r = outerr - vdist * a / (2 * math.pi)
            if r < vdist: break
            x = game.x + math.sin(a) * r
            y = game.y + math.cos(a) * r
            b = game.place(x, y, 30, -a * 180 / math.pi + 90, RoundBlock1)
            a += 122 / r
            
    def script3(game):
        r = game.radius + 20
        a = 0
        while a < math.pi * 2:
            x = game.x + math.sin(a) * r
            y = game.y + math.cos(a) * r
            b = game.placedeco(x, y, 18, 180 * -a / math.pi, Block1)
            a += 118.7 / r

    def script4(game, x, y, dx, dy):
        prev = None
        r = game.new_size
        for i in range(40):
            orb = Orb(x, y, r)
            orb.spawn(game.spatialhash)
            game.orbs.append(orb)

            x += dx * game.new_size * 2
            y += dy * game.new_size * 2
            if prev:
                orb.append(prev)
            prev = orb

    def script5(game):
        r = game.radius + 20
        a = 0
        while a < math.pi * 2:
            x = game.x + math.sin(a) * r
            y = game.y + math.cos(a) * r
            b = game.placedeco(x, y, 18, 180 * -a / math.pi - 90, Wall)
            a += 118.7 / r

    def script6(game):
        r = 400

        game.player = Allefant(game.x, game.y + r - 21, 20)
        game.player.spawn(game.spatialhash)
        game.orbs.append(game.player)
        game.active.append(game.player)

        outside = InverseOrb(game.x, game.y, r)
        outside.spawn(game.spatialhash)
        game.orbs.append(outside)

        a = 0
        r += 20
        while a < math.pi * 2:
            x = game.x + math.sin(a) * r
            y = game.y + math.cos(a) * r
            b = game.placedeco(x, y, 18, 180 * -a / math.pi, Block1)
            a += 118.7 / r

    def script7(game):
        for orb in game.orbs[:]:
            if orb.__class__ == Orb:
                game.remove(orb)
            elif orb.__class__ == Wall:
                a = orb.angle * math.pi / 180.0
                x = orb.x
                y = orb.y
                ax = math.sin(a)
                ay = -math.cos(a)
                game.place(x + 42 * ax, y + 42 * ay, 19, a, Orb)
                game.place(x - 42 * ax, y - 42 * ay, 19, a, Orb)
                game.place(x + 21 * ax, y + 21 * ay, 19, a, Orb)
                game.place(x - 21 * ax, y - 21 * ay, 19, a, Orb)
            elif orb.__class__ == Block1:
                a = orb.angle * math.pi / 180.0
                x = orb.x
                y = orb.y
                ax = math.cos(a)
                ay = math.sin(a)
                game.place(x + 42 * ax, y + 42 * ay, 19, a, Orb)
                game.place(x - 42 * ax, y - 42 * ay, 19, a, Orb)
                game.place(x + 21 * ax, y + 21 * ay, 19, a, Orb)
                game.place(x - 21 * ax, y - 21 * ay, 19, a, Orb)

    def colliders(self, x, y, r):
        orb = Orb(x, y, r)
        orb.hash = self.spatialhash
        return [x for x in orb.colliders() if not x.__class__ == InverseOrb]

    def render(self):
        px = (self.player.x - self.x) * 0.25
        py = (self.player.y - self.y) * 0.25
        glPushMatrix()
        glScalef(1 + 0.01 * math.cos(self.twist * math.pi * 2 / 120.0),
            1 + 0.01 * math.sin(self.twist * math.pi * 2 / 120.0), 1)
        self.background1.draw_centered(self.view.x - px, self.view.y - py)
        glPopMatrix()

        drawn = 0
        diagonal = (self.vw ** 2 + self.vh ** 2) ** 0.5
        x, y = self.player.x, self.player.y
        pvs = self.decohash.get_in_circle(x, y, diagonal / 2)
        for orb in pvs:
            orb.draw()
            drawn += 1

        pvs = self.spatialhash.get_in_circle(x, y, diagonal / 2)
        for layer in [-1, 0, 1]:
            for orb in pvs:
                if orb.layer() == layer:
                    orb.draw()
                    drawn += 1

        if run.run.debugging:
            for layer in [-1, 0, 1]:
                for orb in pvs:
                    if orb.layer() == layer:
                        orb.draw_debug()

        glLoadIdentity()
        run.run.font.write(0, 443, "Level %d/6" % self.level, alpha = 0.8)

        run.run.font.write(320, 443, "Health %.f" % self.player.health,
            red = 1, green = 0, blue = 0, alpha = 0.8, center = True)

        run.run.font.write(640, 443, "Coins %d/%d" % (self.player.coins, self.coins),
            red = 1, green = 0.8, blue = 0.1, alpha = 0.8, right = True)

        if self.rider:
            if not self.rider.dead:
                run.run.font.write(320, 400, "Boss %.f" % self.rider.lifes,
                    red = 1, green = 0.5, blue = 0, alpha = 0.8, center = True)
                

    def tick(self):
        for orb in self.active:
            if not orb.dead:
                d = (orb.x - self.player.x) ** 2 + (orb.y - self.player.y) ** 2
                if d < orb.activity_radius * orb.activity_radius:
                    orb.tick()
        self.view.x = self.player.x - 320
        self.view.y = self.player.y - 240

        self.twist += 1

    def insert_action(game, x, y):
        orb = Orb(x, y, game.new_size)
        orb.spawn(game.spatialhash)
        game.orbs.append(orb)

    def place(game, x, y, r, a, what):
        orb = what(x, y, r)
        orb.angle = a
        orb.spawn(game.spatialhash)
        game.orbs.append(orb)
        return orb

    def insert_stuff(game, x, y, what):
        r = {"Wall" : 20, "Python" : 15, "Rider" : 50, "Spikes" : 20,
            "RoundBlock1" : 30, "Coin" : 10, "Leprechaun" : 15, "Lever" : 15,
            "Laser" : 40, "Portal" : 20}
        orb = game.place(x, y, r[what], 0, getattr(sprites, what))
        orb.align()
        if orb.is_active(): game.active.append(orb)
        return orb

    def remove(game, orb):
        if not orb: return
        orb.disappear()
        if orb in game.orbs: game.orbs.remove(orb)
        if orb in game.deco: game.deco.remove(orb)
        if orb in game.active: game.active.remove(orb)

    def placedeco(game, x, y, r, a, what):
        orb = what(x, y, r)
        orb.angle = a
        orb.spawn(game.decohash)
        game.deco.append(orb)
        return orb

    def insert_block1(game, x, y):
        a = -game.view.angle
        b = game.place(x, y, 19, a, Block1)

    def insert_rotated_block1(game, x, y):
        a = -game.view.angle + 90
        b = game.place(x, y, 19, a, Block1)

    def insert_wall(game, x, y):
        a = -game.view.angle
        b = game.place(x, y, 19, a, Wall)

    def place_moving_ball(game, x, y, a, dx, dy):
        orb = Ball1(x, y, 30)
        orb.angle = a
        orb.spawn(game.spatialhash)
        orb.movex = dx
        orb.movey = dy
        game.orbs.append(orb)
        game.active.append(orb)

    def place_moving_cogwheel(game, x, y, a):
        orb = Cogwheel(x, y, 25)
        orb.angle = a
        orb.spawn(game.spatialhash)
        orb.movex = 1
        game.orbs.append(orb)
        game.active.append(orb)

    def place_moving_spring(game, x, y):
        orb = Spring(x, y, 10)
        orb.align()
        orb.spawn(game.spatialhash)
        orb.movey = 1
        game.orbs.append(orb)
        game.active.append(orb)

    def save_level(self, num):
        fp = data.savepath("levels/%d" % num)
        f = open(fp, "w")
        for orb in self.deco:
            f.write("deco " + orb.__class__.__name__ + orb.as_string() + "\n")
        for orb in self.orbs:
            f.write("orbs " + orb.__class__.__name__ + orb.as_string() + "\n")
        f.close()

    def load_level(old, num):
        game = Game(old.vw, old.vh)
        game.restart()
        game.level = num
        fp = data.loadblock("levels/%d" % num)
        for line in fp:
            layername, classname, remainder = line.split(None, 2)

            if layername == "orbs":
                layer = game.orbs
                hash = game.spatialhash
            elif layername == "deco":
                layer = game.deco
                hash = game.decohash

            if classname == "Allefant":
                o = Allefant.from_string(remainder)
                o.spawn(hash)
                layer.append(o)
                game.player = o
            elif classname == "InverseOrb":
                o = InverseOrb.from_string(remainder)
                o.spawn(hash)
                layer.append(o)
            else:
                o = globals()[classname].from_string(remainder)
                o.spawn(hash)
                layer.append(o)
                if classname == "Laser":
                    game.lasers[o.id] = o
                if classname == "Coin": game.coins += 1
                if classname == "Rider": game.rider = o
            if o.is_active(): game.active.append(o)

        return game