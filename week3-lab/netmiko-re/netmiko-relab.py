# netmiko-re.py (Final Corrected Version)

import re
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

LEGACY_ARGS = {
    'disabled_algorithms': dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"]),
}

R1 = {
    'device_type': 'cisco_ios',
    'host': '172.31.147.4',
    'username': 'admin',
    'use_keys': True,
    'key_file': os.path.expanduser('~/.ssh/admin_openssh'),
    **LEGACY_ARGS
}

R2 = {
    'device_type': 'cisco_ios',
    'host': '172.31.147.5',
    'username': 'admin',
    'use_keys': True,
    'key_file': os.path.expanduser('~/.ssh/admin_openssh'),
    **LEGACY_ARGS
}

devices = {'R1': R1, 'R2': R2}


def get_active_interfaces(device_name, device_config):
    """
    Connects to a device, gets interface status, and prints active interfaces
    and their "last input" time as a proxy for uptime.
    """
    print(f"--- Attempting to connect to {device_name} ({device_config['host']}) ---")
    try:
        with ConnectHandler(**device_config) as net_connect:
            print(f"[SUCCESS] Connected to {device_name}.")
            output = net_connect.send_command('show interfaces', use_textfsm=False)

            interface_blocks = re.split(r'\n(?=\S)', output)

            print(f"\nActive Interfaces on {device_name}:")
            found_active_interface = False

            for block in interface_blocks:
                if "is up, line protocol is up" in block:
                    found_active_interface = True
                    
                    interface_name_match = re.search(r'^(\S+)', block)
        
                    last_activity_match = re.search(r'Last input (.+?),', block)

                    if interface_name_match:
                        interface_name = interface_name_match.group(1)

                        if last_activity_match:
                            last_activity = last_activity_match.group(1).strip()
                            print(f"  - Interface: {interface_name:<20} | Last Input: {last_activity}")
                        else:

                            print(f"  - Interface: {interface_name:<20} | Last Input: (no traffic received)")

            if not found_active_interface:
                print("  (No active interfaces found in the output)")

    except (NetmikoTimeoutException, ConnectionRefusedError):
        print(f"[FAILURE] Connection to {device_name} timed out or was refused.")
    except NetmikoAuthenticationException:
        print(f"[FAILURE] Authentication failed for {device_name}.")
    except Exception as e:
        print(f"[FAILURE] An unexpected error occurred with {device_name}: {e}")
    finally:
        print("-" * 50 + "\n")


if __name__ == "__main__":
    for name, config in devices.items():
        get_active_interfaces(name, config)