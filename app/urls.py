from django.urls import path
from . import views

urlpatterns = [
    path(route='parameter/<str:name_system>', view = views.parameters_form, name= 'parameters_form_system'),
 

    path("edit/subsystem/<str:subsystem_name>/", views.edit_subsystem, name="edit_subsystem"),
    path("edit/parameter/<str:name_system>/<str:parameter_name>/", views.edit_parameter, name="edit_parameter"),
    path('edit/parameter_relations/<str:to_parameter>/<str:from_parameter>/', view= views.parameter_relations_form, name='parameter_relatoins_edit'),
    path('show/subsystem/<str:name_system>/', view=views.show_tree, name='show_tree'),
    
    path('del/parameter/<str:name_system>/<str:name_parameter>', views.del_object, name='del_parameter'),
    path('del/system/<str:name_system>', views.del_object, name='del_system'),
    path('del/parameter_relations/<str:name_to_parameter>/<str:name_from_parameter>', views.del_object, name='del_parameter_relations'),


    path("show/system/<str:name_system>", view = views.show_system, name="show_system"),
    path("goal_parameter/<str:name_system>/<str:name_goal_parameter>", view=views.goal_parameter, name='goal_parameter'),
    path("goal_parameter/select/", view=views.goal_parameter_select, name='goal_parameter_select'),


    path("form_goal_parameter/<str:name_system>/<str:name_goal_parameter>/<str:name_min_subsystem>/<str:name_min_parameter>",
         views.form_goal_parameter,
         name='form_goal_parameter'),

    #buttons in sidebar
    path(
        route="parameters_tree/<str:system>", 
        view=views.parameters_tree, 
        name='parameters_tree'
    ),

    path(
        route="parameters_tree/goal/<str:system>",
        view = views.parameters_tree_goal,
        name='parameters_tree_goal'
    ),
    path(
        route="parameters_tree/goal/show/<str:parameter>/<str:system>",
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
         route = 'api/tree/<str:name_system>', 
         view = views.api_tree, 
         name = 'api_tree',
     ),
     path(
         route = 'd3tree/<str:name_system>',
         view = views.show_d3_tree,
         name = 'show_d3_tree',
     ),

     # Показываю дерево параметров

     path(
         route = 'api/parameters_tree/<str:name_system>',
         view = views.api_parameters_tree,
         name = 'api_parameters_tree',
     ),

     path(
         route = 'parameters_d3/<str:name_system>',
         view = views.all_parameters_tree,
         name = 'show_parameters_tree',
     ),

     path(
         route = 'api/goal/parameters/tree/<str:name_parameter>/<str:name_system>/<int:number>',
         view = views.api_goal_parameters_tree,
         name = 'api_goal_parameters_tree',
     ),
     path(
         route = 'goal/parameters/tree/<str:name_parameter>/<str:name_system>/<int:number>',
         view = views.goal_parameters_tree,
         name = 'goal_parameters_tree',
     ),

     path (
         route = 'important/matrices/<str:name_goal_parameter>/<str:name_system>/<int:number>',
         view = views.important_matrices,
         name = 'important_matrices',
     ),
     path (
        route = 'important/matrices/process/<str:name_goal_parameter>/<str:name_system>/<int:number>',
        view = views.new_view,
        name = 'important_matrices_process',    
     ),
]
