import requests
from scapy.all import ARP, Ether, srp
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Replace with your NodeMCU MAC address
TARGET_MAC = config["SPIDER-BOT"]["MAC_ADDRESS"].lower()
SUBNET = config["SPIDER-BOT"]["SUBNET"]

def get_ip_from_mac(mac, subnet=SUBNET):
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=2, verbose=0)[0]
    for sent, received in result:
        if received.hwsrc.lower() == mac:
            return received.psrc
    return None

def esp_walk(steps: int):
    """Makes the spider bot walk"""
    ip = get_ip_from_mac(TARGET_MAC)
    
    if ip == None:
        return "Command failed. Retry again."
    else:
        url = f"http://{ip}/walk"
        resp = requests.get(url, timeout=10, params={"steps": steps})
        return resp.text