import logging
from pathlib import Path
from subprocess import run

from iotaa import Asset, collection, external, task  # provided by uwtools
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class Inference(DriverTimeInvariant):
    """
    Runs anemoi-inference.
    """

    # Public tasks

    @task
    def anemoi_config(self):
        """
        Anemoi-inference config created with specified checkpoint path.
        """
        yield self.taskname("inference config")
        path = self.rundir / "inference.yaml"
        yield Asset(path, path.is_file)
        config = get_yaml_config(self.config["anemoi"])
        ckpt_dir = self.config.get("checkpoint_dir")
        ckpt_path = (
            max(
                Path(ckpt_dir).glob("*/inference-last.ckpt"),
                key=lambda p: p.stat().st_mtime,
            )
            if ckpt_dir
            else Path(config["checkpoint_path"])
        )
        yield self._checkpoint(ckpt_path)
        self._validate_checkpoint(ckpt_path)
        if ckpt_dir:
            config["checkpoint_path"] = str(ckpt_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        config.dump(path)

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname("provisioned run directory")
        yield [
            self.anemoi_config(),
            self.runscript(),
        ]

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        """
        Provide the name of this driver.
        """
        return "inference"

    # Private methods

    @external
    def _checkpoint(self, path: Path):
        """
        Checkpoint exists at the given path.
        """
        taskname = "Checkpoint exists %s" % path
        yield taskname
        yield Asset(path, path.exists)

    def _validate_checkpoint(self, ckpt_path: Path):
        """
        Warn if checkpoint is incompatible with the current anemoi-inference version.
        """
        logfile = self.rundir / "validate.log"
        result = run(
            "anemoi-inference validate %s >%s 2>&1" % (ckpt_path, logfile),
            check=False,
            cwd=self.rundir,
            shell=True,
        )
        if result.returncode:
            logging.warning(
                "Checkpoint %s may be incompatible with the current anemoi-inference version.",  # noqa: E501
                ckpt_path,
            )
