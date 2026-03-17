from subprocess import run

from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class Training(DriverTimeInvariant):
    """
    Trains an Anemoi model.
    """

    # Public tasks

    @task
    def anemoi_config(self):
        """
        The anemoi-training default and custom configs, provisioned to the rundir.
        """
        yield self.taskname("training config")
        path = self.rundir / "training.yaml"
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        logfile = self.rundir / "config.log"
        run(
            "anemoi-training config generate >%s 2>&1" % logfile,
            check=False,
            cwd=self.rundir,
            shell=True,
        )
        config = get_yaml_config(self.rundir / "config.yaml")
        if "defaults" in config:
            del config["defaults"]
        config.update_from(self.config["anemoi"])
        config.dump(path)

    @task
    def runscript(self):
        """
        Script to run the training executable after removing any specified config keys.
        """
        yield self.taskname("training runscript")
        path = self._runscript_path
        yield Asset(path, path.is_file)
        yield None
        if rm := self._config.get("remove"):
            rmkeys = " ".join(f"~{k}" for k in rm)
            self._config["execution"]["executable"] += f" {rmkeys}"
        self._write_runscript(path)

    @collection
    def provisioned_rundir(self):
        """
        Rundir provisioned with the training config and runscript.
        """
        yield self.taskname("provisioned run directory")
        yield [
            self.anemoi_config(),
            self.runscript(),
        ]

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "training"
