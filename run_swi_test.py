import argparse
import os
import sys

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

import shutil

def resolve_bet_path(user_path=None):
    if user_path: return user_path
    fsl_dir = os.environ.get('FSLDIR')
    if fsl_dir:
        bet_path = os.path.join(fsl_dir, 'bin', 'bet')
        if os.path.exists(bet_path): return bet_path
    bet_path = shutil.which('bet')
    if bet_path: return bet_path
    return 'bet'

def main():
    parser = argparse.ArgumentParser(description="Run SWI skull stripping.")
    parser.add_argument("--flair", required=True, help="Path to FLAIR brain (unused, kept for compat)")
    parser.add_argument("--swi", required=True, help="Path to raw SWI image")
    parser.add_argument("--out", required=True, help="Output prefix")
    parser.add_argument("--bet", help="Path to FSL BET (optional)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.swi):
        print(f"Error: SWI file not found: {args.swi}")
        return
        
    bet_bin = resolve_bet_path(args.bet)
    print(f"Using BET: {bet_bin}")

    # 1. Run BET
    swi_bet_out = f"{args.out}swi_bet.nii.gz"
    cmd_bet = f"{bet_bin} {args.swi} {swi_bet_out} -f 0.3 -R"
    
    if not run_command(cmd_bet):
        print("BET failed. Aborting.")
        return

    # 2. Run Refinement
    strip_swi(swi_bet_out, args.out)

if __name__ == "__main__":
    main()
