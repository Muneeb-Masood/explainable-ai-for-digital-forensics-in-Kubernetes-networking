"""
Simple feature mapping script to convert CICFlowMeter column names 
to the names expected by the DVWA model.
"""

import pandas as pd
import argparse
from pathlib import Path


# Mapping from CICFlowMeter columns to DVWA model expected names
FEATURE_MAPPING = {
    # Original CICFlowMeter -> Expected DVWA names
    'bwd_seg_size_avg': 'bwd_segment_size_cov',  # Approximation
    'flow_iat_tot': 'packet_IAT_total',
    'flow_iat_max': 'packet_IAT_max',
    'init_fwd_win_byts': 'fwd_init_win_bytes',
    'ack_flag_cnt': 'ack_flag_percentage_in_total',  # Will calculate percentage
    'fwd_pkt_len_min': 'min_fwd_payload_bytes_delta_len',  # Approximation
    'fin_flag_cnt': 'bwd_fin_flag_percentage_in_total',  # Will calculate percentage
    'bwd_header_len': 'variance_bwd_header_bytes_delta_len',  # Approximation
    'fwd_header_len': 'mean_header_bytes',  # Will calculate mean
    'bwd_pkt_len_max': 'max_bwd_packets_delta_len',
    'bwd_pkt_len_std': 'std_bwd_header_bytes_delta_len',
    'fwd_seg_size_avg': 'fwd_segment_size_cov',  # Approximation
    'fwd_pkt_len_max': 'fwd_segment_size_max',
    'syn_flag_cnt': 'syn_flag_percentage_in_total',  # Will calculate percentage
    'fwd_pkt_len_std': 'variance_fwd_payload_bytes_delta_len',
    'fwd_pkt_len_max': 'max_fwd_packets_delta_len',
    'pkt_len_std': 'std_payload_bytes_delta_len',
    'bwd_pkt_len_max': 'max_bwd_payload_bytes_delta_len',
    'flow_pkts_s': 'container_network_transmit_packets_rate',
    'pkt_len_var': 'fwd_segment_size_variance',
}


def map_features(input_csv, output_csv, verbose=True):
    """
    Map CICFlowMeter features to DVWA model expected names.
    
    Args:
        input_csv: Path to CICFlowMeter output CSV
        output_csv: Path to save mapped features
        verbose: Print progress
    """
    
    if verbose:
        print(f"Loading CICFlowMeter data: {input_csv}")
    
    # Load data
    df = pd.read_csv(input_csv)
    
    if verbose:
        print(f"  Input shape: {df.shape}")
        print(f"  Input columns: {len(df.columns)}")
    
    # Create new dataframe with mapped columns
    mapped_df = pd.DataFrame()
    
    # Track which mappings worked
    mapped_count = 0
    missing_count = 0
    
    for cic_col, dvwa_col in FEATURE_MAPPING.items():
        if cic_col in df.columns:
            # Special handling for percentage calculations
            if 'percentage' in dvwa_col:
                # Calculate percentage (flag_count / total_packets * 100)
                total_pkts = df['tot_fwd_pkts'] + df['tot_bwd_pkts']
                total_pkts = total_pkts.replace(0, 1)  # Avoid division by zero
                mapped_df[dvwa_col] = (df[cic_col] / total_pkts) * 100
            
            # Special handling for mean calculations
            elif dvwa_col == 'mean_header_bytes':
                # Average of forward and backward header lengths
                mapped_df[dvwa_col] = (df['fwd_header_len'] + df['bwd_header_len']) / 2
            
            else:
                # Direct mapping
                mapped_df[dvwa_col] = df[cic_col]
            
            mapped_count += 1
            if verbose:
                print(f"  ✓ Mapped: {cic_col} -> {dvwa_col}")
        else:
            # Column not found, fill with 0
            mapped_df[dvwa_col] = 0
            missing_count += 1
            if verbose:
                print(f"  ⚠ Missing: {cic_col} (filling {dvwa_col} with 0)")
    
    if verbose:
        print(f"\n  Successfully mapped: {mapped_count}/{len(FEATURE_MAPPING)}")
        print(f"  Missing columns: {missing_count}/{len(FEATURE_MAPPING)}")
        print(f"  Output shape: {mapped_df.shape}")
    
    # Save mapped features
    mapped_df.to_csv(output_csv, index=False)
    
    if verbose:
        print(f"\n✓ Saved mapped features to: {output_csv}")
        print(f"  Columns: {list(mapped_df.columns)}")
    
    return mapped_df


def main():
    parser = argparse.ArgumentParser(
        description="Map CICFlowMeter features to DVWA model expected names"
    )
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("ai-model/cic_features_output.csv"),
        help="Input CICFlowMeter CSV file"
    )
    parser.add_argument(
        "--output", 
        type=Path, 
        default=Path("ai-model/top20_features_for_model.csv"),
        help="Output CSV with mapped feature names"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Validate input exists
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        return 1
    
    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Map features
    map_features(args.input, args.output, verbose=not args.quiet)
    
    print("\n✅ Feature mapping complete!")
    return 0


if __name__ == "__main__":
    exit(main())
