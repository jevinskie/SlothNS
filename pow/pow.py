from ctypes import *
from construct import *
import os
from multiprocessing import sharedctypes

class _pow_t(Structure):
    _fields_ = [("rand", c_uint32 * 4),
                ("seed", c_uint32),
                ("size", c_uint32),
                ("n", c_uint32),
                ("perm_table", c_uint32 * 2**22),]
    _pack_ = 1
_pow_t_p = POINTER(_pow_t)

class _pow_req_t(Structure):
    _fields_ = [("x0", c_uint32),
                ("check", c_uint32),
                ("l", c_uint32),
                ("v", POINTER(c_uint32)),
                ("w", POINTER(c_uint32)),]
    _pack_ = 1
_pow_req_t_p = POINTER(_pow_req_t)

class _pow_res_t(Structure):
    _fields_ = [("path", c_uint32),]
    _pack_ = 1
_pow_res_t_p = POINTER(_pow_res_t)

_lib_dir = os.path.dirname(os.path.abspath(__file__)) + '/.libs/'
_pow_lib = cdll.LoadLibrary(_lib_dir + "libpow.so")

_pow_lib.pow_create.argtypes = [c_uint32, c_uint32]
_pow_lib.pow_create.restype = _pow_t_p
_pow_lib.create = _pow_lib.pow_create

_pow_lib.pow_destroy.argtypes = [_pow_t_p]
_pow_lib.pow_destroy.restype = None
_pow_lib.destroy = _pow_lib.pow_destroy

_pow_lib.pow_create_req.argtypes = [_pow_t_p, c_uint32]
_pow_lib.pow_create_req.restype = _pow_req_t_p
_pow_lib.create_req = _pow_lib.pow_create_req

_pow_lib.pow_destroy_req.argtypes = [_pow_req_t_p]
_pow_lib.pow_destroy_req.restype = None
_pow_lib.destroy_req = _pow_lib.pow_destroy_req

_pow_lib.pow_verify_res.argtypes = [_pow_t_p, _pow_req_t_p, _pow_res_t_p]
_pow_lib.pow_verify_res.res_type = c_int
_pow_lib.verify_res = _pow_lib.pow_verify_res

_pow_lib.pow_create_res.argtypes = [_pow_t_p, _pow_req_t_p]
_pow_lib.pow_create_res.restype = _pow_res_t_p
_pow_lib.create_res = _pow_lib.pow_create_res

_pow_lib.pow_destroy_res.argtypes = [_pow_res_t_p]
_pow_lib.pow_destroy_res.restype = None
_pow_lib.destroy_res = _pow_lib.pow_destroy_res

_pow_res_wire = \
    Struct("pow_res_wire",
        Const(String("magic", 8), "SLOTHRES"),
        String("hex_path", 8),
        String("hex_x0", 8),
    )

_pow_req_wire = \
    Struct("pow_req_wire",
        Const(String("magic", 8), "SLOTHREQ"),
        UBInt32("seed"),
        UBInt8("n"),
        UBInt32("x0"),
        UBInt32("check"),
        UBInt8("l"),
        Array(lambda ctx: ctx.l, UBInt32("v")),
        Array(lambda ctx: ctx.l, UBInt32("w")),
    )

_pow_res_wire_lite = \
    Struct("pow_res_wire_lite",
        Const(String("magic", 8), "SLOTHRSL"),
        UBInt32("id"),
        UBInt32("path"),
        UBInt32("x0"),
    )

_pow_req_wire_lite = \
    Struct("pow_req_wire_lite",
        Const(String("magic", 8), "SLOTHRQL"),
        UBInt32("id"),
        UBInt32("seed"),
        UBInt8("n"),
        UBInt32("x0"),
        UBInt32("check"),
        UBInt8("l"),
        Array(lambda ctx: ctx.l, UBInt32("v")),
        Array(lambda ctx: ctx.l, UBInt32("w")),
    )

_pow_init_wire_lite = \
    Struct("pow_init_wire_lite",
        Const(String("magic", 8), "SLOTHINT"),
        UBInt32("id"),
    )

_pow_fin_wire_lite = \
    Struct("pow_fin_wire_lite",
        Const(String("magic", 8), "SLOTHFIN"),
        UBInt32("id"),
        UBInt8("ok"),
    )



class pow_res(object):
    def __init__(self, pow_obj, req, wire = None, wire_lite = None):
        self.pow = pow_obj
        self.req = req
        self.res_t = _pow_lib.create_res(pointer(self.pow.pow_t), self.req.req_t)
        if wire:
            res = _pow_res_wire.parse(wire)
            self.path = int(res.hex_path, 16)
        elif wire_lite:
            res = _pow_res_wire_lite.parse(wire_lite)
            self.path = res.path
            self.id = res.id

    def __del__(self):
        _pow_lib.destroy_res(self.res_t)

    def __getattr__(self, name):
        try:
            return self.res_t.contents.__getattribute__(name)
        except:
            raise AttributeError

    def __setattr__(self, name, value):
        if 'res_t' in self.__dict__ and any(name in f for f in self.res_t.contents._fields_):
            self.res_t.contents.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def pack(self):
        c = Container()
        c.magic = None
        c.hex_path = "%08X" % self.path
        c.hex_x0 = "%08X" % self.req.x0
        return _pow_res_wire.build(c)

    def pack_lite(self, idd):
        c = Container()
        c.magic = None
        c.id = idd
        c.path = self.path
        c.x0 = self.req.x0
        return _pow_res_wire_lite.build(c)

class pow_req(object):
    def __init__(self, pow_obj = None, l = None, wire = None, wire_lite = None):
        if wire:
            c = _pow_req_wire.parse(wire)
            if pow_obj == None:
                pow_obj = pow(c.n, c.seed)
            l = c.l
        elif wire_lite:
            c = _pow_req_wire_lite.parse(wire_lite)
            if pow_obj == None:
                pow_obj = pow(c.n, c.seed)
            l = c.l
            self.id = c.id
        self.pow = pow_obj
        self.req_t = _pow_lib.create_req(pointer(self.pow.pow_t), l)
        if wire or wire_lite:
            for i in range(l):
                self.v[i] = c.v[i]
                self.w[i] = c.w[i]
            self.x0 = c.x0
            self.check = c.check

    def __del__(self):
        _pow_lib.destroy_req(self.req_t)

    def __getattr__(self, name):
        try:
            return self.req_t.contents.__getattribute__(name)
        except:
            raise AttributeError

    def __setattr__(self, name, value):
        if 'req_t' in self.__dict__ and any(name in f for f in self.req_t.contents._fields_):
            self.req_t.contents.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def verify_res(self, res):
        if _pow_lib.verify_res(pointer(self.pow.pow_t), self.req_t, res.res_t):
            return True
        else:
            return False

    def create_res(self):
        return pow_res(pow_obj = self.pow, req = self)

    def pack(self):
        c = Container()
        c.magic = None
        c.seed = self.pow.seed
        c.n = self.pow.n
        c.x0 = self.x0
        c.check = self.check
        c.l = self.l
        c.v = [self.v[i] for i in range(self.l)]
        c.w = [self.w[i] for i in range(self.l)]
        return _pow_req_wire.build(c)

    def pack_lite(self, idd):
        c = Container()
        c.magic = None
        c.id = idd
        c.seed = self.pow.seed
        c.n = self.pow.n
        c.x0 = self.x0
        c.check = self.check
        c.l = self.l
        c.v = [self.v[i] for i in range(self.l)]
        c.w = [self.w[i] for i in range(self.l)]
        return _pow_req_wire_lite.build(c)


class pow(object):
    def __init__(self, n, seed, share = None):
        if share == None:
            self.pow_t = _pow_lib.create(n, seed).contents
        else:
            p = sharedctypes.copy(share.pow_t)
            self.pow_t = p

    #def __del__(self):
    #    _pow_lib.destroy(self.pow_t)

    def __getattr__(self, name):
        try:
            return self.pow_t.__getattribute__(name)
        except:
            raise AttributeError

    def __setattr__(self, name, value):
        if 'pow_t' in self.__dict__ and any(name in f for f in self.pow_t._fields_):
            self.pow_t.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def create_req(self, l):
        return pow_req(pow_obj = self, l = l)

