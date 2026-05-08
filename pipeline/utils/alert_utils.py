"""Utility functions for alert management."""

import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    Calculate statistics for array data.

    Args:
        data: NumPy array

    Returns:
        Dictionary with min, max, mean, std
    """
    try:
        data_clean = data[~np.isnan(data)]
        return {
            "min": float(np.min(data_clean)),
            "max": float(np.max(data_clean)),
            "mean": float(np.mean(data_clean)),
            "std": float(np.std(data_clean)),
        }
    except Exception as e:
        logger.error(f"Failed to calculate statistics: {e}")
        return {}


def detect_anomaly(
    current_value: float,
    historical_values: List[float],
    threshold_std: float = 2.0,
) -> Tuple[bool, float]:
    """
    Detect anomaly using z-score method.

    Args:
        current_value: Current value to test
        historical_values: List of historical values
        threshold_std: Number of standard deviations for threshold

    Returns:
        Tuple of (is_anomaly, z_score)
    """
    try:
        if len(historical_values) < 2:
            return False, 0.0

        values_clean = [v for v in historical_values if v is not None]
        if not values_clean:
            return False, 0.0

        mean = np.mean(values_clean)
        std = np.std(values_clean)

        if std == 0:
            return False, 0.0

        z_score = (current_value - mean) / std
        is_anomaly = abs(z_score) > threshold_std

        return is_anomaly, z_score

    except Exception as e:
        logger.error(f"Failed to detect anomaly: {e}")
        return False, 0.0


def classify_severity(
    z_score: float, anomaly_type: str
) -> str:
    """
    Classify severity based on z-score and anomaly type.

    Args:
        z_score: Z-score value
        anomaly_type: Type of anomaly (pollution_spike, heat_wave, etc.)

    Returns:
        Severity level (low, medium, high, critical)
    """
    abs_z = abs(z_score)

    if abs_z < 2.5:
        return "low"
    elif abs_z < 3.0:
        return "medium"
    elif abs_z < 3.5:
        return "high"
    else:
        return "critical"
