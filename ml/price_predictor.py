"""
HarvestHub — Crop Price Prediction (Linear Regression)
-------------------------------------------------------
Trains one LinearRegression model per crop using historical
month/year data from data/crop_prices.csv.
Exposes  predict_price(crop_name, year, month) → float
"""

import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ── Globals ─────────────────────────────────────────────────────
_models = {}        # { crop_name: trained LinearRegression }
_crop_names = []    # list of unique crop names in the dataset
_is_loaded = False


def _data_path() -> str:
    """Return absolute path to the CSV regardless of working dir."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "data", "crop_prices.csv")


def load_models():
    """Read the CSV and train one model per crop.  Called once at startup."""
    global _models, _crop_names, _is_loaded

    df = pd.read_csv(_data_path())
    _crop_names = sorted(df["crop_name"].unique().tolist())

    for crop in _crop_names:
        subset = df[df["crop_name"] == crop].copy()

        # Features: year and month
        X = subset[["year", "month"]].values
        y = subset["price"].values

        model = LinearRegression()
        model.fit(X, y)
        _models[crop] = model

    _is_loaded = True


def get_crop_names() -> list:
    """Return the list of crops available for prediction."""
    if not _is_loaded:
        load_models()
    return _crop_names


def predict_price(crop_name: str, year: int, month: int) -> float:
    """
    Predict the price of *crop_name* for the given year/month.

    Returns
    -------
    float – predicted price (₹ per quintal), rounded to 2 decimals.
    """
    if not _is_loaded:
        load_models()

    if crop_name not in _models:
        raise ValueError(f"Unknown crop: {crop_name}. "
                         f"Available: {_crop_names}")

    X_new = np.array([[year, month]])
    price = _models[crop_name].predict(X_new)[0]
    return round(float(price), 2)
