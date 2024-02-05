from static.menu.menu_items import menu_item_groups, lookup_menu_index
from bs4 import BeautifulSoup, NavigableString


def build() -> str:
    soup = BeautifulSoup('')
    nav = soup.new_tag("nav", **{'class': 'sidebar'})

    for group in menu_item_groups:
        title_div = soup.new_tag("div", **{'class': 'text'})
        title_div.insert(0, NavigableString(group))
        option_list = soup.new_tag("ul", **{'class': 'main_side'})
        for menu_item in menu_item_groups[group]:
            list_entry = soup.new_tag("li")

            link = soup.new_tag("a", href=f"/graph?page={lookup_menu_index(menu_item)}")
            link.insert(0, NavigableString(menu_item))

            list_entry.append(link)
            option_list.append(list_entry)

        nav.append(title_div)
        nav.append(option_list)

    return str(nav)


menu = build()
