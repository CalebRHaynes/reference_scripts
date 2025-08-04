import subprocess
import glob
import os
from pathlib import Path

feat_script = "./scripts/run_feat.sh"
fsf_pattern = "./data/**/*.fsf"

fsf_files = glob.glob(fsf_pattern, recursive=True)

for fsf in fsf_files[:300]:
    feat_dir = fsf.replace(".fsf", ".feat")

    # Skip if corresponding .feat directory already exists
    if Path(feat_dir).exists():
        print(f"Skipping {fsf} (feat directory already exists)")
        continue

    print(f"Running feat for {fsf}")
    result = subprocess.run(
        ["sbatch", feat_script, fsf],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"Submitted job for {fsf}: {result.stdout.strip()}")
    else:
        print(f"Failed to submit job for {fsf}: {result.stderr.strip()}")

