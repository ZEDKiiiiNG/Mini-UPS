from constant import *
import ups
import amazon_ups_pb2
import time


def test_resend(ups_fd):
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
        ups.send_ack(ups_fd, seq, amazon_ups_pb2.AMsg)
    return

def test_truck_req(ups_fd):
    a_msg = amazon_ups_pb2.AMsg()
    truck_req = a_msg.truckreq.add(upsaccount="test_user", packageid=2, seqnum=3)
    # only have add() for repeated field
    truck_req.wh.id = 6
    truck_req.wh.x = 7
    truck_req.wh.y = 8
    truck_req.things.add(id=4, description="banana", count=5)
    ups.send_msg(ups_fd, a_msg)
    return


if __name__ == "__main__":
    ups_fd = ups.build_client(UPS_HOST, UPS_PORT)
    # test_resend(ups_fd)
    test_send_world_id(ups_fd)
    test_truck_req(ups_fd)
