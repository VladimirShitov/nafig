import numpy as np
import pandas as pd
import pytest

from nafig.utils import _bin_features


@pytest.mark.parametrize(
    ("num_bins", "na_percentages", "bin_ranges", "expected_output"),
    [
        (
            4,
            pd.Series([10, 20, 30], index=("a", "b", "c")),
            [0, 25, 50, 75, 100],
            np.array([["a", "b"], ["c"], [], []], dtype=object),
        ),
    ],
)
def test_bin_features(num_bins, na_percentages, bin_ranges, expected_output):
    assert np.array_equal(
        _bin_features(num_bins, na_percentages, bin_ranges), expected_output
    )
