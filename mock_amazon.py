from constant import *
import ups
import amazon_ups_pb2
import time


def test_send_world_id_resend(ups_fd):
    count = 10
    for i in range(count):
        u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
        print(i)
        print(u_msg)
    return

def test_send_world_id(ups_fd):
    u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    for w in u_msg.worldid:
        seq = w.seqnum
        print("seq: {}".format(seq))
        a_msg = amazon_ups_pb2.AMsg()
        a_msg.acks.append(seq)
        ups.send_msg(ups_fd, a_msg)
    return

if __name__ == "__main__":
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    test_send_world_id_resend(ups_fd)
    # test_send_world_id(ups_fd)
