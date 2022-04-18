import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from constant import *
import amazon_ups_pb2
import time
import select
 
def send_msg(fd, msg):
    msg_str = msg.SerializeToString()
    _EncodeVarint(fd.sendall, len(msg_str), None)
    fd.sendall(msg_str)
    return

def recv_msg(fd, msg_type):
    msg_str = fd.recv(MSG_LEN)
    msg = msg_type()
    msg.ParseFromString(msg_str[1:])
    return msg

def build_server(host, port):
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.bind((host, port))
    fd.listen(1)
    return fd

def build_client(host, port):
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.connect((host, port))
    return fd

def connect_world(world_fd):
    # ups send UConnect to world
    u_msg = world_ups_pb2.UConnect()
    u_msg.isAmazon = False
    for i in range(TRUCK_NUM):
        u_msg.trucks.add(id=i, x=i, y=i)
    send_msg(world_fd, u_msg)
    # ups receive UConnected from world
    w_msg = recv_msg(world_fd, world_ups_pb2.UConnected)
    world_id = w_msg.worldid
    result = w_msg.result
    if result != CONNECTED:
        print("error: {}".format(result))
    print("world id: {}".format(world_id))
    return world_id

def send_world_id(amazon_fd, world_id, seq, exp_seqs):
    u_msg = amazon_ups_pb2.U2AWorldId()
    u_msg.worldid = world_id
    u_msg.seqnum = seq
    send_msg(amazon_fd, u_msg)
    exp_seqs[seq] = [amazon_fd, u_msg, time.time()]
    return

def main():
    seq = 0
    ack_seqs = set()
    exp_seqs = {}

    world_fd = build_client(WORLD_HOST, WORLD_PORT)
    world_id = connect_world(world_fd)
    listen_fd = build_server(UPS_HOST, UPS_PORT)
    amazon_fd, _ = listen_fd.accept()
    send_world_id(amazon_fd, world_id, seq, exp_seqs)
    seq += 1
    return

if __name__ == "__main__":
    main()
