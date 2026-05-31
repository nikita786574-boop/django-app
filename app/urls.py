from django.urls import path
from . import views

urlpatterns = [
    path(route='parameter/<slug:system_slug>', view = views.parameters_form, name= 'parameters_form_system'),


    path("edit/subsystem/<slug:system_slug>/", views.edit_subsystem, name="edit_subsystem"),
    path("edit/parameter/<slug:parameter_slug>/", views.edit_parameter, name="edit_parameter"),
    path('edit/parameter_relations/<slug:to_slug>/<slug:from_slug>/', view= views.parameter_relations_form, name='parameter_relatoins_edit'),
    path('show/subsystem/<slug:system_slug>/', view=views.show_tree, name='show_tree'),

    path('del/parameter/<slug:parameter_slug>', views.del_object, name='del_parameter'),
    path('del/system/<slug:system_slug>', views.del_object, name='del_system'),
    path('del/parameter_relations/<slug:to_slug>/<slug:from_slug>', views.del_object, name='del_parameter_relations'),


    path("show/system/<slug:system_slug>", view = views.show_system, name="show_system"),
    path("goal_parameter/<slug:parameter_slug>", view=views.goal_parameter, name='goal_parameter'),
    path("goal_parameter/select/", view=views.goal_parameter_select, name='goal_parameter_select'),


    path("form_goal_parameter/<slug:goal_slug>/<slug:min_slug>",
         views.form_goal_parameter,
         name='form_goal_parameter'),

    #buttons in sidebar
    path(
        route="parameters_tree/<slug:system_slug>",
        view=views.parameters_tree,
        name='parameters_tree'
    ),

    path(
        route="parameters_tree/goal/<slug:system_slug>",
        view = views.parameters_tree_goal,
        name='parameters_tree_goal'
    ),
    path(
        route="parameters_tree/goal/show/<slug:parameter_slug>",
        view = views.parameters_tree_goal_show,
        name='parameters_tree_goal_show'
    ),

    #buttons in header

    path(route = 'subsystem/',
         view=views.subsystem_form,
         name='subsystem_form'),

    path(route ='',
         view = views.view_main,
         name= "main_page"),

    path(route='parameter/',
         view = views.parameters_form,
         name= 'parameters_form'),

    path(   route='parameter_relations/',
            view= views.parameter_relations_form,
            name='parameter_relations_form'),



    path(   route='show_processes/',
            view = views.show_processes,
            name='show_processes'),
     #sidebar main_page
     path( route='all_parameters/',
          view = views.all_parameters,
          name='all_parameters',
          ),

     path(
          route='all_parameter_relations/',
          view=views.all_parameter_relations,
          name='all_parameter_relations',
     ),


     # Показывать дерево D3 tree urls
     path(
         route = 'api/tree/<slug:system_slug>',
         view = views.api_tree,
         name = 'api_tree',
     ),
     path(
         route = 'd3tree/<slug:system_slug>',
         view = views.show_d3_tree,
         name = 'show_d3_tree',
     ),

     # Показываю дерево параметров

     path(
         route = 'api/parameters_tree/<slug:system_slug>',
         view = views.api_parameters_tree,
         name = 'api_parameters_tree',
     ),

     path(
         route = 'parameters_d3/<slug:system_slug>',
         view = views.all_parameters_tree,
         name = 'show_parameters_tree',
     ),

     path(
         route = 'api/goal/parameters/tree/<slug:parameter_slug>',
         view = views.api_goal_parameters_tree,
         name = 'api_goal_parameters_tree',
     ),
     path(
         route = 'goal/parameters/tree/<slug:parameter_slug>',
         view = views.goal_parameters_tree,
         name = 'goal_parameters_tree',
     ),

     path (
         route = 'important/matrices/<slug:parameter_slug>',
         view = views.important_matrices,
         name = 'important_matrices',
     ),
     path (
        route = 'important/matrices/process/<slug:parameter_slug>',
        view = views.new_view,
        name = 'important_matrices_process',
     ),

     # Тип связи (А1/А2/А3) — форма и матрица (Таблица 27)
     path(
         route = 'relation/type/process/<slug:parameter_slug>',
         view = views.relation_type_process,
         name = 'relation_type_process',
     ),
     path(
         route = 'relation/type/matrix/<slug:parameter_slug>',
         view = views.relation_type_matrix,
         name = 'relation_type_matrix',
     ),
]
