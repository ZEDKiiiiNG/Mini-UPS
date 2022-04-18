from constant import *
import ups
import amazon_ups_pb2
import time


def test_send_world_id(ups_fd):
    count = 10
    for _ in range(count):
        u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
        print(count)
        print(u_msg)
    return


if __name__ == "__main__":
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    test_send_world_id(ups_fd)
