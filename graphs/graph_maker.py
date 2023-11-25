import pandas as pd
import plotly.graph_objects as go
import bs4
from graphs.config import CompoundConfig
from graphs import analysis


def bar_color(i: bool):
    if i:
        return "red"
    else:
        return "green"


def get_title(compound_config: CompoundConfig, operation: str):
    limit = compound_config.get_limit(operation)
    title = compound_config.get_name_display()
    if limit is not None:
        title += " - лимит {limit} µg/m3".format(limit=limit)

    return title


def make_graph(compound_config: CompoundConfig, operation: str, raw_data: pd.DataFrame) -> str:
    title = ""
    if operation == "mean":
        title = "Средни денонощни стойности"
    elif operation == "max":
        title = "Максимални еднократни стойности за денонощие"

    limit = compound_config.get_limit(operation)
    if limit is not None:
        title += " - лимит {limit} µg/m3".format(limit=limit)

    graph = "<h2>{title}</h2>".format(title=title)

    fig = go.Figure()
    fig.update_layout(showlegend=False)

    data = analysis.perform_analysis(raw_data, operation, compound_config)

    compound_name = compound_config.get_name()
    fig.add_trace(
        go.Bar(
            x=data['DateTime'],
            y=data[compound_name],
            name=compound_name,
            marker_color=list(map(bar_color, data["Limit"])),
        )
    )

    limit = compound_config.get_limit(operation)
    max_val = data[compound_name].max()

    if limit is not None and (float(limit) / float(max_val)) <= 3:
        fig.add_hline(
            y=limit,
            line_dash='dot',
            line_color="#FF0000",
            line_width=2
        )

    fig.update_xaxes(title_text="Дата")
    fig.update_yaxes(title_text=compound_config.get_name_display() + " (µg/m3)")

    graph += fig.to_html(full_html=False, include_plotlyjs='cdn')
    return graph


def generate_html(compound_config: CompoundConfig, raw_data: pd.DataFrame):
    graphs = "<h1>{compound}</h1>".format(compound=compound_config.get_name_display())
    for operation in ['mean', 'max']:
        graphs += make_graph(
            compound_config=compound_config,
            operation=operation,
            raw_data=raw_data
        )

    html_input = "templates/template.html"
    html_output = "templates/{compound_name}.html".format(compound_name=compound_config.get_name())

    with open(html_input, 'r', encoding="UTF8") as f:
        content = f.read()

    soup = bs4.BeautifulSoup(content, "html.parser")

    graphs_soup = bs4.BeautifulSoup(graphs, "html.parser")

    soup.find("div", {"class", "content"}).append(graphs_soup)
    soup.find(attrs={"id": compound_config.get_name()})['class'] = "active"

    with open(html_output, 'w', encoding="UTF8") as f:
        f.write(str(soup))
        f.flush()
