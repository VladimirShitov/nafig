import numpy as np
import pandas as pd


def _bin_features(num_bins, na_percentages, bin_ranges) -> np.array:
    binned_features = [[] for _ in range(num_bins)]

    # Group features into respective bins
    for i, percentage in enumerate(na_percentages):
        for j in range(num_bins):
            if bin_ranges[j] <= percentage < bin_ranges[j + 1]:
                binned_features[j].append(na_percentages.index[i])
                break

    return np.array(binned_features, dtype=object)


def create_example_data(
    n_obs: int = 1000, n_var: int = 300, mean_na: float = 0.5, std_na: float = 0.3
) -> pd.DataFrame:
    """Create example data with missing values

    Parameters
    ----------
    n_obs : int = 1000
        Number of observations
    n_var : int = 300
        Number of features
    mean_na : float = 0.5
        Average proportion of missing values for each feature
    std_na : float = 0.3
        Standard deviation of the proportion of missing values for each feature

    Returns
    -------
    df : Dataframe with missing values
    feature_types : Array with feature types
    """
    data = np.random.normal(size=(n_obs, n_var))

    # Make some NAs for each feature
    for i in range(n_var):
        na_prop = np.random.normal(loc=mean_na, scale=std_na)
        na_prop = np.clip(na_prop, 0, 1)
        is_na = np.random.choice(np.arange(n_obs), size=int(na_prop * n_obs))
        data[is_na, i] = np.nan

    df = pd.DataFrame(data, columns=[f"feature_{i}" for i in range(n_var)])
    feature_types = np.random.choice(
        ["Continuous", "Categorical", "Binary"], size=df.shape[1]
    )

    return df, feature_types
