from netmiko import ConnectHandler
import os
import argparse

# --- Device Inventory ---
private_key_path = os.path.expanduser('~/.ssh/admin_openssh')
legacy_crypto_settings = {
    'use_keys': True,
    'key_file': private_key_path,
    'disabled_algorithms': dict(pubkeys=['rsa-sha2-512', 'rsa-sha2-256']),
}

devices = {
    "R1": {
        "device_type": "cisco_ios",
        "host": "172.31.147.4",
        "username": "admin",
        **legacy_crypto_settings,
    },
    "R2": {
        "device_type": "cisco_ios",
        "host": "172.31.147.5",
        "username": "admin",
        **legacy_crypto_settings,
    },
    "S1": {
        "device_type": "cisco_ios",
        "host": "172.31.147.3",
        "username": "admin",
        **legacy_crypto_settings,
    }
}


def normalize_interface(intf):
    """Normalize interface names to full form (e.g., Gig 0/1 → GigabitEthernet0/1)."""
    if not intf:
        return None
    intf = intf.replace(" ", "")
    if intf.startswith("Gig"):
        return intf.replace("Gig", "GigabitEthernet")
    if intf.startswith("Fa"):
        return intf.replace("Fa", "FastEthernet")
    if intf[0].isdigit():  # e.g., "0/1" → assume GigabitEthernet
        return f"GigabitEthernet{intf}"
    return intf


def generate_descriptions(device_name, parsed_data):
    """Generate interface descriptions according to lab rules."""
    descriptions = {}

    for entry in parsed_data:
        remote_device = entry.get("neighbor_name")
        local_intf = normalize_interface(entry.get("local_interface"))
        remote_intf = normalize_interface(entry.get("neighbor_interface"))

        if not (remote_device and local_intf and remote_intf):
            print(f"[WARN] Skipping entry with unexpected keys: {entry}")
            continue

        descriptions[local_intf] = f"Connect to {remote_intf} of {remote_device}"

    # Special cases
    if device_name == "R2":
        descriptions["GigabitEthernet0/3"] = "Connect to WAN"
    if device_name == "S1":
        descriptions["GigabitEthernet1/1"] = "Connect to PC"
    if device_name == "R1":
        descriptions["GigabitEthernet0/1"] = "Connect to PC"

    return descriptions


def apply_descriptions(device_name, device_params, dry_run=False):
    """Connect to device, parse CDP neighbors, and configure descriptions."""
    print(f"\n{'='*30}\nConnecting to {device_name} ({device_params['host']})...\n{'='*30}")
    try:
        with ConnectHandler(**device_params) as conn:
            print(f"Connected to {device_name}")

            # Use Netmiko + ntc-templates integration
            parsed_data = conn.send_command("show cdp neighbors", use_textfsm=True)
            if not parsed_data:
                print(f"[WARN] No CDP neighbors found on {device_name}")
                parsed_data = []

            descriptions = generate_descriptions(device_name, parsed_data)

            config_cmds = []
            for intf, desc in descriptions.items():
                config_cmds.append(f"interface {intf}")
                config_cmds.append(f"description {desc}")

            if dry_run:
                print(f"[Dry-Run] Would apply on {device_name}:")
                for cmd in config_cmds:
                    print(cmd)
            else:
                if config_cmds:
                    print(f"\nApplying {len(config_cmds)//2} descriptions on {device_name}...")
                    result = conn.send_config_set(config_cmds)
                    print(result)
                    conn.save_config()
                    print(f"Descriptions applied and saved on {device_name}.")
                else:
                    print(f"No configs to apply for {device_name}")

    except Exception as e:
        print(f"[ERROR] Failed to configure {device_name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply interface descriptions using Netmiko + ntc-templates")
    parser.add_argument("--dry-run", action="store_true", help="Preview configs without applying")
    args = parser.parse_args()

    if not os.path.exists(private_key_path):
        print(f"\n[CRITICAL ERROR] Private key not found: {private_key_path}")
    else:
        for dev_name, dev_info in devices.items():
            apply_descriptions(dev_name, dev_info, dry_run=args.dry_run)
