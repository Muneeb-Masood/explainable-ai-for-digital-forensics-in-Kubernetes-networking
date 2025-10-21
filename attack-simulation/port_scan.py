"""
Port Scanning Attack Simulation

This script simulates a port scanning attack to detect open ports
on the target service.
"""

import socket
import time
from datetime import datetime
import threading

# Configuration
TARGET_HOST = "localhost"
PORT_RANGE = range(1, 1000)  # Scan ports 1-999
TIMEOUT = 0.5
NUM_THREADS = 10

open_ports = []
lock = threading.Lock()

def scan_port(host, port):
    """
    Try to connect to a specific port
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            with lock:
                open_ports.append(port)
                print(f"[+] Port {port} is OPEN")
        
        sock.close()
    except Exception as e:
        pass

def scan_ports_range(host, ports):
    """
    Scan a range of ports
    """
    for port in ports:
        scan_port(host, port)

def main():
    print("="*60)
    print("PORT SCANNING ATTACK SIMULATION")
    print("="*60)
    print(f"Target: {TARGET_HOST}")
    print(f"Port Range: {PORT_RANGE.start} - {PORT_RANGE.stop}")
    print(f"Threads: {NUM_THREADS}")
    print("="*60)
    
    print("\n⚠️  WARNING: This is for educational purposes only!")
    print("Make sure you're scanning your OWN test environment.\n")
    
    input("Press Enter to start the port scan...")
    
    start_time = datetime.now()
    print(f"\n[{start_time}] Port scan started!\n")
    
    # Divide ports among threads
    ports_list = list(PORT_RANGE)
    chunk_size = len(ports_list) // NUM_THREADS
    threads = []
    
    for i in range(NUM_THREADS):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < NUM_THREADS - 1 else len(ports_list)
        ports_chunk = ports_list[start_idx:end_idx]
        
        thread = threading.Thread(target=scan_ports_range, args=(TARGET_HOST, ports_chunk))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print(f"[{end_time}] Port scan completed!")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Ports scanned: {len(PORT_RANGE)}")
    print(f"Open ports found: {len(open_ports)}")
    
    if open_ports:
        print("\nOpen Ports:")
        for port in sorted(open_ports):
            print(f"  - {port}")
    
    print("="*60)

if __name__ == "__main__":
    main()
