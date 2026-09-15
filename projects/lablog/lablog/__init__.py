"""lablog - a local-first experiment tracker, comparison engine and dashboard.

lablog is intentionally dependency-free at runtime: it ships its own SQLite
storage layer, its own statistics engine (including Welch's t-test implemented
from the incomplete beta function) and its own HTTP API built on the standard
library.  That makes it trivial to run on an air-gapped workstation, in CI, or
inside a locked-down cluster where installing a service is not an option.
"""

from .compare import Comparison, compare_runs
from .config import ProjectConfig, load_config
from .models import Run, coerce_value, format_value, new_run_id
from .storage import Storage

__all__ = [
    "Storage",
    "Run",
    "Comparison",
    "ProjectConfig",
    "compare_runs",
    "load_config",
    "coerce_value",
    "format_value",
    "new_run_id",
    "__version__",
]

__version__ = "1.0.0"
