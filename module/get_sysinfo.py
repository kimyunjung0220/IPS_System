from scapy.all import get_if_list

#get NIC interface
def get_interface() -> str:
    interfaces = get_if_list()
    for interface in interfaces:
        if interface.startswith('eth') or interface.startswith('ens'):
            return interface