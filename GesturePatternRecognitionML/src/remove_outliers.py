import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy
from sklearn.neighbors import LocalOutlierFactor

plt.style.use("fivethirtyeight")
plt.rcParams["figure.figsize"] = (20, 5)
plt.rcParams["figure.dpi"] = 100


df = pd.read_csv("../data/interim/01_data_processed_new.csv")
outlier_columns = list(df.columns[1:7])

df[outlier_columns[:3] + ["label"]].boxplot(by="label", figsize=(20, 10), layout=(1, 3))
df[outlier_columns[3:] + ["label"]].boxplot(by="label", figsize=(20, 10), layout=(1, 3))


def plot_binary_outliers(dataset, col, outlier_col, reset_index):

    dataset = dataset.dropna(axis=0, subset=[col, outlier_col])
    dataset[outlier_col] = dataset[outlier_col].astype("bool")

    if reset_index:
        dataset = dataset.reset_index()

    fig, ax = plt.subplots()

    plt.xlabel("samples")
    plt.ylabel("value")

    # Plot non outliers in default color
    ax.plot(
        dataset.index[~dataset[outlier_col]],
        dataset[col][~dataset[outlier_col]],
        "+",
    )
    # Plot data points that are outliers in red
    ax.plot(
        dataset.index[dataset[outlier_col]],
        dataset[col][dataset[outlier_col]],
        "r+",
    )

    plt.legend(
        ["outlier " + col, "no outlier " + col],
        loc="upper center",
        ncol=2,
        fancybox=True,
        shadow=True,
    )
    plt.show()
    
    
def mark_outliers_iqr(dataset, col):

    dataset = dataset.copy()

    Q1 = dataset[col].quantile(0.25)
    Q3 = dataset[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    dataset[col + "_outlier"] = (dataset[col] < lower_bound) | (
        dataset[col] > upper_bound
    )

    return dataset


for col in outlier_columns:
    dataset = mark_outliers_iqr(df, col)
    plot_binary_outliers(dataset=dataset, col=col, outlier_col=col+"_outlier", reset_index=True)


df1 = df[df["label"] == 2]
df1[outlier_columns[:3] + ["label"]].plot.hist(by="label", figsize=(20, 20), layout=(3, 3))
df1[outlier_columns[3:] + ["label"]].plot.hist(by="label", figsize=(20, 20), layout=(3, 3))


def mark_outliers_chauvenet(dataset, col, C=2):

    dataset = dataset.copy()
    # Compute the mean and standard deviation.
    mean = dataset[col].mean()
    std = dataset[col].std()
    N = len(dataset.index)
    criterion = 1.0 / (C * N)

    # Consider the deviation for the data points.
    deviation = abs(dataset[col] - mean) / std

    # Express the upper and lower bounds.
    low = -deviation / math.sqrt(C)
    high = deviation / math.sqrt(C)
    prob = []
    mask = []

    # Pass all rows in the dataset.
    print(len(dataset.index))
    for i in range(0, len(dataset.index)):
        # Determine the probability of observing the point
        prob.append(
            1.0 - 0.5 * (scipy.special.erf(high[i]) - scipy.special.erf(low[i]))
        )
        # And mark as an outlier when the probability is below our criterion.
        mask.append(prob[i] < criterion)
    dataset[col + "_outlier"] = mask
    return dataset


for col in outlier_columns:
    dataset = mark_outliers_chauvenet(df, col)
    plot_binary_outliers(dataset=dataset, col=col, outlier_col=col+"_outlier", reset_index=True)


# Unsupervised Outlier Detection using the Local Outlier Factor (LOF).

def mark_outliers_lof(dataset, columns, n=20):

    dataset = dataset.copy()

    lof = LocalOutlierFactor(n_neighbors=n)
    data = dataset[columns]
    outliers = lof.fit_predict(data)
    X_scores = lof.negative_outlier_factor_

    dataset["outlier_lof"] = outliers == -1
    return dataset, outliers, X_scores


dataset, outliers, X_score = mark_outliers_lof(df, outlier_columns)
for col in outlier_columns:
    plot_binary_outliers(dataset=dataset, col=col, outlier_col="outlier_lof", reset_index=True)


label = 0
for col in outlier_columns:
    dataset = mark_outliers_iqr(df[df["label"]==label], col)
    plot_binary_outliers(dataset=dataset, col=col, outlier_col=col+"_outlier", reset_index=True)
    
for col in outlier_columns:
    dataset = mark_outliers_chauvenet(df[df["label"]==label], col)
    plot_binary_outliers(dataset=dataset, col=col, outlier_col=col+"_outlier", reset_index=True)
    
dataset, outliers, X_score = mark_outliers_lof(df[df["label"]==label], outlier_columns)
for col in outlier_columns:
    plot_binary_outliers(dataset=dataset, col=col, outlier_col="outlier_lof", reset_index=True)


outliers_removed_df = df.copy()
for col in outlier_columns:
    for label in df["label"].unique():
        dataset = mark_outliers_chauvenet(df[df["label"] == label].reset_index(drop=True), col)
        dataset.loc[dataset[col+"_outlier"], col] = np.nan
        
        outliers_removed_df.loc[outliers_removed_df["label"] == label, col] = dataset[col]
        
        n_outliers = len(dataset) - len(dataset[col].dropna())
        print(f"Removed {n_outliers} from {col} for {label}")
        
        
for col in outlier_columns:
    for participant in df["participant"].unique():
        for label in df[df["participant"] == participant]["label"].unique():
            participant_label_data = df[(df["participant"] == participant) & (df["label"] == label)]

            dataset = mark_outliers_chauvenet(participant_label_data.reset_index(drop=True), col)
            dataset.loc[dataset[col+"_outlier"], col] = np.nan
            condition = (outliers_removed_df["participant"] == participant) & (outliers_removed_df["label"] == label)
            outliers_removed_df.loc[condition, col] = dataset[col]

            n_outliers = len(participant_label_data) - len(dataset[col].dropna())
            print(f"Removed {n_outliers} outliers from {col} for participant {participant} and label {label}")
        
outliers_removed_df.info()
outliers_removed_df.to_csv("data/interim/02_outliers_removed_chauvnets_new.csv", index=False)
