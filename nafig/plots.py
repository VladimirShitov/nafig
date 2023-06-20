from typing import Literal, Union

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from nafig.utils import _bin_features


def na_text_barplot(
    df,
    num_bins=10,
    remove_empty_bins: Union[bool, Literal["right"]] = False,
    font_size=6,
    line_height=1,
    y_tick_step=10,
    hue=None,
    palette="tab10",
    fig_width=15,
    dpi=100,
    xlabel="NA percentage",
    xlabel_fontsize=12,
    title_pad=1,
    title="",
    title_loc="center",
    title_fontsize=12,
    background_color="white",
    legend_title: str = "Feature type",
    legend_fontsize: int = 12,
    legend_title_fontsize: int = 12,
) -> plt.Axes:
    """Visualize missing values in a dataframe. Splits features (columns) in bins grouped by proportion of NA values.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to visualize
    num_bins : int = 10
        Number of bins to split the features into
    remove_empty_bins : Union[bool, Literal["right"]] = False,
        Whether to remove bins that have no features in them. If "right", only the rightmost empty bins are removed.
    font_size : int = 6
        Font size for the feature names
    line_height : float = 1
        Height of each line in the plot
    y_tick_step : int = 10
        How frequently ticks for the number of features in a group are drawn
    hue : Union[Iterable, bool] = None
        Array-like object with length equal to the number of features in the dataframe. Can specify feature types
        or any other grouping variable for features. If None, data types of columns are used. If False, no hue is used.
    palette : str = "tab10"
        Palette to use for coloring the features
    fig_width : int = 15
        Width of the figure. Height is calculated based on the number of features in the highest bin and `line_height`
    dpi : int = 100
        Dots per inch for the figure
    xlabel : str = "NA percentage"
        Label for the x axis
    xlabel_fontsize : int = 12
        Font size for the x axis label
    title_pad : float = 1
        Padding for the title
    title : str = ""
        Title for the plot
    title_loc : str = "center"
        Location of the title. Can be one of "left", "center", "right"
    title_fontsize : int = 12
        Font size for the title
    background_color : str = "white"
        Background color for the plot
    legend_title : str = "Feature type"
        Title for the legend
    legend_fontsize : int = 12
        Font size for the legend
    legend_title_fontsize : int = 12
        Font size for the legend title

    Returns
    -------
    matplotlib axis

    """
    # table where 1 mean that feature is missed for an observations, and 0 that it is present
    na_df = df.isna().astype(int)

    # How many NAs does each feature has
    sorted_na_counts = na_df.sum(axis=0).sort_values(ascending=False)

    percentages = (sorted_na_counts / df.shape[0]) * 100

    # Split the data into bins
    bin_ranges = list(range(0, 101, 100 // num_bins))
    bin_labels = np.array(
        [f"{bin_ranges[i]}-{bin_ranges[i + 1]}%" for i in range(num_bins)]
    )

    binned_features = _bin_features(
        num_bins=num_bins, na_percentages=percentages, bin_ranges=bin_ranges
    )

    if hue is None:
        hue = df.dtypes

    # Sort features within each bin based on hue
    if hue is not False:
        for bin_features in binned_features:
            bin_features.sort(key=lambda feature: hue[df.columns.get_loc(feature)])

    bin_lengths = np.array([len(feature_bin) for feature_bin in binned_features])

    bins_to_leave = np.ones_like(binned_features, dtype=bool)

    if remove_empty_bins is True:
        bins_to_leave = bin_lengths > 0
    elif remove_empty_bins == "right":
        empty_bins = bin_lengths == 0
        for i in range(len(empty_bins) - 1, -1, -1):
            if not empty_bins[i]:
                break
            bins_to_leave[i] = False

    binned_features = binned_features[bins_to_leave]
    bin_labels = bin_labels[bins_to_leave]
    bin_lengths = bin_lengths[bins_to_leave]

    bin_indices = np.arange(len(binned_features))

    # Find the largest bin to extract y ticks from it
    largest_bin_idx = np.argmax(bin_lengths)
    max_features_per_bin = bin_lengths[largest_bin_idx]

    fig, ax = plt.subplots(figsize=(fig_width, 6), dpi=dpi)

    fig.patch.set_facecolor(background_color)
    ax.patch.set_facecolor(background_color)

    ax.set_xlim(-1, len(binned_features))
    ax.set_ylim(0, max_features_per_bin)

    if hue is not False:
        # Create a colormap based on the specified palette
        colors = sns.color_palette(palette, len(np.unique(hue)))
        cmap = dict(zip(np.unique(hue), colors))

        # Add legend with colors
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=cmap[label],
                markersize=5,
                label=label,
            )
            for label in np.unique(hue)
        ]
        ax.legend(
            handles=legend_elements,
            title=legend_title,
            fontsize=legend_fontsize,
            title_fontsize=legend_title_fontsize,
        )

    # Plot the feature names at specified coordinates
    for i, features in enumerate(binned_features):
        for j, feature in enumerate(features):
            color = "black" if hue is False else cmap[hue[df.columns.get_loc(feature)]]
            ax.text(
                i,
                j * line_height,
                feature,
                ha="center",
                va="bottom",
                fontdict={"size": font_size, "color": color},
            )

            # Add a new tick each `y_tick_step` iterations
            if i == largest_bin_idx and j % y_tick_step == 0 and j > 0:
                tick_y = (j - 1) * line_height
                ax.text(x=-1, y=tick_y, s=f"{j} –")

    title_y = max_features_per_bin * line_height + title_pad

    if title:
        if title_loc == "left":
            title_x = -1
        elif title_loc == "center":
            title_x = np.mean(bin_indices)
        else:
            title_x = np.max(bin_indices)

        ax.text(
            title_x, title_y, title, ha=title_loc, fontdict={"size": title_fontsize}
        )

    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize)

    ax.set_xticks(bin_indices, bin_labels)
    ax.set_yticks([], [])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    return ax
