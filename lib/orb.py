import OpenGL, math
from OpenGL.GL import *
import run

AIR_FRICTION = 0.90
BOUNCE = 0.95

DEBUG = run.DEBUG

class Orb:
    activity_radius = 400

    def __init__(self, x, y, r):
        self.x, self.y = x, y
        self.r = r
        self.hash = None
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.dead = False

    vars = ["x", "y", "r", "dx", "dy", "angle"]

    @classmethod
    def from_string(cls, s):
        o = cls(0, 0, 0)
        kv = s.split()
        for i in range(0, len(kv), 2):
            k = kv[i]
            v = kv[i + 1]
            if k[-1] == "!":
                b = False
                if v == "True": b = True
                setattr(o, k[:-1], b)
            else:
                setattr(o, k, float(v))
        return o

    def as_string(self):
        r = ""
        for k in self.vars:
            rk = k
            if rk[-1] == "!": rk = rk[:-1]
            r += " " + k + " " + str(getattr(self, rk))
        return r

    def hash_x(self):
        a = self.x - self.r
        b = self.x + self.r
        gw = self.hash.cellw
        return range(int(a / gw), int(b / gw) + 1)

    def hash_y(self):
        a = self.y - self.r
        b = self.y + self.r
        gh = self.hash.cellh
        return range(int(a / gh), int(b / gh) + 1)

    def spawn(self, hash):
        self.hash = hash
        self.appear()

    def appear(self):
        for x in self.hash_x():
            for y in self.hash_y():
                self.hash.add(x, y, self)

    def disappear(self):
        for x in self.hash_x():
            for y in self.hash_y():
                self.hash.remove(x, y, self)

    def overlap(self, x, y, r):
        dx = self.x - x
        dy = self.y - y
        dr = self.r + r
        return dx * dx + dy * dy < dr * dr

    def normal(self, x, y):
        dx = x - self.x
        dy = y - self.y
        d = (dx ** 2 + dy ** 2) ** 0.5
        if d > 0:
            return dx / d, dy / d
        else:
            return 0.0, 1.0

    def colliders(self):
        cs = set()
        for x in self.hash_x():
            for y in self.hash_y():
                for c in self.hash.get(x, y):
                    if c.overlap(self.x, self.y, self.r):
                        cs.add(c)
        return cs

    def can_be_pushed(self, bywho): return False
    def is_active(self): return False
    def interact(self): pass
    def layer(self): return 0
    def touch(self, bywho, speed): pass
    def spiked(self, howmuch = 1): pass
    def want_touch(self, who): return True

    def push(self, dx, dy):
        oldx = self.x
        oldy = self.y
        self.disappear()
        self.x += dx
        self.y += dy
        ok = True
        for c in self.colliders():
            if c.can_be_pushed(self):
                if c.push(dx, dy): continue
            self.x = oldx
            self.y = oldy
            ok = False
            break

        self.appear()
        return ok

    def collision_response(self, touched):
        n = len(touched)
        speed = (self.dx ** 2 + self.dy ** 2) ** 0.5
        speed /= n
        self.dx = 0
        self.dy = 0
        for t in touched:
            dx, dy = t.normal(self.x, self.y)
            self.dx += dx * speed * BOUNCE
            self.dy += dy * speed * BOUNCE
            t.touch(self, speed)

    def move(self):
        oldx = self.x
        oldy = self.y
        dx = self.dx
        dy = self.dy
        self.disappear()
        touched = set()
        while 1:
            self.x = oldx + dx
            self.y = oldy + dy
            cs = self.colliders()
            if not cs: break
            for c in cs:
                if c.want_touch(self):
                    touched.add(c)
            if not touched: break
            dx /= 2
            dy /= 2
            if dx * dx + dy * dy < 0.5 * 0.5:
                self.x = oldx
                self.y = oldy
                break
        self.appear()

        if touched:
            self.collision_response(touched)

    def get_colliders(self, dx, dy):
        oldx = self.x
        oldy = self.y
        self.disappear()
        self.x += dx
        self.y += dy
        cs = self.colliders()
        self.x = oldx
        self.y = oldy
        self.appear()
        return cs

    def _shift(self, dx, dy):
        self.disappear()
        self.x += dx
        self.y += dy
        self.appear()

    def teleport_to(self, x, y):
        dx = x - self.x
        dy = y - self.y
        self._shift(dx, dy)

    def set_radius(self, r):
        self.disappear()
        self.r = r
        self.appear()

    def tick(self):
        self.move()
        self.dx *= AIR_FRICTION
        self.dy *= AIR_FRICTION

    def draw(self):
        pass

    def draw_debug(self):
        glColor4f(0, 1, 0, 1)
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_LINE_LOOP)
        n = 32
        a = 0
        ai = math.pi * 2 / n
        cx = self.x
        cy = self.y
        while a < math.pi * 2:
            c, s = math.cos(a), math.sin(a)
            glVertex2f(cx + self.r * c, cy + self.r * s)
            a += ai
        glEnd()

        glEnable(GL_TEXTURE_2D)

    def sameway(self, dx, dy):
        """
        If dx/dy is a unit length vector - how much are we going into the same
        direction? If we go fully to the same direction, the full
        """
        return self.dx * dx + self.dy * dy

    def orientation(self):
        game = run.run.game

        dx = self.x - run.run.game.x
        dy = self.y - run.run.game.y
        d = (dx ** 2 + dy ** 2) ** 0.5
        dx /= d
        dy /= d

        rx = dy
        ry = -dx

        return rx, ry, dx, dy

    def align(self):
        rx, ry, dx, dy = self.orientation()
        self.angle = 180 * math.atan2(-dx, dy) / math.pi

class InverseOrb(Orb):
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)

    def touch(self, who, speed):
        if speed > 0.5:
            v = speed / 5.0
            if v > 1.0: v = 1.0
            run.run.wood2.play(v, who)

    def appear(self):
        for x in range(self.hash.w):
            for y in range(self.hash.h):
                for i in [0, 1]:
                    for j in [0, 1]:
                        px = self.hash.cellw * (i + x)
                        py = self.hash.cellh * (j + y)
                        dx = px - self.x
                        dy = py - self.y
                        if dx * dx + dy * dy  > self.r * self.r:
                            self.hash.add(x, y, self)

    def overlap(self, x, y, r):
        dx = self.x - x
        dy = self.y - y
        dr = self.r - r
        return dx * dx + dy * dy > dr * dr

    def normal(self, x, y):
        dx = self.x - x
        dy = self.y - y
        d = (dx ** 2 + dy ** 2) ** 0.5
        return dx / d, dy / d

    def tick(self):
        pass

    def draw(self):
        pass

    def draw_debug(self):
        glColor4f(1, 0, 0, 1)
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_LINE_LOOP)
        n = 128
        a = 0
        ai = math.pi * 2 / n
        cx = self.x
        cy = self.y
        while a < math.pi * 2:
            c, s = math.cos(a), math.sin(a)
            glVertex2f(cx + self.r * c, cy + self.r * s)
            a += ai
        glEnd()
        glEnable(GL_TEXTURE_2D)

class SpatialHash:
    def __init__(self, cellw, cellh, w, h):
        self.cellw, self.cellh = cellw, cellh
        self.w, self.h = w, h
        self.grid = []
        for i in range(self.w):
            row = []
            for j in range(self.h):
                row.append([])
            self.grid.append(row)

    def add(self, x, y, orb):
        self.grid[x][y].append(orb)

    def remove(self, x, y, orb):
        self.grid[x][y].remove(orb)

    def get(self, x, y):
        return self.grid[x][y]

    def get_in_circle(self, x, y, r):
        cx1 = int((x - r) / self.cellw)
        cy1 = int ((y - r) / self.cellh)
        cx2 = int((x + r) / self.cellw)
        cy2 = int ((y + r) / self.cellh)
        inside = set()
        for cx in range(cx1, cx2 + 1):
            for cy in range(cy1, cy2 + 1):
                for c in self.grid[cx][cy]:
                    inside.add(c)
        return inside