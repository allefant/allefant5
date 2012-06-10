import pygame, data
from OpenGL.GL import *

cache = {}

def Picture(path, area = None):
    if path in cache: return cache[path]
    pic = CachedPicture(path, area)
    cache[path] = pic
    return pic

class CachedPicture:
    def __init__(self, path, area = None):

        glEnable(GL_TEXTURE_2D)

        image = pygame.image.load(data.loadblock(path))

        self.w = image.get_width()
        self.h = image.get_height()

        if area:
            x, y, w, h = area
            sub = image.subsurface(area)
            rgbadata = pygame.image.tostring(sub, "RGBA", True)
            self.w = w
            self.h = h
        else:
            rgbadata = pygame.image.tostring(image, "RGBA", True)

        def pot(x):
            y = 1.0
            while y < x: y *= 2
            return y

        self.texw = pot(self.w)
        self.texh = pot(self.h)

        if self.texw != self.w or self.texh != self.h:
            olddata = rgbadata
            rgbadata = ""
            for row in range(int(self.texh - self.h)):
                rgbadata += olddata[-4 * self.w :]
                rgbadata += rgbadata[-4:] * int(self.texw - self.w)
            for row in range(self.h):
                rgbadata += olddata[4 * row * self.w : 4 * (row + 1) * self.w]
                rgbadata += rgbadata[-4:] * int(self.texw - self.w)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, self.texw, self.texh, 0, GL_RGBA,
            GL_UNSIGNED_BYTE, rgbadata)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) #NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR) #NEAREST)

    def texpos(self, x, y):
        tx = float(x) / self.w
        ty = float(y) / self.h
        return tx, ty

    def draw_part(self, x, y, l, t, r, b, red = 1, green = 1, blue = 1, alpha = 1):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor4f(red, green, blue, alpha)
        tw, th = self.texw, self.texh

        w = r - l
        h = b - t

        glBegin(GL_POLYGON)
        glTexCoord2f(l / tw, 1 - t / th)
        glVertex2f(x, y)
        glTexCoord2f(r / tw, 1 - t / th)
        glVertex2f(x + w, y)
        glTexCoord2f(r / tw, 1 - b / th)
        glVertex2f(x + w, y +h)
        glTexCoord2f(l / tw, 1 - b / th)
        glVertex2f(x, y + h)
        glEnd()

    def draw(self, x, y, red = 1, green = 1, blue = 1, alpha = 1):
        glColor4f(red, green, blue, alpha)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        tw, th = self.texw, self.texh

        glBegin(GL_POLYGON)
        glTexCoord2f(0, 1)
        glVertex2f(x, y)
        glTexCoord2f(self.w / tw, 1)
        glVertex2f(x + self.w, y)
        glTexCoord2f(self.w / tw, 1 - self.h / th)
        glVertex2f(x + self.w, y + self.h)
        glTexCoord2f(0, 1 - self.h / th)
        glVertex2f(x, y + self.h)
        glEnd()
    

    def draw_centered(self, x, y):
        x -= self.w * 0.5
        y -= self.h * 0.5
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_POLYGON)
        glTexCoord2f(0, 1)
        glVertex2f(x, y)
        glTexCoord2f(1, 1)
        glVertex2f(x + self.w, y)
        glTexCoord2f(1, 0)
        glVertex2f(x + self.w, y + self.h)
        glTexCoord2f(0, 0)
        glVertex2f(x, y + self.h)
        glEnd()

    def draw_centered_mirror(self, x, y):
        x -= self.w * 0.5
        y -= self.h * 0.5
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_POLYGON)
        glTexCoord2f(1, 1)
        glVertex2f(x, y)
        glTexCoord2f(0, 1)
        glVertex2f(x + self.w, y)
        glTexCoord2f(0, 0)
        glVertex2f(x + self.w, y + self.h)
        glTexCoord2f(1, 0)
        glVertex2f(x, y + self.h)
        glEnd()
