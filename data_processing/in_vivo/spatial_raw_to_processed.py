import os
import pandas as pd

from common import get_data_path


cell_type_map = {"Red":"sensitive", "Green":"resistant", "Blue":"unknown"}


def raw_to_processed():
    raw_data_path = get_data_path("in_vivo", "raw")
    processed_data_path = get_data_path("in_vivo", "processed")

    for file_name in os.listdir(raw_data_path):
        source = file_name[0:-4]
        df = pd.read_csv(f"{raw_data_path}/{file_name}")
        df = df[["class_label", "geometry.X", "geometry.Y"]]
        df = df.rename(columns={"geometry.X":"x",
                                "geometry.Y":"y",
                                "class_label":"type"})
        df["type"] = df["type"].map(cell_type_map)
        df.to_csv(f"{processed_data_path}/{source} 0.csv", index=False)


if __name__ == "__main__":
    raw_to_processed()