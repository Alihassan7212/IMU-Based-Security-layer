import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from LearningAlgorithms import ClassificationAlgorithms
import seaborn as sns
import itertools
from sklearn.metrics import accuracy_score, confusion_matrix

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['lines.linewidth'] = 1.5


df = pd.read_csv('../data/interim/03_data_features_new.csv')

X = df.drop(["participant", 'time'], axis=1)
y = df["participant"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
fig, ax = plt.subplots(figsize=(10, 5))
y_test.value_counts().plot(kind="bar", ax=ax, color="royalblue", label="Test")
plt.legend()
plt.show()

learner = ClassificationAlgorithms()

max_features = 10

selected_features, ordered_features, ordered_scores = learner.forward_selection(
    max_features, X_train, y_train
)
print(selected_features, ordered_features, ordered_scores)

plt.figure(figsize=(10, 5))
plt.plot(np.arange(1, max_features + 1, 1), ordered_scores)
plt.xlabel("Number of features")
plt.ylabel("Accuracy")
plt.xticks(np.arange(1, max_features + 1, 1))
plt.show()

basic_features = ["ax", "ay", "az", "wx", "wy", "wz"]
feature_set_1 = list(set(basic_features))

square_features = ["acc_r", "gyr_r"]
pca_features = ["pca_1", "pca_2", "pca_3"]
lowpass_features = [f for f in X.columns if "_lowpass" in f]
time_features = [f for f in X.columns if "_temp" in f]
freq_features = [f for f in X.columns if ("_freq" in f) or ("_pse" in f)]

feature_set_2 = list(set(basic_features + square_features + pca_features))
feature_set_3 = list(set(feature_set_2 + lowpass_features))
feature_set_4 = list(set(feature_set_2 + time_features))

selected_features = [
    "az_freq_0.0_Hz_ws_14",
    "ax_freq_0.0_Hz_ws_14",
    "gyr_r_pse",
    "ay_freq_0.0_Hz_ws_14",
    "gz_freq_0.714_Hz_ws_14",
    "gyr_r_freq_1.071_Hz_ws_14",
    "gz_freq_0.357_Hz_ws_14",
    "gx_freq_1.071_Hz_ws_14",
    "ax_max_freq",
    "gz_max_freq",
]

possible_feature_sets = [feature_set_1, feature_set_2, feature_set_3]
feature_names = ["Feature Set 1", "Feature Set 2", "Feature Set 3"]

iterations = 20
score_df = pd.DataFrame()

for i, f in zip(range(len(possible_feature_sets)), feature_names):
    print("Feature set:", i)
    selected_train_X = X_train[possible_feature_sets[i]]
    selected_test_X = X_test[possible_feature_sets[i]]

    performance_test_nn = 0
    performance_test_rf = 0

    for it in range(0, iterations):
        print("\tTraining neural network,", it)
        (
            class_train_y,
            class_test_y,
            class_train_prob_y,
            class_test_prob_y,
        ) = learner.feedforward_neural_network(
            selected_train_X,
            y_train,
            selected_test_X,
            gridsearch=True,
        )
        performance_test_nn += accuracy_score(y_test, class_test_y)

        print("\tTraining random forest,", it)
        (
            class_train_y,
            class_test_y,
            class_train_prob_y,
            class_test_prob_y,
        ) = learner.random_forest(
            selected_train_X, y_train, selected_test_X, gridsearch=True
        )
        performance_test_rf += accuracy_score(y_test, class_test_y)

    performance_test_nn = performance_test_nn / iterations
    performance_test_rf = performance_test_rf / iterations

    # And we run our deterministic classifiers:
    print("\tTraining KNN")
    (
        class_train_y,
        class_test_y,
        class_train_prob_y,
        class_test_prob_y,
    ) = learner.k_nearest_neighbor(
        selected_train_X, y_train, selected_test_X, gridsearch=True
    )
    performance_test_knn = accuracy_score(y_test, class_test_y)

    print("\tTraining decision tree")
    (
        class_train_y,
        class_test_y,
        class_train_prob_y,
        class_test_prob_y,
    ) = learner.decision_tree(
        selected_train_X, y_train, selected_test_X, gridsearch=True
    )
    performance_test_dt = accuracy_score(y_test, class_test_y)

    print("\tTraining naive bayes")
    (
        class_train_y,
        class_test_y,
        class_train_prob_y,
        class_test_prob_y,
    ) = learner.naive_bayes(selected_train_X, y_train, selected_test_X)

    performance_test_nb = accuracy_score(y_test, class_test_y)

    # Save results to dataframe
    models = ["NN", "RF", "KNN", "DT", "NB"]
    new_scores = pd.DataFrame(
        {
            "model": models,
            "feature_set": f,
            "accuracy": [
                performance_test_nn,
                performance_test_rf,
                performance_test_knn,
                performance_test_dt,
                performance_test_nb,
            ],
        }
    )
    score_df = pd.concat([score_df, new_scores])

score_df.sort_values(by="accuracy", ascending=False)
print(score_df)
score_df.to_csv(f"reports/results/model_performance.csv")

sns.barplot(x="feature_set", y="accuracy", data=score_df)
plt.xlabel("Model")
plt.ylabel("Accuracy")
plt.ylim(0.7, 1)

plt.legend(loc="lower right")
plt.show()

(class_train_y,
 class_test_y,
 class_train_prob_y,
 class_test_prob_y,
) = learner.decision_tree(
    X_train[feature_set_3], y_train, X_test[feature_set_3], gridsearch=True
)

accuracy = accuracy_score(class_test_y, class_test_y)

classes = class_test_prob_y.columns
cm = confusion_matrix(y_test, class_test_y, labels=classes)

plt.figure(figsize=(10, 10))
plt.imshow(cm, interpolation='nearest')
plt.title("Confusion matrix")

plt.colorbar()

tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes, rotation=45)
plt.yticks(tick_marks, classes)

plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)

thresh = cm.max() / 2.0
for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(
        j, i, format(cm[i, j]),
        horizontalalignment="center",
        color="white" if cm[i, j] > thresh else "black"
    )

plt.ylabel("True label")
plt.xlabel("Predicted label")
plt.grid(False)
plt.show()

