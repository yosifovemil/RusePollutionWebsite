from static.form import constants
from bs4 import BeautifulSoup, NavigableString, Tag


def build(dates: str, measurement: str, interval: str) -> str:
    soup = BeautifulSoup('')
    form = soup.new_tag("form", **{'action': '/', 'method': 'POST'})

    measurement_select = build_select(soup=soup, value_type="measurement", options=constants.measurements,
                                      selected=measurement)
    interval_select = build_select(soup=soup, value_type="interval", options=constants.intervals, selected=interval)
    dates_input = build_date_input(soup=soup, name="dates", value=dates)
    submit = soup.new_tag("input", **{'type': 'submit', 'value': 'Submit'})

    form.append(measurement_select)
    form.append(interval_select)
    form.append(dates_input)
    form.append(submit)

    return str(form)


def build_select(soup: BeautifulSoup, value_type: str, options: list[str], selected: str) -> Tag:
    select = Tag(
        builder=soup.builder,
        name='select',
        attrs={'class': value_type, 'name': value_type}
    )

    for option in options:
        entry = soup.new_tag("option", **{'value': option})
        entry.insert(0, NavigableString(option))
        if option == selected:
            entry.attrs['selected'] = ""
        select.append(entry)

    return select


def build_date_input(soup: BeautifulSoup, name: str, value: str) -> Tag:
    return Tag(
        builder=soup.builder,
        name='input',
        attrs={'name': name, 'value': value}
    )
