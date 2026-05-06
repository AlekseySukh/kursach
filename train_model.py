import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

DATASET_FILE = Path(__file__).parent / "dataset.csv"
MODEL_FILE = Path(__file__).parent / "model.pkl"
ENCODERS_FILE = Path(__file__).parent / "encoders.pkl"


def train():
    dataframe = pd.read_csv(DATASET_FILE, encoding="utf-8-sig")

    encoders = {}
    for column in dataframe.select_dtypes(include=["object", "str"]).columns:
        encoder = LabelEncoder()
        dataframe[column] = encoder.fit_transform(dataframe[column]) 
        encoders[column] = encoder

    features = dataframe.drop(columns=["Вид"])
    target = dataframe["Вид"]

    features_train, features_test, target_train, target_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features_train, target_train)

    predictions = model.predict(features_test)
    accuracy = accuracy_score(target_test, predictions)

    print(f"Точность на тестовой выборке: {accuracy * 100:.1f}%")
    print()
    print(classification_report(
        target_test, predictions,
        target_names=encoders["Вид"].classes_
    ))

    with open(MODEL_FILE, "wb") as file:
        pickle.dump(model, file)

    with open(ENCODERS_FILE, "wb") as file:
        pickle.dump(encoders, file)

    print(f"Модель сохранена: {MODEL_FILE}")
    print(f"Энкодеры сохранены: {ENCODERS_FILE}")


if __name__ == "__main__":
    train()