import json
import os
from pathlib import Path

CONFIG_FILE_LOCATION = os.path.join(os.path.expanduser("~"), "Config", "RusePollutionWebsite.json")

CONFIG_TEMPLATE = {'data_db': "", 'website-db': ""}


class Config:
    def __init__(self):
        cfg = read_config()

        self.data_db_path = Path(cfg['data_db'])
        self.website_db_path = Path(cfg['website-db'])


def read_config() -> dict:
    if not os.path.exists(CONFIG_FILE_LOCATION):
        with open(CONFIG_FILE_LOCATION, 'w', encoding="UTF8") as f:
            f.write(json.dumps(CONFIG_TEMPLATE, indent=2))

    with open(CONFIG_FILE_LOCATION, 'r', encoding="UTF8") as f:
        config = json.load(f)

    return config
