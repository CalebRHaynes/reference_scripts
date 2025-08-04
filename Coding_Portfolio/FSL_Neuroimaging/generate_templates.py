import os
import glob
import json
import pandas as pd
import nibabel as nib
from pathlib import Path

# Load config
with open("config.json") as f:
    cfg = json.load(f)

csv_file = cfg["csv_file"]
study_name = cfg["study_name"]
processing_dir = cfg["processing_dir"]
slice_timing_file = os.path.join(processing_dir, cfg["slice_timing_file"])
template_file = os.path.join(processing_dir, cfg["template_file"])
event_timing_dir = os.path.join(processing_dir, cfg["event_timing_dir"])
t1_patterns = cfg["t1_search_patterns"]

# Load study data
df = pd.read_csv(csv_file)
df_study = df[df["Study"] == study_name]

for _, row in df_study.iterrows():
    func_file = row["Path"]
    output_dir = os.path.dirname(os.path.dirname(func_file))
    taskname = row["Task"]
    subject = row["SubjectID"]
    session = row["Session"]

    # Ensure fsl5 dir exists
    fsl5_dir = os.path.join(os.path.dirname(func_file), "fsl5")
    os.makedirs(fsl5_dir, exist_ok=True)
    output = os.path.join(fsl5_dir, taskname)

    # Read image header info
    img = nib.load(func_file)
    hdr = img.header
    zooms = hdr.get_zooms()
    if len(zooms) <= 3:
        raise ValueError(f"Missing TR info in header for file {func_file}")
    tr = zooms[3]
    nvols = img.shape[3] if len(img.shape) > 3 else None
    nvox = img.shape[0] * img.shape[1] * img.shape[2]

    # Find T1 file using patterns from config
    t1file = ""
    subject_dir = os.path.dirname(output_dir)
    session_prefix = session[:4]
    for pattern in t1_patterns:
        search_pattern = pattern.format(
            output_dir=output_dir,
            subject_dir=subject_dir,
            subject=subject,
            session_prefix=session_prefix
        )
        candidates = glob.glob(search_pattern)
        if candidates:
            t1file = candidates[0]
            break

    if not t1file:
        print(f"No T1 file found for subject {subject}, session {session}")
        continue

    # Load FSF template
    template = Path(template_file).read_text()

    # Replace placeholders
    out_text = (
        template.replace("@output@", output)
                .replace("@tr@", str(tr))
                .replace("@nvols@", str(nvols))
                .replace("@nvox@", str(nvox))
                .replace("@stfile@", slice_timing_file)
                .replace("@func@", func_file)
                .replace("@t1@", t1file)
                .replace("@taskname@", taskname)
                .replace("@evfile@", os.path.join(event_timing_dir, f"{taskname}.txt"))
    )

    # Write new FSF file
    out_file = os.path.join(fsl5_dir, f"{taskname}.fsf")
    with open(out_file, "w") as f:
        f.write(out_text)

    print(f"Generated FSF for {subject} {session} {taskname}: {out_file}")

