"""Plot the game quadrant"""

import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from spatial_egt.common import game_colors, get_data_path


def plot_gamespace(save_loc, save_name, df, hue):
    df["C - A"] = df["c"] - df["a"]
    df["B - D"] = df["b"] - df["d"]
    if hue == "game":
        palette = game_colors.values()
        hue_order = game_colors.keys()
    else:
        palette = sns.color_palette("hls", len(df[hue].unique()))
        hue_order = sorted(df[hue].unique())
    hue_formatted = hue.replace("_", " ").title()
    df = df.rename({hue:hue_formatted}, axis=1)
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    sns.scatterplot(
        data=df, x="C - A", y="B - D", s=200, hue=hue_formatted, palette=palette, hue_order=hue_order, ax=ax
    )
    ax.axvline(0, color="black")
    ax.axhline(0, color="black")
    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    plt.savefig(f"{save_loc}/gamespace_{save_name}.png", dpi=200)


def get_samples(data_type, source, sample_ids):
    data_path = get_data_path(data_type, ".")
    df_labels = pd.read_csv(f"{data_path}/labels.csv")
    df_labels["sample"] = df_labels["sample"].astype(str)
    if source is not None:
        df_labels = df_labels[df_labels["source"] == source]
    if sample_ids is not None:
        df_labels = df_labels[df_labels["sample"].isin(sample_ids)]
    return df_labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_vitro_pc9")
    parser.add_argument("-hue", "--hue", type=str, default="cell_types")
    parser.add_argument("-src", "--source", type=str, default=None)
    parser.add_argument("-samples", "--sample_ids", type=str, nargs="*", default=None)
    args = parser.parse_args()

    save_name = args.hue
    source = None
    sample_ids = None
    if args.source is not None:
        source = args.source
        save_name += "_" + args.source
    if args.sample_ids is not None:
        sample_ids = args.sample_ids
        save_name += "_" + source + "_" + "_".join(sample_ids)

    image_data_path = get_data_path(args.data_type, "images")
    df = get_samples(args.data_type, source, sample_ids)
    plot_gamespace(image_data_path, save_name, df, args.hue)

    print("Payoff parameter ranges:")
    for p in ["a", "b", "c", "d"]:
        print("\t", p, df[p].min(), df[p].max())


if __name__ == "__main__":
    main()
