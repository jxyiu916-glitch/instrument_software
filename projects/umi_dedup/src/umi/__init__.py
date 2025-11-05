"""UMI deduplication package.

Public functions are provided in `dedup`, `clustering`, `consensus`, and
`ml_models` modules. This package contains production-ready algorithms used by
the molecule counting and downstream analysis pipelines.
"""

from .dedup import deduplicate, collapse_directional
from .clustering import cluster, hamming_distance
from .consensus import consensus
from .ml_models import UMIErrorPredictor

__all__ = [
	"deduplicate",
	"collapse_directional",
	"cluster",
	"hamming_distance",
	"consensus",
	"UMIErrorPredictor",
]
