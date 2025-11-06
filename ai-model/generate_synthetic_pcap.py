"""
Generate synthetic network traffic PCAP for testing CICFlowMeter.
Creates a small PCAP file with various traffic patterns.
"""

from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
import random

def generate_synthetic_pcap(output_file="attack_traffic.pcap", packet_count=1000):
    """Generate synthetic network traffic and save to PCAP"""
    
    print(f"Generating {packet_count} synthetic packets...")
    packets = []
    
    # Source and destination IPs
    src_ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30", "10.0.0.5"]
    dst_ips = ["192.168.1.100", "8.8.8.8", "1.1.1.1", "192.168.1.200"]
    
    for i in range(packet_count):
        src_ip = random.choice(src_ips)
        dst_ip = random.choice(dst_ips)
        
        # Generate different types of traffic
        traffic_type = random.choices(
            ["normal_http", "normal_https", "ddos_syn", "port_scan", "icmp"],
            weights=[40, 30, 15, 10, 5]
        )[0]
        
        if traffic_type == "normal_http":
            # Normal HTTP traffic
            pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=random.randint(1024, 65535), dport=80, flags="PA") / Raw(load="GET / HTTP/1.1\r\n\r\n")
            
        elif traffic_type == "normal_https":
            # Normal HTTPS traffic
            pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=random.randint(1024, 65535), dport=443, flags="PA") / Raw(load=b"\x16\x03\x01" + bytes(random.getrandbits(8) for _ in range(50)))
            
        elif traffic_type == "ddos_syn":
            # SYN flood attack pattern
            pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=random.randint(1024, 65535), dport=random.choice([80, 443, 22, 3306]), flags="S")
            
        elif traffic_type == "port_scan":
            # Port scanning pattern
            pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=54321, dport=random.randint(1, 1024), flags="S")
            
        else:  # icmp
            # ICMP traffic
            pkt = IP(src=src_ip, dst=dst_ip) / ICMP()
        
        packets.append(pkt)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{packet_count} packets...")
    
    # Write packets to PCAP file
    print(f"\nWriting packets to {output_file}...")
    wrpcap(output_file, packets)
    print(f"✓ Successfully created {output_file} with {len(packets)} packets")
    print(f"  File size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Generate synthetic PCAP for testing")
    parser.add_argument("--output", "-o", default="attack_traffic.pcap", help="Output PCAP filename")
    parser.add_argument("--count", "-c", type=int, default=1000, help="Number of packets to generate")
    
    args = parser.parse_args()
    
    try:
        generate_synthetic_pcap(args.output, args.count)
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure scapy is installed: pip install scapy")
