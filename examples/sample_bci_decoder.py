"""
Example: Benchmarking a Continuous BCI Neural Decoder on Substrate Drift (SDR).
Evaluates decoder retention under non-stationary cortical manifold covariance shift.
"""

from typing import List
from cyborgbench.tasks.neural_drift import NeuralDriftTask


class AdaptiveBCIDecoder:
    """
    Simulated BCI decoder with online ridge projection.
    """
    def __init__(self, channels: int = 64, out_dim: int = 2):
        self.channels = channels
        self.out_dim = out_dim
        # Initialize default identity projection
        self.weights = [[0.05 for _ in range(out_dim)] for _ in range(channels)]

    def predict(self, X: List[List[float]]) -> List[List[float]]:
        preds = []
        for row in X:
            p = [sum(row[i] * self.weights[i][k] for i in range(len(row))) for k in range(self.out_dim)]
            preds.append(p)
        return preds


def main():
    print("=== Evaluating BCI Decoder on Substrate Drift Task (SDR) ===")
    task = NeuralDriftTask(num_channels=64, num_samples=400, seed=42)
    decoder = AdaptiveBCIDecoder()

    result = task.run(
        custom_decoder=None,  # Benchmarks standard baseline ridge adaptation
        drift_angle_deg=20.0,
        gain_shift=1.15,
        channel_drop_rate=0.10
    )

    print(f"Task Name:             {result.task_name}")
    print(f"Neural Drift Score:    {result.score:.2f} / 100.0")
    print(f"Baseline R²:           {result.baseline_r2:.4f}")
    print(f"Drift R²:              {result.drift_r2:.4f}")
    print(f"Retention Ratio:       {result.retention_ratio * 100:.1f}%")
    print(f"Tracking RMSE:         {result.mean_tracking_rmse:.4f}")
    print(f"Channels Dropped:      {result.channels_dropped}")
    print(f"Passed:                {result.passed}")


if __name__ == "__main__":
    main()
