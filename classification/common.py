import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import game_colors, get_data_path

feature_sets = {"prop_s":["Proportion_Sensitive"],
                "nc":["NC_Resistant_Mean", "NC_Resistant_SD", "NC_Resistant_Skew",
                      "NC_Sensitive_Mean", "NC_Sensitive_SD", "NC_Sensitive_Skew"],
                "nn":["NN_Resistant_Mean", "NN_Resistant_SD", "NN_Resistant_Skew",
                      "NN_Sensitive_Mean", "NN_Sensitive_SD", "NN_Sensitive_Skew"],
                "sfs2": ['NN_Resistant_SD', 'NN_Sensitive_SD', 'NC_Sensitive_SD', 'NC_Sensitive_Skew'],
                "top_pairs":["NC_Sensitive_Mean", "NN_Sensitive_Skew",
                             "SES", "Cross_Ripleys_k_Sensitive_Max",
                             "NC_Resistant_Skew",
                             "NC_Resistant_Mean", "Global_Morans_i_Sensitive",
                             "NC_Sensitive_Skew"],
                "top_pairs_noncorr":["NN_Sensitive_Skew", "NC_Resistant_SD",
                                    "SES", "KL_Divergence",
                                    "NN_Resistant_Skew", "NC_Sensitive_SD",
                                    "Proportion_Sensitive"]}
feature_sets = feature_sets | {"nc_plus":feature_sets["nc"]+["CPCF_Min"]}
feature_sets = feature_sets | {"nc_noncorr_plus":["NC_Resistant_Mean", "NC_Resistant_SD", "NC_Sensitive_SD", "CPCF_Min"]}


def df_to_xy(df, label_name):
    feature_names = list(df.columns)
    feature_names.remove(label_name)
    label_classes = list(game_colors.keys())
    class_to_int = {lc:i for i,lc in enumerate(label_classes)}
    int_to_class = {i:lc for i,lc in enumerate(label_classes)}
    X = df[feature_names].values.tolist()
    y = [class_to_int[x] for x in df[label_name].values]
    return X, y, int_to_class, feature_names


def clean_feature_data(df):
    df = df[df["game"] != "Unknown"]
    return df


def remove_correlated(df, label_names):
    feature_names = sorted(list(df.columns))
    [feature_names.remove(ln) for ln in label_names]
    num_features = len(feature_names)

    corr_matrix = df[feature_names].corr()
    features_to_keep = []
    for i in range(num_features):
        feature_i = feature_names[i]
        unique = True
        for j in range(i+1, num_features):
            feature_j = feature_names[j]
            corr = corr_matrix[feature_i][feature_j]
            if abs(corr) >= 0.9:
                unique = False
                break
        if unique:
            features_to_keep.append(feature_i)

    return features_to_keep


def read_and_clean_features(data_types, labels, feature_set_name):
    df = pd.DataFrame()
    for data_type in data_types:
        features_data_path = get_data_path(data_type, "features")
        df_dt = pd.read_csv(f"{features_data_path}/all.csv")
        df_dt = df_dt.drop(["source", "sample"], axis=1)
        df = pd.concat([df, df_dt])
    df = clean_feature_data(df)

    if feature_set_name == "all":
        feature_df = df
    elif feature_set_name == "noncorr":
        features = remove_correlated(df, labels)
        feature_df = df[features+labels]
    else:
        features = feature_sets[feature_set_name]
        feature_df = df[features+labels]

    return feature_df


def get_model():
    estimator = MLPClassifier(hidden_layer_sizes=(100,100,100), max_iter=500)
    clf = make_pipeline(StandardScaler(), estimator)
    return clf
