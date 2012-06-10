'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os, struct, sys
from StringIO import StringIO

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))
origdata_dir = os.path.normpath(os.path.join(data_py, '..', 'origdata'))

class Dump: pass
dump = None

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def savepath(filename):
    return os.path.join(origdata_dir, filename)

def once():
    global dump
    dump = Dump()
    dump.mem = open(filepath("memdump"), "rb").read()
    pos = 0
    n = struct.unpack("<i", dump.mem[:4])[0]
    pos = 4
    dump.index = {}
    for i in range(n):
        name = ""
        while 1:
            c = dump.mem[pos]
            pos += 1
            if c == "\0": break
            name += c
       
        o, l = struct.unpack("<ii", dump.mem[pos:pos + 8])
        dump.index[name] = dump.mem[o:o + l]
        name = ""
        pos += 8
    dump.mem = None

def loadblock(filename):
    #return file(os.path.join(origdata_dir, filename), "rb")

    if not dump: once()

    io = StringIO(dump.index[filename])
    return io

