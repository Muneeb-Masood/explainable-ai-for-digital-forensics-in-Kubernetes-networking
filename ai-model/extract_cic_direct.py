"""
Extract CIC flow features directly from PCAP using scapy + cicflowmeter session.
This bypasses the tcpdump requirement for reading files.
"""

import argparse
from pathlib import Path
import sys


def extract_cic_features(pcap_file, output_csv):
    """Extract CIC flow features directly from PCAP file"""
    
    print(f"Loading PCAP: {pcap_file}")
    
    try:
        from scapy.all import rdpcap, IP
        from cicflowmeter.flow_session import FlowSession
        import time
        
        # Read all packets
        packets = rdpcap(str(pcap_file))
        print(f"  Loaded {len(packets)} packets")
        
        if len(packets) == 0:
            print("ERROR: No packets in PCAP file")
            return False
        
        # Create flow session for CSV output
        print("Processing flows...")
        session = FlowSession(output_mode="csv", output=str(output_csv))
        
        # Process packets using the process() method
        processed = 0
        for i, pkt in enumerate(packets):
            # FlowSession.process() requires TCP or UDP packets
            session.process(pkt)
            processed += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(packets)} packets...")
        
        print(f"  Total packets processed: {processed}")
        
        # Flush all remaining flows to file
        print("Flushing flows to CSV...")
        session.flush_flows()
        
        print(f"✓ Successfully extracted features to: {output_csv}")
        return True
        
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Install with: pip install --user cicflowmeter scapy")
        return False
    except Exception as e:
        print(f"ERROR processing PCAP: {e}")
        import traceback
        traceback.print_exc()
        return False


def filter_to_top20(full_csv, features_txt, output_csv):
    """Filter CIC features to top-20 list"""
    
    print(f"\nFiltering to top-20 features...")
    print(f"  Features list: {features_txt}")
    print(f"  Output: {output_csv}")
    
    try:
        import pandas as pd
        
        # Load feature names
        with open(features_txt, 'r', encoding='utf-8') as f:
            wanted_features = [line.strip() for line in f if line.strip()]
        
        print(f"  Target features: {len(wanted_features)}")
        
        # Load full CIC CSV
        df = pd.read_csv(full_csv)
        print(f"  Input shape: {df.shape}")
        print(f"  Input columns: {list(df.columns)[:5]}... (showing first 5)")
        
        # Ensure all wanted features exist (fill missing with 0)
        for col in wanted_features:
            if col not in df.columns:
                print(f"  Warning: Column '{col}' not found, filling with 0")
                df[col] = 0
        
        # Select only wanted features
        df_filtered = df[wanted_features]
        print(f"  Output shape: {df_filtered.shape}")
        
        # Save
        df_filtered.to_csv(output_csv, index=False)
        print(f"✓ Successfully saved top-20 features to: {output_csv}")
        return True
        
    except Exception as e:
        print(f"ERROR filtering features: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Extract CIC features from PCAP (direct method)")
    parser.add_argument("--pcap", required=True, type=Path, help="Input PCAP file")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV for full CIC features")
    parser.add_argument("--top20", type=Path, help="Feature list file for top-20 filtering")
    parser.add_argument("--top20_out", type=Path, help="Output CSV for top-20 features")
    
    args = parser.parse_args()
    
    # Validate input
    if not args.pcap.exists():
        print(f"ERROR: PCAP file not found: {args.pcap}")
        sys.exit(1)
    
    # Create output directories
    args.out.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract full CIC features
    success = extract_cic_features(args.pcap, args.out)
    if not success:
        sys.exit(2)
    
    # Filter to top-20 if requested
    if args.top20 and args.top20_out:
        if not args.top20.exists():
            print(f"ERROR: Features list not found: {args.top20}")
            sys.exit(3)
        
        args.top20_out.parent.mkdir(parents=True, exist_ok=True)
        success = filter_to_top20(args.out, args.top20, args.top20_out)
        if not success:
            sys.exit(4)
    
    print("\n✓ All done!")


if __name__ == "__main__":
    main()
