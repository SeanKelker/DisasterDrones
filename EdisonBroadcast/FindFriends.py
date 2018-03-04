import os
from sys import stdout
import sys
import time
import re
import subprocess

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

def configure_network(ssid, network):
    if network["sec"] == "OPEN":
        return '''
network={{
  ssid="{0}"
  {1}
  key_mgmt=NONE
}}
'''.format(ssid, "")

    elif network["sec"] == "WEP":
        return '''
network={{
  ssid="{0}"
  {1}
  key_mgmt=NONE
  group=WEP104 WEP40
  wep_key0="{2}"
}}
'''.format(ssid, "", network["password"])

    elif network["sec"] == "WPA-PSK":
        return '''
network={{
  ssid="{0}"
  {1}
  key_mgmt=WPA-PSK
  pairwise=CCMP TKIP
  group=CCMP TKIP WEP104 WEP40
  eap=TTLS PEAP TLS
  psk="{2}"
}}
'''.format(ssid, "", network["password"])

    elif network["sec"] == "WPA-EAP":
        return '''
network={{
  ssid="{0}"
  {1}
  key_mgmt=WPA-EAP
  pairwise=CCMP TKIP
  group=CCMP TKIP WEP104 WEP40
  eap=TTLS PEAP TLS
  identity="{2}"
  password="{3}"
  phase1="peaplabel=0"
}}
'''.format(ssid, "", network["user"], network["password"])

def connect_wifi(ssid, network):
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
    wpa_supplicant.write(configure_network(ssid, network))
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

    pipe = os.popen("ifconfig | grep -A1 'wlan0' | grep 'inet'| awk -F' ' '{ print $2 }' | awk -F':' '{ print $2 }'")
    addr = pipe.read().rstrip()
    pipe.close()
    return addr

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
                    conf["security"] = "OPEN"
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

# n = sys.argv[1]
# sec = sys.argv[3]
# passwd = sys.argv[2]

print(get_current_config())

# while True:
#     networks = list_networks()
#     if


# new_address = connect_wifi(n, networks[n])
# print("Selected new network")
# print(new_address)