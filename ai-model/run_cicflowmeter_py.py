"""
Run CICFlowMeter from Python and (optionally) filter to the top-20 features.

This script:
 1) Verifies tcpdump availability and the PCAP path
 2) Uses cicflowmeter.sniffer.create_sniffer to generate a full features CSV
 3) Optionally filters the CSV to the features listed in dvwa_features_top20.txt

Usage examples (PowerShell):
  python run_cicflowmeter_py.py --pcap attack_traffic.pcap --out cic_features_output.csv
  python run_cicflowmeter_py.py --pcap attack_traffic.pcap --out cic_features_output.csv --top20 saved_models/dvwa_features_top20.txt --top20_out top20_features_for_model.csv

Requirements:
    - pip install --user cicflowmeter
    - Note: tcpdump is ONLY required when capturing live from an interface.
        For offline PCAP/PCAPNG files (what we use here), tcpdump is NOT required.
"""

from pathlib import Path
import argparse
import shutil
import sys


def ensure_tcpdump():
    """Check if tcpdump exists in PATH (used only for live capture).

    CICFlowMeter can process offline PCAP/PCAPNG without tcpdump,
    so we will not block execution if we're reading from a file.
    """
    return shutil.which("tcpdump") is not None


def run_cicflowmeter(pcap, out_csv):
    try:
        from cicflowmeter.sniffer import create_sniffer
    except Exception as ie:
        print("ERROR: Could not import cicflowmeter. Install it first, e.g.:")
        print("  pip install --user cicflowmeter")
        raise ie

    sniffer, session = create_sniffer(
        input_file=str(pcap),
        input_interface=None,
        output_mode="csv",
        output=str(out_csv),
        fields=None,
        verbose=False,
    )
    sniffer.start()
    try:
        sniffer.join()
    finally:
        # Stop GC thread if present and flush
        if hasattr(session, "_gc_stop"):
            session._gc_stop.set()
            session._gc_thread.join(timeout=2.0)
        session.flush_flows()


def filter_top20(full_csv, features_txt, top20_out):
    import pandas as pd

    with open(features_txt, "r", encoding="utf-8") as f:
        wanted = [line.strip() for line in f if line.strip()]

    df = pd.read_csv(full_csv)
    for col in wanted:
        if col not in df.columns:
            df[col] = 0
    df[wanted].to_csv(top20_out, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcap", required=True, type=Path, help="Path to pcap file")
    ap.add_argument("--out", required=True, type=Path, help="Output CSV for full CIC features")
    ap.add_argument("--top20", required=False, type=Path, help="Path to txt with top-20 feature names (one per line)")
    ap.add_argument("--top20_out", required=False, type=Path, help="Output CSV for top-20 filtered features")
    args = ap.parse_args()

    # Validations
    if not args.pcap.exists():
        print(f"ERROR: PCAP not found: {args.pcap}")
        sys.exit(2)
    # For offline PCAP processing tcpdump is not needed; warn only if missing
    if not ensure_tcpdump():
        print("Warning: tcpdump not found in PATH. This is fine for offline PCAP processing.")

    print(f"Running CICFlowMeter on {args.pcap} -> {args.out}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    try:
        run_cicflowmeter(args.pcap, args.out)
        print(f"Saved full CIC features to: {args.out}")
    except Exception as e:
        print(f"ERROR running CICFlowMeter: {e}")
        sys.exit(4)

    if args.top20 and args.top20_out:
        try:
            print(f"Filtering to top-20 features -> {args.top20_out}")
            args.top20_out.parent.mkdir(parents=True, exist_ok=True)
            filter_top20(args.out, args.top20, args.top20_out)
            print(f"Saved top-20 features to: {args.top20_out}")
        except Exception as e:
            print(f"ERROR filtering top-20: {e}")
            sys.exit(5)


if __name__ == "__main__":
    main()
