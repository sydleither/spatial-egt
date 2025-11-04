"""Generate bash script for processing coordinates into spatial statistics"""

import argparse
import os

from spatial_database import STATISTIC_REGISTRY
from spatial_egt.common import get_data_path


def write_individual(run_cmd, python_file, data_type, time, statistic):
    """Write run for each sample of a given spatial statistic"""
    processed_path = get_data_path(data_type, "processed", time)
    output = []
    for sample_file in os.listdir(processed_path):
        source = sample_file.split(" ")[0]
        sample = sample_file.split(" ")[1][:-4]
        output.append(
            f"{run_cmd} {python_file} -dir {data_type} -stat {statistic} -time {time} -source {source} -sample {sample}\n"
        )
    output_batches = [output[i : i + 900] for i in range(0, len(output), 900)]
    for i, batch in enumerate(output_batches):
        with open(f"run_{data_type}_{time}_{statistic}_{i}.sh", "w", encoding="UTF-8") as f:
            for output_line in batch:
                f.write(output_line)
    get_data_path(data_type, f"statistics/{statistic}", time)


def write_aggregated(run_cmd, python_file, data_type, time, statistic_names):
    """Write run for each spatial statistic"""
    output = []
    for statistic_name in statistic_names:
        output.append(
            f"{run_cmd} {python_file} -dir {data_type} -stat {statistic_name} -time {time}\n"
        )
    with open(f"run_{data_type}_{time}.sh", "w", encoding="UTF-8") as f:
        for output_line in output:
            f.write(output_line)
    get_data_path(data_type, "statistics", time)


def main():
    """Generate and save bash script"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-run_cmd", "--run_cmd", type=str, default="python3 -m")
    parser.add_argument("-stat", "--statistic", type=str, default=None)
    args = parser.parse_args()

    python_file = "spatial_egt.data_processing.processed_to_statistic"
    if args.statistic is None:
        write_aggregated(
            args.run_cmd, python_file, args.data_type, args.time, STATISTIC_REGISTRY.keys()
        )
    else:
        write_individual(args.run_cmd, python_file, args.data_type, args.time, args.statistic)


if __name__ == "__main__":
    main()
