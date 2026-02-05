import pandas as pd
import yaml
import os


def create_yaml(
    yaml_name,
    initial_conditions,
    init,
    end,
):
    with open(f"{yaml_name}.yaml", "r") as file:
        config = yaml.safe_load(file)
        
    if yaml_name == "inference":
        # remember in inference start and end mean what dates you want to run inference over
        config["start_date"] = initial_conditions.strftime("%Y-%m-%dT%H")
        config["end_date"] = initial_conditions.strftime("%Y-%m-%dT%H")
    else:
        config["source"]["t0"]["start"] = init.strftime("%Y-%m-%dT%H")
        config["source"]["t0"]["end"] = end.strftime("%Y-%m-%dT%H")
        

    init_str = initial_conditions.strftime("%Y-%m-%dT%H")
    updated_yaml_name = f"data/{yaml_name}_{init_str}.yaml"

    os.makedirs("data", exist_ok=True)
    with open(updated_yaml_name, "w") as conf:
        yaml.dump(config, conf)

    return None


def prep_workflow():
    # set init
    # first set to floor of 6 hours, as initialization are always only on 6 hr windwos
    # then go back one initialization (6hr) for intended latency
    initial_conditions = pd.Timestamp.now(tz="UTC").floor("6h") - pd.Timedelta("6h")

    # because inference wants previous timestep, we actually start loading data one timestep back from that
    init = initial_conditions - pd.Timedelta("6h")

    lead_time = 48
    end = initial_conditions + pd.Timedelta(f"{lead_time}h")

    # create gfs yaml
    create_yaml(
        yaml_name="gfs",
        initial_conditions=initial_conditions,
        init=init,
        end=end,
    )
    
    # create hrrr yaml
    create_yaml(
        yaml_name="hrrr",
        initial_conditions=initial_conditions,
        init=init,
        end=end,
    )

    # create inference yaml
    create_yaml(
        yaml_name="inference",
        initial_conditions=initial_conditions,
        init=init,
        end=end,
    )


if __name__ == "__main__":
    prep_workflow()
