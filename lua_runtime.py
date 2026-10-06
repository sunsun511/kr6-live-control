import ctypes
import os

class LuaRuntime:
    def __init__(self, game_dir):
        self.dll_dir = os.add_dll_directory(str(game_dir))
        self.lib = ctypes.CDLL(str(game_dir / 'lua51.dll'))
        specs = {
            'luaL_newstate': ([], ctypes.c_void_p),
            'luaL_openlibs': ([ctypes.c_void_p], None),
            'luaL_loadstring': ([ctypes.c_void_p, ctypes.c_char_p], ctypes.c_int),
            'lua_pcall': ([ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int], ctypes.c_int),
            'lua_tolstring': ([ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p], ctypes.c_char_p),
            'lua_close': ([ctypes.c_void_p], None),
        }
        for name, (args, result) in specs.items():
            fn = getattr(self.lib, name)
            fn.argtypes, fn.restype = args, result

    def run(self, script):
        state = self.lib.luaL_newstate()
        try:
            self.lib.luaL_openlibs(state)
            result = self.lib.luaL_loadstring(state, script.encode('utf-8'))
            result = result or self.lib.lua_pcall(state, 0, 1, 0)
            value = self.lib.lua_tolstring(state, -1, None)
            message = value.decode('utf-8', errors='replace') if value else ''
            if result:
                raise RuntimeError(message)
            return message
        finally:
            self.lib.lua_close(state)

def lua_bytes(data):
    return '"' + ''.join('\\%03d' % v for v in data) + '"'
