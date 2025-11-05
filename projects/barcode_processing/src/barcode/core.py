"""High-performance barcode processing for single-cell analysis.

This module provides essential barcode handling functionality for single-cell workflows:
1. Efficient barcode extraction from raw reads
2. Advanced error correction using white-listed sequences
3. Quality assessment and filtering
4. High-throughput parallel processing

Key Features:
- Pattern-based barcode extraction
- Hamming distance correction
- Whitelist management
- Quality filtering
- Performance optimized for large-scale single-cell data
"""

from typing import Iterable, Set, Dict, Tuple, List

# Re-export helpers from split modules for backwards compatibility
from .extractor import extract_barcode_from_read
from .correction import hamming_distance, correct_barcode
from .whitelist import build_whitelist, barcode_counts, top_barcodes
