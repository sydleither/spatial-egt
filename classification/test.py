import pickle
import sys

from classification.common import get_model, read_and_clean_features
from classification.performance_plots import plot_all
from common import get_data_path


def test_model(save_loc, X, y, int_to_name):
    with open(f"{save_loc}/model.pkl", "rb") as f:
        clf = pickle.load(f)
    y_pred = clf.predict(X)
    plot_all(save_loc, int_to_name, [y], [y_pred], "test")


def main(experiment_name, *data_types):
    save_loc = get_data_path(".", f"model/{experiment_name}")
    X, y, int_to_name = read_and_clean_features(data_types[0])
    test_model(save_loc, X, y, int_to_name)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2:])
    else:
        print("Please provide an experiment name and the data types to train the model with.")
