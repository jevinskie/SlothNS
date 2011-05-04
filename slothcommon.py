from twisted.names import dns

def readPrecisely(file, l):
    buff = file.read(l)
    if len(buff) < l:
        raise EOFError
    return buff

class NULLAbuseQuery(dns.Query):
    def __init__(self, l):
        self.name = NULLAbuseName(l)
        self.type = dns.NULL
        self.cls = dns.IN

class NULLAbuseName(dns.Name):
    def __init__(self, l=None):
        if l is None:
            l = []
        self.l = l

    def encode(self, strio):
        for part in self.l:
            strio.write(chr(len(part)))
            strio.write(part)
        strio.write(chr(0))

    def decode(self, strio):
        self.l = []
        off = 0
        while True:
            l = ord(readPrecisely(strio, 1))
            if l == 0:
                if off > 0:
                    strio.seek(off)
                return
            part = readPrecisely(strio, l)
            self.l.append(part)

    def __eq__(self, other):
        if isinstance(other, Name):
            return str(self) == str(other)
        return 0


    def __hash__(self):
        return hash(str(self))


    def __str__(self):
        return str(self.l)
