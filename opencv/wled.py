import socket
import struct
import time
from collections import namedtuple

Color = namedtuple("Color", ['R', 'G', 'B'], defaults=[0,0,0])

class WLED:
    timeout = 2

    MSG_HEADER = message = struct.pack("BBBB", 4, 2, 0, 0)
    MSG_EMPTY_PIXEL = struct.pack("BBB", 0, 0, 0)

    def __init__(self, ip: str, port: int) -> None:
        self.IP   = ip
        self.PORT = port

        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        pass

    def setTimeout(self, timeout: int) -> None:
        self.timeout = timeout
        pass

    def setLEDSingle(self, color: Color, num: int) -> None:
        msg = self.MSG_HEADER # DNRGB Header

        while num > 0:
            msg += self.MSG_EMPTY_PIXEL
            num -= 1
        
        msg += struct.pack("BBB", color.R, color.G, color.G)

        self.sock.sendto(msg, (self.IP, self.PORT)) 
        pass
    