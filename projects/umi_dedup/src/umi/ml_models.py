"""Lightweight ML model utilities for UMI error prediction.

This module provides a small wrapper around scikit-learn models used to
predict the probability that a UMI/read is an error, based on simple
features (read count, nearest edit distance, average base quality).

The implementation intentionally keeps the API small and testable: you can
train a model with `fit(X, y)`, call `predict_proba(X)` and persist the
model with `save`/`load`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence
import pickle
import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
except Exception:  # pragma: no cover - sklearn may not be available in all environments
    LogisticRegression = None


@dataclass
class UMIErrorPredictor:
    """Wrapper for a logistic regression classifier predicting UMI errors."""
    model: Optional[object] = None

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[int]) -> None:
        """Fit the model on features X and binary labels y.

        Features expected: [count, nearest_distance, avg_quality]
        """
        if LogisticRegression is None:
            raise RuntimeError("scikit-learn is required for training")
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        clf = LogisticRegression(solver="liblinear")
        clf.fit(X, y)
        self.model = clf

    def predict_proba(self, X: Sequence[Sequence[float]]) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if self.model is None:
            # Fallback heuristic: logistic over count and quality
            counts = X[:, 0]
            dist = X[:, 1]
            qual = X[:, 2] if X.shape[1] > 2 else np.zeros(len(counts))
            score = 1.0 / (1.0 + np.exp(-((dist - 0.5) * 2.0 - np.log1p(counts) + (30 - qual)/10)))
            return np.vstack([1 - score, score]).T
        return self.model.predict_proba(X)

    def save(self, path: str) -> None:
        with open(path, "wb") as fh:
            pickle.dump(self.model, fh)

    def load(self, path: str) -> None:
        with open(path, "rb") as fh:
            self.model = pickle.load(fh)
"""Neural network-based error prediction and UMI analysis models."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from torch.utils.data import Dataset, DataLoader

@dataclass
class UMIErrorPrediction:
    """Prediction results from error model."""
    probability: float
    confidence: float
    suggested_correction: Optional[str]
    quality_score: float

# If torch is available, provide neural-network utilities under different names
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from typing import List, Tuple


    class TorchUMIErrorNet(nn.Module):
        """Neural network for UMI error prediction (PyTorch).

        Note: this is an advanced model used for research/production where
        GPU acceleration is available. It is provided here as an optional
        component and is not used by the lightweight scikit-learn wrapper.
        """
        def __init__(self, sequence_length: int, embedding_dim: int = 32, hidden_dim: int = 64):
            super().__init__()
            self.embedding = nn.Embedding(5, embedding_dim)  # ACGTN
            self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
            self.attention = nn.MultiheadAttention(2 * hidden_dim, num_heads=4)
            self.fc1 = nn.Linear(2 * hidden_dim, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, 1)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.embedding(x)
            x, _ = self.lstm(x)
            x, _ = self.attention(x, x, x)
            x = torch.mean(x, dim=1)
            x = F.relu(self.fc1(x))
            return torch.sigmoid(self.fc2(x))


    class TorchUMIClusterNet(nn.Module):
        """Neural network for UMI clustering decisions (PyTorch)."""
        def __init__(self, sequence_length: int, embedding_dim: int = 32):
            super().__init__()
            self.embedding = nn.Embedding(5, embedding_dim)
            self.conv1 = nn.Conv1d(embedding_dim, 64, kernel_size=3)
            self.conv2 = nn.Conv1d(64, 32, kernel_size=3)
            self.fc = nn.Linear(32 * max(1, sequence_length - 4), 1)

        def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
            x1 = self.embedding(x1).transpose(1, 2)
            x2 = self.embedding(x2).transpose(1, 2)
            x1 = F.relu(self.conv1(x1))
            x2 = F.relu(self.conv1(x2))
            x1 = F.relu(self.conv2(x1))
            x2 = F.relu(self.conv2(x2))
            x = torch.abs(x1 - x2)
            x = x.view(x.size(0), -1)
            return torch.sigmoid(self.fc(x))


    def predict_umi_errors(
        sequences: List[str],
        model: TorchUMIErrorNet,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ) -> List[UMIErrorPrediction]:
        """Predict errors in UMI sequences using neural network model."""
        nucleotide_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
        tensors = []
        for seq in sequences:
            tensor = torch.tensor([nucleotide_map.get(n, 4) for n in seq], device=device)
            tensors.append(tensor)

        x = torch.nn.utils.rnn.pad_sequence(tensors, batch_first=True, padding_value=4)
        model.to(device)
        model.eval()

        with torch.no_grad():
            predictions = model(x)

        results = []
        for i, pred in enumerate(predictions):
            results.append(UMIErrorPrediction(
                probability=float(pred.squeeze()),
                confidence=0.0,
                suggested_correction=None,
                quality_score=float(pred.squeeze())
            ))

        return results


    def should_cluster_umis(
        umi1: str,
        umi2: str,
        model: TorchUMIClusterNet,
        threshold: float = 0.5,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ) -> Tuple[bool, float]:
        nucleotide_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
        tensor1 = torch.tensor([nucleotide_map.get(n, 4) for n in umi1], device=device).unsqueeze(0)
        tensor2 = torch.tensor([nucleotide_map.get(n, 4) for n in umi2], device=device).unsqueeze(0)

        model.to(device)
        model.eval()

        with torch.no_grad():
            prediction = model(tensor1, tensor2)

        probability = float(prediction.squeeze())
        return probability >= threshold, probability
except Exception:
    # If torch is not available, do not expose deep-learning utilities
    TorchUMIErrorNet = None
    TorchUMIClusterNet = None
