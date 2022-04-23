import socket
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
from constant import *
import amazon_ups_pb2
import time
import select
# import modelsInterface as db
from multiprocessing import Process
 

def send_msg(fd, msg):
    print("send msg {}".format(msg))
    msg_str = msg.SerializeToString()
    _EncodeVarint(fd.sendall, len(msg_str), None)
    fd.sendall(msg_str)
    return


def send_msg_with_seq(fd, msg, curr_seq, exp_seqs):
    print("send msg {}".format(msg))
    send_msg(fd, msg)
    exp_seqs[curr_seq[0]] = [fd, msg, time.time()]
    curr_seq[0] += 1
    return


def recv_stream_msg(fd, msg_type):
    buf = fd.recv(MSG_LEN)
    ans = []
    n = 0
    while n < len(buf):
        msg_len, new_pos = _DecodeVarint32(buf, n)
        n = new_pos
        msg_buf = buf[n:n+msg_len]
        n += msg_len
        msg = msg_type()
        msg.ParseFromString(msg_buf)
        ans.append(msg)
    return ans


def recv_msg(fd, msg_type):
    buffer = []
    while True:
        print("buffer: {}".format(buffer))
        temp = fd.recv(1)
        if not temp:
            return temp
        buffer += temp
        msg_len, pos = _DecodeVarint32(buffer, 0)
        if pos != 0:
            break
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
        truck_id, x, y = i, i, i
        u_msg.trucks.add(id=truck_id, x=x, y=y)
        # db.createTruck(truck_id, x, y, IDLE)
    send_msg(world_fd, u_msg)
    # ups receive UConnected from world
    w_msg = recv_msg(world_fd, world_ups_pb2.UConnected)
    world_id = w_msg.worldid
    result = w_msg.result
    if result != CONNECTED:
        print("error: {}".format(result))
    print("world id: {}".format(world_id))
    return world_id


def send_world_id(amazon_fd, world_id, curr_seq, exp_seqs):
    u_msg = amazon_ups_pb2.UMsg()
    u_msg.worldid.add(worldid=world_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


def send_ack(fd, seq, msg_type):
    print("seq: {}".format(seq))
    msg = msg_type()
    msg.acks.append(seq)
    send_msg(fd, msg)
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


# AMAZON CASE 1
def handle_truck_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg):
    for truck_req in a_msg.truckreq:
        seq = truck_req.seqnum
        send_ack(amazon_fd, seq, amazon_ups_pb2.UMsg)
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            # truck_id = get_pickup_truck()
            truck_id = 0
            whid = truck_req.wh.id
            package_id = truck_req.packageid
            # db.savePackage(truck_id, truck_req)
            # db.updateTruckstatus(truck_id, TRAVELING)
            send_pickup(world_fd, curr_seq, exp_seqs, truck_id, whid)
            send_truck_sent(amazon_fd, curr_seq, exp_seqs, truck_id, package_id)
    return


# def get_pickup_truck():
#     truck_id = -1
#     while truck_id == -1:
#         truck_id = db.getPickupTruck()
#         time.sleep(RETRY_INTERVAL)
#     return truck_id


def send_pickup(world_fd, curr_seq, exp_seqs, truck_id, whid):
    u_msg = world_ups_pb2.UCommands()
    u_msg.pickups.add(truckid=truck_id, whid=whid, seqnum=curr_seq[0])
    send_msg_with_seq(world_fd, u_msg, curr_seq, exp_seqs)
    return


def send_truck_sent(amazon_fd, curr_seq, exp_seqs, truck_id, package_id):
    u_msg = amazon_ups_pb2.UMsg()
    u_msg.trucksent.add(truckid=truck_id, packageid=package_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


# AMAZON CASE 2
def handle_deliver_req(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, a_msg):
    for deliver_req in a_msg.deliverreq:
        seq = deliver_req.seqnum
        send_ack(amazon_fd, seq, amazon_ups_pb2.UMsg)
        package_id = deliver_req.packageid
        truck_id = deliver_req.truckid
        dest_x = deliver_req.dest_x
        dest_y = deliver_req.dest_y
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            # dest_x, dest_y = get_dest(dest_x, dest_y, package_id)
            # db.updatePackagestatus(package_id, OUT_FOR_DELIVERY)
            send_deliver(world_fd, curr_seq, exp_seqs, truck_id, package_id, dest_x, dest_y)
    return


def send_deliver(world_fd, curr_seq, exp_seqs, truck_id, package_id, dest_x, dest_y):
    u_msg = world_ups_pb2.UCommands()
    deliver = u_msg.deliveries.add(truckid=truck_id, seqnum=curr_seq[0])
    deliver.packages.add(packageid=package_id, x=dest_x, y=dest_y)
    send_msg_with_seq(world_fd, u_msg, curr_seq, exp_seqs)
    return


def get_dest(dest_x, dest_y, package_id):
    new_dest_x, new_dest_y = db.getDest(package_id)
    if new_dest_x == -1 or new_dest_y == -1:
        return dest_x, dest_y
    return new_dest_x, new_dest_y


# WORLD CASE 1
def handle_completion(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, w_msg):
    for completion in w_msg.completions:
        seq = completion.seqnum
        send_ack(world_fd, seq, world_ups_pb2.UCommands)
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            truck_id = completion.truckid
            x = completion.x
            y = completion.y
            status = completion.status
            # db.updateTruckstatus(truck_id, status)
            if status == ARRIVE_WAREHOUSE:
                # package_id = db.updatePackagestatusAccordingTruck(truck_id, x, y)[0]
                package_id = 2
                print("package id : {} arrived".format(package_id))
                send_truck_arrived(amazon_fd, curr_seq, exp_seqs, truck_id, package_id)
    return


def send_truck_arrived(amazon_fd, curr_seq, exp_seqs, truck_id, package_id):
    u_msg = amazon_ups_pb2.UMsg()
    #for package_id in package_ids:
    u_msg.truckarrived.add(truckid=truck_id, packageid=package_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


# WORLD CASE 2
def handle_delivered(world_fd, amazon_fd, curr_seq, exp_seqs, ack_seqs, w_msg):
    for delivered in w_msg.delivered:
        seq = delivered.seqnum
        send_ack(world_fd, seq, world_ups_pb2.UCommands)
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            package_id = delivered.packageid
            # db.updatePackagestatus(package_id, DELIVERED)
            send_deliver_resp(amazon_fd, curr_seq, exp_seqs, package_id)
    return


def send_deliver_resp(amazon_fd, curr_seq, exp_seqs, package_id):
    u_msg = amazon_ups_pb2.UMsg()
    u_msg.delivered.add(packageid=package_id, seqnum=curr_seq[0])
    send_msg_with_seq(amazon_fd, u_msg, curr_seq, exp_seqs)
    return


# WORLD CASE 3
def handle_finish(world_fd, w_finish_msg, world_id):
    if w_finish_msg.HasField("finished") and w_finish_msg.finished:
        print("handle finish, {}".format(w_finish_msg))
        time.sleep(2)
        send_reconnect(world_fd, world_id)
        time.sleep(2)
        w_conn_msg = recv_msg(world_fd, world_ups_pb2.UConnected)
        print("reconnect msg: {}".format(w_conn_msg))
        world_id = w_conn_msg.worldid
        result = w_conn_msg.result
        if result != CONNECTED:
            print("error: {}".format(result))
        print("reconnect to world id: {}".format(world_id))
    return


def send_reconnect(world_fd, world_id):
    u_msg = world_ups_pb2.UConnect()
    u_msg.worldid = world_id
    u_msg.isAmazon = False
    send_msg(world_fd, u_msg)
    return


# COMMON CASE 1
def handle_acks(msg, exp_seqs):
    for ack in msg.acks:
        print("ack: {}".format(ack))
        if ack in exp_seqs:
            exp_seqs.pop(ack)
    return


# COMMON CASE 2
def handle_error(fd, ack_seqs, msg, msg_type):
    for error in msg.error:
        err_msg = error.err
        origin_seq = error.originseqnum
        seq = error.seqnum
        send_ack(fd, seq, msg_type)
        if seq not in ack_seqs:
            ack_seqs.add(seq)
            print("origin seq: {}".format(origin_seq))
            print("{}".format(err_msg))
    return


def run_service(amazon_fd, curr_seq, exp_seqs, amazon_ack_seqs, world_ack_seqs):
    world_fd = build_client(WORLD_HOST, WORLD_PORT)
    world_id = connect_world(world_fd)
    send_world_id(amazon_fd, world_id, curr_seq, exp_seqs)
    while True:
        ready_fds, _, _ = select.select([world_fd, amazon_fd], [], [], 0)
        if amazon_fd in ready_fds:
            a_msg = recv_msg(amazon_fd, amazon_ups_pb2.AMsg)
            if not a_msg:  # amazon close connection
                print("amazon close connection")
                return
            print("receive a_msg: {}".format(a_msg))
            handle_truck_req(world_fd, amazon_fd, curr_seq, exp_seqs, amazon_ack_seqs, a_msg)
            handle_deliver_req(world_fd, amazon_fd, curr_seq, exp_seqs, amazon_ack_seqs, a_msg)
            handle_acks(a_msg, exp_seqs)
            handle_error(amazon_fd, amazon_ack_seqs, a_msg, amazon_ups_pb2.UMsg)
        if world_fd in ready_fds:
            w_msgs = recv_stream_msg(world_fd, world_ups_pb2.UResponses)
            for w_msg in w_msgs:
                print("receive w_msg: {}".format(w_msg))
                handle_completion(world_fd, amazon_fd, curr_seq, exp_seqs, world_ack_seqs, w_msg)
                handle_delivered(world_fd, amazon_fd, curr_seq, exp_seqs, world_ack_seqs, w_msg)
                handle_acks(w_msg, exp_seqs)
                handle_error(world_fd, world_ack_seqs, w_msg, world_ups_pb2.UCommands)
                handle_finish(world_fd, w_msg, world_id)
        handle_resend(exp_seqs)
    return


def main():
    print("ups running..")
    curr_seq = [0]
    amazon_ack_seqs = set()
    world_ack_seqs = set()
    exp_seqs = {}
    listen_fd = build_server(UPS_HOST, UPS_PORT)
    while True:
        amazon_fd, _ = listen_fd.accept()
        Process(target=run_service, args=(amazon_fd, curr_seq, exp_seqs, amazon_ack_seqs, world_ack_seqs)).start()
    return


if __name__ == "__main__":
    main()
