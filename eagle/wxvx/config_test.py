from pathlib import Path

from uwtools.api.config import compose

ROOT = Path(__file__).parents[2]


def test_nested_stageiv_config(tmp_path):
    config = compose(
        [
            ROOT / "config" / "base.yaml",
            ROOT / "config" / "nested.yaml",
            ROOT / "config" / "ursa.yaml",
        ],
        realize=True,
        output_file=tmp_path / "nested.yaml",
    )

    stageiv = config["vx"]["grid2stageiv"]["lam"]["wxvx"]
    wxvx = stageiv["wxvx"]
    forecast_path = (
        "{{ meta.post_files }}/nested-lam.{{ yyyymmdd[:4] }}-"
        "{{ yyyymmdd[4:6] }}-{{ yyyymmdd[6:8] }}T{{ hh }}."
        "{{ meta.max_leadtime }}h.nc"
    )

    assert stageiv["name"] == "grid2stageiv-lam"
    assert stageiv["prewxvx"]["eagle_tools"]["vars_of_interest"][-1] == "accum_tp"
    assert wxvx["forecast"]["path"] == forecast_path
    assert wxvx["truth"] == {
        "name": "STAGEIV",
        "type": "grid",
        "url": (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/com/pcpanl/prod/"
            "pcpanl.{{ yyyymmdd }}/st4_conus.{{ yyyymmdd }}{{ hh }}.01h.grb2"
        ),
    }
    assert wxvx["regrid"] == {"method": "NEAREST", "to": "forecast"}
    assert wxvx["variables"] == {"accum_tp": {"level_type": "surface", "name": "tp"}}

    assert (
        "accum_tp"
        not in config["prewxvx"]["global"]["prewxvx"]["eagle_tools"]["vars_of_interest"]
    )
    assert (
        "accum_tp" not in config["vx"]["grid2grid"]["lam"]["wxvx"]["wxvx"]["variables"]
    )
    assert (
        "accum_tp" not in config["vx"]["grid2obs"]["lam"]["wxvx"]["wxvx"]["variables"]
    )
