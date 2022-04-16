import socket
import world_ups_pb2

HOST = "vcm-24667.vm.duke.edu"
PORT = 12345

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as world_fd:
        world_fd.connect((HOST, PORT))

        u_connect = world_ups_pb2.UConnect()
        # add one truck
        u_init_truck = u_connect.trucks.add()
        u_init_truck.id = 1
        u_init_truck.x = 2
        u_init_truck.y = 3
        u_connect.isAmazon = False

        world_fd.sendall(u_connect.SerializeToString())
        u_connected = world_ups_pb2.UConnected()
        msg = world_fd.recv(1024)
        u_connected.ParseFromString(msg)
        print("world id: {}".format(u_connected.worldid))
        print("result: {}".format(u_connected.result))
