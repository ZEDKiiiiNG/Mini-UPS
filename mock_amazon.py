from constant import *
import ups
import amazon_ups_pb2


def main():
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    u_msg = ups.recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    world_id = u_msg.worldid
    seq = u_msg.seqnum
    print("world id: {}".format(world_id))
    print("seq: {}".format(seq))
    return


if __name__ == "__main__":
    main()
