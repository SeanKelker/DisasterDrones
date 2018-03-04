import os
from sys import stdout
import sys
import time
import re
import subprocess
import socket
import threading
import select

STATE_DIR = '/var/lib/edison_config_tools'

def list_networks():
    os.popen("systemctl stop hostapd").close()
    time.sleep(2)
    os.popen("systemctl start wpa_supplicant").close()
    print("Stoped hostapd and started wpa supplicant")
    time.sleep(5)
    os.popen("wpa_cli scan").close()
    time.sleep(5)
    pipe = os.popen("wpa_cli scan_results")
    found = [l.split("\t") for l in pipe.read().split("\n")]
    pipe.close()
    networks = {}

    found_open = []

    WPAPSK_REGEX=re.compile(r'\[WPA[2]?-PSK-.+\]')
    WPAEAP_REGEX=re.compile(r'\[WPA[2]?-EAP-.+\]')
    WEP_REGEX=re.compile(r'\[WEP.*\]')

    for n in found:
        if (len(n) == 5):
            ssid = n[-1]
        else:
            continue
        if ssid not in networks and not ssid == "" and "\\x00" not in ssid:
            flags = n[-2]
            networks[ssid] = {
                'mac': n[0]
            }
            if WPAPSK_REGEX.search(flags):
                networks[ssid]["sec"] = "WPA-PSK"
            elif WPAEAP_REGEX.search(flags):
                networks[ssid]["sec"] = "WPA-EAP"
            elif WEP_REGEX.search(flags):
                networks[ssid]["sec"] = "WEP"
            else:
                networks[ssid]["sec"] = "OPEN"
    
    return networks

def connect_wifi(ssid):
    if not os.path.isfile('/etc/wpa_supplicant/wpa_supplicant.conf.original'):
        subprocess.call("cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.original", shell=True)

    wpa_supplicant = open('/etc/wpa_supplicant/wpa_supplicant.conf','w') #Will not take care of duplicates at the moment.
    header = """
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
config_methods=virtual_push_button virtual_display push_button keypad
update_config=1
fast_reauth=1
device_name=Edison
manufacturer=Intel
model_name=Edison
"""
    wpa_supplicant.write(header)
    wpa_supplicant.write('''
network={{
  ssid="{0}"
  {1}
  key_mgmt=NONE
}}
'''.format(ssid, ""))
    wpa_supplicant.close()

    print("Updated supplicant file")

    try:
        if int(subprocess.check_output("systemctl status wpa_supplicant | grep 'active (running)' | wc -l", shell=True)) == 0:
            subprocess.call("systemctl stop hostapd &> /dev/null", shell=True)
            subprocess.call("systemctl start wpa_supplicant &> /dev/null", shell=True)
            time.sleep(10)
        else:
            subprocess.call("wpa_cli reconfigure &> /dev/null && sleep 2", shell=True)

        print("Completed reconfigure")

        network_count = int(subprocess.check_output('wpa_cli list_networks | wc -l', shell=True))
        subprocess.call("wpa_cli select_network " + str(network_count - 2 - 1) + " &> /dev/null", shell=True)
        time.sleep(5)

        print("Selected")

        ifarray = subprocess.check_output("wpa_cli ifname", shell=True).split()
        subprocess.call("udhcpc -i " + str(ifarray[len(ifarray)-1]) + " -n &> /dev/null", shell=True)
    except Exception as e:
        print(e)
        print("Sorry. Could not get an IP address.")

    time.sleep(1)

    pipe = os.popen("iwgetid -r")
    ssid = pipe.read().rstrip()
    pipe.close()
    return ssid

def get_current_config():
    pipe = os.popen("iwgetid -r")
    ssid = pipe.read().rstrip()
    pipe.close()

    conf = {}
    cssid = None

    line = ""

    wpa_supplicant = open('/etc/wpa_supplicant/wpa_supplicant.conf','r')
    line = wpa_supplicant.readline()
    while line != "":
        if "network" in line and "{" in line:
            while "}" not in line:
                if "ssid" in line:
                    bits = line.split('"')
                    cssid = bits[1]
                if "wep_key0" in line or "psk" in line or "password" in line:
                    bits = line.split('"')
                    conf["password"] = bits[1]
                    if "wep_key0" in line:
                        conf["sec"] = "WEP"
                    elif "psk" in line:
                        conf["sec"] = "WPA-PSK"
                    elif "password" in line:
                        conf["sec"] = "WPA-EAP"
                elif "identity" in line:
                    bits = line.split('"')
                    conf["user"] = bits[1]
                line = wpa_supplicant.readline()
            if cssid == ssid:
                if "password" not in conf:
                    conf["sec"] = "OPEN"
                conf["ssid"] = ssid
                wpa_supplicant.close()
                return conf
        line = wpa_supplicant.readline()
    wpa_supplicant.close()
    return None

# hack4humanity OPEN
# NiceMeme.jpg WPA-PSK datboi12345!!
# dd-wrt WPA-PSK c242wifi
# c242-router-1

n = sys.argv[1]

if len(sys.argv) > 2:
    new_address = connect_wifi(n)
    print("addr:", new_address)
    sys.exit(0)
    
# sec = sys.argv[3]
# passwd = sys.argv[2]

old_network = get_current_config()

networks = {}

while n not in networks:
    networks = list_networks()

if networks[n]["sec"] != "OPEN":
    print("Only open wifi networks can be hot swapped")
    sys.exit(1)

print("network found, swapping")
new_address = connect_wifi(n)
print("Networks swapped, data will be pushed")
print("new ssid:", new_address)

n_sent = 0
n_recv = 0

pass_other = None

def listen_for_pass():
    global n_recv
    global pass_other
    passing = True
    com = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    com.bind(('',(242*106)^(1337)))
    com.settimeout(10)
    with open('data_file_new.dat','w+') as recv_data:
        while passing:
            try:
                data = com.recvfrom(1024)
                if pass_other is None:
                    pass_other = data[1][0]
                msg = data[0].decode('ascii')
                if msg[0] != "~":
                    continue
                if msg == "~term":
                    print("Thats a term, terming")
                    passing = False
                    break

                recv_data.write(msg + '\n')

                n_recv += 1
            except Exception as e:
                passing = False
                break
                print("Listen timed out")
    print("Listen done")
    com.close()

broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

broadcast.sendto(
    b"Req Dump",
    ('255.255.255.255',(242*106)^(1337))
)

thr = threading.Thread(target=listen_for_pass, args=(), kwargs={})
thr.daemon = True
thr.start()

recv_data = None

start_t = time.time()

while pass_other is None:
    time.sleep(1)
    if start_t + 30 < time.time():
        break

print("Spin lock exiting")

try:
    recv_data = open('data_file.dat','r')

    for line in recv_data.readlines():
        try:
            sent = broadcast.sendto(
                b"~" + str.encode(line.strip()),
                (pass_other,(242*106)^(1337))
            )
            n_sent += 1
        finally:
            try:
                sent = broadcast.sendto(
                    b"~term",
                    (pass_other,(242*106)^(1337))
                )
            except Exception as ex:
                print("Pass terminated early without ~term sent")
            break
except Exception:
    print("data_file.dat not found, not data will be sent")
finally:
    if pass_other is not None:
        sent = broadcast.sendto(
            b"~term",
            (pass_other,(242*106)^(1337))
        )
    pass_other = None
    if recv_data is not None:
        recv_data.close()

broadcast.close()

thr.join()

new_dat = open('data_file_new.dat','r+')
old_dat = open('data_file.dat', 'a+')

for line in new_dat:
    old_dat.write(line)

new_dat.close()
old_dat.close()

print("Pass complete\n{0} records sent, {1} records recv".format(n_sent, n_recv))
print(old_network)
new_address = connect_wifi(old_network["ssid"])
print("returned ssid:", new_address)