"""
game type: twisted platformer
main character: allefant
weapon: stomp on enemies
alternate weapon: -
special move: -

In this 5th adventure of the Allefant, the Allefant has become entrapped into
a twisted world. Unlike before, reaching the end of a level will not advance
to the next - but levels are twisted like a Moebius strip and at the end the
same level just all starts over. Is there any way to escape from such a twisted
situation - or is this the final game in the Allefant series? You decide..

Did you know that a twisted platform looks like a ball?

= intro level =
boss: -
background: sky, beach
tiles: grass, trees
enemies: balls

= level 1 =
boss: white rider, shoots arrows
background: clockwork
tiles: wood blocks, metal
enemies: cogwheels, springs

= level 2 =
boss: red rider, sword fighter
background: sky, clouds (fog of war)
tiles: clouds
enemies: winged knights

= level 3 =
boss: black rider, scales (drops weights)
background: stars
tiles: glass
enemies: weights

= level 4 =
boss: pale rider (grim reaper), fights with scythe
background: hell
tiles: black iron
enemies: fire

"""

DEBUG = not True
EDITING = not True

import pygame, sys, os, math, data, sys, edit

from game import Game

import OpenGL
from OpenGL.GL import *
from picture import Picture
from font import Font
from sound import Sound
from message import Message

class Config:
    def __init__(self):
        self.fullscreen = False
        self.nomusic = False
        self.level = 1

    def load(self):
        try:
            f = open(data.filepath("config"))
        except IOError:
            return
        for row in f:
            if row.startswith("fullscreen"): self.fullscreen = True
            if row.startswith("nomusic"): self.nomusic = True
            if row.startswith("level"): self.level = int(row[6:])

    def save(self):
        f = open(data.filepath("config"), "w")
        if self.fullscreen: f.write("fullscreen\n")
        if self.nomusic: f.write("nomusic\n")
        f.write("level %d\n" % self.level)
        f.close()

class Run:
    w = 640
    h = 480
    FPS = 60
    run = None

    paused = False
    message = None

    editing = EDITING
    debugging = DEBUG

    first_time = True

run = Run.run = Run()

def main():
    c = Config()
    c.load()

    pygame.init()
    pygame.display.set_mode((run.w, run.h), pygame.OPENGL | pygame.DOUBLEBUF |
        (c.fullscreen and pygame.FULLSCREEN or 0))

    pygame.mouse.set_visible(False)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(0, run.w, run.h, 0, -1, 1)

    run.game_over = False
    run.level_done = False
    run.last_level = c.level
    run.game = Game(run.w, run.h)
    run.font = Font("abc/")

    run.wood = Sound("wood.ogg")
    run.wood2 = Sound("wood2.ogg")
    run.wood3 = Sound("wood3.ogg")
    run.jump = Sound("jump.ogg")
    run.spring = Sound("spring.ogg")
    run.ding = Sound("ding.ogg")
    run.ow = Sound("ow.ogg")

    run.run_game = run_game

    run.edit_level = 0

    run.config = c
    run.help = False

    import title
    title.run_title()

def run_game():
    game = run.game = run.game.load_level(run.last_level)

    clock = pygame.time.Clock()

    debug_no_render = False

    if not run.config.nomusic:
        pygame.mixer.music.load(data.filepath("loop/level1.ogg"))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

    cursor = Picture("mouse.png")

    if run.first_time:
        run.message = Message(["Move: Left/Right or A/D",
            "Jump: Up or W", "Interact: Down or S"])
        run.first_time = False

    fps = []
    quit = False
    next = pygame.time.get_ticks() + 1000.0 / run.FPS
    while not quit:

        p = game.player

        gx = p.x - game.x
        gy = p.y - game.y
        gd = (gx ** 2 + gy ** 2) ** 0.5

        if gd > 1:
            downx = gx / gd
            downy = gy / gd
        else:
            downx = 0
            downy = 1
        rightx = downy
        righty = -downx

        #gx /= game.radius
        #gy /= game.radius

        if gd > 30:
            gx = downx
            gy = downy
        else:
            gx = 0
            gy = 0

        mx, my = pygame.mouse.get_pos()
        rx = mx - game.vw / 2
        ry = my - game.vh / 2
        x = p.x + rightx * rx + downx * ry
        y = p.y + righty * rx + downy * ry

        game.reloaded = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    quit = True
                if e.key == pygame.K_RETURN:
                    if e.mod & pygame.KMOD_ALT:
                        pygame.display.toggle_fullscreen()
                if e.key == pygame.K_DOWN or e.key == ord("s"):
                    if run.message:
                        if not run.message.showfull: run.message.showfull = True
                        else: run.message = None
                if e.key == ord("p"):
                    run.paused = not run.paused
                if run.debugging:
                    if e.key == pygame.K_F12:
                        debug_no_render = not debug_no_render
                if run.editing:
                    edit.run = run
                    edit.game = game
                    edit.x = x
                    edit.y = y
                    edit.rightx = rightx
                    edit.righty = righty

                    for i in range(0, len(edit.commands), 2):
                        com, func = edit.commands[i : i + 2]
                        if (type(com) == str and e.key == ord(com)) or \
                            e.key == com: func()

            elif e.type == pygame.MOUSEBUTTONUP and run.editing:
                if e.button == 1:
                    game.selected = game.dragged
                    game.dragged = None
                    if game.selected: game.new_size = game.selected.r
            elif e.type == pygame.MOUSEBUTTONDOWN and run.editing:
                mx, my = e.pos

                if e.button == 1:
                    o = game.colliders(x, y, 10)
                    if o:
                        game.dragged = o[0]
                        game.drag = (x, y)
                if e.button == 3:
                    pass

        if game.reloaded:
            game = run.game
            continue

        if game.dragged:
            drx, dry = game.drag
            dro = game.dragged
            game.dragged.teleport_to(x + dro.x - drx, y + dro.y - dry)
            game.drag = (x, y)

        kx, ky = 0, 0
        k = pygame.key.get_pressed()
        if not run.editing:
            if k[pygame.K_a] and not k[pygame.K_d]: kx = -1
            if k[pygame.K_d] and not k[pygame.K_a]: kx = 1
            if k[pygame.K_w] and not k[pygame.K_s]: ky = -1
            if k[pygame.K_s] and not k[pygame.K_w]: ky = 1
        
        if k[pygame.K_LEFT] and not k[pygame.K_RIGHT]: kx = -1
        if k[pygame.K_RIGHT] and not k[pygame.K_LEFT]: kx = 1
        if k[pygame.K_UP] and not k[pygame.K_DOWN]: ky = -1
        if k[pygame.K_DOWN] and not k[pygame.K_UP]: ky = 1

        b1, b2, b3 = pygame.mouse.get_pressed()

        game.gravityx = gx * 2
        game.gravityy = gy * 2
        game.downx = downx
        game.downy = downy
        game.rightx = rightx
        game.righty = righty

        if run.paused:
            pass
        elif run.message:
            run.message.tick()
        elif run.game_over:
            run.game_over = False
            quit = True
        elif run.level_done:
            run.level_done = False
            run.last_level += 1
            game = run.game = game.load_level(run.last_level)
            if run.last_level > run.config.level:
                run.config.level = run.last_level
                run.config.save()
            continue
        else:
            p.kx = kx
            p.ky = ky
            game.tick()

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        game.view.angle = 180 * math.atan2(downx, downy) / math.pi
        p.angle = -game.view.angle
        game.view.x = p.x
        game.view.y = p.y
        glTranslate(game.vw / 2, game.vh / 2, 0)
        glRotate(game.view.angle, 0, 0, 1)
        glTranslate(-game.view.x, -game.view.y, 0)

        if not debug_no_render:
            game.render()

        glLoadIdentity()

        def show_fps():
            now = pygame.time.get_ticks()
            while fps and fps[0] <= now - 1000:
                fps.pop(0)
            ds = []
            for i in range(1, len(fps)):
                ds.append(1.0 * fps[i] - fps[i - 1])

            if ds:
                avg = sum(ds) / len(ds)
                avg = 1000.0 / avg
                a = 1000.0 / min(ds)
                b = 1000.0 / max(ds)
            else:
                avg = a = b = 0

            run.font.write(640, 0, "FPS: %.1f (%.1f - %.1f)" % (avg, b, a),
                right = True)
        #show_fps()

        if run.help:
            helptext = "\n"
            x = 0
            pos = 0
            for i in range(0, len(edit.commands), 2):
                func = edit.commands[i + 1]
                if func.__doc__: helptext += func.__doc__ + "\n"
                else: helptext += "?\n"
                pos += 1
                if pos == 10:
                    run.font.write(x, 0, helptext)
                    x += 150
                    pos = 0
                    helptext = "\n"
            run.font.write(x, 0, helptext)

        if run.message:
            run.message.display()

        if run.editing:
            cursor.draw_centered(mx, my)

        pygame.display.flip()

        t = pygame.time.get_ticks()
        fps.append(t)
        w = int(next - t)

        if w > 0:
            pygame.time.wait(w)
        # If we're lagging behind, we can either skip rendering some frames,
        # or slow down. We choose the latter.
        if w < -500:
            next = t
        next += 1000.0 / run.FPS
