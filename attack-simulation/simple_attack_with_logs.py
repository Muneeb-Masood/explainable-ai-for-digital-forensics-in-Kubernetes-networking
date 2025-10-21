"""
Simple Attack Simulator with Logging
No Kubernetes needed - Runs locally and generates logs!

This simulates network traffic and attacks, generates logs,
and you can use those logs for AI training.
"""

import time
import random
import csv
import os
from datetime import datetime
import threading

class SimpleWebServer:
    """Simulates a simple web server"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.active = True
        
    def handle_request(self):
        """Simulate handling a request"""
        self.request_count += 1
        
        # Simulate response time
        response_time = random.uniform(50, 200)
        self.response_times.append(response_time)
        
        # Simulate occasional errors
        if random.random() < 0.02:  # 2% error rate normally
            self.error_count += 1
            return False
        return True
    
    def get_stats(self):
        """Get current statistics"""
        if not self.response_times:
            return {
                'requests_per_second': 0,
                'avg_response_time': 0,
                'error_rate': 0
            }
        
        return {
            'requests_per_second': self.request_count,
            'avg_response_time': sum(self.response_times) / len(self.response_times),
            'error_rate': (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.request_count = 0
        self.error_count = 0
        self.response_times = []

class AttackSimulator:
    """Simulates different types of attacks"""
    
    def __init__(self, server):
        self.server = server
        self.logs = []
        
    def simulate_normal_traffic(self, duration=10):
        """Simulate normal user traffic"""
        print("\n" + "="*60)
        print("📊 SIMULATING NORMAL TRAFFIC")
        print("="*60)
        
        for second in range(duration):
            # Normal traffic: 40-60 requests per second
            num_requests = random.randint(40, 60)
            
            for _ in range(num_requests):
                self.server.handle_request()
            
            # Log statistics
            stats = self.server.get_stats()
            self.log_traffic('Normal', stats, second)
            
            print(f"[Second {second+1:2d}] "
                  f"Requests: {num_requests:3d} | "
                  f"Avg Response: {stats['avg_response_time']:.0f}ms | "
                  f"Errors: {stats['error_rate']:.1f}%")
            
            self.server.reset_stats()
            time.sleep(0.1)  # Speed up simulation
        
        print("✅ Normal traffic completed")
    
    def simulate_ddos_attack(self, duration=10):
        """Simulate DDoS attack"""
        print("\n" + "="*60)
        print("🚨 SIMULATING DDoS ATTACK")
        print("="*60)
        
        for second in range(duration):
            # DDoS: 500-1000 requests per second
            num_requests = random.randint(500, 1000)
            
            # Simulate server struggling
            for _ in range(num_requests):
                self.server.handle_request()
                # Higher error rate during attack
                if random.random() < 0.15:  # 15% error rate
                    self.server.error_count += 1
            
            # Slower response times during attack
            self.server.response_times = [random.uniform(400, 800) for _ in range(num_requests)]
            
            stats = self.server.get_stats()
            self.log_traffic('DDoS', stats, second)
            
            print(f"[Second {second+1:2d}] "
                  f"⚠️  Requests: {num_requests:4d} | "
                  f"Avg Response: {stats['avg_response_time']:.0f}ms | "
                  f"Errors: {stats['error_rate']:.1f}%")
            
            self.server.reset_stats()
            time.sleep(0.1)
        
        print("✅ DDoS attack simulation completed")
    
    def simulate_port_scan(self, duration=10):
        """Simulate port scanning attack"""
        print("\n" + "="*60)
        print("⚠️  SIMULATING PORT SCAN ATTACK")
        print("="*60)
        
        for second in range(duration):
            # Port scan: Many connections but small packets
            num_requests = random.randint(80, 150)
            num_scans = random.randint(40, 80)
            
            for _ in range(num_requests):
                self.server.handle_request()
            
            # Fast response times (just checking if port is open)
            self.server.response_times = [random.uniform(20, 60) for _ in range(num_requests)]
            
            stats = self.server.get_stats()
            stats['port_scan_count'] = num_scans
            self.log_traffic('PortScan', stats, second)
            
            print(f"[Second {second+1:2d}] "
                  f"🔍 Requests: {num_requests:3d} | "
                  f"Port Scans: {num_scans:3d} | "
                  f"Avg Response: {stats['avg_response_time']:.0f}ms")
            
            self.server.reset_stats()
            time.sleep(0.1)
        
        print("✅ Port scan simulation completed")
    
    def log_traffic(self, attack_type, stats, second):
        """Log traffic data"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'second': second,
            'attack_type': attack_type,
            'requests_per_second': stats['requests_per_second'],
            'avg_response_time': stats['avg_response_time'],
            'error_rate': stats['error_rate'],
            'port_scan_count': stats.get('port_scan_count', 0),
            'unique_ips': random.randint(10, 300) if attack_type == 'DDoS' else random.randint(5, 30),
            'cpu_usage': random.uniform(0.7, 0.9) if attack_type == 'DDoS' else random.uniform(0.1, 0.3),
            'memory_usage': random.uniform(0.6, 0.8) if attack_type == 'DDoS' else random.uniform(0.3, 0.5),
            'network_bytes': stats['requests_per_second'] * random.randint(200, 500)
        }
        self.logs.append(log_entry)
    
    def save_logs(self, filename='data/attack_simulation_logs.csv'):
        """Save logs to CSV file"""
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w', newline='') as f:
            if self.logs:
                writer = csv.DictWriter(f, fieldnames=self.logs[0].keys())
                writer.writeheader()
                writer.writerows(self.logs)
        
        print(f"\n✅ Logs saved to: {filename}")
        print(f"   Total log entries: {len(self.logs)}")

def main():
    print("="*60)
    print("ATTACK SIMULATION WITH LOGGING")
    print("="*60)
    print("\nThis simulates:")
    print("  1. Normal traffic (10 seconds)")
    print("  2. DDoS attack (10 seconds)")
    print("  3. Port scanning attack (10 seconds)")
    print("\nAll activity is logged for AI training!")
    print("="*60)
    
    input("\nPress Enter to start simulation...")
    
    # Create server and simulator
    server = SimpleWebServer()
    simulator = AttackSimulator(server)
    
    # Run simulations
    start_time = time.time()
    
    simulator.simulate_normal_traffic(duration=10)
    time.sleep(0.5)
    
    simulator.simulate_ddos_attack(duration=10)
    time.sleep(0.5)
    
    simulator.simulate_port_scan(duration=10)
    
    end_time = time.time()
    
    # Save logs
    simulator.save_logs()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SIMULATION SUMMARY")
    print("="*60)
    print(f"Total duration: {end_time - start_time:.1f} seconds")
    print(f"Total log entries: {len(simulator.logs)}")
    print(f"\nBreakdown:")
    
    for attack_type in ['Normal', 'DDoS', 'PortScan']:
        count = sum(1 for log in simulator.logs if log['attack_type'] == attack_type)
        print(f"  {attack_type:12} : {count} entries")
    
    print("\n" + "="*60)
    print("✅ SIMULATION COMPLETED!")
    print("="*60)
    print("\n📁 Logs saved to: data/attack_simulation_logs.csv")
    print("\n🎯 Next steps:")
    print("  1. View logs: type 'notepad data\\attack_simulation_logs.csv'")
    print("  2. Train AI: python ai-model/train_from_logs.py")
    print("  3. Analyze: python explainable-ai/explain_predictions.py")
    
    # Show sample logs
    print("\n📋 Sample logs (first 5 entries):")
    print("-"*60)
    import pandas as pd
    df = pd.read_csv('data/attack_simulation_logs.csv')
    print(df.head().to_string())

if __name__ == "__main__":
    main()
