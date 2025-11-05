"""Core UMI deduplication and analysis functionality with ML integration."""

from __future__ import annotations  # Enable postponed evaluation of type annotations

# Standard library imports
import logging
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any, Dict, Iterable, List, Optional, Protocol, Set,
    TYPE_CHECKING, Tuple, TypeVar, Union, cast
)

# Third-party imports
import numpy as np

# Protocol definitions for type checking
class HasQualityScore(Protocol):
    """Protocol for objects with quality score and probability."""
    quality_score: float
    probability: float

class HasDevice(Protocol):
    """Protocol for objects with device property."""
    device: str

# Type variables for generic types
T = TypeVar('T')
UMIErrorType = TypeVar('UMIErrorType', bound=HasQualityScore)
ModelType = TypeVar('ModelType', bound=HasDevice)

# Optional dependency flags
HAS_ML_DEPS = False
HAS_VIZ_DEPS = False

# Type-only imports for static type checking
if TYPE_CHECKING:
    import dash  # type: ignore
    import pandas as pd  # type: ignore
    import plotly.graph_objects as go  # type: ignore
    import torch  # type: ignore
    from .ml_models import (  # type: ignore
        ModelType, PredictionOutput, UMIClusterPredictor,
        UMIErrorPrediction, UMIErrorPredictor,
    )
    from .visualization import UMIVisualizationData  # type: ignore

# Optional ML dependencies
UMIErrorPredictor: Any = None
UMIClusterPredictor: Any = None
predict_umi_errors: Any = None
should_cluster_umis: Any = None
UMIErrorPrediction: Any = None

try:
    from .ml_models import (  # type: ignore
        UMIErrorPredictor,
        UMIClusterPredictor,
        predict_umi_errors,
        should_cluster_umis,
        UMIErrorPrediction
    )
    import torch  # type: ignore
    HAS_ML_DEPS = True
except ImportError as e:
    warnings.warn(
        f"ML dependencies not available ({str(e)}). Some functionality will be limited. "
        "To enable all features: pip install -r requirements-ml.txt"
    )

# Optional visualization dependencies
go: Any = None
pd: Any = None
UMIVisualizationData: Any = None
create_dashboard: Any = None

try:
    import plotly.graph_objects as go  # type: ignore
    import pandas as pd  # type: ignore
    from .visualization import UMIVisualizationData, create_dashboard  # type: ignore
    HAS_VIZ_DEPS = True
except ImportError:
    warnings.warn(
        "Visualization dependencies not available. Plotting will be disabled. "
        "To enable visualization: pip install -r requirements-ml.txt"
    )

logger = logging.getLogger(__name__)

class UMIProcessor:
    """High-performance UMI processing engine with ML integration.
    
    Requires ML dependencies to be installed for full functionality:
    pip install -r requirements-ml.txt
    """
    
    def __init__(
        self,
        error_model: Optional[Any] = None,
        cluster_model: Optional[Any] = None,
        use_gpu: bool = True,
        num_threads: int = 4
    ):
        if not HAS_ML_DEPS:
            raise ImportError(
                "ML dependencies not available. Install required packages: "
                "pip install -r requirements-ml.txt"
            )
        
        self.error_model = error_model
        self.cluster_model = cluster_model
        self.num_threads = num_threads
        
        # Set device with proper error handling
        self.device = "cpu"
        if use_gpu and HAS_ML_DEPS:
            try:
                if torch.cuda.is_available():  # type: ignore
                    self.device = "cuda"
            except (AttributeError, ImportError, RuntimeError) as e:
                logger.warning(f"GPU initialization failed: {e}")
        
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize ML models if not provided."""
        if self.error_model is None:
            try:
                self.error_model = UMIErrorPredictor(sequence_length=16)  # type: ignore
                # TODO: Load pre-trained weights
            except Exception as e:
                logger.error(f"Failed to initialize error model: {e}")
                raise ImportError("Error model initialization failed")
        
        if self.cluster_model is None:
            try:
                self.cluster_model = UMIClusterPredictor(sequence_length=16)  # type: ignore
                # TODO: Load pre-trained weights
            except Exception as e:
                logger.error(f"Failed to initialize cluster model: {e}")
                raise ImportError("Cluster model initialization failed")
    
    def process_batch(
        self,
        umi_list: List[str],
        quality_threshold: float = 0.9,
        cluster_threshold: float = 0.5
    ) -> Tuple[Dict[str, int], Optional[Any]]:  # For visualization data
        """Process a batch of UMIs with ML-enhanced accuracy.
        
        Args:
            umi_list: List of UMI sequences to process
            quality_threshold: Minimum quality score to keep UMI
            cluster_threshold: Minimum probability to cluster UMIs
            
        Returns:
            Tuple of (clusters, visualization_data). If visualization deps
            are not available, visualization_data will be None.
        """
        # Predict errors and quality scores
        error_predictions = cast(
            List["UMIErrorPrediction"],  # type: ignore
            predict_umi_errors(umi_list, self.error_model, self.device)  # type: ignore
        )
        
        # Filter low-quality UMIs
        filtered_umis = [
            umi for umi, pred in zip(umi_list, error_predictions)
            if pred.quality_score >= quality_threshold
        ]
        
        # Perform clustering
        clusters = self._cluster_umis(filtered_umis, cluster_threshold)
        
        # Prepare visualization data
        viz_data = self._prepare_visualization_data(
            umi_list,
            error_predictions,
            clusters
        )
        
        return clusters, viz_data
    
    def _cluster_umis(
        self,
        umi_list: List[str],
        threshold: float
    ) -> Dict[str, int]:
        """Cluster UMIs using ML-guided approach."""
        clusters: Dict[str, Set[str]] = defaultdict(set)
        processed = set()
        
        def process_umi_pair(umi1: str, umi2: str) -> Optional[Tuple[str, str, float]]:
            if umi1 != umi2 and umi2 not in processed:
                should_cluster, prob = should_cluster_umis(
                    umi1, umi2, self.cluster_model, threshold, self.device
                )
                if should_cluster:
                    return (umi1, umi2, prob)
            return None
        # Process UMIs in parallel
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            for umi1 in umi_list:
                if umi1 in processed:
                    continue
                
                # Find cluster members in parallel
                future_results = [
                    executor.submit(process_umi_pair, umi1, umi2)
                    for umi2 in umi_list
                ]
                
                cluster = {umi1}
                for future in future_results:
                    result = future.result()
                    if result:
                        _, umi2, _ = result
                        cluster.add(umi2)
                
                if cluster:
                    rep = min(cluster)  # Use lexicographically smallest as representative
                    clusters[rep].update(cluster)
                    processed.update(cluster)
        
        # Convert to count dictionary
        return {rep: len(members) for rep, members in clusters.items()}
    
    def _prepare_visualization_data(
        self,
        umi_list: List[str],
        error_predictions: List[Any],  # For UMIErrorPrediction
        clusters: Dict[str, int]
    ) -> Optional[Any]:  # For UMIVisualizationData
        """Prepare data for visualization dashboard.
        
        Returns None if visualization dependencies are not available.
        """
        if not HAS_VIZ_DEPS:
            warnings.warn("Visualization dependencies not available. Returning None.")
            return None
            
        error_rates = {
            umi: pred.probability
            for umi, pred in zip(umi_list, error_predictions)
        }
        
        quality_scores = {
            umi: pred.quality_score
            for umi, pred in zip(umi_list, error_predictions)
        }
        
        # Calculate cluster relationships
        relationships = []
        cluster_umis = list(clusters.keys())
        for i, umi1 in enumerate(cluster_umis):
            for umi2 in cluster_umis[i+1:]:
                _, prob = should_cluster_umis(
                    umi1, umi2, self.cluster_model, threshold=0.5, device=self.device
                )
                if prob > 0.2:  # Only include significant relationships
                    relationships.append((umi1, umi2, prob))
        
        return UMIVisualizationData(
            cluster_sizes=clusters,
            error_rates=error_rates,
            quality_scores=quality_scores,
            cluster_relationships=relationships
        )


def dedup_umis(umi_list: Iterable[str]) -> Dict[str, int]:
    """Legacy function for backwards compatibility.
    
    Note: This function requires ML dependencies to be installed:
    pip install -r requirements-ml.txt
    """
    # If ML dependencies are available, use the ML-backed processor.
    if HAS_ML_DEPS:
        try:
            processor = UMIProcessor()
            clusters, _ = processor.process_batch(list(umi_list))
            return clusters
        except Exception as e:
            logger.error(f"UMI deduplication failed (ML path): {e}")
            # Fall through to non-ML implementation as a robust fallback

    # Fallback: simple exact-count deduplication (preserves behavior expected
    # by legacy callers/tests which expect identical UMIs to be collapsed only).
    try:
        from collections import Counter
        return dict(Counter(umi_list))
    except Exception as e:
        logger.error(f"UMI deduplication failed (fallback path): {e}")
        raise RuntimeError("Failed to deduplicate UMIs") from e


def dedup_umis_clustered(umi_list: Iterable[str], max_distance: int = 1) -> Dict[str, int]:
    """Cluster-based deduplication convenience wrapper.

    Performs single-linkage clustering by Hamming distance and returns the
    representative -> count mapping.
    """
    from .dedup import deduplicate as _dedup
    return _dedup(list(umi_list), method='cluster', max_distance=max_distance)


def umi_consensus(members: List[str]) -> str:
    """Convenience wrapper for consensus building on a cluster of UMIs."""
    from .consensus import consensus as _cons
    return _cons(members)


def unique_umi_fraction(umi_list: Iterable[str]) -> float:
    """Calculate the fraction of unique UMIs in the dataset."""
    total = 0
    unique = set()
    for umi in umi_list:
        total += 1
        unique.add(umi)
    return len(unique) / total if total > 0 else 0.0


def hamming_distance(a: str, b: str) -> int:
    """Calculate Hamming distance between two sequences."""
    if len(a) != len(b):
        raise ValueError("UMIs must have equal length for Hamming distance")
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))


def analyze_umi_quality(
    umi_list: List[str],
    quality_threshold: float = 0.9
) -> Tuple[Dict[str, Any], float]:  # For UMIErrorPrediction
    """Analyze UMI quality using ML model.
    
    Requires ML dependencies to be installed for full functionality:
    pip install -r requirements-ml.txt
    """
    if not HAS_ML_DEPS:
        raise ImportError(
            "ML dependencies not available. Install required packages: "
            "pip install -r requirements-ml.txt"
        )
    
    try:
        processor = UMIProcessor()
        error_predictions = predict_umi_errors(umi_list, processor.error_model)  # type: ignore
    except Exception as e:
        logger.error(f"Failed to analyze UMI quality: {e}")
        raise RuntimeError("UMI quality analysis failed") from e
    
    # Calculate overall quality metrics
    high_quality = sum(1 for pred in error_predictions if pred.quality_score >= quality_threshold)
    quality_rate = high_quality / len(umi_list) if umi_list else 0.0
    
    return dict(zip(umi_list, error_predictions)), quality_rate


def create_analysis_dashboard(umi_list: List[str]) -> "dash.Dash":  # type: ignore
    """Create interactive analysis dashboard for UMI data."""
    if not HAS_ML_DEPS:
        raise ImportError(
            "Visualization dependencies not available. Install required packages: "
            "pip install -r requirements-ml.txt"
        )
    
    processor = UMIProcessor()
    clusters, viz_data = processor.process_batch(umi_list)
    return create_dashboard(viz_data)  # type: ignore


def get_ml_predictions(
    umi_list: List[str],
    use_gpu: bool = True
) -> List["UMIErrorPrediction"]:  # type: ignore
    """Get ML model predictions for a list of UMIs."""
    if not HAS_ML_DEPS:
        raise ImportError(
            "ML dependencies not available. Install required packages: "
            "pip install -r requirements-ml.txt"
        )
    
    processor = UMIProcessor(use_gpu=use_gpu)
    return predict_umi_errors(umi_list, processor.error_model)  # type: ignore


