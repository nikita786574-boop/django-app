from django import template
from django.urls import reverse

register = template.Library()

from app.views import buttons_list


def _build_button(title, name_url, *args):
    return {
        'title': title,
        'url': reverse(name_url, args=args) if args else reverse(name_url),
    }


@register.inclusion_tag('app/new_buttons.html', name='buttons')
def buttons():
    return {'all_buttons': buttons_list}


@register.inclusion_tag('app/new_buttons.html', name='buttons_sidebar')
def buttons_sidebar(syst):
    return {
        'all_buttons': [
            _build_button('Все параметры', 'parameters_tree', syst),
            _build_button('Целевые параметры', 'parameters_tree_goal', syst),
        ],
        'sidebar': True,
    }


@register.inclusion_tag('app/new_buttons.html', name='buttons_sidebar_main_page')
def buttons_sidebar_main_page():
    return {
        'all_buttons': [
            _build_button('Все параметры', 'all_parameters'),
            _build_button('Все связи между параметрами', 'all_parameter_relations'),
        ],
        'sidebar': True,
    }
