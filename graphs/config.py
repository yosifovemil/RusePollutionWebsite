import os
import json

CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser("~"), "Config", "RusePollutionWebsite.json")


class Config:
    def __init__(self):
        cfg = read_config()

        self._dataLocation = cfg['dataLocation']
        self._compounds = read_compounds(cfg)

    def get_data_location(self):
        return self._dataLocation

    def get_compounds(self):
        return self._compounds


class CompoundConfig:
    def __init__(self, config: dict):
        self._name = config['name']
        self._nameDisplay = config['nameDisplay']
        self._limits = config['limits']

    def get_limit(self, operation):
        if operation in self._limits.keys():
            return self._limits[operation]
        else:
            None

    def get_name(self):
        return self._name

    def get_name_display(self):
        return self._nameDisplay


def read_config() -> dict:
    with open(CONFIG_FILE_LOCATION, 'r', encoding="UTF8") as f:
        config = json.load(f)

    return config


def read_compounds(config: dict):
    compounds = []
    for compound_config in config['compounds']:
        compounds.append(
            CompoundConfig(compound_config)
        )

    return compounds
