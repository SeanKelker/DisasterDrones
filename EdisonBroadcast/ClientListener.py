import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('',242*106))

while True:
    msg = s.recvfrom(1024)
    reply = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Got ping, replying")
    print(msg[0])
    reply.sendto(
        b"~I enjoy the plant",
        (msg[1][0],242*106)
    )
    reply.close()
    # print(msg[1][0])