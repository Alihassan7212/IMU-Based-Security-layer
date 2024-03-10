import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from IPython.display import display

mpl.rcParams["figure.figsize"] = (20, 5)
mpl.rcParams["figure.dpi"] = 100


df = pd.read_csv("../data/interim/01_data_processed_new.csv")

for label in df["participant"].unique():
    subset = df[df["participant"] == label]
    fig, ax = plt.subplots()
    plt.plot(subset['ax'].reset_index(drop=True), label=label)
    plt.legend()
    plt.show()


labels = df["label"].unique()
participants = df["participant"].unique()

for label in labels:
    for participant in participants:
        combined_plot_df = df.query(f"label == {label}").query(f"participant == '{participant}'").reset_index()
        
        fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
        combined_plot_df[["ax", "ay", "az"]].plot(ax=ax[0])
        combined_plot_df[["wx", "wy", "wz"]].plot(ax=ax[1])
        
        ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True)
        ax[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True)
        
        ax[1].set_xlabel("samples")
        
        plt.savefig(f"reports/figures/{str(label).title()}_{participant}_new.png")
        plt.show()
        