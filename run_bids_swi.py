import argparse
import os
import sys
import glob
from pathlib import Path

# Ensure we can import from local cvsutils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cvsutils.swi_strip import strip_swi

import subprocess

def run_command(cmd):
    print(f"Running: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def run_bids_processing(bids_root, bet_bin, limit=None, swi_suffix="swi.nii.gz"):
    """
    Run SWI stripping on a BIDS dataset.
    """
    bids_path = Path(bids_root)
    rawdata_path = bids_path / "rawdata"
    derivatives_path = bids_path / "derivatives" / "swi_strip"
    
    if not rawdata_path.exists():
        print(f"Error: rawdata directory not found at {rawdata_path}")
        return

    # Find all subjects
    subjects = sorted([d.name for d in rawdata_path.iterdir() if d.is_dir() and d.name.startswith("sub-")])
    
    if limit:
        subjects = subjects[:limit]
    
    print(f"Found {len(subjects)} subjects: {subjects}")
    
    for sub in subjects:
        sub_path = rawdata_path / sub
        
        # Find sessions
        sessions = sorted([d.name for d in sub_path.iterdir() if d.is_dir() and d.name.startswith("ses-")])
        
        if not sessions:
            print(f"No sessions found for {sub}, skipping or checking root...")
            continue
            
        for ses in sessions:
            print(f"\nProcessing {sub} {ses}...")
            
            ses_path = sub_path / ses
            anat_path = ses_path / "anat"
            swi_path = ses_path / "swi"
            
            # Find FLAIR
            flair_files = list(anat_path.glob(f"{sub}_{ses}_FLAIR.nii.gz"))
            if not flair_files:
                print(f"  No FLAIR found for {sub} {ses}, skipping.")
                continue
            flair_file = flair_files[0]
            
            # Find SWI
            swi_search = f"{sub}_{ses}_{swi_suffix}"
            swi_files = list(swi_path.glob(swi_search))
            if not swi_files:
                print(f"  No SWI found for {sub} {ses} with suffix {swi_suffix}, skipping.")
                continue
            swi_file = swi_files[0]
            
            # Prepare Output
            out_ses_dir = derivatives_path / sub / ses / "swi"
            out_ses_dir.mkdir(parents=True, exist_ok=True)
            
            output_prefix = out_ses_dir / f"{sub}_{ses}_"
            
            print(f"  Input FLAIR: {flair_file}")
            print(f"  Input SWI:   {swi_file}")
            print(f"  Output Prefix: {output_prefix}...")
            
            # 1. Run BET
            swi_bet_out = out_ses_dir / f"{sub}_{ses}_swi_bet.nii.gz"
            cmd_bet = f"{bet_bin} {swi_file} {swi_bet_out} -f 0.3 -R"
            
            if not run_command(cmd_bet):
                print("  BET failed. Skipping.")
                continue

            # 2. Run Refinement
            try:
                strip_swi(str(swi_bet_out), str(output_prefix))
            except Exception as e:
                print(f"  Error: {e}")

import shutil

def resolve_bet_path(user_path=None):
    """
    Resolve the path to FSL BET.
    Priority:
    1. User provided path (--bet)
    2. FSLDIR environment variable
    3. System PATH
    """
    if user_path:
        return user_path
    
    # Check FSLDIR
    fsl_dir = os.environ.get('FSLDIR')
    if fsl_dir:
        bet_path = os.path.join(fsl_dir, 'bin', 'bet')
        if os.path.exists(bet_path):
            return bet_path
            
    # Check PATH
    bet_path = shutil.which('bet')
    if bet_path:
        return bet_path
        
    return 'bet' # Default to command name and hope for the best

def main():
    parser = argparse.ArgumentParser(description="Run improved SWI skull stripping on BIDS dataset.")
    parser.add_argument("--bids-root", required=True, help="Path to BIDS root directory (containing rawdata)")
    parser.add_argument("--bet", help="Path to FSL BET (optional, auto-detected if FSLDIR is set)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of subjects to process")
    parser.add_argument("--swi-suffix", default="swi.nii.gz", help="Suffix for SWI file (default: swi.nii.gz)")
    
    args = parser.parse_args()
    
    bet_bin = resolve_bet_path(args.bet)
    print(f"Using BET: {bet_bin}")
    
    run_bids_processing(
        args.bids_root,
        bet_bin=bet_bin,
        limit=args.limit,
        swi_suffix=args.swi_suffix
    )

if __name__ == "__main__":
    main()
