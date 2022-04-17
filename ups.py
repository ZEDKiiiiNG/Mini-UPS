import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from constant import *

def encode_msg(fd, msg):
    msg_str = msg.SerializeToString()
    _EncodeVarint(fd.sendall, len(msg_str), None)
    return msg_str

# return world_id
def connect_world(world_fd):
    # ups send UConnect to world
    u_connect = world_ups_pb2.UConnect()
    u_connect.isAmazon = False
    for i in range(TRUCK_NUM):
        u_connect.trucks.add(id=i, x=i, y=i)
    msg_str = encode_msg(world_fd, u_connect)
    world_fd.sendall(msg_str)
    # ups receive UConnected from world
    msg = world_fd.recv(MSG_LEN)
    u_connected = world_ups_pb2.UConnected()
    u_connected.ParseFromString(msg[1:])  # first byte is length
    world_id = u_connected.worldid
    result = u_connected.result
    if result != CONNECTED:
        print("error: {}".format(result))
    print("world id: {}".format(world_id))
    return world_id

def send_world_id(amazon_fd):
    return



def main():
    world_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_fd.connect((WORLD_HOST, WORLD_PORT))
    connect_world(world_fd)

    # listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # listen_fd.bind(UPS_HOST, UPS_PORT)
    # listen_fd.listen(1)
    # amazon_fd, _ = listen_fd.accept()



if __name__ == "__main__":
    main()
