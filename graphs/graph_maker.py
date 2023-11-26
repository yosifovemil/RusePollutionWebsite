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


def build_tooltip(operation: str, title: str):
    html = """
    <div class='tooltip_{operation}'>
        <a href='javascript:;'><h2>{title}</h2></a>
        <p class='tooltiptext'>{text}</p>
    </div>
    """

    text = ""
    if operation == "mean":
        text += "Станцията на Линамар предоставя измервания на всеки 30 минути. Графиката показва осреднената стойност от тези измервания за период от 24 часа."
    elif operation == "max":
        text += "Станцията на Линамар предоставя измервания на всеки 30 минути. Графиката показва максималната стойност от тези измервания за период от 24 часа."

    return html.format(title=title, text=text, operation=operation)


def build_plot_title(operation: str, compound_config: CompoundConfig):
    title = ""
    if operation == "mean":
        title = "Средни денонощни стойности"
    elif operation == "max":
        title = "Максимални еднократни стойности за денонощие"

    limit = compound_config.get_limit(operation)
    if limit is not None:
        title += " - лимит {limit} µg/m3".format(limit=limit)

    title = build_tooltip(operation, title)

    return title


def make_graph(compound_config: CompoundConfig, operation: str, raw_data: pd.DataFrame) -> str:
    graph = build_plot_title(operation, compound_config)

    modebar = go.layout.Modebar(remove=("lasso", "lasso2d", "select", "select2d"))

    layout = go.Layout(
        margin=dict(r=10, l=10, t=30, b=10),
        xaxis={'fixedrange': True, 'title': 'Дата'},
        yaxis={'fixedrange': True, 'title': compound_config.get_name_display() + " (µg/m3)"},
        showlegend=False,
        modebar=modebar
    )

    fig = go.Figure(layout=layout)

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
