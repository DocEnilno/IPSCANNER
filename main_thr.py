import socket
import threading

# Lock for synchronization
file_lock = threading.Lock()

def store_entry_to_text(domain, ip, filename='./domains.txt'):
    with file_lock:
        with open(filename, 'a') as text_file:
            text_file.write(f"{ip},{domain}\n")

def get_domain(ip_address):
    try:
        domain = socket.gethostbyaddr(ip_address)[0]
        print(f",{ip_address} {domain}")
        store_entry_to_text(domain, ip_address)
    except:
        pass

def is_port_open(ip_address, port=80):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((ip_address, port))
        print(f"Port {port} is open on {ip_address}")
        return get_domain(ip_address)
    except socket.error:
        return False
    finally:
        s.close()

def scan_ip_range(start, end):
    for a in range(start, end):
        for b in range(256):
            for c in range(256):
                for d in range(256):
                    ip_address = f"{d}.{c}.{b}.{a}"
                    if ip_address.split(".")[0] != "0":
                        is_port_open(ip_address)

def threaded_scan_ip_range(start, end):
    threads = []
    for a in range(start, end):
        thread = threading.Thread(target=scan_ip_range, args=(a, a + 1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Split the IP range into multiple threads
    threaded_scan_ip_range(0, 64)  # You can adjust the range based on your requirements
