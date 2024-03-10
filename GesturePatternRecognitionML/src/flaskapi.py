from flask import Flask, request, jsonify
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from src.remove_outliers import *
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Load your pre-trained model
model_path = '../reports/results/decision_tree_model.joblib'  # Update this path
model = joblib.load(model_path)


def process_firestore_data(cred_path, collection_name, output_csv_path, uuid):
    """
    Fetch data from Firestore, process it into a DataFrame, and save it to a CSV file.

    Parameters:
    - cred_path: Path to the Firebase Admin SDK JSON credentials file.
    - collection_name: Name of the Firestore collection to fetch data from.
    - output_csv_path: Path to save the processed DataFrame as a CSV file.
    """
    # Initialize Firebase app
    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    # Connect to Firestore
    db = firestore.client()

    # Fetch documents from the specified collection
    docs = db.collection(collection_name).get()

    # Process documents into a DataFrame
    final_df = pd.DataFrame()
    participant_counter = 1
    for doc in docs:
        if uuid == doc:
            data = doc.to_dict()
            sub_df = pd.DataFrame()
            for label, d in data.items():
                df = pd.DataFrame(d)
                df["label"] = label
                sub_df = pd.concat([sub_df, df])
            sub_df["participant"] = participant_counter
            participant_counter += 1
            final_df = pd.concat([final_df, sub_df])
        else:
            return {'status': False}

    # Rename and reorder DataFrame columns
    if final_df:
        final_df.columns = ["ax", "ay", "wx", "wy", "wz", "az", "time", "label", "participant"]
        new_order = ['time', 'ax', 'ay', 'az', 'wx', 'wy', 'wz', 'participant', 'label']
        final_df = final_df[new_order]

    # Save the processed DataFrame to CSV
    final_df.to_csv(output_csv_path, index=False)
    print(f"Data processed and saved to {output_csv_path}")
    return {'status': True}


@app.route('/predict', methods=['POST'])
def predict():
    # Example expecting JSON with a list of instances
    data = request.get_json()
    instances = data.get('instances', [])
    predictions = model_func().predict(instances)
    return jsonify(predictions.tolist())


@app.route('/train', methods=['POST', 'GET'])
def train():
    data = request.get_json()
    uuid = data.get('uuid', [])

    cred_path = "../data/guestureoauth-firebase-adminsdk-2yrpo-f951a66b8a.json"
    collection_name = "inputs"
    output_csv_path = "../data/interim/01_data_processed_new.csv"
    process_firestore_data(cred_path, collection_name, output_csv_path, uuid)

    df = pd.read_csv(output_csv_path)
    X, y = df.drop("participant", axis=1), df["participant"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Retrain the model
    model_func().fit(X_train, y_train)

    # Optionally save the retrained model
    model_path = "../reports/results/decision_tree_model.joblib"
    joblib.dump(model, model_path)

    # Test the retrained model
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return jsonify({'message': 'Model retrained', 'accuracy': accuracy})


def model_func():
    model = joblib.load("../reports/results/decision_tree_model.joblib")
    return model


if __name__ == '__main__':
    app.run(debug=True)
