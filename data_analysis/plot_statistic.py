import argparse

import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns

from spatial_egt.common import game_colors, get_data_path, get_spatial_statistic_type


def plot_funcs(save_loc, file_name, df, label, stat_name, col):
    df = df.explode(stat_name)
    df["x"] = df.groupby(["source", "sample", label]).cumcount()
    col_order = None
    if col == "game":
        col_order = game_colors.keys()
    else:
        col_order = sorted(df[col].unique())
    facet = sns.FacetGrid(
        df,
        col=col,
        col_order=col_order,
        height=4,
        aspect=1,
    )
    facet.map_dataframe(sns.lineplot, x="x", y=stat_name, color="hotpink", errorbar="sd")
    facet.set_titles(col_template="{col_name}")
    facet.tight_layout()
    facet.figure.patch.set_alpha(0.0)
    facet.savefig(f"{save_loc}/{file_name}_{label}.png", bbox_inches="tight")


def plot_dists(save_loc, file_name, df, label_name, stat_name, col):
    df = df.explode(stat_name).reset_index()
    order = None
    if col == "game":
        order = game_colors.keys()
    else:
        order = sorted(df[col].unique())
    facet = sns.FacetGrid(df, col=col, col_order=order, height=4, aspect=1, sharey=False)
    bins = np.histogram_bin_edges(df[stat_name].dropna())
    facet.map_dataframe(
        sns.histplot,
        x=stat_name,
        hue="sample",
        multiple="stack",
        bins=bins,
        edgecolor=None,
        stat="proportion",
        common_norm=False,
    )
    facet.set_titles(col_template="{col_name}")
    facet.tight_layout()
    facet.figure.patch.set_alpha(0.0)
    facet.savefig(f"{save_loc}/{file_name}_{label_name}.png", bbox_inches="tight")


def plot_values(save_loc, file_name, df, label, stat_name, col):
    """https://matplotlib.org/matplotblog/posts/create-ridgeplots-in-matplotlib/"""
    labels = sorted(df[col].unique())
    num_labels = len(labels)
    colors = sns.color_palette("hls", num_labels)
    gs = grid_spec.GridSpec(num_labels, 1)
    fig = plt.figure()
    axes = []
    min_val = df[stat_name].min()
    x = np.linspace(min_val, df[stat_name].max(), 100)
    for c, class_name in enumerate(labels):
        well_data = df.loc[df[col] == class_name][stat_name]
        kde = stats.gaussian_kde(well_data)
        axes.append(fig.add_subplot(gs[c : c + 1, 0:1]))
        axes[-1].plot(x, kde(x), color="white")
        axes[-1].fill_between(x, kde(x), alpha=0.75, color=colors[c])
        rect = axes[-1].patch
        rect.set_alpha(0)
        axes[-1].set_yticklabels([])
        if c == num_labels - 1:
            axes[-1].set_xlabel(stat_name)
        else:
            axes[-1].set(xticklabels=[], xticks=[])
        axes[-1].text(min_val - np.std(df[stat_name]) / 3, 0, class_name, ha="right")
        axes[-1].set(yticks=[])
        for s in ["top", "right", "left", "bottom"]:
            axes[-1].spines[s].set_visible(False)
    gs.update(hspace=-0.7)
    fig.tight_layout()
    fig.figure.patch.set_alpha(0.0)
    plt.savefig(f"{save_loc}/{file_name}_{label}.png", bbox_inches="tight")


def get_data(df_stat, data_type, label_name, stat_name, source=None, sample_ids=None):
    data_path = get_data_path(data_type, ".")
    df_labels = pd.read_csv(f"{data_path}/labels.csv")
    df_labels["sample"] = df_labels["sample"].astype(str)

    if source:
        df_labels = df_labels[df_labels["source"] == source]
    if sample_ids:
        df_labels = df_labels[df_labels["sample"].isin(sample_ids)]

    df_stat["sample"] = df_stat["sample"].astype(str)
    df = df_labels.merge(df_stat, on=["source", "sample"])
    df = df[["source", "sample", label_name, stat_name]]

    return df


def idv_plots(df_stat, data_type, time, label_name, stat_name, source, plot, *sample_ids):
    save_loc = get_data_path(data_type, "images", time)
    df = get_data(df_stat, data_type, label_name, stat_name, source=source, sample_ids=sample_ids)
    file_name = stat_name + "_" + source + "_" + "_".join(sample_ids)
    plot(save_loc, file_name, df, label_name, stat_name, "sample")


def agg_plot(df_stat, data_type, time, label_name, stat_name, source, plot):
    save_loc = get_data_path(data_type, "images", time)
    df = get_data(df_stat, data_type, label_name, stat_name, source=source)
    df = df.loc[:, ~df.columns.duplicated()]
    file_name = stat_name
    if source:
        file_name += "_" + source
    plot(save_loc, file_name, df, label_name, stat_name, label_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--data_type", type=str, default="in_vitro_pc9")
    parser.add_argument("-label", "--label", type=str, default="game")
    parser.add_argument("-time", "--time", type=int, default=72)
    parser.add_argument("-stat", "--statistic", type=str, default="Proportion_Sensitive")
    parser.add_argument("-src", "--source", type=str, default=None)
    parser.add_argument("-samples", "--sample_ids", type=str, nargs="*", default=None)
    args = parser.parse_args()

    features_data_path = get_data_path(args.data_type, "statistics", args.time)
    df_stat = pd.read_pickle(f"{features_data_path}/{args.statistic}.pkl")
    function_type = get_spatial_statistic_type(df_stat, args.statistic)
    if function_type == "distribution":
        plot = plot_dists
    elif function_type == "function":
        plot = plot_funcs
    else:
        plot = plot_values

    if args.sample_ids is None:
        agg_plot(df_stat, args.data_type, args.time, args.label, args.statistic, args.source, plot)
    else:
        idv_plots(
            df_stat,
            args.data_type,
            args.time,
            args.label,
            args.statistic,
            args.source,
            plot,
            *args.sample_ids,
        )


if __name__ == "__main__":
    main()
