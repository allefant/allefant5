import pygame, data, run

class Sound:
    def __init__(self, filename):
        self.sound = pygame.mixer.Sound(data.loadblock(filename))
    def play(self, volume, orb):
        def fallof(x, near, far):
            d = far - near
            v = (far - x) / d
            if v > 1: v = 1
            if v < 0: v = 0
            return v

        g = run.run.game
        dx = orb.x - g.player.x
        dy = orb.y - g.player.y

        upx = g.x - g.player.x
        upy = g.y - g.player.y
        u = (upx ** 2 + upy ** 2) ** 0.5
        upx /= u
        upy /= u
        rix = -upy
        riy = upx

        x = rix * dx + riy * dy
        y = upx * dx + upy * dy

        if x > 0:
            vr = fallof(x, 100.0, 300.0)
            vl = fallof(x, 0.0, 100.0)
        else:
            vl = fallof(-x, 100.0, 300.0)
            vr = fallof(-x, 0.0, 100.0)
        v = fallof(abs(y), 100.0, 300.0)
        v *= volume
        vl *= v
        vr *= v

        if vl > 0.02 or vr > 0.02:
            c = pygame.mixer.find_channel(True)
            c.stop()
            c.set_volume(vl, vr)
            c.play(self.sound)