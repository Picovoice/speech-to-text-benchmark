import argparse
import json
import os
import time

import psutil

from benchmark import RESULTS_FOLDER
from dataset import Datasets
from engine import Engines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=[ds.value for ds in Datasets], required=True)
    parser.add_argument("--engine", choices=[en.value for en in Engines], required=True)
    args = parser.parse_args()

    dataset_name = args.dataset
    engine_type = args.engine

    base_used_memory = psutil.virtual_memory().used
    base_used_swap = psutil.swap_memory().used

    results_folder = os.path.join(RESULTS_FOLDER, dataset_name)
    max_mem = 0
    print(f"Monitoring memory usage for {engine_type}")
    try:
        print("Press Ctrl+C to stop monitoring")
        while True:
            used_memory = psutil.virtual_memory().used
            used_swap = psutil.swap_memory().used
            total_engine_memory = used_memory - base_used_memory + used_swap - base_used_swap
            max_mem = max(max_mem, total_engine_memory)
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"Max memory usage: {max_mem / 1024 / 1024} MiB")
        results_path = os.path.join(results_folder, f"{engine_type}_mem.json")
        os.makedirs(results_folder, exist_ok=True)
        results = dict()
        results["max_mem_GiB"] = max_mem / 1024 / 1024 / 1024
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
