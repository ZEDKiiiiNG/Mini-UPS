from constant import *
from ups import *
import amazon_ups_pb2
import time


def test_resend(ups_fd):
    count = 10
    for i in range(count):
        u_msg = recv_msg(ups_fd, amazon_ups_pb2.UMsg)
        print(i)
        print(u_msg)
    return


def test_send_world_id(ups_fd):
    u_msg = recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    for w in u_msg.worldid:
        seq = w.seqnum
        send_ack(ups_fd, seq, amazon_ups_pb2.AMsg)
    return


def test_truck_req(ups_fd):
    # amazon send truck_req and recv ack from ups
    a_msg = amazon_ups_pb2.AMsg()
    truck_req = a_msg.truckreq.add(upsaccount="test_user", packageid=2, seqnum=20)
    # only have add() for repeated field
    truck_req.wh.id = 6
    truck_req.wh.x = 7
    truck_req.wh.y = 8
    truck_req.things.add(id=4, description="banana", count=5)
    send_msg(ups_fd, a_msg)
    recv_ack(ups_fd)

    # amazon recv truck_sent and send ack to ups
    u_msg2 = recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    print(u_msg2)
    for truck_sent in u_msg2.trucksent:
        seq = truck_sent.seqnum
        send_ack(ups_fd, seq, amazon_ups_pb2.AMsg)
    return


def test_deliver_req(ups_fd):
    # amazon send deliver_req and recv ack from ups
    a_msg = amazon_ups_pb2.AMsg()
    a_msg.deliverreq.add(packageid=2, truckid=2, dest_x=5, dest_y=8, seqnum=21)
    send_msg(ups_fd, a_msg)
    recv_ack(ups_fd)
    return


def recv_ack(ups_fd):
    u_msg = recv_msg(ups_fd, amazon_ups_pb2.UMsg)
    for ack in u_msg.acks:
        print("ack: {}".format(ack))
    return


def main():
    ups_fd = build_client(UPS_HOST, UPS_PORT)
    # test_resend(ups_fd)
    test_send_world_id(ups_fd)
    test_truck_req(ups_fd)
    # test_deliver_req(ups_fd)
    while True:
        pass
    return


if __name__ == "__main__":
    main()
