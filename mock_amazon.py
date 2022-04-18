from constant import *
import ups
import amazon_ups_pb2


def test_send_world_id(ups_fd):
    u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    print(u_msg)
    # does not reply ack
    u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    print(u_msg)
    return


if __name__ == "__main__":
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    test_send_world_id(ups_fd)
