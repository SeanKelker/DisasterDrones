import socket, threading, time

mutex = threading.Lock()

f = open("message.txt", "r")
static_reply = ''.join(f.readlines())
f.close()

def listen_clients():
    global mutex
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',242*106))
    try:
        while True:
            data = s.recvfrom(1024)
            msg = data[0].decode('ascii')
            if msg == "Ping":
                reply = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                reply.sendto(
                    str.encode("~" + static_reply),
                    (data[1][0],242*106)
                )
                reply.close()
            else:
                print("hit:",msg)
                mutex.acquire()
                recv_data = open('data_file.dat','a+')
                recv_data.write(msg + "\n")
                recv_data.close()
                mutex.release()
    finally:
        s.close()

records_written = False

to_sent_to = None

def send_all_records():
    global records_written
    global to_sent_to
    recv_data = open('data_file.dat','r')
    
    data_dump = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    n_sent = 0

    for line in recv_data.readlines():
        print("sending,", line)
        try:
            sent = data_dump.sendto(
                b"~" + str.encode(line.strip()),
                (to_sent_to,(242*106)^(1337))
            )
            n_sent += 1
        except Exception as e:
            print("Send excpt:", e)
            break

    
    try:
        sent = data_dump.sendto(
            b"~term",
            (to_sent_to,(242*106)^(1337))
        )
    except Exception as ex:
        print("Pass terminated early without ~term sent")
    
    recv_data.close()
    data_dump.close()


    start_t = time.time()

    while not records_written:
        time.sleep(1)
        if start_t + 30 < time.time():
            print("No records were recv")
            break

    n_recv = 0

    try:
        new_dat = open('data_file_new.dat','r')
        old_dat = open('data_file.dat', 'a+')

        mutex.acquire()
        for line in new_dat:
            old_dat.write(line)
            n_recv += 1
        mutex.release()
        new_dat.close()
        old_dat.close()
    except IOError:
        print("no data recv")

    print("Pass complete\n{0} records sent, {1} records recv".format(n_sent, n_recv))
    

def listen_drones():
    global records_written
    global to_sent_to
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',(242*106)^(1337)))
    recv_data = None
    while True:
        try:
            data = s.recvfrom(1024)
            msg = data[0].decode('ascii')
            if msg == "Req Dump":
                print("Data request")
                records_written = False
                to_sent_to = data[1][0]
                sender = threading.Thread(target=send_all_records, args=(), kwargs={})
                sender.daemon = True
                sender.start()
            elif msg[0] == '~':
                print("Got dump:", msg)
                if msg == "~term":
                    records_written = True
                    recv_data.close()
                    recv_data = None
                    continue
                if recv_data is None:
                    recv_data = open('data_file_new.dat','w+')
                recv_data.write(msg + "\n")
        except Exception as e:
            s.close()

thr = threading.Thread(target=listen_drones, args=(), kwargs={})
thr.daemon = True
thr.start()
print("listening!")
listen_clients()