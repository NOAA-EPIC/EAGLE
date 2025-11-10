import eagle.tools.prewxvx as prewxvx
import yaml
import os

# Postprocess LAM (CONUS)
with open("postprocess_lam.yaml", "r") as file:
    lam_config = yaml.safe_load(file)

output_dir_lam = lam_config.get("output_path")
os.makedirs(output_dir_lam, exist_ok=True)

prewxvx.main(lam_config)

# Postprocess Global
with open("postprocess_global.yaml", "r") as file:
    global_config = yaml.safe_load(file)

output_dir_global = global_config.get("output_path")
os.makedirs(output_dir_global, exist_ok=True)

prewxvx.main(global_config)
