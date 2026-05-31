from django.shortcuts import render, get_object_or_404, redirect
from .models import SubSystem, Parameters, ParameterRelations, ParameterImportance
from django.http import Http404, HttpResponseRedirect
from django.utils.html import escape
from django.utils.safestring import mark_safe
from .forms import SubSystemForm, ParametersForm, ParameterRelationsForm, ParameterImportanceForm, ParameterRelationTypeForm
from django.urls import reverse
from app.forms import ParameterRelationsFormSecond
from django.http import JsonResponse
import json


buttons_list = [
    {'title': 'Главная страница',                                        'name_url': 'main_page',             'additional_parameter': None},
    {'title': 'Форма для subsystem',                                     'name_url': 'subsystem_form',        'additional_parameter': None},
    {'title': 'Форма для parameter',                                     'name_url': 'parameters_form',       'additional_parameter': None},
    {'title': 'Форма для определения важных параметров',                 'name_url': 'goal_parameter_select', 'additional_parameter': None},
    {'title': 'Форма для отображения начатых и законченных процессов',   'name_url': 'show_processes',        'additional_parameter': None},
]


def edit_subsystem(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    form = SubSystemForm(instance=system)

    if request.method == 'POST':
        form = SubSystemForm(request.POST, instance=system)
        if form.is_valid():
            name = dict(form.data)['name'][0]
            if SubSystem.objects.filter(name=name).exclude(pk=system.pk).exists():
                form.add_error('name', 'Подсистема с таким именем уже существует')
            else:
                form.save()
                return HttpResponseRedirect('/')
    return render(request, 'app/form_template.html', context={'form': form})


def edit_parameter(request, parameter_slug):
    parameter = get_object_or_404(Parameters, slug=parameter_slug)
    if request.method == 'POST':
        form = ParametersForm(request.POST, instance=parameter)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ParametersForm(instance=parameter)
    return render(request, 'app/form_template.html', context={'form': form})


def view_main(request):
    subsystems = SubSystem.objects.filter(is_root=True)
    return render(request, 'app/main2.html', context={'subsystems': subsystems})


def subsystem_form(request):
    form = SubSystemForm()
    if request.method == 'POST':
        form = SubSystemForm(request.POST)
        if form.is_valid():
            name = dict(form.data)['name'][0]
            if SubSystem.objects.filter(name=name).exists():
                form.add_error('name', 'Подсистема с таким именем уже существует')
            else:
                form.save()
                return HttpResponseRedirect('/')
    return render(request, template_name='app/form_template.html', context={'form': form, 'title': 'SubSystem Form'})


def parameters_form(request, system_slug=None):
    form = ParametersForm()
    if request.method == 'POST':
        form = ParametersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('parameters_form')
    if system_slug is not None:
        system = get_object_or_404(SubSystem, slug=system_slug)
        form = ParametersForm(initial={'subsystem': system})
    return render(request, template_name='app/form_template.html', context={'form': form, 'title': 'Parameters form'})


def parameter_relations_form(request, to_slug=None, from_slug=None):
    form = ParameterRelationsForm()
    if request.method == 'POST':
        form = ParameterRelationsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    if request.method == 'GET' and to_slug is not None and from_slug is not None:
        relation = get_object_or_404(ParameterRelations, to_parameter__slug=to_slug, from_parameter__slug=from_slug)
        form = ParameterRelationsForm(instance=relation)
    return render(request, template_name='app/form_template.html', context={'form': form, 'title': 'Parameter Relation Form'})


def show_tree(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    return render(request, template_name='app/show_tree.html', context={'node': system})


def show_system(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    return render(request, template_name='app/show_system.html', context={'system': system})


def goal_parameter_select(request):
    parameters = Parameters.objects.exclude(subsystem=None).select_related('subsystem')
    return render(request, 'app/goal_parameter/select.html', {'parameters': parameters})


def goal_parameter(request, parameter_slug=None):
    if parameter_slug is not None:
        parameter = get_object_or_404(Parameters, slug=parameter_slug)
        system = parameter.subsystem

        if not system:
            return render(request, 'app/with_context.html', context={
                'title': 'Ошибка',
                'content': mark_safe('<h2>Параметр не привязан к какой-либо системе</h2>'),
            })

        if ParameterRelations.objects.filter(to_parameter=parameter).exists():
            return render(request, 'app/with_context.html', context={
                'title': 'Ошибка',
                'content': mark_safe('<h2>Процесс этим параметром уже создан.</h2>'),
            })

        # Создаём связи с параметрами того же уровня
        for same_level_parameter in Parameters.objects.filter(subsystem=system):
            if same_level_parameter != parameter:
                ParameterRelations.objects.create(
                    to_parameter=parameter,
                    from_parameter=same_level_parameter,
                    is_affect=None,
                )

        # Создаём связи с параметрами дочерних подсистем
        children = system.children
        if not any(child.parameters.exists() for child in children.all()):
            return render(request, 'app/with_context.html', context={
                'title': 'Ошибка',
                'content': mark_safe('<h2>У этого параметра нет параметров нижних уровней.</h2>'),
            })

        for child in children.all():
            for param in child.parameters.all():
                ParameterRelations.objects.create(
                    to_parameter=parameter,
                    from_parameter=param,
                    is_affect=None,
                )
        return HttpResponseRedirect('/')

    else:
        parameters = Parameters.objects.exclude(subsystem=None)
        items = ''.join(
            f'<div>'
            f'<a href="{reverse("goal_parameter", kwargs={"parameter_slug": param.slug})}">'
            f'<button>{escape(param.name)}</button></a>'
            f'<p>{escape(str(param))}</p>'
            f'</div>'
            for param in parameters
            if param.subsystem
        )
        return render(request, 'app/with_context.html', context={
            'title': 'параметры',
            'content': mark_safe(items),
        })


def del_object(request, parameter_slug=None, system_slug=None, to_slug=None, from_slug=None):
    if system_slug is not None:
        system = get_object_or_404(SubSystem, slug=system_slug)
        system.delete()
    elif parameter_slug is not None:
        parameter = get_object_or_404(Parameters, slug=parameter_slug)
        parameter.delete()
    else:
        parameter_relations = get_object_or_404(
            ParameterRelations,
            to_parameter__slug=to_slug,
            from_parameter__slug=from_slug,
        )
        parameter_relations.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return HttpResponseRedirect('/')


def show_processes(request):
    if request.method == 'GET':
        # Получаем следующий необработанный параметр для каждого целевого
        mins = find_min()  # [(min_param, goal_parameter), ...]

        # Все уникальные целевые параметры, у которых есть хотя бы одна входящая связь
        all_goal_params = list(
            Parameters.objects.filter(incoming_links__isnull=False).distinct()
        )

        active_processes = []
        completed_processes = []

        for goal_parameter in all_goal_params:
            total = ParameterRelations.objects.filter(to_parameter=goal_parameter).count()
            processed = ParameterRelations.objects.filter(
                to_parameter=goal_parameter, is_affect__isnull=False
            ).count()
            percent = int(processed * 100 / total) if total > 0 else 0

            min_param = next((mp for mp, gp in mins if gp == goal_parameter), None)

            entry = {
                'min_parameter': min_param,
                'goal_parameter': goal_parameter,
                'percent': percent,
            }
            if percent == 100 or min_param is None:
                completed_processes.append(entry)
            else:
                active_processes.append(entry)

        return render(request, template_name='app/processes.html', context={
            'active_processes': active_processes,
            'completed_processes': completed_processes,
        })


def form_goal_parameter(request, goal_slug, min_slug):
    rel = get_object_or_404(
        ParameterRelations,
        to_parameter__slug=goal_slug,
        from_parameter__slug=min_slug,
    )

    if request.method == 'POST':
        form = ParameterRelationsFormSecond(request.POST, instance=rel)
        if form.is_valid():
            form.save()
            mins = find_min()
            if not mins:
                return HttpResponseRedirect(reverse(viewname='main_page'))
            return HttpResponseRedirect(
                reverse(
                    viewname='form_goal_parameter',
                    kwargs={
                        'goal_slug': rel.to_parameter.slug,
                        'min_slug': mins[0][0].slug,
                    },
                )
            )

    form = ParameterRelationsFormSecond(instance=rel)
    return render(request, template_name='app/form_goal_parameter.html', context={
        'form': form,
        'goal': rel.to_parameter,
        'source': rel.from_parameter,
    })


def parameters_tree(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    return render(request, template_name='app/subsystem/parameter_tree.html', context={'nodes': [system], 'parameter_flag': True})


def parameters_tree_goal(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    parameters = system.parameters.all()
    parameters_goal = [p for p in parameters if p.is_goal]
    return render(request, template_name='app/subsystem/parameter_goal.html', context={
        'nodes': [system],
        'parameter_flag': True,
        'parameters_goal': parameters_goal,
    })


def parameters_tree_goal_show(request, parameter_slug):
    """parameters_tree/goal/show/<slug:parameter_slug>"""
    parameter = get_object_or_404(Parameters, slug=parameter_slug)
    system = parameter.subsystem
    parameter_affect_goal = who_is_matter(parameter)
    return render(request, template_name='app/goal_parameter/tree_goal_parameter.html', context={
        'nodes': [system],
        'goal_parameter': parameter,
        'parameter_affect_goal': parameter_affect_goal,
    })


def find_min():
    """Возвращает список кортежей (min_param, goal_parameter) —
    следующий необработанный параметр для каждого целевого."""
    part_process = ParameterRelations.objects.filter(
        is_affect__isnull=True
    ).select_related('to_parameter', 'from_parameter__subsystem')

    to_rel = []
    for data in part_process:
        if data.to_parameter not in to_rel:
            to_rel.append(data.to_parameter)

    result = []
    for goal_parameter in to_rel:
        parameters = [
            data.from_parameter
            for data in part_process
            if data.to_parameter == goal_parameter
        ]
        min_param = None
        min_sys_num = float('inf')
        min_param_num = float('inf')
        for param in parameters:
            if not param.subsystem:
                continue
            sys_num = param.subsystem.number
            if sys_num < min_sys_num or (sys_num == min_sys_num and param.number < min_param_num):
                min_sys_num = sys_num
                min_param_num = param.number
                min_param = param
        result.append((min_param, goal_parameter))
    return result


def who_is_matter(goal_param):
    """Найти список параметров, которые влияют на целевой goal_param (объект Parameters)."""
    relations = ParameterRelations.objects.filter(
        is_affect=True, to_parameter=goal_param
    ).select_related('from_parameter')
    return [rel.from_parameter for rel in relations]


def all_parameter_relations(request):
    parameter_relations = ParameterRelations.objects.all()
    return render(request, 'app/all_parameter_relations/all_parameter_relations.html', context={
        'parameter_relations': parameter_relations,
    })


def all_parameters(request):
    parameters = Parameters.objects.all()
    return render(request, 'app/all_parameters/all_parameters.html', context={'parameters': parameters})


# API для дерева D3

def api_tree(request, system_slug):
    """API endpoint, возвращающий дерево в JSON-формате для D3.js."""
    system = get_object_or_404(SubSystem, slug=system_slug)
    return JsonResponse(system.to_dict())


def show_d3_tree(request, system_slug):
    """Рендер страницы с D3-деревом."""
    system = get_object_or_404(SubSystem, slug=system_slug)
    return render(request, 'app/d3/d3_tree.html', context={'node': system})


def api_parameters_tree(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    return JsonResponse(system.to_dict())


def all_parameters_tree(request, system_slug):
    system = get_object_or_404(SubSystem, slug=system_slug)
    all_params = get_all_parameters_recursive(system)
    goal_parameters = []
    for param in all_params:
        if param.is_goal:
            affected = ParameterRelations.objects.filter(
                to_parameter=param, is_affect=True
            ).values_list('from_parameter_id', flat=True)
            goal_parameters.append({
                'id': param.id,
                'name': param.name,
                'affected_ids': list(affected),
            })
    return render(request, 'app/d3/all_parameters_tree.html', {
        'node': system,
        'goal_parameters': goal_parameters,
        'goal_parameters_json': mark_safe(json.dumps(goal_parameters)),
    })


def api_goal_parameters_tree(request, parameter_slug):
    parameter = get_object_or_404(Parameters, slug=parameter_slug)
    system = parameter.subsystem
    if not parameter.is_goal:
        raise Http404()
    data = system.to_dict()
    for relation in ParameterRelations.objects.filter(to_parameter=parameter, is_affect=True):
        if not rec_change_parameter(data, relation.from_parameter.id):
            raise ValueError(f'Параметр id={relation.from_parameter.id} не найден в дереве')
    return JsonResponse(data)


def goal_parameters_tree(request, parameter_slug):
    parameter = get_object_or_404(Parameters, slug=parameter_slug)
    system = parameter.subsystem
    return render(request, 'app/d3/goal_parameters_tree.html', {'node': system, 'goal_parameter': parameter})


def rec_change_parameter(data, id):
    """Рекурсивно помечает параметр с нужным id как is_affect=True."""
    for param in data.get('parameters', []):
        if param['id'] == id:
            param['is_affect'] = True
            return 1
    for child in data.get('children', []):
        if rec_change_parameter(child, id) == 1:
            return 1
    return 0


def get_all_parameters_recursive(subsystem):
    """Рекурсивно собирает все параметры системы и её потомков."""
    params = list(subsystem.parameters.all())
    for child in subsystem.children.all():
        params.extend(get_all_parameters_recursive(child))
    return params


def important_matrices(request, parameter_slug):
    parameter = get_object_or_404(Parameters, slug=parameter_slug)
    name_goal_parameter = parameter.name
    if request.method == 'GET':
        all_relations = ParameterRelations.objects.filter(to_parameter=parameter)
        same_level = []
        low_level = []
        for relation in all_relations:
            to_par = relation.to_parameter
            from_par = relation.from_parameter
            if to_par.subsystem != from_par.subsystem:
                low_level.append(from_par)
            else:
                same_level.append(from_par)
        count_same_level = len(same_level)
        count_low_level = len(low_level)
        matrix_same_level = [[] for _ in range(count_same_level + 2)]
        matrix_low_level = [[] for _ in range(count_low_level)]

        for i in range(count_same_level + 2):
            for j in range(count_same_level + 2):
                if i == j:
                    matrix_same_level[i].append('-')
                elif i == 0 and j == 1:
                    matrix_same_level[i].append(name_goal_parameter)
                elif i == 0:
                    matrix_same_level[i].append(same_level[j - 2].name)
                elif j == 0 and i == 1:
                    matrix_same_level[i].append(name_goal_parameter)
                elif j == 0:
                    matrix_same_level[i].append(same_level[i - 2].name)
                else:
                    obj = ParameterImportance.objects.filter(
                        first_parameter__in=[same_level[i - 2], same_level[j - 2]],
                        second_parameter__in=[same_level[i - 2], same_level[j - 2]],
                    )
                    matrix_same_level[i].append(len(obj))

        for i in range(2):
            for j in range(count_low_level + 1):
                if i == j == 0:
                    matrix_low_level[i].append('-')
                elif i == 0:
                    matrix_low_level[i].append(low_level[j - 1].name)
                elif i == 1 and j == 0:
                    matrix_low_level[i].append(name_goal_parameter)
                else:
                    matrix_low_level[i].append('none')

        return render(request, template_name='app/important_matrices/important_matrices.html', context={
            'goal_parameter': parameter,
            'count_same_level': range(count_same_level + 2),
            'count_low_level': range(count_low_level + 2),
            'matrix_low_level': matrix_low_level,
            'matrix_same_level': matrix_same_level,
        })


def new_view(request, parameter_slug):
    goal_parameter = get_object_or_404(Parameters, slug=parameter_slug)
    all_relations = ParameterRelations.objects.filter(
        to_parameter=goal_parameter,
        from_parameter__subsystem=goal_parameter.subsystem,
    )
    affected_parameters = [relation.from_parameter for relation in all_relations]
    all_parameters = affected_parameters + [goal_parameter]

    all_parameters_importance = []
    for i in range(len(all_parameters)):
        for j in range(len(all_parameters)):
            if i == j:
                continue
            one1 = ParameterImportance.objects.filter(
                second_parameter=all_parameters[i], first_parameter=all_parameters[j]
            )
            second2 = ParameterImportance.objects.filter(
                first_parameter=all_parameters[i], second_parameter=all_parameters[j]
            )
            if not one1.exists() and not second2.exists():
                obj = ParameterImportance.objects.create(
                    first_parameter=all_parameters[i],
                    second_parameter=all_parameters[j],
                )
                all_parameters_importance.append(obj)
            elif one1.exists():
                all_parameters_importance.append(one1[0])
            elif second2.exists():
                all_parameters_importance.append(second2[0])

    all_parameters_importance_without_value = [
        pi for pi in all_parameters_importance if pi.value == 0
    ]

    if not all_parameters_importance_without_value:
        return render(request, 'app/with_context.html', context={
            'title': 'Готово',
            'content': mark_safe('<h2>Все значения важности уже заполнены.</h2>'),
        })

    if request.method == 'POST':
        form = ParameterImportanceForm(request.POST, instance=all_parameters_importance_without_value[0])
        if form.is_valid():
            form.save()
            return redirect(request.path_info)
    else:
        form = ParameterImportanceForm(instance=all_parameters_importance_without_value[0])
    return render(request, template_name='app/important_matrices/important_matrices_form.html', context={
        'parameter_importance': all_parameters_importance_without_value[0],
          'form': form,
    })


def relation_type_process(request, parameter_slug):
    """Форма заполнения типа связи (А1/А2/А3) для каждой пары параметров."""
    goal_parameter = get_object_or_404(Parameters, slug=parameter_slug)
    all_relations = ParameterRelations.objects.filter(
        to_parameter=goal_parameter,
        from_parameter__subsystem=goal_parameter.subsystem,
    )
    affected_parameters = [rel.from_parameter for rel in all_relations]
    all_parameters = affected_parameters + [goal_parameter]

    # Собираем все уникальные пары ParameterImportance для этого набора
    all_pairs = []
    seen = set()
    for i in range(len(all_parameters)):
        for j in range(len(all_parameters)):
            if i == j:
                continue
            p1, p2 = all_parameters[i], all_parameters[j]
            key = tuple(sorted([p1.pk, p2.pk]))
            if key in seen:
                continue
            seen.add(key)
            obj = (
                ParameterImportance.objects.filter(first_parameter=p1, second_parameter=p2).first()
                or ParameterImportance.objects.filter(first_parameter=p2, second_parameter=p1).first()
            )
            if obj:
                all_pairs.append(obj)

    pending = [pi for pi in all_pairs if not pi.relation_type]

    if not pending:
        return render(request, 'app/with_context.html', context={
            'title': 'Готово',
            'content': mark_safe('<h2>Типы связей для всех пар уже определены.</h2>'),
        })

    current = pending[0]

    if request.method == 'POST':
        form = ParameterRelationTypeForm(request.POST, instance=current)
        if form.is_valid():
            form.save()
            return redirect(request.path_info)
    else:
        form = ParameterRelationTypeForm(instance=current)

    return render(request, template_name='app/important_matrices/relation_type_form.html', context={
        'parameter_importance': current,
        'form': form,
        'done': len(all_pairs) - len(pending),
        'total': len(all_pairs),
        'goal_parameter': goal_parameter,
    })


def relation_type_matrix(request, parameter_slug):
    """Таблица 27: матрица типов связей (А1/А2/А3) между параметрами."""
    goal_parameter = get_object_or_404(Parameters, slug=parameter_slug)
    all_relations = ParameterRelations.objects.filter(
        to_parameter=goal_parameter,
        from_parameter__subsystem=goal_parameter.subsystem,
    )
    affected_parameters = [rel.from_parameter for rel in all_relations]
    all_parameters = affected_parameters + [goal_parameter]

    # Fetch all relevant ParameterImportance objects in one query
    # and build a frozenset-keyed lookup for symmetric pair lookup
    pair_lookup = {}
    for pi in ParameterImportance.objects.filter(
        first_parameter__in=all_parameters,
        second_parameter__in=all_parameters,
    ):
        key = frozenset([pi.first_parameter_id, pi.second_parameter_id])
        if pi.relation_type:
            pair_lookup[key] = {'label': pi.get_relation_type_display(), 'type': pi.relation_type}

    matrix = []
    for param in all_parameters:
        cells = []
        for other in all_parameters:
            if param.pk == other.pk:
                cells.append({'label': '—', 'type': 'diag'})
            else:
                key = frozenset([param.pk, other.pk])
                cells.append(pair_lookup.get(key, {'label': '?', 'type': None}))
        matrix.append({'param': param, 'cells': cells})

    return render(request, template_name='app/important_matrices/relation_type_matrix.html', context={
        'goal_parameter': goal_parameter,
        'parameters': all_parameters,
        'matrix': matrix,
    })
