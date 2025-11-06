"""
DDoS Attack Simulation Script

This script simulates a Distributed Denial of Service (DDoS) attack
by sending multiple requests to the target service.
"""

import requests
import time
import threading
from datetime import datetime

# Configuration
TARGET_URL = "http:// :"  # Minikube service URL
NUM_THREADS = 50  # Number of concurrent attack threads
DURATION_SECONDS = 60  # Attack duration
REQUESTS_PER_THREAD = 1000

def attack_thread(thread_id):
    """
    Single attack thread that sends multiple requests
    """
    print(f"[Thread {thread_id}] Starting attack...")
    success_count = 0
    fail_count = 0
    
    for i in range(REQUESTS_PER_THREAD):
        try:
            response = requests.get(TARGET_URL, timeout=2)
            success_count += 1
            if i % 100 == 0:
                print(f"[Thread {thread_id}] Sent {i} requests")
        except Exception as e:
            fail_count += 1
    
    print(f"[Thread {thread_id}] Finished. Success: {success_count}, Failed: {fail_count}")

def main():
    print("="*60)
    print("DDoS ATTACK SIMULATION")
    print("="*60)
    print(f"Target: {TARGET_URL}")
    print(f"Threads: {NUM_THREADS}")
    print(f"Duration: {DURATION_SECONDS}s")
    print(f"Requests per thread: {REQUESTS_PER_THREAD}")
    print("="*60)
    
    # Warning
    print("\n⚠️  WARNING: This is for educational purposes only!")
    print("Make sure you're attacking your OWN test environment.\n")
    
    input("Press Enter to start the attack...")
    
    start_time = datetime.now()
    print(f"\n[{start_time}] Attack started!\n")
    
    # Create and start threads
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=attack_thread, args=(i,))
        thread.start()
        threads.append(thread)
        time.sleep(0.01)  # Small delay between thread starts
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print(f"[{end_time}] Attack completed!")
    print(f"Total duration: {duration:.2f} seconds")
    print(f"Total requests sent: ~{NUM_THREADS * REQUESTS_PER_THREAD}")
    print("="*60)
    
    print("\n✅ Now check your Kubernetes cluster:")
    print("   kubectl get pods -w")
    print("   kubectl get hpa")

if __name__ == "__main__":
    main()


