from ups import *
import world_ups_pb2
from constant import *
from mock_amazon import recv_ack

def test_completion(ups_fd):
    w_msg =  world_ups_pb2.UResponses()
    w_msg.completions.add(truckid=2, x=3, y=4, status=ARRIVE_WAREHOUSE, seqnum=40)
    send_msg(ups_fd, w_msg)
    return


def main():
    listen_fd = build_server(WORLD_HOST, WORLD_PORT)
    ups_fd, _ = listen_fd.accept()
    test_completion(ups_fd)
    recv_ack(ups_fd)
    while True:
        pass
    return


if __name__ == "__main__":
    main()