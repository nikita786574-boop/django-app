from django.shortcuts import render, get_object_or_404
from .models import SubSystem, Parameters , ParameterRelations
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
from .forms import SubSystemForm, ParametersForm, ParameterRelationsForm

from django.urls import reverse

from app.forms import ParameterRelationsFormSecond

from django.http import JsonResponse
import json



buttons_list = [
    {'title': 'Главная страница',                        'name_url': 'main_page',               'additional_parameter':None},
    {'title': 'Форма для subsystem',                     'name_url': 'subsystem_form',          'additional_parameter':None},
    {'title': 'Форма для parameter',                     'name_url': 'parameters_form',         'additional_parameter':None},
   # {'title': 'Форма для parameter relations',           'name_url': 'parameter_relations_form','additional_parameter':None},
    {'title': 'Форма для определения важных параметров',               'name_url': 'goal_parameter',          'additional_parameter':None},
    {'title': 'Форма для отображения начатых и законченных процессов', 'name_url': 'show_processes',          'additional_parameter':None},
]




def edit_subsystem(request, subsystem_name):
    system = get_object_or_404(SubSystem, name=subsystem_name)
    form = SubSystemForm(instance=system)

    if request.method=='POST':
        form = SubSystemForm(request.POST, instance=system)
        if form.is_valid():
            print(dict(form.data)['name'][0])
            name = dict(form.data)['name'][0]
            print(len(list(SubSystem.objects.filter(name=name))))
            if len(list(SubSystem.objects.filter(name=name)))!=0:
                form.add_error('name', 'Подсистема с таким именем уже существует')
            else:
                form.save()
                return HttpResponseRedirect('/')
    return render(request, 'app/form_template.html', context = {'form': form})

def edit_parameter(request, parameter_name):
    parameter = get_object_or_404(Parameters, name=parameter_name)
    if request.method == 'POST':

        form= ParametersForm(request.POST,instance = parameter)
        form.save()
        return HttpResponseRedirect('/')
    form = ParametersForm(instance=parameter)
    return render(request, 'app/form_template.html', context={"form":form})

def view_main(request):
    subsystems = SubSystem.objects.filter(is_root = True)
    return render(request, 'app/main2.html', context={'subsystems':subsystems})

def subsystem_form(request):
    form = SubSystemForm()
    if request.method =="POST":
        form =SubSystemForm(request.POST)    
        if form.is_valid():
            name = dict(form.data)['name'][0]
            print(len(list(SubSystem.objects.filter(name=name))))
            if len(list(SubSystem.objects.filter(name=name)))!=0:
                form.add_error('name', 'Подсистема с таким именем уже существует')
            else:
                form.save()
                return HttpResponseRedirect('/')

    return render(request, template_name='app/form_template.html', context={'form':form, 'title':'SubSystem Form'})

def parameters_form(request, name_system=None):
    form = ParametersForm()
    if request.method == 'POST':
        form = ParametersForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    if name_system!=None:
        system = get_object_or_404(SubSystem, name= name_system)
        form=ParametersForm(initial={'subsystem':system})
    return render(request, template_name ='app/form_template.html', context={'form':form, 'title':'Parameters form'})

def parameter_relations_form(request, to_parameter=None, from_parameter=None):
    form = ParameterRelationsForm()
    if request.method=='POST':
        form = ParameterRelationsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    if request.method=='GET' and to_parameter != None and from_parameter!=None:
        relation = get_object_or_404(ParameterRelations, to_parameter__name=to_parameter, from_parameter__name=from_parameter)
        print(relation)
        if relation:
            form = ParameterRelationsForm( instance=relation)

    return render(request, template_name = 'app/form_template.html', context={'form':form, 'title':'Parameter Relation Form'})


def show_tree(request, name_system):
    system = get_object_or_404(SubSystem, name=name_system)
    return render(request, template_name='app/show_tree.html', context={'node':system})

def show_system(request, name_system):
    system = get_object_or_404(SubSystem, name = name_system)
    return render(request, template_name = 'app/show_system.html', context={'system':system})


def goal_parameter(request, name_goal_parameter=None):
    #Должен быть участником какой-то подсистемы
    #Создаём связи в таблице relation
    #name_goal_parameter передаётся, если пользователь
    #Нажал на какую-то кнопку с параметром.
    if name_goal_parameter!=None:
        parameter=get_object_or_404(Parameters, name=name_goal_parameter)
        system = parameter.subsystem
        # кнопка начать процесс нажата
        if not system:
            title='Ошибка'
            content = mark_safe("""
<h2>Параметер не привязан к какой-либо системе</h2>""")
            return render(request,'app/with_context.html',context={'title':title, 'content':content})
        
        if any(ParameterRelations.objects.filter(to_parameter__name=name_goal_parameter)):
            content = mark_safe("""
<h2>Процесс этим параметром уже создан.</h2>""")
            title='Ошибка'
            return render(request,'app/with_context.html',context={'title':title, 'content':content})
        
        #Надо создать много связей в parameter relations
        children = system.children
        print(type(children))
        for child in children.all():
            for param in child.parameters.all():
                rel = ParameterRelations(
                    to_parameter = parameter,
                    from_parameter = param,
                    is_affect =None
                )
                rel.save()
        return HttpResponseRedirect('/')

        if request.method=='POST':
            data = dict(request.POST)
            del data['csrfmiddlewaretoken']
            for key in data.keys():
                value = request.POST[key]
                from_parameter_rel = Parameters.objects.get(name=key, subsystem__name=value)
                form = ParameterRelations(to_parameter=parameter, from_parameter=from_parameter_rel)
                form.save()
                return HttpResponseRedirect('/')
        return render(request, 'app/tree_parameter.html', context={'parameter':parameter, 'system':system})
    else:
        parameters=Parameters.objects.exclude(subsystem=None)
        string=''
        for param in parameters:
            string +=f"""
<div>
<a href='/goal_parameter/{param.name}'><button>{param.name}</button></a>
<p>{param}</p>
</div>
"""
        
        return render(request, 'app/with_context.html', context={'title':'параметры', 'content':mark_safe(string)})
    


def del_object(request,name_system=None, name_parameter=None, name_to_parameter=None, name_from_parameter=None):
    if name_system!=None:
        system = get_object_or_404(SubSystem, name= name_system)
        system.delete()
    elif name_parameter!=None:
        parameter=get_object_or_404(Parameters, name=name_parameter)
        parameter.delete()
    else:
        parameter_relations = get_object_or_404(ParameterRelations, to_parameter__name=name_to_parameter, from_parameter__name = name_from_parameter)
        parameter_relations.delete()
    return HttpResponseRedirect('/')


def show_processes(request):
    #Здесь же создание процесса
    #Выводить начатые процессы
    if request.method=='GET':
        #Надо найти незаконченные процессы
        # При нажатии надо продолжать процесс
        #Пока что при нажатии на процесс можно просто выкидывать следующую форму
        # Когда пользователь её заполняет, его будет перекидывать на страницу с
        # процессами. 
        #part_process = ParameterRelations.objects.filter(is_affect__isnull=True)
        part_process = ParameterRelations.objects.all()
        #Я буду выводить кнопку для следующего этапа в процессе.
        to_rel =list()
        for data in part_process:
            if data.to_parameter not in to_rel:
                to_rel.append(data.to_parameter)
        #минимальная подсистема и минимальный номер параметра
        pairs_with_progress = []
        for goal_parameter in to_rel:
            parameters = []
            for data in part_process:
                if data.to_parameter == goal_parameter:
                    parameters.append(data.from_parameter)
            print(parameters)
            min_number_systems=10000
            min_param=None
            min_param_num=100000
            for param in parameters:
                sys_num = param.subsystem.number
                if sys_num<=min_number_systems:
                    min_number_systems=sys_num
                    if min_param_num>param.number:
                        min_param_num = param.number
                        min_param=param
            # Рассчитываем прогресс для этого целевого параметра
            total = ParameterRelations.objects.filter(to_parameter=goal_parameter).count()
            processed = ParameterRelations.objects.filter(to_parameter=goal_parameter, is_affect__isnull=False).count()
            if total > 0:
                percent = int(processed * 100 / total)
            else:
                percent = 0
            pairs_with_progress.append({
                'min_parameter': min_param,
                'goal_parameter': goal_parameter,
                'percent': percent
            })
        active_processes = [p for p in pairs_with_progress if p['percent'] < 100]
        completed_processes = [p for p in pairs_with_progress if p['percent'] == 100]
        
        return render(request, template_name='app/processes.html', context={'active_processes': active_processes, 'completed_processes': completed_processes})


def form_goal_parameter(request, name_goal_parameter, name_min_parameter):
    rel = get_object_or_404(ParameterRelations, to_parameter__name=name_goal_parameter, from_parameter__name=name_min_parameter)

    if request.method=='POST':
        data = request.POST
        form = ParameterRelationsFormSecond(request.POST, instance=rel)
        if form.is_valid():
            form.save()
            mins = find_min()
            print('-'*100)
            print(mins)
            print('-'*100)
            # Сейчас делаю через mins[0][0], но это не верно. 
            # Надо искать goal_parameter
            if len(mins)==0:
                return HttpResponseRedirect(
                    reverse(
                        viewname='main_page'
                    )
                )
            return HttpResponseRedirect(
                reverse(
                    viewname = 'form_goal_parameter',
                    kwargs={
                        'name_goal_parameter': name_goal_parameter,
                        'name_min_parameter':mins[0][0].name,
                    }
                )
            )
        
    rel = get_object_or_404(ParameterRelations, to_parameter__name=name_goal_parameter, from_parameter__name=name_min_parameter)
    form = ParameterRelationsFormSecond(instance=rel)
    return render(request,
                   template_name="app/form_goal_parameter.html",
                   context={
            'form': form,
            'goal': rel.to_parameter,
            'source': rel.from_parameter
        })



def parameters_tree(request, system):
    system = SubSystem.objects.get(name=system)
    return render(request, template_name='app/subsystem/parameter_tree.html', context={'nodes':[system], 'parameter_flag':True})

def parameters_tree_goal(request, system):
    # Надо отобразить все целевые параметры, которые есть у системы
    system=SubSystem.objects.get(name=system)
    parameters = system.parameters.all()
    parameters_goal = [parameter for parameter in parameters if parameter.is_goal]
    #for parameter in parameters:
    #    if len(ParameterRelations.objects.filter(to_parameter__name=parameter.name)):
    #        parameters_goal.append(parameter)
    return render(request, 
                  template_name='app/subsystem/parameter_goal.html', 
                  context={
                      'nodes':[system], 
                      'parameter_flag':True, 
                      'parameters_goal':parameters_goal
                      }
                )


def parameters_tree_goal_show(request, parameter, system):
    """
    parameters_tree/goal/show/<str:parameter>/<str:system>
    """
    #Пробежаться по подсистемам и там найти
    system=get_object_or_404(SubSystem, name=system)
    parameter_affect_goal = who_is_matter(parameter)
    parameter = get_object_or_404(Parameters, name=parameter)

    return render(request, 
                  template_name='app/goal_parameter/tree_goal_parameter.html', 
                  context={
                      'nodes':[system], 
                      'goal_parameter': parameter,
                      'parameter_affect_goal':parameter_affect_goal,
                      }
                )



def find_min():
    '''Возвращает список из кортежей (кто влияет, на кого влияет)
    При этом кто влияет - следующий в списке в порядке очереди.
    '''
    part_process = ParameterRelations.objects.filter(is_affect__isnull=True)
    #Я буду выводить кнопку для следующего этапа в процессе.
    to_rel =list()
    for data in part_process:
        if data.to_parameter not in to_rel:
            to_rel.append(data.to_parameter)
    #минимальная подсистема и минимальный номер параметра
    result=[]
    for goal_parameter in to_rel:
        parameters = []
        for data in part_process:
            if data.to_parameter == goal_parameter:
                parameters.append(data.from_parameter)
        print(parameters)
        min_number_systems=10000
        min_param=None
        min_param_num=100000
        for param in parameters:
            sys_num = param.subsystem.number
            if sys_num<=min_number_systems:
                min_number_systems=sys_num
                if min_param_num>param.number:
                    min_param_num = param.number
                    min_param=param
        result.append((min_param, goal_parameter))
    return result

def who_is_matter(goal_param):
    '''Найти список параметров, которые влияют на целевой goal_param'''
    part_process = ParameterRelations.objects.filter(is_affect=True)
    #Я буду выводить кнопку для следующего этапа в процессе.
    to_rel =list()
    for data in part_process:
        if data.to_parameter.name == goal_param:
            to_rel.append(data.from_parameter)
    return to_rel
 
def all_parameter_relations(request):
    parameter_relations = ParameterRelations.objects.all()
    return render(
        request, 
        'app/all_parameter_relations/all_parameter_relations.html',
        context={
            'parameter_relations':parameter_relations,
            }
        )
def all_parameters(request):
    parameters = Parameters.objects.all()
    return render(request, 'app/all_parameters/all_parameters.html', context={'parameters':parameters})



# Api для дерева D3

def api_tree(request, name_system):
    """
    API endpoint, который возвращает дерево в JSON формате
    Используется D3.js для построения визуального дерева
    """

    system = get_object_or_404(SubSystem, name=name_system)
    # Можно возращать и потомков. Он просто будет отрисо
    # вывать дерево начиная с них
    return JsonResponse(system.to_dict())

def show_d3_tree(request, name_system):
    """
    Рендер страницы с d3 деревом
    """
    system= get_object_or_404(SubSystem, name=name_system)
    return render(request, 'app/d3/d3_tree.html', context={'node':system})

def api_parameters_tree(request, name_system):
    system = get_object_or_404(SubSystem, name = name_system)
    return JsonResponse(system.to_dict())

def all_parameters_tree(request, name_system):
    system = get_object_or_404(SubSystem, name=name_system)
    # Для каждого целевого параметра вычисляем затронутые параметры
    all_params = get_all_parameters_recursive(system)
    goal_parameters = []
    for param in all_params:
        if param.is_goal:
            affected = ParameterRelations.objects.filter(
                to_parameter=param,
                is_affect=True
            ).values_list('from_parameter_id', flat=True)
            goal_parameters.append({
                'id': param.id,
                'name': param.name,
                'affected_ids': list(affected)
            })
    # Также нужно собрать все параметры (включая потомков) для фронтенда
    # Данные будут загружены через api_parameters_tree, но можно передать goal_parameters
    return render(request, 'app/d3/all_parameters_tree.html', {
        'node': system,
        'goal_parameters': goal_parameters,
        'goal_parameters_json': mark_safe(json.dumps(goal_parameters))
    })

def api_goal_parameters_tree(request, name_parameter, name_system, number):
    parameter = get_object_or_404(Parameters, number=number, subsystem__name = name_system)
    system = get_object_or_404(SubSystem, name = name_system)
    if parameter.is_goal == False:
        return Http404()
    else:
        #Добавить данные, чтобы как можно меньше логики передавать на фронтенд
        data = system.to_dict()
        affects = ParameterRelations.objects.filter(to_parameter = parameter)
        for relation in affects:
            if relation.is_affect == True:
                name = relation.from_parameter.name
                number = relation.from_parameter.number
                id = relation.from_parameter.id
                if rec_change_parameter(data, id):
                    print('success')
                else:
                    raise ValueError('Пиздец, нихуя не работает')
        # Данные добавлены
        return JsonResponse(data)
    #Теперь написать новый фронтенд и модель

def goal_parameters_tree(request, name_parameter, name_system, number):
    system = get_object_or_404(SubSystem, name=name_system)
    parameter = get_object_or_404(Parameters, name=name_parameter, number=number)
    return render(request, 'app/d3/goal_parameters_tree.html', {'node':system,'goal_parameter':parameter})

def rec_change_parameter(data, id):
    #Проверяю параметры data, потом рекурсивно по детям проверяю
    for param in data.get('parameters', []):
        print(param)
        print(param['id'], id)
        if param['id']==id:
            param['is_affect']=True
            return 1
    for child in data.get('children', []):
        if rec_change_parameter(child, id)==1:
            return 1
    return 0

def get_all_parameters_recursive(subsystem):
    """Рекурсивно собирает все параметры системы и ее потомков"""
    params = list(subsystem.parameters.all())
    for child in subsystem.children.all():
        params.extend(get_all_parameters_recursive(child))
    return params
    