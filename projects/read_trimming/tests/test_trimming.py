import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from trim.core import trim_adapter_exact, quality_trim_tail, sliding_window_trim, detect_adapter_ml


def test_trim_adapter_exact():
    seq = 'ACGTACGTAGATCGGAAGAGC'
    trimmed = trim_adapter_exact(seq, 'AGATCGGAAGAGC')
    assert trimmed.endswith('ACGTACGT')
    # no adapter
    assert trim_adapter_exact('AAAA', 'TTT') == 'AAAA'


def test_quality_trim_tail():
    seq = 'ACGTACGT'
    quals = [30,30,30,10,5,4,3,2]
    trimmed = quality_trim_tail(seq, quals, min_quality=10)
    assert trimmed == 'ACGT'


def test_sliding_window_trim():
    seq = 'AAAAACCCCC'
    quals = [30,30,30,30,1,1,1,1,1,1]
    trimmed = sliding_window_trim(seq, quals, window=3, min_avg=20)
    assert trimmed.startswith('AAAA')


def test_detect_adapter_ml():
    seq = 'XXXXAGATCGGAAGAGCYYYY'
    assert detect_adapter_ml(seq) is True
    # fake model
    def fake(s):
        return 0.9 if 'ADAPTER' in s else 0.0
    assert detect_adapter_ml('NOADAPTER', model_predict=fake, threshold=0.5) is False
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from trim.core import trim_adapter_exact, quality_trim_tail, sliding_window_trim, detect_adapter_ml


def test_trim_adapter_exact():
    seq = 'ACGTACGTAGATCGGAAGAGC'
    trimmed = trim_adapter_exact(seq, 'AGATCGGAAGAGC')
    assert trimmed.endswith('ACGTACGT')
    # no adapter
    assert trim_adapter_exact('AAAA', 'TTT') == 'AAAA'


def test_quality_trim_tail():
    seq = 'ACGTACGT'
    quals = [30, 30, 30, 10, 5, 4, 3, 2]
    trimmed = quality_trim_tail(seq, quals, min_quality=10)
    assert trimmed == 'ACGT'


def test_sliding_window_trim():
    seq = 'AAAAACCCCC'
    quals = [30, 30, 30, 30, 1, 1, 1, 1, 1, 1]
    trimmed = sliding_window_trim(seq, quals, window=3, min_avg=20)
    assert trimmed.startswith('AAAA')


def test_detect_adapter_ml():
    seq = 'XXXXAGATCGGAAGAGCYYYY'
    assert detect_adapter_ml(seq) is True
    # fake model
    def fake(s):
        return 0.9 if 'ADAPTER' in s else 0.0

    assert detect_adapter_ml('NOMATCH', model_predict=fake, threshold=0.5) is False