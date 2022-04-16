import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint

HOST = "vcm-24846.vm.duke.edu"
PORT = 23456
MSG_LEN = 1024

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as world_fd:
        world_fd.connect((HOST, PORT))

        u_connect = world_ups_pb2.UConnect()
        u_connect.isAmazon = False
        u_connect.trucks.add(id=1,x=1,y=1) # add one truck
        u_connect_msg = u_connect.SerializeToString()
        _EncodeVarint(world_fd.sendall, len(u_connect_msg), None)
        world_fd.sendall(u_connect_msg)

        msg = world_fd.recv(MSG_LEN)
        u_connected = world_ups_pb2.UConnected()
        u_connected.ParseFromString(msg[1:])  # first byte is length
        print("world id: {}".format(u_connected.worldid))
        print("result: {}".format(u_connected.result))
