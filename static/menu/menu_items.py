import itertools


def build_menu_item_index() -> list[tuple[int, str]]:
    measurements_by_group = [menu_item_groups[group] for group in menu_item_groups]
    measurements = itertools.chain.from_iterable(measurements_by_group)
    return list(enumerate(measurements))


menu_item_groups = {
    "Замърсители": [
        "m- p-Ксилен",
        "p-Крезол",
        "Азотен диоксид NO2",
        "Азотен оксид NO",
        "Бензен",
        "Въглероден оксид CO",
        "Етилбензен",
        "Ксилен",
        "Нафтален",
        "Озон О3",
        "Серен диоксид SO2",
        "Толуен",
        "Фенол",
        "Фини прахови частици ФПЧ10",
        "Фини прахови частици ФПЧ2.5",
        "о-Крезол",
        "о-Ксилен",
        "р-Крезол"
    ],
    "Метеорологични": [
        "Атмосферно налягане",
        "Валежи",
        "Относителна влажност",
        "Посока на вятъра",
        "Посока на вятъра (глобална)",
        "Радиационен гама фон",
        "Скорост на вятъра",
        "Слънчева радиация",
        "Стандартно отклонение на посока на вятъра",
        "Температура на въздуха"
    ]
}
menu_item_index = build_menu_item_index()


def lookup_menu_index(name: str) -> int:
    menu_item = [item for item in menu_item_index if item[1] == name]
    if len(menu_item) != 1:
        raise Exception(f"Unexpected number of items {len(menu_item)}")
    else:
        return menu_item[0][0]
