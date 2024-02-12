import json
import os
from pathlib import Path

CONFIG_FILE_LOCATION = os.path.join(
    os.path.expanduser("~"), "Config", "RusePollutionWebsite", "RusePollutionWebsite.json"
)
GOOGLE_SECRET_LOCATION = os.path.join(
    os.path.expanduser("~"), "Config", "RusePollutionWebsite", "client_secret.json"
)
WEBSITE_SECRET_LOCATION = os.path.join(
    os.path.expanduser("~"), "Config", "RusePollutionWebsite", "website_secret.txt"
)

CONFIG_TEMPLATE = {'data_db': "", 'website-db': ""}


class Config:
    def __init__(self):
        if not os.path.exists(CONFIG_FILE_LOCATION):
            with open(CONFIG_FILE_LOCATION, 'w', encoding="UTF8") as f:
                f.write(json.dumps(CONFIG_TEMPLATE, indent=2))

        website_config = read_config(CONFIG_FILE_LOCATION)
        self.data_db_path = Path(website_config['data_db'])
        self.website_db_path = Path(website_config['website-db'])

        self.google_secret = read_config(GOOGLE_SECRET_LOCATION)['web']
        self.website_secret = read_file(WEBSITE_SECRET_LOCATION)


def read_config(file_location: str) -> dict:
    with open(file_location, 'r', encoding="UTF8") as f:
        config = json.load(f)

    return config


def read_file(file_location: str) -> str:
    with open(file_location, 'r', encoding="UTF-8") as f:
        content = f.read()

    return content
