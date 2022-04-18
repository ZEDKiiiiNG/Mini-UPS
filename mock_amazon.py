from constant import *
import ups
import amazon_ups_pb2


def test_send_world_id():
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    for w in u_msg.worldid:
        world_id = w.worldid
        seq = w.seqnum
        print("world id: {}".format(world_id))
        print("seq: {}".format(seq))
    return


if __name__ == "__main__":
    test_send_world_id()
