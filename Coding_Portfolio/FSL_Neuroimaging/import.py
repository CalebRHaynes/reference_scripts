import os
import subprocess
import pandas as pd
import flywheel
import json
from dotenv import load_dotenv

load_dotenv()

def import_flywheel(config_path="config.json"):
    # Load config
    with open(config_path) as f:
        config = json.load(f)

    output_log = config.get("output_log", "./logs/output")
    error_log = config.get("error_log", "./logs/error")
    os.makedirs(output_log, exist_ok=True)
    os.makedirs(error_log, exist_ok=True)

    import_log_csv = config.get("import_log_csv", "./import_log.csv")
    df = pd.read_csv(import_log_csv)

    studies_cfg = config.get("studies", {})

    fw = flywheel.Client(os.getenv("FLYWHEEL_API_KEY"))

    for _, row in df.iterrows():
        study_name = row["study"]
        if study_name not in studies_cfg:
            continue

        cfg = studies_cfg[study_name]
        project_path = cfg["project_path"]
        cluster_slice = slice(*cfg["cluster_id_slice"])

        project = fw.resolve(project_path)

        for elem in project.children:
            ID = elem.label
            cluster_id = "P0000" + ID[cluster_slice]
            flywheel_session = "S00" + ID[-2:]

            if row["subid"] == cluster_id and row["session"] == flywheel_session:
                dicom_dir = os.path.join(".", "data", study_name, cluster_id, row["session"], "DICOM")
                if os.path.exists(dicom_dir):
                    continue  # Already imported

                import_cmd = (
                    f"sbatch -o {output_log}/import_{cluster_id}_{row['session']}.out "
                    f"-e {error_log}/import_{cluster_id}_{row['session']}.err --parsable "
                    f"./scripts/flywheel_import.sh {study_name} {cluster_id} {row['session']} {project_path} {ID}"
                )
                subprocess.Popen(import_cmd, shell=True, stdout=subprocess.PIPE, text=True).communicate()

if __name__ == "__main__":
    import_flywheel()


