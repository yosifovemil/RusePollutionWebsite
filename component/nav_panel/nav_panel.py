from bs4 import BeautifulSoup, NavigableString, Tag
from flask import url_for

from component.nav_panel import constants


def build_form(dates: str, measurement: str, interval: str) -> Tag:
    soup = BeautifulSoup('')
    form = soup.new_tag(
        name="form",
        attrs={'action': '/graph', 'method': 'POST', 'class': 'navbar-nav'}
    )

    measurement_attrs = {
        'class': 'measurement align-middle',
        'style': 'height: 100%',
        'id': 'large-select2-options-single-field',
        'name': 'measurement'
    }

    measurement_select = __build_select(
        soup=soup,
        options=constants.measurements,
        selected=measurement,
        attrs=measurement_attrs
    )

    measurement_div = __build_div(attrs={'class': 'nav-item'})
    measurement_div.insert(0, measurement_select)

    interval_attrs = {
        'class': 'interval align-middle nav-item',
        'name': 'interval'
    }

    interval_select = __build_select(
        soup=soup,
        options=constants.intervals,
        selected=interval,
        attrs=interval_attrs
    )

    dates_input = __build_date_input(soup=soup, name="dates", value=dates)
    submit = __build_button(img_src="static/graph.svg", attrs={'class': 'btn btn-secondary align-middle nav-item'})
    submit_input = soup.new_tag("input", **{'type': 'submit'})
    submit_input.insert(0, submit)

    form.append(measurement_div)
    form.append(interval_select)
    form.append(dates_input)
    form.append(submit)

    return form


def build_nav_buttons(admin: bool) -> list[Tag]:
    buttons = []
    button_attrs = {
        'class': 'nav-item btn btn-secondary',
        'data-bs-toggle': 'modal',
        'data-bs-target': '#adminModal'
    }
    if False:  # TODO if admin:
        admin_button = __build_button(
            img_src="static/admin.svg",
            attrs=button_attrs
        )

        buttons.append(admin_button)

    logout_button = __build_button(
        img_src="static/logout.svg",
        attrs=button_attrs
    )

    soup = BeautifulSoup("")
    logout_link = soup.new_tag("a", href=url_for("auth.logout"))
    logout_link.append(logout_button)

    buttons.append(logout_link)

    return buttons


def build_admin_modal(admin: bool) -> Tag | None:
    if not admin:
        return None

    modal = __build_div(
        attrs={
            'class': 'modal fade',
            'id': 'adminModal',
            'tabindex': '-1',
            'aria-labelledby': 'adminModalLabel',
            'aria-hidden': 'true'
        }
    )

    modal_dialog = __build_div(attrs={'class': 'modal-dialog'})
    modal.insert(0, modal_dialog)

    modal_content = __build_div(attrs={'class': 'modal-content'})
    modal_dialog.insert(0, modal_content)

    modal_header = __build_admin_header()
    modal_content.insert(0, modal_header)

    modal_body = __build_admin_body()
    modal_content.insert(1, modal_body)

    return modal


def __build_admin_header() -> Tag:
    soup = BeautifulSoup("")

    modal_header = __build_div(attrs={'class': 'modal-header'})

    title = soup.new_tag("h5", attrs={'class': 'modal-title', 'id': 'adminModalLabel'})
    title.insert(0, NavigableString("Администрация"))
    modal_header.insert(0, title)

    button = soup.new_tag("button", attrs={
        'class': 'btn-close',
        'data-bs-dismiss': 'modal',
        'aria-label': 'Close'
    })
    modal_header.insert(1, button)

    return modal_header


def __build_admin_body() -> Tag:
    body = __build_div(attrs={'class': 'modal-body'})

    soup = BeautifulSoup("")
    img = soup.new_tag("img", src="static/under_construction.jpg", style='width: 100%')
    body.insert(0, img)

    return body


def __build_button(img_src: str, attrs: dict):
    soup = BeautifulSoup('')
    img = soup.new_tag("img", **{'src': img_src, 'width': "30"})
    button = soup.new_tag("button", attrs=attrs)
    button.insert(0, img)
    return button


def __build_select(
        soup: BeautifulSoup,
        options: list[str],
        selected: str,
        attrs: dict) -> Tag:
    select = soup.new_tag(name="select", attrs=attrs)

    for option in options:
        entry = soup.new_tag("option", **{'value': option})
        entry.insert(0, NavigableString(option))
        if option == selected:
            entry.attrs['selected'] = ""
        select.append(entry)

    return select


def __build_date_input(soup: BeautifulSoup, name: str, value: str) -> Tag:
    return Tag(
        builder=soup.builder,
        name='input',
        attrs={
            'name': name,
            'value': value,
            'class': 'dates-input align-middle nav-item'
        }
    )


def __build_div(attrs: dict) -> Tag:
    soup = BeautifulSoup("")
    return soup.new_tag("div", attrs=attrs)
