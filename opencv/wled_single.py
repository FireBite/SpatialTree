import socket
import struct
import time

UDP_IP   = "4.3.2.1"
UDP_PORT = 21324

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("Press Ctrl-C to exit")

message = struct.pack("BBBB", 4, 2, 0, 0) # DNRGB Header

pixel = struct.pack("BBB", 255, 0, 0)

message = message + pixel

print(message)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

try:
    while True:
        sock.sendto(message, (UDP_IP, UDP_PORT))
        time.sleep(0.02)
except KeyboardInterrupt:
    exit()
    