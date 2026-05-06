import pickle
import pandas as pd
from pathlib import Path

MODEL_FILE = Path(__file__).parent.parent / "model.pkl"
ENCODERS_FILE = Path(__file__).parent.parent / "encoders.pkl"

_model = None
_encoders = None


def is_available() -> bool:
    return MODEL_FILE.exists() and ENCODERS_FILE.exists()


def _load_model():
    global _model, _encoders
    if _model is None or _encoders is None:
        with open(MODEL_FILE, "rb") as model_file:
            _model = pickle.load(model_file)
        with open(ENCODERS_FILE, "rb") as encoders_file:
            _encoders = pickle.load(encoders_file)


def reload_model():
    global _model, _encoders
    _model = None
    _encoders = None


def predict(input_values: dict) -> dict:
    _load_model()

    row = {}
    for column in _model.feature_names_in_:
        value = input_values.get(column)
        if column in _encoders:
            value = _encoders[column].transform([str(value)])[0]
        row[column] = float(value)

    dataframe = pd.DataFrame([row])

    predicted = _encoders["Вид"].inverse_transform(_model.predict(dataframe))[0]

    wood_names = _encoders["Вид"].classes_
    raw_probabilities = _model.predict_proba(dataframe)[0]

    probabilities = sorted(
        [(wood_names[i], raw_probabilities[i]) for i in range(len(wood_names))],
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "result": predicted,
        "probabilities": probabilities,
    }