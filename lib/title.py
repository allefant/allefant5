import pygame, data, math, os, sys
from run import Run
from picture import Picture
import OpenGL
from OpenGL.GL import *
from font import Font
import main

run = Run.run

def run_title():
    class Title: pass
    run.quit = False
    game = run.game

    title = Picture("title.png")
    subtitle = Picture("subtitle.png")
    menu = Picture("menu.png")
    menu2 = Picture("menu2.png")
    menu3 = Picture("menu3.png")
    menu3hl = Picture("menu3hl.png")

    cursor = Picture("mouse.png")

    if not run.config.nomusic:
        pygame.mixer.music.load(data.filepath("loop/menu.ogg"))
        pygame.mixer.music.play(-1)

    def button_ng():
        run.run_game()
        if not run.config.nomusic:
            pygame.mixer.music.load(data.filepath("loop/menu.ogg"))
            pygame.mixer.music.play(-1)
        title.next = pygame.time.get_ticks() + 1000.0 / run.FPS

    def button_next():
        if run.last_level < run.config.level: run.last_level += 1

    def button_prev():
        if run.last_level > 1: run.last_level -= 1

    def button_fs():
        run.config.fullscreen = not run.config.fullscreen
        run.config.save()
        main.main()

    def button_nm():
        run.config.nomusic = not run.config.nomusic
        if not run.config.nomusic:
            pygame.mixer.music.load(data.filepath("loop/menu.ogg"))
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
        run.config.save()

    def button_q():
        run.quit = True

    rects = (
        (220, 274, 417, 323, button_ng),
        (170, 344, 320, 400, button_fs),
        (340, 344, 470, 400, button_nm),
        (283, 417, 358, 466, button_q),
        (130, 260, 210, 286, button_next),
        (130, 301, 210, 326, button_prev),
        )

    selected = None
    t = 0
    title.next = pygame.time.get_ticks() + 1000 / run.FPS
    while not run.quit:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run.quit = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    rects[3][4]()
                if e.key == pygame.K_RETURN:
                    rects[0][4]()
            elif e.type == pygame.MOUSEBUTTONUP:
                x, y = e.pos
                if e.button == 1:
                    if selected != None:
                        selected[4]()

        mx, my = pygame.mouse.get_pos()

        glClearColor(1, 0.6, 0.4, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        t += 1
        tt = (t * 4) % (480 + 512)

        game.background1.draw_centered(0, 0)
        game.background1.draw_centered(640, 480)
        game.background1.draw_centered(320, tt)
        game.background1.draw_centered(320, tt - 512 - 480)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        selected = None
        black = {"red" : 0, "green" : 0, "blue" : 0}
        beat = (t % 30)
        if beat < 20: beat = 0
        else:
            if beat < 25: beat = (beat - 20) / 5.0
            else: beat = 1 - (beat - 25) / 5.0
        d = (t / 30) % 3
        a, b, c = ((0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5))[d]
        flash = {"red" : beat * a, "green" : beat * b, "blue" : beat * c}
        d = 160.0
        if t < d:
            tt = 1 - t / d

            title.draw(0, 0 - tt * 480, **flash)
            subtitle.draw(0, 0 + tt * 480, **black)
            menu.draw(0 + tt * 640, 0, **black)
            menu2.draw(0 - tt * 640, 0, **black)
        elif t < d * 2:
            tt = t - d
            tt = tt / d

            title.draw(0, 0, **flash)
            subtitle.draw(0, -tt * 220, **black)
            menu.draw(240 * tt, 80 * tt, **black)
            menu2.draw(-80 * tt, 80 * tt, **black)
        else:
            tt = (t - d * 2) / d
            if tt > 1.0: tt = 1.0
            title.draw(0, 0, **flash)
            subtitle.draw(0, -220, **black)
            glPushMatrix()
            glTranslate(240 + 550, 80 + 350, 0)
            glRotate(10 * math.sin(1 * 2 * math.pi * (t - d * 2) / 60), 0, 0, 1)
            glTranslate(-550, -350, 0)
            menu.draw(0, 0, **black)
            glPopMatrix()
            menu2.draw(-80, 80, **black)
            menu3.draw(0, 0, red = 0, green = 0, blue = 0, alpha = tt)

            for r in rects:
                if mx >= r[0] and my >= r[1] and mx <= r[2] and my <= r[3]:
                    selected = r
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                    menu3hl.draw_part(r[0] - 8, r[1] - 8, r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8)
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    menu3.draw_part(r[0] - 8, r[1] - 8, r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8,
                        red = 1, green = 0.5, blue = 0, alpha = 0.5)
                    selected = r

            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            x, y = 395 + 230 * (run.last_level - 1) / 7, 245
            menu3hl.draw_part(x, y, x, y, 395 + 230 * run.last_level / 7, 290)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            menu3hl.draw_part(x, y, x, y, 395 + 230 * run.last_level / 7, 290,
                red = 1, green = 0.5, blue = 0, alpha = 0.5)

        cursor.draw_centered(mx, my)

        pygame.display.flip()

        ft = pygame.time.get_ticks()
        pygame.time.wait(int(title.next - ft))
        ft = title.next
        title.next = ft + 1000.0 / run.FPS
