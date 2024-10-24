import pandas as pd

from common import (cell_type_map, experiment_names, 
                    processed_data_path, raw_data_path)


def raw_to_processed():
    for experiment_name in experiment_names:
        # Process spatial file
        spatial_name = f"locations_df_processed_{experiment_name}_plate1.csv"
        df_sp = pd.read_csv(f"{raw_data_path}/{spatial_name}")
        df_sp = df_sp[df_sp["Time_index"] == df_sp["Time_index"].max()]
        df_sp = df_sp.reset_index()
        df_sp = df_sp.rename(columns={"Location_Center_X":"x",
                                      "Location_Center_Y":"y",
                                      "CellType": "type"})
        df_sp = df_sp[["PlateId", "WellId", "type", "x", "y"]]
        df_sp["type"] = df_sp["type"].map(cell_type_map)
        df_sp["x"] = df_sp["x"].round(0).astype(int)
        df_sp["y"] = df_sp["y"].round(0).astype(int)
        # Save processed spatial dataframe
        df_sp.to_csv(f"{processed_data_path}/spatial_{experiment_name}.csv", index=False)


if __name__ == "__main__":
    raw_to_processed()