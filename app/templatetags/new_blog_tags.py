from django import template
from django.urls import reverse

register = template.Library()
from app.views import buttons_list


def build_button(title, name_url, *args):
    return {
        "title": title,
        "url": reverse(name_url, args=args) if args else reverse(name_url)
    }


@register.inclusion_tag('app/new_buttons.html', name='buttons')
def buttons():
    return {
        "all_buttons": buttons_list
    }


@register.inclusion_tag('app/new_buttons.html', name='buttons_sidebar')
def buttons_sidebar(syst):
    buttons = [
        build_button("Все параметры", "parameters_tree", syst),
        build_button("Целевые параметры", "parameters_tree_goal", syst),
    ]
    return {"all_buttons": buttons, "sidebar": True}


@register.inclusion_tag('app/new_buttons.html', name='buttons_sidebar_main_page')
def buttons_sidebar_main_page():
    buttons = [
        build_button("Все параметры", "all_parameters"),
        build_button("Все связи между параметрами", "all_parameter_relations"),
    ]
    return {"all_buttons": buttons, "sidebar": True}
