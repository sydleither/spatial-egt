import sys

import pandas as pd

from common import get_data_path


def main(data_type):
    features_data_path = get_data_path(data_type, "features")
    df = pd.read_csv(f"{features_data_path}/all.csv")

    total_samples = len(df)
    print(f"Total Samples: {total_samples}")
    for game in df["game"].unique():
        if game == "unknown":
            continue
        df_game = df[df["game"] == game]
        print(f"\t{game}: {len(df_game)}")
    unknown = len(df[df["game"] == "unknown"])
    print(f"Unknown games: {unknown}")
    high_fs = len(df[df["proportion_s"] > 0.95])
    low_fs = len(df[df["proportion_s"] < 0.05])
    print(f"fS > 0.95: {high_fs}")
    print(f"fS < 0.05: {low_fs}")
    new_total = total_samples - (unknown + high_fs + low_fs)
    print(f"Total Valid Samples: {new_total}")
    df = df[df["game"] != "unknown"]
    df = df[df["proportion_s"] <= 0.95]
    df = df[df["proportion_s"] >= 0.05]
    for game in df["game"].unique():
        df_game = df[df["game"] == game]
        print(f"\t{game}: {len(df_game)}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please provide the data type.")