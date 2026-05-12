"""Convert spatial statistics into features and save as features.csv

Features are defined as the single-valued statistics and the summary
    statistics of the distribution and function statistics.

labels.csv also contains a column with the "class label" for downstream
    machine learning or analysis.
"""

import argparse
import os

import numpy as np
import pandas as pd
from scipy.stats import skew

from spatial_egt.common import get_data_path, get_spatial_statistic_type


def distribution_to_features(row, name):
    """Distribution summary statistics"""
    dist = row[name]
    row[f"{name}_Mean"] = np.mean(dist)
    sd = np.std(dist)
    row[f"{name}_SD"] = sd
    if sd == 0:
        row[f"{name}_Skew"] = 0
    else:
        row[f"{name}_Skew"] = skew(dist)
    return row


def function_to_features(row, name):
    """Function summary statistics"""
    func = row[name]
    row[f"{name}_Min"] = min(func)
    row[f"{name}_Max"] = max(func)
    return row


def main():
    """Convert spatial statistics into features"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_silico")
    parser.add_argument("-label", "--label_name", type=str, default="game")
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-clean", "--clean", type=int, default=1, choices=[0, 1])
    args = parser.parse_args()

    data_path = get_data_path(args.data_type, ".")
    statistics_data_path = get_data_path(args.data_type, "statistics", args.time)
    df = pd.read_csv(f"{data_path}/labels.csv")
    df["sample"] = df["sample"].astype(str)
    df = df[["source", "sample", args.label_name]]

    for statistic_file in os.listdir(statistics_data_path):
        if not statistic_file.endswith(".pkl"):
            continue
        df_feature = pd.read_pickle(f"{statistics_data_path}/{statistic_file}")
        statistic_name = statistic_file[:-4]
        statistic_type = get_spatial_statistic_type(df_feature, statistic_name)
        if statistic_type == "distribution":
            df_feature = df_feature.apply(distribution_to_features, axis=1, args=(statistic_name,))
            df_feature = df_feature.drop(statistic_name, axis=1)
        elif statistic_type == "function":
            df_feature = df_feature.apply(function_to_features, axis=1, args=(statistic_name,))
            df_feature = df_feature.drop(statistic_name, axis=1)
        df_feature["sample"] = df_feature["sample"].astype(str)
        df = pd.merge(df, df_feature, on=["source", "sample"], how="outer")
    df = df[df[args.label_name].notna()]
    if args.clean:
        df = df.drop(["source", "sample"], axis=1)
        labels = df.pop("label")
        df.insert(len(df.columns), "label", labels)
    df.to_csv(f"{statistics_data_path}/features.csv", index=False, na_rep=np.nan)


if __name__ == "__main__":
    main()
