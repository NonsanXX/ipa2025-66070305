import os
from netmiko import ConnectHandler
import yaml
from jinja2 import Environment, FileSystemLoader

PRIVATE_KEY_PATH = os.path.expanduser('~/.ssh/admin_openssh')
VARIABLES_FILE = 'variables.yml'
TEMPLATE_DIR = './templates'

def load_variables(file_path):
    """โหลดตัวแปรจากไฟล์ YAML"""
    print(f"Loading variables from {file_path}...")
    with open(file_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_config(template_file, variables):
    """สร้างคอนฟิกจากไฟล์ template และตัวแปร"""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)
    return template.render(variables)

def apply_config(device_info, config_commands):
    """ฟังก์ชันสำหรับเชื่อมต่อและส่งคอนฟิกไปยังอุปกรณ์"""
    print(f"\n{'='*20}\nConnecting to {device_info['host']}...\n{'='*20}")
    try:
        with ConnectHandler(**device_info) as net_connect:
            print(f"Successfully connected to {device_info['host']} using Public Key.")
            
            commands_as_list = config_commands.splitlines()
            
            output = net_connect.send_config_set(commands_as_list)
            print("\n--- Configuration Output ---")
            print(output)
            
            print("\n--- Saving Configuration ---")
            save_output = net_connect.save_config()
            print(save_output)
            print(f"Configuration applied and saved on {device_info['host']}.")

    except Exception as e:
        print(f"\n*** ERROR: Failed to connect or configure {device_info['host']} ***")
        print(f"Error details: {e}")
        print("Please check:\n1. Is the device reachable?\n2. Is the public key configured correctly?")

if __name__ == "__main__":
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"\n[CRITICAL ERROR] Private key file not found at: {PRIVATE_KEY_PATH}")
    else:
        all_vars = load_variables(VARIABLES_FILE)
        global_vars = all_vars['global_config']
        
        for name, device_vars in all_vars['devices'].items():
            
            netmiko_device = {
                "device_type": device_vars['device_type'],
                "host": device_vars['ip'],
                "username": "admin",
                'use_keys': True,
                'key_file': PRIVATE_KEY_PATH,
                'disabled_algorithms': dict(pubkeys=['rsa-sha2-512', 'rsa-sha2-256']),
            }

            template_context = {**global_vars, **device_vars}
            
            print(f"\nRendering configuration for {name} using {device_vars['template']}...")
            config_to_apply = render_config(device_vars['template'], template_context)
            
            apply_config(netmiko_device, config_to_apply)

        print("\n\nScript finished.")