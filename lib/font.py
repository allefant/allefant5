from picture import Picture
import data

class Font:
    def __init__(self, path):
        self.glyphs = {}
        for i in range(32, 127):
            self.glyphs[chr(i)] = Picture(path + "%d.png" % i)

    def write(self, px, py, text, red = 1, green = 1, blue = 1, alpha = 1,
        center = False, right = False):
        sx = px
        if center:
            sx = px = px - self.width(text) / 2
        if right:
            sx = px = px - self.width(text)
        for letter in text:
            if letter == "\n":
                py += self.glyphs[" "].h
                px = sx
                continue
            g = self.glyphs[letter]
            g.draw(px, py, red = red, green = green, blue = blue, alpha = alpha)
            px += g.w

    def width(self, text):
        x = 0
        for letter in text:
            x += self.glyphs[letter].w
        return x

    def height(self):
        return self.glyphs[" "].h
