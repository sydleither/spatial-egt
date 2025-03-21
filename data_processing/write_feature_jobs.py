import sys

from data_processing.spatial_statistics.custom import nc_dist, proportion_s, sfp_dist
from data_processing.spatial_statistics.muspan import (anni, entropy, cpcf, cross_k,
                                                       kl_divergence, global_moransi,
                                                       local_moransi_dist,
                                                       nn_dist, qcm, wasserstein,
                                                       circularity_dist, fractal_dimension_dist, patch_count)


FEATURE_REGISTRY = {
    # Custom
    "NC_Resistant": nc_dist,
    "NC_Sensitive": nc_dist,
    "Proportion_Sensitive": proportion_s,
    "SFP": sfp_dist,
    # MuSpAn
    "ANNI_Resistant": anni,
    "ANNI_Sensitive": anni,
    "Entropy": entropy,
    "CPCF_Resistant": cpcf,
    "CPCF_Sensitive": cpcf,
    "Cross_Ripleys_k_Resistant": cross_k,
    "Cross_Ripleys_k_Sensitive": cross_k,
    "KL_Divergence": kl_divergence,
    "Global_Morans_i_Resistant": global_moransi,
    "Global_Morans_i_Sensitive": global_moransi,
    "Local_Morans_i_Resistant": local_moransi_dist,
    "Local_Morans_i_Sensitive": local_moransi_dist,
    "NN_Resistant": nn_dist,
    "NN_Sensitive": nn_dist,
    "SES": qcm,
    "Wasserstein": wasserstein,
    # Temp
    "Patch_Count": patch_count,
    "Patch_Circularity": circularity_dist,
    "Patch_Fractal_Dimension": fractal_dimension_dist
}

FEATURE_PARAMS = {
    "in_silico": {
        "ANNI_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "ANNI_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "NC_Resistant": {"radius": 3, "return_fs": True},
        "NC_Sensitive": {"radius": 3, "return_fs": False},
        "SFP": {"sample_length": 5},
        "Cross_Ripleys_k_Resistant": {"max_radius": 6, "step": 1, "cell_type1":"resistant", "cell_type2":"sensitive"},
        "Cross_Ripleys_k_Sensitive": {"max_radius": 6, "step": 1, "cell_type1":"sensitive", "cell_type2":"resistant"},
        "CPCF_Sensitive": {"max_radius": 5, "annulus_step": 1, "annulus_width": 3, "cell_type1":"sensitive", "cell_type2":"resistant"},
        "CPCF_Resistant": {"max_radius": 5, "annulus_step": 1, "annulus_width": 3, "cell_type1":"resistant", "cell_type2":"sensitive"},
        "KL_Divergence": {"mesh_step": 3},
        "Global_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 5},
        "Global_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 5},
        "Local_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 5},
        "Local_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 5},
        "NN_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "NN_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "SES": {"side_length": 10},
        "Patch_Count": {"cell_type": "sensitive", "alpha": 3},
        "Patch_Circularity": {"cell_type": "sensitive", "alpha": 3},
        "Patch_Fractal_Dimension": {"cell_type": "sensitive", "alpha": 3}
    },
    "in_vitro": {
        "ANNI_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "ANNI_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "NC_Resistant": {"radius": 30, "return_fs": True},
        "NC_Sensitive": {"radius": 30, "return_fs": False},
        "SFP": {"sample_length": 50},
        "Cross_Ripleys_k_Resistant": {"max_radius": 60, "step": 10, "cell_type1":"resistant", "cell_type2":"sensitive"},
        "Cross_Ripleys_k_Sensitive": {"max_radius": 60, "step": 10, "cell_type1":"sensitive", "cell_type2":"resistant"},
        "CPCF_Sensitive": {"max_radius": 50, "annulus_step": 10, "annulus_width": 30, "cell_type1":"sensitive", "cell_type2":"resistant"},
        "CPCF_Resistant": {"max_radius": 50, "annulus_step": 10, "annulus_width": 30, "cell_type1":"resistant", "cell_type2":"sensitive"},
        "KL_Divergence": {"mesh_step": 30},
        "Global_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Global_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "Local_Morans_i_Resistant": {"cell_type": "resistant", "side_length": 50},
        "Local_Morans_i_Sensitive": {"cell_type": "sensitive", "side_length": 50},
        "NN_Resistant": {"cell_type1": "resistant", "cell_type2": "sensitive"},
        "NN_Sensitive": {"cell_type1": "sensitive", "cell_type2": "resistant"},
        "SES": {"side_length": 100},
        "Patch_Count": {"cell_type": "sensitive", "alpha": 30},
        "Patch_Circularity": {"cell_type": "sensitive", "alpha": 30},
        "Patch_Fractal_Dimension": {"cell_type": "sensitive", "alpha": 30}
    }
}
FEATURE_PARAMS["in_silico_games"] = FEATURE_PARAMS["in_silico"]

FUNCTION_LABELS = {
    "NC_Resistant": {"x":"Fraction Sensitive in Neighborhood", "y":"Fraction of Resistant Cells"},
    "NC_Sensitive": {"x":"Fraction Resistant in Neighborhood", "y":"Fraction of Sensitive Cells"},
    "SFP": {"x":"Fraction Sensitive", "y":"Frequency Across Subsamples"},
    "CPCF_Resistant": {"x":"r", "y":"g(r)"},
    "CPCF_Sensitive": {"x":"r", "y":"g(r)"},
    "Cross_Ripleys_k_Resistant": {"x":"r", "y":"g(r)"},
    "Cross_Ripleys_k_Sensitive": {"x":"r", "y":"g(r)"},
    "Local_Morans_i_Resistant": {"x":"Moran's i", "y":"Proportion"},
    "Local_Morans_i_Sensitive": {"x":"Moran's i", "y":"Proportion"},
    "NN_Resistant": {"x":"Distance", "y":"Proportion"},
    "NN_Sensitive": {"x":"Distance", "y":"Proportion"},
}

DISTRIBUTION_BINS = {
    "NC_Resistant": (0, 1.1, 0.1),
    "NC_Sensitive": (0, 1.1, 0.1),
    "SFP": (0, 1.1, 0.1),
    "Local_Morans_i_Resistant": (-1, 1.1, 0.1),
    "Local_Morans_i_Sensitive": (-1, 1.1, 0.1),
    "NN_Resistant": (1, 5, 0.2),
    "NN_Sensitive": (1, 5, 0.2),
}


def main(data_type, run_local):
    run_cmd = "python3 -m" if run_local else "sbatch job.sb"
    output = []
    for feature_name in FEATURE_REGISTRY.keys():
        output.append(f"{run_cmd} data_processing.processed_to_feature {data_type} {feature_name}\n")
    with open(f"process_features_{data_type}.sh", "w") as f:
        for output_line in output:
            f.write(output_line)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1], False)
    elif len(sys.argv) == 3:
        main(sys.argv[1], True)
    else:
        print("Please provide the data type and an extra flag if running locally.")
