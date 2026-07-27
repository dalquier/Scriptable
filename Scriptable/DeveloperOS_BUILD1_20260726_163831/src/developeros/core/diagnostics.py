"""Safe, non-sensitive runtime diagnostics."""

import os
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .version import __version__


@dataclass(frozen=True, slots=True)
class DiagnosticsReport:
    """Safe diagnostic snapshot suitable for logs and support output."""

    python_version: str
    operating_system: str
    architecture: str
    developeros_version: str
    current_directory: str
    implementation: str
    executable_name: str

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary."""

        return asdict(self)


def collect_diagnostics() -> DiagnosticsReport:
    """Collect safe runtime information without secrets or environment values."""

    return DiagnosticsReport(
        python_version=platform.python_version(),
        operating_system=f"{platform.system()} {platform.release()}".strip(),
        architecture=platform.machine() or "unknown",
        developeros_version=__version__,
        current_directory=str(Path.cwd()),
        implementation=platform.python_implementation(),
        executable_name=os.path.basename(sys.executable),
    )
