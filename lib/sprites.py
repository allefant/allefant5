from picture import Picture
from orb import Orb
from OpenGL.GL import *
import run, random, math

class Base(Orb):
    pic = None

    def draw(self):
        glPushMatrix()
        glTranslate(self.x, self.y, 0)
        glRotate(self.angle, 0, 0, 1)
        glEnable(GL_TEXTURE_2D)
        self.pic.draw_centered(0, 0)
        glPopMatrix()

class WoodBase(Base):

    def touch(self, who, speed):
        if speed > 0.5:
            v = speed / 5.0
            if v > 1.0: v = 1.0
            if who.dy > 0: # note: this is not up!
                run.run.wood.play(v, who)
            else:
                run.run.wood2.play(v, who)

class Block1(WoodBase):
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        if self.pic == None: self.pic = Picture("items/block10001")

class RoundBlock1(WoodBase):
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        self.pic = Picture("items/ball10001")

class Wall(WoodBase):
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        self.pic = Picture("items/wall10001")

class Laser(WoodBase):
    vars = Base.vars + ["id"]

    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        self.pic = Picture("items/laser0001")
        self.id = 0

    def touch(self, who, speed):
        if isinstance(who, Allefant):
            dx = who.x - self.x
            dy = who.y - self.y
            d = (dx ** 2 + dy ** 2) ** 0.5
            dx /= d
            dy /= d

            who.dx += dx * 4
            who.dy += dy * 4

    def draw(self):
        WoodBase.draw(self)

    def draw_debug(self):
        WoodBase.draw_debug(self)
        run.run.font.write(self.x, self.y, "%d" % self.id)

class Spikes(Base):
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        self.pic = Picture("items/spikes0001")

    def touch(self, bywho, speed):
        bywho.spiked(10)

class Animated(Base):
    frames = None

    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)

        if self.frames == None:
            self.frames = []
            for frame in range(1, self.framecount + 1):
                self.frames.append(Picture(self.files % frame))
        self.frame = random.randint(0, self.framecount - 1)
        self.anim = 0
        self.flipped = False

    def is_active(self): return True

    def tick(self):
        if self.anim < self.animspeed: self.anim += 1
        else:
            self.anim = 0
            self.frame += 1
        if self.frame == self.framecount: self.frame = 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glTranslate(self.xoff, self.yoff, 0)
        glEnable(GL_TEXTURE_2D)
        if self.flipped:
            self.frames[self.frame].draw_centered_mirror(0, 0)
        else:
            self.frames[self.frame].draw_centered(0, 0)
        glPopMatrix()

class Coin(Animated):
    xoff = 0
    yoff = 0
    files = "items/coin%04d"
    framecount = 8
    animspeed = 2

    def want_touch(self, who):
        if isinstance(who, Allefant):
            self.disappear()
            run.run.ding.play(1, self)
            self.dead = True
            who.coins += 1
            if who.health < 100: who.health += 1
        return False

    def tick(self):
        rx, ry, dx, dy = self.orientation()
        Animated.tick(self)
        oldx = self.x
        oldy = self.y
        self.disappear()
        self.x += dx
        self.y += dy
        if self.colliders():
            self.x = oldx
            self.y = oldy
        self.appear()

    def layer(self): return 1

class Portal(Animated):
    xoff = 0
    yoff = -60
    files = "items/portal%04d"
    framecount = 8
    animspeed = 2

    notagain = 0

    def interact(self):
        if run.run.game.player.coins < run.run.game.coins:
            if self.notagain > 0:
                self.notagain -= 1
                return
            self.notagain = 10
            run.run.message = run.Message(["Needs coins to operate!"])
        elif run.run.game.rider and not run.run.game.rider.dead:
            if self.notagain > 0:
                self.notagain -= 1
                return
            self.notagain = 10
            run.run.message = run.Message(["Teleporting...",
                "Aborted by operator!"])
        else:
            run.run.message = run.Message(["Teleporting..."])
            run.run.level_done = True

    def layer(self): return -1

class Leprechaun(Animated):
    xoff = 0
    yoff = 0
    files = "items/leprechaun%04d"
    framecount = 16
    animspeed = 2

    def __init__(self, x, y, r):
        Animated.__init__(self, x, y, r)
        self.lifes = 3
        self.flipped = False
        self.go = False

    def tick(self):
        dx = -math.sin(self.angle * math.pi / 180.0)
        dy = math.cos(self.angle * math.pi / 180.0)
        rx = dy
        ry = -dx
        if not self.flipped:
            rx = -rx
            ry = -ry

        Animated.tick(self)

        ground = False
        # fall
        oldx = self.x
        oldy = self.y
        self.disappear()
        self.x += dx
        self.y += dy
        if self.colliders():
            self.x = oldx
            self.y = oldy
            ground = True
        self.appear()

        if not ground: return

        # walk
        oldx = self.x
        oldy = self.y
        self.disappear()
        self.x += rx
        self.y += ry
        cs = self.colliders()
        if cs:
            for c in cs:
                c.spiked()
            self.x = oldx
            self.y = oldy
            if self.flipped: self.angle -= 2
            else: self.angle += 2
            self.go = True
            if random.randint(0, 60 * 10) == 0:
                self.flipped = not self.flipped
        else:
            if self.go: self.go = False
            else:
                self.x = oldx
                self.y = oldy
            if self.flipped: self.angle += 2
            else: self.angle -= 2
        self.appear()

    def layer(self): return 1

    def touch(self, who, speed):
        if isinstance(who, Allefant):
            rx, ry, dx, dy = self.orientation()
            falling = who.dx * dx + who.dy * dy
            if falling < -4:
                self.lifes -= 1
                if self.lifes == 0:
                    self.disappear()
                    self.dead = True
                    run.run.game.insert_stuff(self.x, self.y, "Coin")
                
            who.dx -= dx * 3
            who.dy -= dy * 3

class Python(Animated):
    texts = {
        0 : ["I am Python!"],
        1 : ["Hint:", "Use Down or S", "to skip text!"],
        2 : ["I am Python!", "Python say: Move right", "to go to exit to left!", "It's twisted!"],
        3 : ["Python is cool!", "Oh, and the hint:", "Avoid the springs!"],
        4 : ["Avoid spikes!", "You can jump longer", "when running!"],
        5 : ["Collect coins to", "unlock the exit!"],
        6 : ["You can jump higher", "when bouncing from", "a previous jump!"],
        7 : ["Well done!"],

        8 : ["Beware of loose cogwheels!"],
        9 : ["Where are the coins?"],

        10 : ["Python say:", "Level 2 comes after level 1!"],
        11 : ["Hint:", "Use the lever to", "switch off the laser!"],
        12 : ["So you made it to", "the other side!"],

        13 : ["Did you know..", "why the wood is so shiny?"],
        14 : ["Did you know..", "where the coins come from?"],

        15 : ["Go this way!"],
        16 : ["Go that way!"],

        17 : ["Grim Reaper...", "Approaching...", "Nigete..."],
        18 : ["Hint:", "He don't like", "jumping on his head!"],

        19 : ["That's it. You win!", "", "/me falls asleep after", "level editing all day.",
            "Hope you enjoyed this pyweek", "as much as I did!"],

        20 : ["Beautiful is better than ugly.", "Explicit is better than implicit."],
        21 : ["Simple is better than complex.", "Complex", "is better than complicated."],
        22 : ["Flat is better than nested.", "Sparse is better than dense."],
        23 : ["Readability counts."],
        24 : ["Special cases aren't special", "enough to break the rules.", "Although practicality", "beats purity."],
        25 : ["Errors should never", "pass silently.", "Unless explicitly silenced."],
        26 : ["In the face of ambiguity,",  "refuse the temptation to guess."],
        27 : ["There should be one", "-- and preferably only one --", "obvious way to do it."],
        28 : ["Although that way may not be", "obvious at first", "unless you're Dutch."],
        29 : ["Now is better than never.", "Although never is often", "better than *right* now."],

        30 : ["Hint:", "Don't talk to those guys.", "They are some weird cult."],
        }
    vars = Base.vars + ["text", "flipped!"]
    xoff = 0
    yoff = -30
    files = "items/python%04d"
    framecount = 16
    animspeed = 4

    def __init__(self, x, y, r):
        Animated.__init__(self, x, y, r)

        self.text = 1
        self.notagain = 0

    def interact(self):
        if self.notagain:
            self.notagain -= 1
            return
        self.notagain = 20
        run.run.message = run.Message(self.texts[self.text])

    def layer(self): return -1

    def draw(self):
        Animated.draw(self)

    def draw_debug(self):
        Animated.draw_debug(self)
        run.run.font.write(self.x, self.y, "%d" % self.text)

class Lever(Base):
    frames = None
    xoff = 0
    yoff = -30

    vars = Base.vars + ["laser"]

    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)

        if self.frames == None:
            self.frames = []
            for frame in range(1, 9):
                self.frames.append(Picture("items/lever%04d" % frame))
        self.frame = 7
        self.anim = 0
        self.laser = 0

    def is_active(self): return True

    def tick(self):
        if self.anim:
            self.frame -= 1
            if self.frame == 0: self.anim = 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glTranslate(self.xoff, self.yoff, 0)
        glEnable(GL_TEXTURE_2D)
        self.frames[self.frame].draw_centered(0, 0)
        glPopMatrix()

    def draw_debug(self):
        Base.draw_debug(self)
        run.run.font.write(self.x, self.y, "%d" % self.laser)      

    def interact(self):
        if self.frame == 7:
            self.anim = 1
            laser = run.run.game.lasers[self.laser]
            laser.dead = True
            laser.disappear()

    def layer(self): return -1

class Ball1(Base):
    activity_radius = 800
    pic = None
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        if self.pic == None: self.pic = Picture("items/ball10001")

    vars = Base.vars + ["movex", "movey"]

    def is_active(self): return True

    def tick(o):
        if not o.push(o.movex, o.movey):
            o.movex = -o.movex
            o.movey = -o.movey
        else: # carry stuff
            o.disappear()
            upx = run.run.game.x - o.x
            upy = run.run.game.y - o.y
            d = (upx ** 2 + upy ** 2) ** 0.5
            upx /= d
            upy /= d
            oldx = o.x
            oldy = o.y
            o.x += upx * 2 - o.movex
            o.y += upy * 2 - o.movey
            cs = o.colliders()
            o.x = oldx
            o.y = oldy
            o.appear()
            rightx = -upy
            righty = upx
            for c in cs:
                if c.can_be_pushed(o):
                    if c.push(o.movex, o.movey):
                        #c.push(upx, upy)
                        go_right = (c.x - o.x) * rightx + (c.y - o.y) * righty
                        if go_right > 1:
                            c.dx -= rightx * 0.1
                            c.dy -= righty * 0.1
                        elif go_right < -1:
                            c.dx += rightx * 0.1
                            c.dy += righty * 0.1
        #Base.tick(o)

class Spring(Base):
    frames = None
    def __init__(self, x, y, r):
        if self.frames == None:
            self.frames = []
            for frame in range(1, 9):
                self.frames.append(Picture("items/spring%04d" % frame))
        self.frame = 0
        self.animating = 0
        self.movey = -1
        Orb.__init__(self, x, y, r)

    def is_active(self): return True

    def tick(self):
        if self.animating:
            self.animating -= 1
            if self.animating == 7:
                run.run.spring.play(1.0, self)
            if self.animating > 7:
                self.frame =  14 - self.animating
            else:
                self.frame = self.animating
            return
        rx, ry, dx, dy = self.orientation()

        if self.movey > 0:
            if self.push(self.dx, self.dy):
                self.dx += dx * 0.2
                self.dy += dy * 0.2
            else:
                self.movey = -1
                self.dx = -self.dx
                self.dy = -self.dy
                self.animating = 14
        else:
            if not self.push(self.dx, self.dy):
                self.movey = 1
                self.dx = 0
                self.dy = 0
            else:
                self.dx *= 0.9
                self.dy *= 0.9
                self.dx -= dx * 0.2
                self.dy -= dy * 0.2

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glEnable(GL_TEXTURE_2D)
        self.frames[self.frame].draw_centered(0, 0)
        glPopMatrix()

class Cogwheel(Base):
    frames = None
    def __init__(self, x, y, r):
        if self.frames == None:
            self.frames = []
            for frame in range(1, 9):
                self.frames.append(Picture("items/cogwheel%04d" % frame))
        self.frame = 0
        self.stuck = 0
        self.revolve = 0
        self.movex = 1
        Orb.__init__(self, x, y, r)

    def is_active(self): return True

    def touch(self, bywho, speed):
        bywho.spiked(10)

    def tick(self):
        rx, ry, dx, dy = self.orientation()

        falling = self.sameway(dx, dy)

        ground = self.get_colliders(dx * 2, dy * 2)

        if self.movex > 0:
            self.frame += 1
            if self.frame == 8:
                self.frame = 0
                self.revolve += 1
        else:
            self.frame -= 1
            if self.frame == -1:
                self.frame = 7
                self.revolve += 1

        if self.revolve >= 1:
            self.revolve = 0
            run.run.wood3.play(0.5, self)

        if ground:
            if falling > 0:
                self.dx -= falling * dx
                self.dy -= falling * dy
            self.dx -= dx * 0.4
            self.dy -= dy * 0.4
        else:
            self.dx += dx * 0.4
            self.dy += dy * 0.4

        self.dx += self.movex * rx * 0.35
        self.dy += self.movex * ry * 0.35

        ox = self.x
        oy = self.y
        Orb.tick(self)
        ox -= self.x
        oy -= self.y
        if ox ** 2 + oy ** 2 < 0.2 * 0.2:
            self.stuck += 1
            if self.stuck > 10:
                self.stuck = 0
                self.movex = -self.movex

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glEnable(GL_TEXTURE_2D)
        self.frames[self.frame].draw_centered(0, 0)
        glPopMatrix()

class Rider(Animated):
    xoff = 0
    yoff = 0
    files = "rider/%04d"
    framecount = 16
    animspeed = 2
    activity_radius = 1000

    def __init__(self, x, y, r):
        Animated.__init__(self, x, y, r)
        self.flipped = False
        self.lifes = 27
        self.turnfrenzy = 0
        self.jumpx = 0
        self.jumpy = 0
        self.invulnerable = 0

    def layer(self): return 1

    def collision_response(self, touched):
        for t in touched:
            if isinstance(t, Allefant):
                if not self.turnfrenzy: t.spiked()
                return
        if not self.turnfrenzy:
            rx, ry, dx, dy = self.orientation()
            self.turnfrenzy = 15
            self.jumpx = self.dx * -0.2
            self.jumpy = self.dy * -0.2
        Animated.collision_response(self, touched)

    def tick(self):
        rx, ry, dx, dy = self.orientation()
        if self.flipped:
            rx = -rx
            ry = -ry

        if self.invulnerable:
            self.invulnerable -= 1

        if self.turnfrenzy:
            if self.turnfrenzy > 1:
                self.dx += self.jumpx
                self.dy += self.jumpy
            self.turnfrenzy -= 1
        else:
            self.dx -= rx * 0.3
            self.dy -= ry * 0.3

        self.angle = 180 * math.atan2(-dx, dy) / math.pi

        if random.randint(0, 60 * 10) == 0:
            self.flipped = not self.flipped
            self.turnfrenzy = 15
            self.jumpx = self.dx * 0.2
            self.jumpy = self.dy * 0.2

        Animated.tick(self)
        Orb.tick(self)

    def touch(self, who, speed):
        if isinstance(who, Allefant):
            rx, ry, dx, dy = self.orientation()
            falling = who.dx * dx + who.dy * dy
            if falling < -4 and not self.invulnerable:
                self.invulnerable = 10
                self.lifes -= 1
                if self.lifes == 0:
                    self.disappear()
                    self.dead = True
                    run.run.game.insert_stuff(self.x, self.y, "Coin")

            who.dx -= dx * 3
            who.dy -= dy * 3

class Allefant(Orb):
    """
    i am the al le fant
    i'm known through out the land
    and when I trod a long
    i'm known to sing this song
    """
    frames = None
    def __init__(self, x, y, r):
        Orb.__init__(self, x, y, r)
        self.frames = []
        for frame in range(1, 17):
            self.frames.append(Picture("allefant/run/%04d" % frame))
        self.frames.append(Picture("allefant/jump/0001"))
        self.frame = 0
        self.runcycle = 0
        self.flipped = False
        self.kx = 0
        self.ky = 0
        self.jumping = 0
        self.health = 100
        self.coins = 0

    def can_be_pushed(self, bywho):
        if isinstance(bywho, Spring):
            if bywho.movey > 0:
                self.spiked(30)
        return True
    def is_active(self): return True

    def spiked(self, damage = 1):
        self.health -= damage
        run.run.ow.play(1, self)
        if self.health <= 0:
            run.run.game_over = True
            run.run.message = run.Message(["Game Over!"])

    def touch(self, bywho, speed):
        if isinstance(bywho, Cogwheel):
            self.spiked()

    def tick(p):
        game = run.run.game
        kx = p.kx
        ky = p.ky
        rx = game.rightx
        ry = game.righty
        dx = game.downx
        dy = game.downy
        gx = game.gravityx
        gy = game.gravityy

        if p.jumping: p.jumping -= 1

        jumpx = 0
        jumpy = 0

        ground = p.get_colliders(dx * 2, dy * 2)
        falling = p.sameway(dx, dy)

        # If we are falling right into the ground, handle it in the next tick
        # after we bounce. Also a fudge factor of 3 pixels to make it all work
        # smooth :P
        if falling > 3: ground = []

        if ground:
            if falling < -1:
                v = falling / -6.0
                if v > 1.0: v = 1.0
                #run.run.wood2.play(v, p)
            if p.frame == 16: p.frame = 0
            gx = 0
            gy = 0
            if ky < 0 and p.jumping == 0:
                if kx == 0:
                    p.frame = 16
                    jumpx = -15 * dx
                    jumpy = -15 * dy
                    v = 1.0
                else:
                    jumpx = -12 * dx + kx * 2 * rx
                    jumpy = -12 * dy + kx * 2 * ry
                    v = 0.8
                p.jumping = 20
                run.run.jump.play(v, p)
        else:
            pass

        for g in ground:
            g.touch(p, 0)

        if ky > 0:
            for g in ground:
                g.interact()

        if kx and ground: # jump a bit up when going sideways
            # If we are actually falling down (no more than 2 pixels due to
            # check earlier) - cancel it away to move smoother.
            if falling > 0:
                p.dx -= falling * dx
                p.dy -= falling * dy
            p.dx -= 0.45 * dx
            p.dy -= 0.45 * dy

        p.dx += kx * 0.4 * rx + jumpx + gx * 0.2
        p.dy += kx * 0.4 * ry + jumpy + gy * 0.2

        if kx > 0:
            p.flipped = True
        if kx < 0:
            p.flipped = False

        if p.frame == 16 and falling > 1:
            p.frame = 0
        
        if kx and p.frame < 16:
            p.runcycle += 8
            p.runcycle %= 256
            p.frame = p.runcycle / 16

        if not kx and p.frame < 16:
            p.runcycle = 0
            p.frame = 0

        Orb.tick(p)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)
        glEnable(GL_TEXTURE_2D)
        if self.flipped:
            self.frames[self.frame].draw_centered_mirror(0, 0)
        else:
            self.frames[self.frame].draw_centered(0, 0)
        glPopMatrix()

