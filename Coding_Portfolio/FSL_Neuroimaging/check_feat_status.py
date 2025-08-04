# check_feat_status.py
"""
Check the status of FSL FEAT analysis folders by inspecting their log files.
"""
import sys
from pathlib import Path

def check_status(feat_dir: Path) -> str:
    """
    Return one of: 'processing', 'errored', 'finished', or 'missing_log'
    based on the contents of report_log.html inside a .feat directory.
    """
    log_file = feat_dir / "report_log.html"
    if not log_file.exists():
        return "missing_log"
    content = log_file.read_text(errors="ignore").lower()
    if "<meta http-equiv=refresh" in content:
        return "processing"
    if "error" in content:
        return "errored"
    return "finished"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <root_path>")
        sys.exit(1)

    root_path = Path(sys.argv[1])
    if not root_path.is_dir():
        print(f"Error: {root_path} is not a valid directory")
        sys.exit(1)

    feat_dirs = list(root_path.rglob("*.feat"))

    statuses = {"processing": [], "errored": [], "finished": [], "missing_log": []}
    for d in feat_dirs:
        statuses[check_status(d)].append(str(d))

    for status, dirs in statuses.items():
        print(f"\n=== {status.upper()} ({len(dirs)}) ===")
        for path in dirs:
            print(path)

