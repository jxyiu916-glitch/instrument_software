"""Plot rendering utilities.

This module provides small, dependency-light plotting helpers. When
matplotlib is available an SVG string is returned; otherwise a stable
placeholder string is returned so callers and tests can still run in
environments without GUI backends.
"""
from typing import Any, Dict, Sequence, Tuple, Optional
import io


def _safe_import_matplotlib():
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        return matplotlib, plt
    except Exception:
        return None, None


def render_plot(data: Dict[str, Any], kind: str = "line", width: int = 600, height: int = 400) -> str:
    """Render a simple plot as an SVG string.

    Supported kinds: 'line', 'hist', 'coverage'. The `data` shape depends on
    kind: for 'line' provide {'x': [...], 'y': [...]}, for 'hist' provide
    {'values': [...]}, and for 'coverage' provide {'coverage': [...]}.

    If matplotlib is unavailable, returns a stable placeholder SVG.
    """
    matplotlib, plt = _safe_import_matplotlib()
    if matplotlib is None or plt is None:
        return f"<svg><!-- placeholder {kind} --></svg>"

    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_subplot(1, 1, 1)

    try:
        if kind == "line":
            x = data.get("x")
            y = data.get("y")
            if x is None:
                x = list(range(len(y or [])))
            ax.plot(x, y or [])
            ax.set_xlabel(data.get("xlabel", "x"))
            ax.set_ylabel(data.get("ylabel", "y"))
        elif kind == "hist":
            vals = data.get("values", [])
            ax.hist(vals, bins=data.get("bins", 20))
            ax.set_xlabel(data.get("xlabel", "value"))
            ax.set_ylabel("count")
        elif kind == "coverage":
            cov = data.get("coverage", [])
            ax.plot(list(range(len(cov))), cov)
            ax.set_xlabel("position")
            ax.set_ylabel("coverage")
        else:
            ax.text(0.5, 0.5, f"Unsupported plot kind: {kind}", ha="center")

        ax.set_title(data.get("title", ""))

        bio = io.BytesIO()
        fig.tight_layout()
        fig.savefig(bio, format="svg")
        plt.close(fig)
        svg = bio.getvalue().decode("utf-8")
        return svg
    except Exception:
        # On any plotting error, return a stable placeholder so callers can
        # programmatically detect rendering failure without raising.
        try:
            plt.close(fig)
        except Exception:
            pass
        return f"<svg><!-- placeholder {kind} (error) --></svg>"
