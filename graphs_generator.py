import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
import bs4


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


def make_graph(config: dict, operation: str, rows: int, cols: int, height: int) -> str:
    if operation == "mean":
        title = "Средни денонощни стойности"
    elif operation == "max":
        title = "Максимални еднократни стойности за денонощие"

    graph = "<h2>{title}</h2>".format(title=title)

    subplot_titles = get_subplot_titles(config, operation)

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles)
    fig.update_layout(showlegend=False)

    col = 1
    row = 1

    for compound_config in config['compounds']:
        compound_name = compound_config['name']

        data = perform_analysis(read_data(compound_name, config), operation, compound_config)

        fig.add_trace(
            go.Bar(
                x=data['DateTime'],
                y=data[compound_name],
                name=compound_name,
                marker_color=list(map(bar_color, data["Limit"])),
            ),
            row=row,
            col=col
        )

        limit = get_limit(compound_config, operation)
        max_val = data[compound_name].max()

        if limit is not None and (float(limit) / float(max_val)) <= 3:
            fig.add_hline(
                y=limit,
                line_dash='dot',
                row=row,
                col=col,
                line_color="#FF0000",
                line_width=2
            )

        fig.update_xaxes(title_text="Дата", row=row, col=col)
        fig.update_yaxes(title_text=compound_config['nameDisplay'] + " (µg/m3)", row=row, col=col)

        col += 1
        if col > cols:
            col = 1
            row += 1

    fig.update_layout(height=height)

    graph += fig.to_html(full_html=False, include_plotlyjs='cdn')
    return graph


def generate_html(config: dict, version_config: dict):
    graphs = ""
    for operation in ['mean', 'max']:
        graphs += make_graph(
            config=config,
            operation=operation,
            rows=version_config['rows'],
            cols=version_config['cols'],
            height=version_config['height']
        )

    with open("templates/{filename}".format(filename=version_config['template']), 'r', encoding="UTF8") as f:
        content = f.read()
        soup = bs4.BeautifulSoup(content, "html.parser")

    graphs_soup = bs4.BeautifulSoup(graphs, "html.parser")

    soup.body.append(graphs_soup)

    with open("templates/{filename}".format(filename=version_config['output']), 'w', encoding="UTF8") as f:
        f.write(str(soup))
        f.flush()


def main():
    desktop_version = {
        'rows': 3,
        'cols': 3,
        'height': 800,
        'template': 'desktop_template.html',
        'output': 'index.html'
    }

    mobile_version = {
        'rows': 7,
        'cols': 1,
        'height': 2500,
        'template': 'mobile_template.html',
        'output': 'index_mobile.html'

    }

    config = read_config()

    generate_html(config, desktop_version)
    generate_html(config, mobile_version)


if __name__ == "__main__":
    main()
