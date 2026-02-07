from django import template

register = template.Library()

from django.utils.safestring import mark_safe



@register.simple_tag
def show_parameters(system):
    pass

from app.views import buttons_list

@register.inclusion_tag('app/buttons.html', name = 'buttons')
def buttons():
    return {'all_buttons': buttons_list}

@register.inclusion_tag('app/buttons.html', name='buttons_sidebar')
def buttons_sidebar(syst):
    buttons_list_new = [
        {'title': 'Все параметры',
            'name_url':'parameters_tree',
            'additional_parameter':syst},
        {'title':'Целевые параметры',
         'name_url': 'parameters_tree_goal',
         'additional_parameter': syst}
    ]
    return {'all_buttons': buttons_list_new,'sidebar':True}

@register.inclusion_tag('app/buttons.html', name='buttons_sidebar_main_page')
def buttons_sidebar_main_page():
    buttons_list_new=[
        {   'title': 'Все параметры',
            'name_url': 'all_parameters',
            'additional_parameter': None},
        {
            'title':'Все связи между параметрами',
            'name_url': 'all_parameter_relations',
            'additional_parameter': None
        }
    ]
    return {'all_buttons': buttons_list_new, 'sidebar':True}