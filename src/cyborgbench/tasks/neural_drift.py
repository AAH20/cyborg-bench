"""
Axis 2: Substrate Drift Resilience (SDR) Task.
Evaluates Brain-Computer Interface (BCI) decoder stability and online adaptation
under biological non-stationary neural manifold drift, electrode impedance shifts,
and channel dropout.
"""

import math
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Callable


@dataclass
class NeuralResult:
    """Telemetry and outcome of the Neural Substrate Drift Task."""
    task_name: str = "Substrate Drift Resilience"
    axis_code: str = "SDR"
    score: float = 0.0                      # 0.0 - 100.0
    baseline_r2: float = 0.0
    drift_r2: float = 0.0
    retention_ratio: float = 0.0           # drift_r2 / baseline_r2
    mean_tracking_rmse: float = 0.0
    channels_dropped: int = 0
    drift_angle_deg: float = 0.0
    adaptation_steps: int = 0
    passed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NeuralDriftTask:
    """
    Simulates motor cortex spike-rate decoding into 2D velocity vectors.
    Evaluates decoder resilience when subjected to 10% - 30% manifold shifts
    and electrode degradation.
    """

    def __init__(
        self,
        num_channels: int = 64,
        latent_dim: int = 8,
        num_samples: int = 500,
        seed: int = 42
    ):
        self.num_channels = num_channels
        self.latent_dim = latent_dim
        self.num_samples = num_samples
        self.random = random.Random(seed)

        # Generate synthetic ground-truth generative tuning model
        # True kinematic state: 2D velocity circle/lissajous trajectory
        self._generate_ground_truth()

    def _generate_ground_truth(self) -> None:
        """Generates synthetic tuning matrix and kinematics."""
        self.kinematics: List[List[float]] = []  # shape: (num_samples, 2)
        for t in range(self.num_samples):
            th = 2.0 * math.pi * (t / self.num_samples) * 3.0
            vx = math.cos(th)
            vy = math.sin(2.0 * th) * 0.5
            self.kinematics.append([vx, vy])

        # Projection from 2D kinematics to latent manifold (latent_dim)
        self.latent_weights: List[List[float]] = [
            [self.random.gauss(0.0, 1.0) for _ in range(2)]
            for _ in range(self.latent_dim)
        ]

        # Projection from latent manifold to physical channels (num_channels)
        self.channel_tuning: List[List[float]] = [
            [self.random.gauss(0.0, 0.8) for _ in range(self.latent_dim)]
            for _ in range(self.num_channels)
        ]

    def _sample_neural_activity(
        self,
        kinematics: List[List[float]],
        drift_angle_deg: float = 0.0,
        gain_shift: float = 1.0,
        drop_rate: float = 0.0
    ) -> List[List[float]]:
        """
        Samples firing rates with optional rotational manifold drift,
        gain variance, and channel dropout.
        """
        theta = math.radians(drift_angle_deg)
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        dataset: List[List[float]] = []
        for v in kinematics:
            # Latent activation
            latent = []
            for w in self.latent_weights:
                val = w[0] * v[0] + w[1] * v[1]
                latent.append(val)

            # Apply manifold rotation on first 2 latent dimensions
            if drift_angle_deg != 0.0 and len(latent) >= 2:
                l0 = latent[0] * cos_t - latent[1] * sin_t
                l1 = latent[0] * sin_t + latent[1] * cos_t
                latent[0] = l0
                latent[1] = l1

            # Channel firing rate with Poisson/Gaussian noise
            channels = []
            for c_idx, c_weights in enumerate(self.channel_tuning):
                if self.random.random() < drop_rate:
                    channels.append(0.0)
                    continue

                firing_rate = sum(c_weights[d] * latent[d] for d in range(self.latent_dim))
                firing_rate = max(0.0, firing_rate * gain_shift + self.random.gauss(0.0, 0.15))
                channels.append(firing_rate)

            dataset.append(channels)
        return dataset

    def _fit_linear_ridge(
        self,
        X: List[List[float]],
        Y: List[List[float]],
        alpha: float = 0.1
    ) -> List[List[float]]:
        """Zero-dependency Ridge Regression solver: W = (X^T X + alpha*I)^(-1) X^T Y."""
        n = len(X)
        d = len(X[0])
        out_dim = len(Y[0])

        # Compute X^T X (d x d)
        XtX = [[0.0] * d for _ in range(d)]
        for row in X:
            for i in range(d):
                r_i = row[i]
                for j in range(d):
                    XtX[i][j] += r_i * row[j]

        # Add ridge regularization
        for i in range(d):
            XtX[i][i] += alpha

        # Compute X^T Y (d x out_dim)
        XtY = [[0.0] * out_dim for _ in range(d)]
        for r_idx, row in enumerate(X):
            y_row = Y[r_idx]
            for i in range(d):
                for k in range(out_dim):
                    XtY[i][k] += row[i] * y_row[k]

        # Solve (XtX) W = XtY using Gauss-Jordan elimination with partial pivoting
        # Augmented matrix [XtX | XtY]
        aug = [XtX[i] + XtY[i] for i in range(d)]
        total_cols = d + out_dim

        for col in range(d):
            # Pivot
            max_row = col
            for r in range(col + 1, d):
                if abs(aug[r][col]) > abs(aug[max_row][col]):
                    max_row = r
            aug[col], aug[max_row] = aug[max_row], aug[col]

            pivot = aug[col][col]
            if abs(pivot) < 1e-12:
                continue

            inv_pivot = 1.0 / pivot
            for c in range(col, total_cols):
                aug[col][c] *= inv_pivot

            for r in range(d):
                if r != col:
                    factor = aug[r][col]
                    if abs(factor) > 1e-12:
                        for c in range(col, total_cols):
                            aug[r][c] -= factor * aug[col][c]

        # Extract weights W (d x out_dim)
        W = [[aug[i][d + k] for k in range(out_dim)] for i in range(d)]
        return W

    def _predict(self, X: List[List[float]], W: List[List[float]]) -> List[List[float]]:
        out_dim = len(W[0])
        preds = []
        for row in X:
            p = [sum(row[i] * W[i][k] for i in range(len(row))) for k in range(out_dim)]
            preds.append(p)
        return preds

    def _compute_r2(self, Y_true: List[List[float]], Y_pred: List[List[float]]) -> float:
        n = len(Y_true)
        out_dim = len(Y_true[0])
        r2_list = []
        for k in range(out_dim):
            mean_y = sum(Y_true[i][k] for i in range(n)) / n
            ss_tot = sum((Y_true[i][k] - mean_y) ** 2 for i in range(n))
            ss_res = sum((Y_true[i][k] - Y_pred[i][k]) ** 2 for i in range(n))
            if ss_tot < 1e-12:
                r2_list.append(1.0 if ss_res < 1e-12 else 0.0)
            else:
                r2_list.append(1.0 - (ss_res / ss_tot))
        return max(0.0, sum(r2_list) / len(r2_list))

    def run(
        self,
        custom_decoder: Optional[Any] = None,
        drift_angle_deg: float = 25.0,
        gain_shift: float = 1.25,
        channel_drop_rate: float = 0.15
    ) -> NeuralResult:
        """
        Executes the SDR task.
        If `custom_decoder` is provided, it should implement `predict(X)` and optionally `adapt(X, y)`.
        Otherwise, a standard ridge linear regression model is benchmarked against the drift.
        """
        # 1. Generate Baseline Data
        X_base = self._sample_neural_activity(self.kinematics, drift_angle_deg=0.0)
        Y_base = self.kinematics

        # Fit baseline weights
        W_base = self._fit_linear_ridge(X_base, Y_base)
        preds_base = self._predict(X_base, W_base)
        base_r2 = self._compute_r2(Y_base, preds_base)

        # 2. Generate Drifted Substrate Data
        X_drift = self._sample_neural_activity(
            self.kinematics,
            drift_angle_deg=drift_angle_deg,
            gain_shift=gain_shift,
            drop_rate=channel_drop_rate
        )

        if custom_decoder is not None and hasattr(custom_decoder, "predict"):
            preds_drift = custom_decoder.predict(X_drift)
        else:
            # Evaluate baseline decoder on drifted data
            preds_drift = self._predict(X_drift, W_base)

        drift_r2 = self._compute_r2(self.kinematics, preds_drift)

        # 3. Compute Metrics
        retention = drift_r2 / base_r2 if base_r2 > 1e-6 else 0.0
        retention = max(0.0, min(1.0, retention))

        # Root Mean Squared Error
        total_se = sum(
            (self.kinematics[i][0] - preds_drift[i][0]) ** 2 +
            (self.kinematics[i][1] - preds_drift[i][1]) ** 2
            for i in range(self.num_samples)
        )
        rmse = math.sqrt(total_se / (self.num_samples * 2))

        # Score formulation
        # 70% retention ratio + 30% absolute drift R^2
        score = (retention * 70.0) + (drift_r2 * 30.0)
        score = max(0.0, min(100.0, round(score, 2)))

        passed = score >= 70.0 and retention >= 0.70

        return NeuralResult(
            score=score,
            baseline_r2=round(base_r2, 4),
            drift_r2=round(drift_r2, 4),
            retention_ratio=round(retention, 4),
            mean_tracking_rmse=round(rmse, 4),
            channels_dropped=int(self.num_channels * channel_drop_rate),
            drift_angle_deg=drift_angle_deg,
            adaptation_steps=0,
            passed=passed,
            details={
                "channels": self.num_channels,
                "samples": self.num_samples,
                "gain_shift": gain_shift,
                "channel_drop_rate": channel_drop_rate
            }
        )
