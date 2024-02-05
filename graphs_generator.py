import pandas as pd
from graphs.config import Config
from graphs import graph_maker


def read_data(compound: str, data_dir: str) -> pd.DataFrame:
    data = pd.read_csv("{data_dir}/{compound}.csv".format(data_dir=data_dir, compound=compound))
    data.DateTime = pd.to_datetime(data.DateTime)
    return data


def main():
    config = Config()

    for compound in config.get_compounds():
        compound_data = read_data(compound.get_name(), config.get_db())
        graph_maker.generate_html(compound_config=compound, raw_data=compound_data)


if __name__ == "__main__":
    main()
