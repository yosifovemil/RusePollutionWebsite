import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np


def read_config() -> dict:
    with open("config.json", 'r', encoding="UTF8") as f:
        config = json.load(f)

    return config


def read_data(compound: str, config: dict) -> pd.DataFrame:
    data = pd.read_csv("{data_dir}/{compound}.csv".format(data_dir=config['dataLocation'], compound=compound))
    data.DateTime = pd.to_datetime(data.DateTime)
    return data


def perform_analysis(data: pd.DataFrame, operation: str, compound_config: dict) -> pd.DataFrame:
    resampled_data = data.resample('D', on='DateTime')

    limit = get_limit(compound_config, operation)

    if operation == 'mean':
        summarised_data = resampled_data.mean()
    elif operation == 'max':
        summarised_data = resampled_data.max()
    else:
        raise RuntimeError("Unknown operation ${op}".format(op=operation))

    summarised_data = summarised_data.reset_index()

    if limit is not None:
        summarised_data['Limit'] = np.where(summarised_data[compound_config['name']] >= limit, True, False)
    else:
        summarised_data['Limit'] = False

    return summarised_data


def bar_color(i: bool):
    if i:
        return "red"
    else:
        return "green"


def get_limit(compound_config: dict, operation: str):
    if operation in compound_config['limits'].keys():
        return int(compound_config['limits'][operation])
    else:
        return None


def get_subplot_titles(config: dict, operation: str):
    subplot_titles = []

    for compound in config['compounds']:
        limit = get_limit(compound, operation)
        title = compound['nameDisplay']
        if limit is not None:
            title += " - лимит {limit} µg/m3".format(limit=limit)

        subplot_titles.append(title)

    return subplot_titles


def make_graph(config: dict, operation: str) -> str:
    if operation == "mean":
        title = "Средни денонощни стойности"
    elif operation == "max":
        title = "Максимални денонощни стойности"

    graph = "<h2>{title}</h2>".format(title=title)

    subplot_titles = get_subplot_titles(config, operation)

    fig = make_subplots(rows=3, cols=3, subplot_titles=subplot_titles)
    fig.update_layout(showlegend=False)

    for compound in config['compounds']:
        compound_name = compound['name']
        data = perform_analysis(read_data(compound_name, config), operation, compound)

        fig.add_trace(
            go.Bar(
                x=data['DateTime'],
                y=data[compound_name],
                name=compound_name,
                marker_color=list(map(bar_color, data["Limit"])),
            ),
            row=compound['row'],
            col=compound['col']
        )

        fig.update_xaxes(title_text="Дата", row=compound['row'], col=compound['col'])
        fig.update_yaxes(title_text=compound['nameDisplay'] + " (µg/m3)", row=compound['row'], col=compound['col'])

    fig.update_layout(height=800)

    graph += fig.to_html(full_html=False, include_plotlyjs='cdn')
    return graph


def main():
    config = read_config()

    graphs = ""
    for operation in ['mean', 'max']:
        graphs += make_graph(config, operation)

    with open("templates/index_empty.html", 'r', encoding="UTF8") as f:
        content = f.read()

    content = content.format(graphs=graphs)

    with open("templates/index.html", 'w', encoding="UTF8") as f:
        f.write(content)
        f.flush()


if __name__ == "__main__":
    main()
