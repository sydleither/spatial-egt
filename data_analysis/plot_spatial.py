"""Visualize the coordinates of a list of samples"""

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from spatial_egt.common import game_colors, get_data_path


def plot_coords():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str)
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-src", "--source", type=str)
    parser.add_argument("-samples", "--sample_ids", type=str, nargs="*")
    parser.add_argument("-s", "--marker_size", type=int, default=5)
    args = parser.parse_args()

    processed_data_path = get_data_path(args.data_type, "processed", args.time)
    image_data_path = get_data_path(args.data_type, "images", args.time)
    fig, ax = plt.subplots(1, len(args.sample_ids), figsize=(6*len(args.sample_ids), 6))
    if len(args.sample_ids) == 1:
        ax = [ax]
    for s,sample_id in enumerate(sorted(args.sample_ids)):
        file_name = f"{args.source} {sample_id}.csv"
        df = pd.read_csv(f"{processed_data_path}/{file_name}")
        sensitive = df[df["type"] == "sensitive"]
        ax[s].scatter(
            sensitive["x"],
            sensitive["y"],
            marker="s",
            s=args.marker_size,
            color=game_colors["Sensitive Wins"],
            alpha=0.66
        )
        resistant = df[df["type"] == "resistant"]
        ax[s].scatter(
            resistant["x"],
            resistant["y"],
            marker="s",
            s=args.marker_size,
            color=game_colors["Resistant Wins"],
            alpha=0.66
        )
        ax[s].get_xaxis().set_visible(False)
        ax[s].get_yaxis().set_visible(False)
        ax[s].set_title(sample_id)
    fig.suptitle(args.source)
    fig.subplots_adjust(wspace=0.04, hspace=0)
    fig.figure.patch.set_alpha(0.0)
    save_name = args.source + "_" + "_".join(args.sample_ids)
    plt.savefig(f"{image_data_path}/{save_name}.png", bbox_inches="tight", dpi=200)


if __name__ == "__main__":
    main()
