
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from database import fetch_all


def train_model():
    rows = fetch_all()

    if len(rows) < 30:
        print("Collect at least 30 samples before training.")
        return None, None

    df = pd.DataFrame(
        rows,
        columns=[
            "id", "timestamp", "cpu_usage",
            "memory_usage", "disk_usage",
            "net_sent", "net_recv", "label"
        ]
    )

    features = [
        "cpu_usage", "memory_usage",
        "disk_usage", "net_sent", "net_recv"
    ]

    X = df[features]
    y = df["label"]

    if y.nunique() < 2:
        print("Need at least two different load classes to train.")
        return None, None

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42,
            stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    model = RandomForestClassifier(
        n_estimators=100, random_state=42
    )
    model.fit(X_train, y_train)

    print("\nModel Evaluation:")
    print(classification_report(
        y_test, model.predict(X_test), zero_division=0
    ))

    return model, features


def predict_load(model, cpu, memory, disk, net_sent, net_recv):
    sample = pd.DataFrame([{
        "cpu_usage": cpu,
        "memory_usage": memory,
        "disk_usage": disk,
        "net_sent": net_sent,
        "net_recv": net_recv
    }])

    return model.predict(sample)[0]

