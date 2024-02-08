import os
import json
from pathlib import Path

CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser("~"), "Config", "RusePollutionWebsite.json")


class Config:
    def __init__(self):
        cfg = read_config()

        self.db_path = Path(cfg['db'])


def read_config() -> dict:
    with open(CONFIG_FILE_LOCATION, 'r', encoding="UTF8") as f:
        config = json.load(f)

    return config
