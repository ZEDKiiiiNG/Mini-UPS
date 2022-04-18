import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from constant import *
import amazon_ups_pb2
import time
 
def send_msg(fd, msg):
    msg_str = msg.SerializeToString()
    _EncodeVarint(fd.sendall, len(msg_str), None)
    fd.sendall(msg_str)

def recv_msg(fd, msg_type):
    msg_str = fd.recv(MSG_LEN)
    msg = msg_type()
    msg.ParseFromString(msg_str[1:])
    return msg

# def start_server():


# return world_id
def connect_world(world_fd):
    # ups send UConnect to world
    u_msg = world_ups_pb2.UConnect()
    u_msg.isAmazon = False
    for i in range(TRUCK_NUM):
        u_msg.trucks.add(id=i, x=i, y=i)
    send_msg(world_fd, u_msg)
    # ups receive UConnected from world
    # w_msg_str = recv_msg(world_fd)
    # w_msg = world_ups_pb2.UConnected()
    # w_msg.ParseFromString(w_msg_str)
    w_msg = recv_msg(world_fd, world_ups_pb2.UConnected)
    world_id = w_msg.worldid
    result = w_msg.result
    if result != CONNECTED:
        print("error: {}".format(result))
    print("world id: {}".format(world_id))
    return world_id

# def send_world_id(amazon_fd, world_id, seq_num, acks):
#     u_msg = amazon_ups_pb2.U2AWorldId()
#     u_msg.worldid = world_id
#     u_msg.seqnum = seq_num
#     while seq_num not in acks:
#         send_msg(amazon_fd, u_msg)
#         a_msg = recv_msg(amazon_fd, amazon_ups_pb2.AMsg)
#         time.sleep(RETRY_INTERVAL)
#     return



def main():
    seq_num = 0
    acks = set()
    world_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_fd.connect((WORLD_HOST, WORLD_PORT))
    connect_world(world_fd)

    # listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # listen_fd.bind(UPS_HOST, UPS_PORT)
    # listen_fd.listen(1)
    # amazon_fd, _ = listen_fd.accept()



if __name__ == "__main__":
    main()
