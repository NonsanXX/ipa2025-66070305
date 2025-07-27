# paramikolab.py (Revised)

import paramiko
import os
import time
import socket

HOSTS = {
    'R0': '172.31.147.1',
    'S0': '172.31.147.2',
    'S1': '172.31.147.3',
    'R1': '172.31.147.4',
    'R2': '172.31.147.5',
}

USERNAME = 'admin'


KEY_FILENAME = os.path.expanduser('~/.ssh/admin_openssh')

def connect_and_test_device(hostname, ip_address):
    """
    Connects to a single device using an explicitly loaded RSA key,
    runs a test command, and prints the output.
    """
    print(f"--- Attempting to connect to {hostname} ({ip_address}) ---")

    try:
        private_key = paramiko.RSAKey.from_private_key_file(KEY_FILENAME)
        print("Successfully loaded RSA private key.")
    except paramiko.ssh_exception.PasswordRequiredException:
        print(f"[FAILURE] Private key at {KEY_FILENAME} is encrypted with a passphrase.")
        print("This script does not support passphrase-protected keys.")
        print("-" * 50)
        return
    except Exception as e:
        print(f"[FAILURE] Could not read or load private key file: {e}")
        print("-" * 50)
        return

    # Initialize SSH Client
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:

        client.connect(
            hostname=ip_address,
            username=USERNAME,
            pkey=private_key,
            timeout=15,
            disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"])
        )

        print(f"[SUCCESS] Connected to {hostname} via public key authentication.")


        stdin, stdout, stderr = client.exec_command('show version | include Cisco IOS')
        time.sleep(2)

        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        print(f"--- Version Info from {hostname} ---")
        if output:
            print(output)
        else:
            print("Could not retrieve version info.")
        if error:
            print(f"[ERROR] Stderr: {error}")
        print("-" * 50)

    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(f"[FAILURE] Could not agree on key exchange algorithm for {hostname}: {e}")
        print("The device might be too old. Check its crypto settings.")
        print("-" * 50)
    except paramiko.ssh_exception.AuthenticationException:
        print(f"[FAILURE] Authentication failed for {hostname}.")
        print("Please ensure your public key is correctly configured on the device.")
        print("-" * 50)
    except (socket.timeout, TimeoutError):
        print(f"[FAILURE] Connection timed out for {hostname}. Check reachability and firewalls.")
        print("-" * 50)
    except Exception as e:
        print(f"[FAILURE] An unexpected error occurred for {hostname}: {e}")
        print("-" * 50)
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    print("Starting Paramiko lab script...")
    if not os.path.exists(KEY_FILENAME):
        print(f"\n[CRITICAL] Private key not found at: {KEY_FILENAME}")
        print("Please ensure your private key exists at this location or update the KEY_FILENAME variable.\n")
    else:
        for device_name, device_ip in HOSTS.items():
            connect_and_test_device(device_name, device_ip)