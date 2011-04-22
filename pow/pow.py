from ctypes import *

class _pow_t(Structure):
    _fields_ = [("perm_table", POINTER(c_uint32)),
                ("rand", c_uint32 * 4),
                ("seed", c_uint32),
                ("size", c_uint32),
                ("n", c_uint32),]
_pow_t_p = POINTER(_pow_t)

class _pow_req_t(Structure):
    _fields_ = [("x0", c_uint32),
                ("check", c_uint32),
                ("l", c_uint32),
                ("v", POINTER(c_uint32)),
                ("w", POINTER(c_uint32)),]
_pow_req_t_p = POINTER(_pow_req_t)

class _pow_res_t(Structure):
    _fields_ = [("path", c_uint32),]
_pow_res_t_p = POINTER(_pow_res_t)

_pow_lib = cdll.LoadLibrary(".libs/libpow.so")

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

class pow_res(object):
    def __init__(self, pow, req):
        self.pow = pow
        self.req = req
        self.res_t = _pow_lib.create_res(self.pow.pow_t, self.req.req_t)
    def __del__(self):
        _pow_lib.destroy_res(self.res_t)

class pow_req(object):
    def __init__(self, pow, l):
        self.pow = pow
        self.req_t = _pow_lib.create_req(self.pow.pow_t, l)
    def __del__(self):
        _pow_lib.destroy_req(self.req_t)
    def verify_res(self, res):
        return _pow_lib.verify_res(self.pow.pow_t, self.req_t, res.res_t)
    def create_res(self):
        return pow_res(self.pow, self)

class pow(object):
    def __init__(self, n, seed):
        self.pow_t = _pow_lib.create(n, seed)
    def __del__(self):
        _pow_lib.destroy(self.pow_t)
    def create_req(self, l):
        return pow_req(self, l)

