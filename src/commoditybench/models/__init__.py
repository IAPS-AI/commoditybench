"""Model provider adapters behind a common interface."""

from .base import ClassifierModel, Prediction
from .registry import build_model, available_models

__all__ = ["ClassifierModel", "Prediction", "build_model", "available_models"]
