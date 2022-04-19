import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
from constant import *
import amazon_ups_pb2
import time
import select
 

def send_msg(fd, msg):
    msg_str = msg.SerializeToString()
    _EncodeVarint(fd.sendall, len(msg_str), None)
    fd.sendall(msg_str)
    return


def send_msg_with_seq(fd, msg, curr_seq, exp_seqs):
    send_msg(fd, msg)
    exp_seqs[curr_seq[0]] = [fd, msg, time.time()]
    curr_seq[0] += 1
    return


def recv_msg(fd, msg_type):
    temp = fd.recv(1)
    if not temp:
        return temp
    msg_len, _ = _DecodeVarint32(temp, 0)
    msg = msg_type()
    msg_str = fd.recv(msg_len)
    msg.ParseFromString(msg_str)
    return msg


def build_server(host, port):
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.bind((host, port))
    fd.listen(1)
    return fd


def build_client(host, port):
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd.connect((host, port))
    return fd


def connect_world(world_fd):
    # ups send UConnect to world
    u_msg = world_ups_pb2.UConnect()
    u_msg.isAmazon = False
    for i in range(TRUCK_NUM):
        u_msg.trucks.add(id=i, x=i, y=i)
    send_msg(world_fd, u_msg)
    # ups receive UConnected from world
    w_msg = recv_msg(world_fd, world_ups_pb2.UConnected)
    world_id = w_msg.worldid
    result = w_msg.result
    if result != CONNECTED:
        print("error: {}".format(result))
    print("world id: {}".format(world_id))
    return world_id


def send_pickup(world_fd, curr_seq, exp_seqs, truck_id, whid):
    u_msg = world_ups_pb2.UCommands()
    u_msg.pickups.add(truckid=truck_id, whid=whid, seqnum=curr_seq[0])
    send_msg_with_seq(world_fd, u_msg, curr_seq, exp_seqs)
    return


def send_deliver(world_fd, curr_seq, exp_seqs, truck_id, package_id, dest_x, dest_y):
    u_msg = world_ups_pb2.UCommands()
    deliver = u_msg.deliveries.add(truckid=truck_id, seqnum=curr_seq[0])
    deliver.packages.add(packageid=package_id, x=dest_x, y=dest_y)
    send_msg_with_seq(world_fd, u_msg, curr_seq, exp_seqs)
    return


def send_world_id(amazon_fd, world_id, curr_seq, exp_seqs):
    u_msg = amazon_ups_pb2.UMsg()
    u_msg.worldid.add(worldid=world_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


def send_truck_sent(amazon_fd, curr_seq, exp_seqs, truck_id, package_id):
    u_msg = amazon_ups_pb2.UMsg()
    u_msg.trucksent.add(truckid=truck_id, packageid=package_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


def handle_acks(msg, exp_seqs):
    for ack in msg.acks:
        print("ack: {}".format(ack))
        if ack in exp_seqs:
            exp_seqs.pop(ack)
    return


def handle_resend(exp_seqs):
    for seq in exp_seqs:
        fd, msg, time_sent = exp_seqs[seq]
        curr_time = time.time()
        if curr_time - time_sent >= RETRY_INTERVAL:
            print("resend msg: {}".format(seq))
            send_msg(fd, msg)
            exp_seqs[seq] = [fd, msg, curr_time]
    return


def handle_truck_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg):
    for truck_req in a_msg.truckreq:
        whid = truck_req.wh.id
        package_id = truck_req.packageid
        seq = truck_req.seqnum
        send_ack(amazon_fd, seq, amazon_ups_pb2.UMsg)
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            # TODO db.save_package()
            # TODO truck_id = db.get_pickup_truck()
            truck_id = 2
            send_pickup(world_fd, curr_seq, exp_seqs, truck_id, whid)
            send_truck_sent(amazon_fd, curr_seq, exp_seqs, truck_id, package_id)
    return


def send_ack(fd, seq, msg_type):
    print("seq: {}".format(seq))
    msg = msg_type()
    msg.acks.append(seq)
    send_msg(fd, msg)
    return


def handle_deliver_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg):
    for deliver_req in a_msg.deliverreq:
        package_id = deliver_req.packageid
        truck_id = deliver_req.truckid
        dest_x = deliver_req.dest_x
        dest_y = deliver_req.dest_y
        seq = deliver_req.seqnum
        print("{},{},{},{},{}", package_id, truck_id, dest_x, dest_y, seq)
        # TODO db.getDest()
        # send_ack(amazon_fd, seq, amazon_ups_pb2.UMsg)
    return


def run_service(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs):
    while True:
        ready_fds, _, _ = select.select([world_fd, amazon_fd], [], [], 0)
        if amazon_fd in ready_fds:
            a_msg = recv_msg(amazon_fd, amazon_ups_pb2.AMsg)
            if not a_msg:  # receive empty msg if amazon close connection
                continue
            handle_acks(a_msg, exp_seqs)
            handle_truck_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg)
            # handle_deliver_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg)
        handle_resend(exp_seqs)
    return


def main():
    print("ups running..")
    curr_seq = [0]
    ack_seqs = set()
    exp_seqs = {}

    listen_fd = build_server(UPS_HOST, UPS_PORT)
    amazon_fd, _ = listen_fd.accept()
    # TODO open thread to serve each amazon
    world_fd = build_client(WORLD_HOST, WORLD_PORT)
    world_id = connect_world(world_fd)

    send_world_id(amazon_fd, world_id, curr_seq, exp_seqs)
    run_service(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs)
    return


if __name__ == "__main__":
    main()
