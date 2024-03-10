import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd


cred = credentials.Certificate("data/guestureoauth-firebase-adminsdk-2yrpo-f951a66b8a.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection('inputs').get()

print(len(docs))

final_df = pd.DataFrame()
c = 1
for doc in docs:
    data = doc.to_dict()

    sub_df = pd.DataFrame()

    for i, d in data.items():
        df = pd.DataFrame(d)
        df["label"] = i
        sub_df = pd.concat([sub_df, df])

    sub_df["participant"] = c
    c += 1
    final_df = pd.concat([final_df, sub_df])

print(final_df.shape)
print(final_df.head())
print(final_df["label"].unique(), final_df["participant"].unique())

final_df.columns = ["ax", "ay", "wx", "wy", "wz", "az", "time", "label", "participant"]
new_order = ['time', 'ax', 'ay', 'az', 'wx', 'wy', 'wz', 'participant', 'label']
final_df = final_df[new_order]


final_df.to_csv("data/interim/01_data_processed_new.csv", index=False)
