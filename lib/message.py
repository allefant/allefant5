import run
import OpenGL
from OpenGL.GL import *

class Message:
    def __init__(self, rows):
        self.rows = rows
        self.duration = 0
        self.showfull = False

    def tick(self):
        self.duration += 1

    def display(self):
        x = run.run.game.vw / 2
        y = run.run.game.vh / 2
        h = run.run.font.height() * len(self.rows)
        y -= 0.5 * h
        w = max([run.run.font.width(text) for text in self.rows])

        glDisable(GL_TEXTURE_2D)
        glColor4f(0.4, 0, 0, 0.6)
        glBegin(GL_QUADS)
        glVertex2d(x - w / 2 - 4, y - 4)
        glVertex2d(x + w / 2 + 4, y - 4)
        glVertex2d(x + w / 2 + 4, y + h + 4)
        glVertex2d(x - w / 2 - 4, y + h + 4)
        glEnd()
        glEnable(GL_TEXTURE_2D)

        time = 0
        for text in self.rows:
            w = run.run.font.width(text)
            px = x - w * 0.5
            for letter in text:
                g = run.run.font.glyphs[letter]
                g.draw(px, y, red = 1, green = 0.9, blue = 0.1, alpha = 0.9)
                px += g.w
                time += 5
                if not self.showfull and time > self.duration: return
            y += run.run.font.height()

        self.showfull = True
        if self.duration - time > time:
            run.message = None
