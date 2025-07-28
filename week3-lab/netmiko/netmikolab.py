from netmiko import ConnectHandler
import os

private_key_path = os.path.expanduser('~/.ssh/admin_openssh')

legacy_crypto_settings = {
    'use_keys': True,
    'key_file': private_key_path,
    'disabled_algorithms': dict(pubkeys=['rsa-sha2-512', 'rsa-sha2-256']),
}

s1 = {
    "device_type": "cisco_ios",
    "host": "172.31.147.3",
    "username": "admin",
    **legacy_crypto_settings,
}

r1 = {
    "device_type": "cisco_ios",
    "host": "172.31.147.4",
    "username": "admin",
    **legacy_crypto_settings,
}

r2 = {
    "device_type": "cisco_ios",
    "host": "172.31.147.5",
    "username": "admin",
    **legacy_crypto_settings,
}


vty_acl_config = [
    'ip access-list standard VTY_ACCESS',
    'remark --- Allow SSH/Telnet from Management Network ---',
    'permit 172.31.147.0 0.0.0.15',
    'remark --- Allow SSH/Telnet from Lab306 Network ---',
    'permit 10.30.6.0 0.0.0.255',
    'deny any log',
    'line vty 0 15',
    'access-class VTY_ACCESS in',
    'transport input ssh telnet',
    'login local',
]

s1_config = [
    'vlan 101',
    'name Control-Data',
    'interface Gi0/1',
    'description --- Link to R2 ---',
    'switchport mode access',
    'switchport access vlan 101',
    'spanning-tree portfast',
    'interface Gi1/1',
    'description --- Link to UbuntuCloudGuest ---',
    'switchport mode access',
    'switchport access vlan 101',
    'spanning-tree portfast',
] + vty_acl_config

r1_config = [
    'interface Loopback0',
    'ip vrf forwarding control-data',
    'description --- OSPF Router-ID ---',
    'ip address 1.1.1.1 255.255.255.255',
    'no router ospf 1',
    'router ospf 1 vrf control-data',
    'router-id 1.1.1.1',
    'network 172.31.148.0 0.0.0.15 area 0',
    'network 172.31.149.0 0.0.0.15 area 0',
    'network 1.1.1.1 0.0.0.0 area 0',
] + vty_acl_config

r2_config = [
    'interface Gi0/3',
    'description --- Link to NAT Cloud ---',
    'ip vrf forwarding control-data',
    'ip address dhcp',
    'ip nat outside',
    'no shutdown',
    'interface Gi0/1',
    'ip nat inside',
    'interface Gi0/2',
    'ip nat inside',
    'interface Loopback0',
    'ip vrf forwarding control-data',
    'description --- OSPF Router-ID ---',
    'ip address 2.2.2.2 255.255.255.255',
    
    'ip access-list standard NAT_SOURCES_ACL',
    'remark --- Define traffic to be translated ---',
    'permit 172.31.148.0 0.0.0.15',
    'permit 172.31.149.0 0.0.0.15',
    'permit 172.31.150.0 0.0.0.15',
    'ip nat inside source list NAT_SOURCES_ACL interface GigabitEthernet0/3 vrf control-data overload',
    'ip route vrf control-data 0.0.0.0 0.0.0.0 GigabitEthernet0/3 dhcp',
    
    'router ospf 1 vrf control-data',
    'router-id 2.2.2.2',
    'network 172.31.149.0 0.0.0.15 area 0',
    'network 172.31.150.0 0.0.0.15 area 0',
    'network 2.2.2.2 0.0.0.0 area 0',
    'default-information originate',
] + vty_acl_config


def apply_config(device, config_commands):
    """ฟังก์ชันสำหรับเชื่อมต่อและส่งคอนฟิกไปยังอุปกรณ์ (เหมือนเดิม)"""
    print(f"\n{'='*20}\nConnecting to {device['host']}...\n{'='*20}")
    try:
        with ConnectHandler(**device) as net_connect:
            print(f"Successfully connected to {device['host']} using Public Key.")
            output = net_connect.send_config_set(config_commands)
            print("\n--- Configuration Output ---")
            print(output)
            print("\n--- Saving Configuration ---")
            save_output = net_connect.save_config()
            print(save_output)
            print(f"Configuration applied and saved on {device['host']}.")
    except Exception as e:
        print(f"\n*** ERROR: Failed to connect or configure {device['host']} ***")
        print(f"Error details: {e}")
        print("Please check:\n1. Is the device reachable?\n2. Is the public key configured correctly on the device?")

if __name__ == "__main__":
    if not os.path.exists(private_key_path):
        print(f"\n[CRITICAL ERROR] Private key file not found at: {private_key_path}")
    else:
        devices_to_configure = {
            "S1": (s1, s1_config),
            "R1": (r1, r1_config),
            "R2": (r2, r2_config),
        }
        for name, (device_info, config) in devices_to_configure.items():
            apply_config(device_info, config)
        print("\n\nScript finished.")