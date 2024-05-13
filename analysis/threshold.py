import matplotlib.pyplot as plt
import pandas as pd

from common import read_all, plot_line


def get_times_to_progression(df, col_name):
    progression_times = []
    for threshold in sorted(df["threshold"].unique()):
        df_thr = df.loc[df["threshold"] == threshold]
        for experiment in df_thr["experiment"].unique():
            df_exp = df_thr.loc[df_thr["experiment"] == experiment]
            for rep in df_exp["rep"].unique():
                df_rep = df_exp.loc[df_exp["rep"] == rep]
                progression_amt = 1.2 * df_rep.loc[df_rep["time"] == 0][col_name].tolist()[0]
                progressed = df_rep.loc[df_rep[col_name] >= progression_amt]["time"].tolist()
                if len(progressed) == 0:
                    print(experiment+str(threshold), df["dimension"].to_list()[0], rep)
                    progression_times.append({"rep":rep, "threshold":threshold, "experiment":experiment,
                                            "progression_time":progression_times[-1]["progression_time"]})
                else:
                    progression_times.append({"rep":rep, "threshold":threshold, "experiment":experiment,
                                            "progression_time":progressed[0]})
    df_pt = pd.DataFrame(progression_times)
    return df_pt


def threshold_plot(df, exp_dir, dimension):
    experiments = sorted(df["experiment"].unique())
    figure, axis = plt.subplots(1, len(experiments), figsize=(18,10), dpi=150)
    df_d = df.loc[df["dimension"] == dimension]
    df_pt = get_times_to_progression(df_d, "adaptive_total")
    df_pt_cont = get_times_to_progression(df_d, "continuous_total")
    ymin = df_pt["progression_time"].min()
    ymax = df_pt["progression_time"].max()
    colors = ["sienna", "green", "steelblue"]
    thresholds = sorted(df["threshold"].unique())
    for i,experiment in enumerate(experiments):
        plot_line(axis[i], df_pt.loc[df_pt["experiment"] == experiment], "threshold", "progression_time", colors[i], "adaptive")
        plot_line(axis[i], df_pt_cont.loc[df_pt_cont["experiment"] == experiment], "threshold", "progression_time", "gray", "continuous")
        axis[i].set(xlabel="Threshold", ylabel="Time to Progression", title=experiment, xticks=thresholds, ylim=(ymin, ymax))
        axis[i].legend()
    figure.suptitle(dimension)
    figure.tight_layout()
    plt.savefig(f"output/{exp_dir}/{dimension}_thresholds.png", transparent=False)
    plt.close()


def main():
    exp_dir = "threshold"
    df = read_all(exp_dir)
    df["experiment"] = df["condition"].str[0:-1]
    df["threshold"] = pd.to_numeric(df["condition"].str[-1])
    df["adaptive_total"] = df["adaptive_sensitive"] + df["adaptive_resistant"]
    df["null_total"] = df["null_sensitive"] + df["null_resistant"]
    df["continuous_total"] = df["continuous_sensitive"] + df["continuous_resistant"]

    threshold_plot(df, exp_dir, "2D")
    threshold_plot(df, exp_dir, "3D")
    threshold_plot(df, exp_dir, "WM")


if __name__ == "__main__":
    main()