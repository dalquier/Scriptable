from pathlib import Path

from developeros.core.bootstrap import bootstrap
from developeros.core.diagnostics import collect_diagnostics
from developeros.core.lifecycle import KernelState


def test_complete_kernel_flow(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('[developeros]\nenvironment="test"\nlog_level="ERROR"\n', encoding="utf-8")
    kernel = bootstrap(config)
    kernel.start()
    assert kernel.state is KernelState.RUNNING
    assert kernel.health.report().to_dict()["status"] == "HEALTHY"
    assert collect_diagnostics().developeros_version == "0.1.0"
    kernel.stop()
    assert kernel.state is KernelState.STOPPED
