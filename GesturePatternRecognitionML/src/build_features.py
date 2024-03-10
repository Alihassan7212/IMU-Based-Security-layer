import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DataTransformation import LowPassFilter, PrincipalComponentAnalysis
from TemporalAbstraction import NumericalAbstraction
from FrequencyAbstraction import FourierTransformation

plt.style.use("fivethirtyeight")
plt.rcParams["figure.figsize"] = (20, 5)
plt.rcParams["figure.dpi"] = 100
plt.rcParams["lines.linewidth"] = 2


df = pd.read_csv("../data/interim/02_outliers_removed_chauvnets_new.csv")
print("Original df Shape", df.shape)
print("Cate1 Shape", (df[df["participant"] == 1]).shape)
print("Cate2 Shape", (df[df["participant"] == 2]).shape)

predictor_columns = list(df.columns[1:7])

# Fill missing values

for col in predictor_columns:
    df[col] = df[col].interpolate()
    
df.info()

# Butterworth lowpass filter -> Smoothing

df_lowpass = df.copy()
LowPass = LowPassFilter()

fs = 500
cuttoff = 2.5

df_lowpass = LowPass.low_pass_filter(df_lowpass, "ay", fs, cuttoff, order=5)

subset = df_lowpass[df_lowpass["participant"] == "Ali"]

fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
ax[0].plot(subset["ay"].reset_index(drop=True), label="raw data")
ax[1].plot(subset["ay_lowpass"].reset_index(drop=True), label="butterworth filter")
ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True)
ax[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True)

plt.show()

for col in predictor_columns:
    df_lowpass = LowPass.low_pass_filter(df_lowpass, col, fs, cuttoff, order=5)

    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
    ax[0].plot(df_lowpass[col].reset_index(drop=True), label="raw data")
    ax[1].plot(df_lowpass[col+"_lowpass"].reset_index(drop=True), label="butterworth filter")
    ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True)
    ax[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True)
    plt.savefig(f"reports/figures/{str(col+'_lowpass').title()}.png")
    plt.show()

print(df_lowpass.shape)

# PCA

df_pca = df_lowpass.copy()
PCA = PrincipalComponentAnalysis()

pc_values = PCA.determine_pc_explained_variance(df_pca, predictor_columns)

plt.figure(figsize=(10, 10))
plt.plot(range(1, len(predictor_columns)+1), pc_values)
plt.xlabel("principal component number")
plt.ylabel("explained variance")
plt.show()

df_pca = PCA.apply_pca(df_pca, predictor_columns, 3)

for participant in df_pca['participant'].unique():
    subset = df_pca[df_pca["participant"] == participant]
    subset[["pca_1", "pca_2", "pca_3"]].plot(title=f"PCA Components for {participant}")
    plt.legend(title='PCA Components')
    plt.xlabel('Index')
    plt.ylabel('Component Value')
    plt.savefig(f"reports/figures/{str('pca').title()}_{participant}.png")
    plt.show()

print(df_pca.shape)

# Sum of squares attributes

df_squared = df_pca.copy()
acc_r = (df_squared["ax"] ** 2) + (df_squared["ay"] ** 2) + (df_squared["az"] ** 2)
gyr_r = (df_squared["wx"] ** 2) + (df_squared["wy"] ** 2) + (df_squared["wz"] ** 2)

df_squared["acc_r"] = np.sqrt(acc_r)
df_squared["gyr_r"] = np.sqrt(gyr_r)

# Temporal abstraction

df_temporal = df_squared.copy()
NumAbs = NumericalAbstraction()

predictor_columns = predictor_columns + ["acc_r", "gyr_r"]

ws = 500
df_temporal_list = []

for participant in df_temporal["participant"].unique():
    for label in df_temporal[df_temporal["participant"] == participant]["label"].unique():
        subset = df_temporal[(df_temporal["participant"] == participant) & (df_temporal["label"] == label)].copy()
        for col in predictor_columns:
            subset = NumAbs.abstract_numerical(subset, [col], ws, "mean")
            subset = NumAbs.abstract_numerical(subset, [col], ws, "std")
        df_temporal_list.append(subset)

df_temporal = pd.concat(df_temporal_list).set_index("time", drop=True)
df_temporal = df_temporal.dropna()

for s in df_temporal["participant"].unique():
    for l in df_temporal[df_temporal["participant"] == s]["label"].unique():
        subset = df_temporal[(df_temporal["participant"] == s) & (df_temporal["label"] == l)]
        for col in predictor_columns:
            fig, ax = plt.subplots()
            ax.plot(subset[col], label=f"Raw {col}")
            ax.plot(subset[f"{col}_temp_mean_ws_{ws}"], label=f"{col} Mean Window {ws}")
            ax.plot(subset[f"{col}_temp_std_ws_{ws}"], label=f"{col} Std Dev Window {ws}")
            ax.legend()
            ax.set_title(f"{s} - {l} - {col}")
            plt.show()

# Frequency features

df_freq = df_squared.copy().reset_index()
FreqAbs = FourierTransformation()

fs = 500
ws = int(10)

df_freq = FreqAbs.abstract_frequency(df_freq, ["ay"], ws, fs)

subset = df_freq[df_freq["participant"] == "Ali"]
subset[["ay"]].plot()
subset[
    [
        "ay_max_freq",
        "ay_freq_weighted",
        "ay_pse",
        "ay_freq_71.429_Hz_ws_14",
        "ay_freq_250.0_Hz_ws_14"
    ]
].plot()
plt.show()

df_freq_list = []

for participant in df_freq["participant"].unique():
    for label in df_freq[df_freq["participant"] == participant]["label"].unique():
        subset = df_freq[(df_freq["participant"] == participant) & (df_freq["label"] == label)].copy()
        subset = FreqAbs.abstract_frequency(subset, predictor_columns, ws, fs)
        df_freq_list.append(subset)

df_freq = pd.concat(df_freq_list).set_index("time", drop=True)

# Dealing with overlapping windows - overfitting
df_freq = df_freq.dropna()
print(df_freq.shape)

subset = df_freq[(df_freq["participant"] == "Osama") & (df_freq["label"] == 8)]
subset[["ax"]].plot()
subset[
    [
        "ay_max_freq",
        "ay_freq_weighted",
        "ay_pse",
        "ay_freq_71.429_Hz_ws_14",
        "ay_freq_250.0_Hz_ws_14"
    ]
].plot()
plt.show()

df_freq.to_csv("data/interim/03_data_features_new.csv", index=False)
