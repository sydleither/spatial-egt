"""Combine individual sample's spatial statistics into one pkl

For use when processed_to_statistics was run over individual samples
"""

import argparse
import os

import pandas as pd

from spatial_egt.common import get_data_path


def main():
    """Combine individual sample's spatial statistics"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    parser.add_argument("-stat", "--statistic", type=str)
    parser.add_argument("-time", "--time", type=int, default=72)
    args = parser.parse_args()

    save_loc = get_data_path(args.data_type, "statistics", args.time)
    statistics_path = f"{save_loc}/{args.statistic}"
    df = pd.DataFrame()
    for file_name in os.listdir(statistics_path):
        df_sample = pd.read_pickle(f"{statistics_path}/{file_name}")
        df = pd.concat([df, df_sample])
    df.to_pickle(f"{save_loc}/{args.statistic}.pkl")


if __name__ == "__main__":
    main()
