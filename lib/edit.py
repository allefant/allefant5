import pygame
from sprites import Python, Lever, Laser
from message import Message

def comma():
    ", rot lef"
    if game.selected:
        game.selected.angle -= 5

def dot():
    ". rot rig"
    if game.selected:
        game.selected.angle += 5

def minus():
    "- fli"
    if game.selected:
        if hasattr(game.selected, "flipped"):
            game.selected.flipped = not game.selected.flipped

def one():
    "1 scr"
    game.restart()
    game.script1()

def two():
    "2 scr"
    game.script2()

def three():
    "3 scr"
    game.script3()

def four():
    "4 scr"
    game.script4(x, y, rightx, righty)

def five():
    "5 scr"
    game.script5()

def six():
    "6 scr"
    game.restart()

def seven():
    "7 scr"
    game.script7()

def f1():
    "F1 help"
    run.help = not run.help

def f2():
    "F2 save"
    game.save_level(run.edit_level)

def f3():
    "F3 load"
    run.game = game.load_level(run.edit_level)
    run.last_level = run.edit_level
    game.reloaded = True

def f4():
    "F4 prev"
    run.edit_level -= 1
    run.message = Message(["Level is %d!" % run.edit_level])

def f5():
    "F5 next"
    run.edit_level += 1
    run.message = Message(["Level is %d!" % run.edit_level])

def f6():
    "F6 dbg"
    run.run.debugging = not run.run.debugging

def insert():
    "Ins ins"
    game.insert_action(x, y)

def delete():
    "Del del"
    os = game.colliders(x, y, 1)
    for o in os:
        game.remove(o)
        break
    game.selected = None

def home():
    "Ho id-"
    for o in game.colliders(x, y, 1):
        if isinstance(o, Python):
            o.text -= 1
        if isinstance(o, Lever):
            o.laser -= 1
        if isinstance(o, Laser):
            o.id -= 1

def end():
    "End id+"
    for o in game.colliders(x, y, 1):
        if isinstance(o, Python):
            o.text += 1
        if isinstance(o, Lever):
            o.laser += 1
        if isinstance(o, Laser):
            o.id += 1

def key_h():
    "h hball"
    game.place_moving_ball(x, y, -game.view.angle,
        rightx, righty)
def key_c():
    "c cogl"
    game.place_moving_cogwheel(x, y, -game.view.angle)
def key_s():
    "s spring"
    game.place_moving_spring(x, y)
def key_b():
    "b block"
    game.insert_block1(x, y)
def key_n():
    "n block"
    game.insert_rotated_block1(x, y)
def key_i():
    "i wall"
    game.insert_wall(x, y)
def key_r():
    "r round"
    game.insert_stuff(x, y, "RoundBlock1")
def key_l():
    "l lever"
    game.insert_stuff(x, y, "Lever")
def key_y():
    "y pyton"
    game.insert_stuff(x, y, "Python")
def key_x():
    "x rider"
    game.insert_stuff(x, y, "Rider")
def key_a():
    "a spike"
    game.insert_stuff(x, y, "Spikes")
def key_d():
    "d lepre"
    game.insert_stuff(x, y, "Leprechaun")
def key_g():
    "g gold"
    game.insert_stuff(x, y, "Coin")
def key_w():
    "w wall2"
    game.insert_stuff(x, y, "Wall")
def key_f():
    "f laser"
    game.insert_stuff(x, y, "Laser")
def key_o():
    "o portal"
    game.insert_stuff(x, y, "Portal")
def key_v():
    "v vball"
    game.place_moving_ball(x, y, -game.view.angle, downx, downy)

def pageup():
    "Pup big"
    if game.selected:
        r = int(game.selected.r) + 1.0
        game.selected.set_radius(r)
        game.new_size = r
def pagedown():
    "Pdn small"
    if game.selected:
        r = int(game.selected.r) - 1.0
        game.selected.set_radius(r)
        game.new_size = r

commands = [
    ",", comma,
    ".", dot,
    "-", minus,
    "1", one,
    "2", two,
    "3", three,
    "4", four,
    "5", five,
    "6", six,
    "7", seven,
    pygame.K_F1, f1,
    pygame.K_F2, f2,
    pygame.K_F3, f3,
    pygame.K_F4, f4,
    pygame.K_F5, f5,
    pygame.K_F6, f6,
    pygame.K_INSERT, insert,
    pygame.K_DELETE, delete,
    pygame.K_HOME, home,
    pygame.K_END, end,
    "h", key_h,
    "c", key_c,
    "s", key_s,
    "b", key_b,
    "n", key_n,
    "i", key_i,
    "r", key_r,
    "l", key_l,
    "y", key_y,
    "x", key_x,
    "a", key_a,
    "d", key_d,
    "g", key_g,
    "w", key_w,
    "f", key_f,
    "o", key_o,
    "v", key_v,
    pygame.K_PAGEUP, pageup,
    pygame.K_PAGEDOWN, pagedown,
    ]
                    


    