import socket
import world_ups_pb2
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

HOST = "vcm-24846.vm.duke.edu"
PORT = 23456

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as world_fd:
        world_fd.connect((HOST, PORT))

        u_connect = world_ups_pb2.UConnect()
        u_connect.isAmazon = False
        u_connect.trucks.add(id=1,x=1,y=1) # add one truck
        u_connect_str = u_connect.SerializeToString()
        _EncodeVarint(world_fd.sendall, len(u_connect_str), None)
        world_fd.sendall(u_connect_str)

        var_int_buff = []
        while True:
            buf = world_fd.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        whole_message_str = world_fd.recv(msg_len)

        # msg = world_fd.recv(1024)
        # print(len(msg))
        # msg_len, new_pos = _DecodeVarint32(msg, 0)
        # print("here {}, {}".format(msg_len, new_pos))
        # msg = msg[:msg_len]


        u_connected = world_ups_pb2.UConnected()
        u_connected.ParseFromString(whole_message_str)
        print("world id: {}".format(u_connected.worldid))
        print("result: {}".format(u_connected.result))
