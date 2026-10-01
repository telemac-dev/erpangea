from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Project, Task, TaskStatusEnum, ProjectStatusEnum
from .forms import TaskForm

def _get_kanban_context(project):
    tasks = Task.objects.filter(fase__projeto=project) if project else []
    return {
        'project': project,
        'a_fazer': [t for t in tasks if t.status == TaskStatusEnum.A_FAZER],
        'andamento': [t for t in tasks if t.status == TaskStatusEnum.EM_ANDAMENTO],
        'impedimento': [t for t in tasks if t.status == TaskStatusEnum.IMPEDIMENTO],
        'concluidas': [t for t in tasks if t.status == TaskStatusEnum.CONCLUIDA],
    }

def kanban_board(request):
    project = Project.objects.first()
    context = _get_kanban_context(project)
    context['all_projects'] = Project.objects.all()
    return render(request, 'projects/kanban.html', context)

def kanban_content(request):
    project_id = request.GET.get('project_id')
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
    else:
        project = Project.objects.first()
    context = _get_kanban_context(project)
    return render(request, 'projects/partials/kanban_columns.html', context)

def create_task_modal(request):
    project = Project.objects.first()
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            form.save()
            response = HttpResponse('<div class="alert alert-success m-3">Tarefa criada com sucesso!</div>')
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = TaskForm(project=project)
        
    return render(request, 'projects/partials/create_task_modal.html', {'form': form, 'project': project})

def move_task(request, pk, new_status):
    task = get_object_or_404(Task, pk=pk)
    if new_status in TaskStatusEnum.values:
        task.status = new_status
        task.save()
    project = task.fase.projeto
    context = _get_kanban_context(project)
    return render(request, 'projects/partials/kanban_columns.html', context)

def advance_status_modal(request, pk):
    project = get_object_or_404(Project, pk=pk)
    error_msg = None
    success_msg = None

    if request.method == 'POST':
        novo_status = request.POST.get('novo_status')
        if novo_status in ProjectStatusEnum.values:
            status_antigo = project.status
            project.status = novo_status
            try:
                project.full_clean()
                project.save()
                response = HttpResponse('<div class="alert alert-success m-3">Status do projeto atualizado com sucesso!</div>')
                response['HX-Refresh'] = 'true'
                return response
            except ValidationError as e:
                project.status = status_antigo # Reverte
                error_msg = "; ".join(e.messages)

    return render(request, 'projects/partials/advance_status_modal.html', {
        'project': project,
        'statuses': ProjectStatusEnum.choices,
        'error_msg': error_msg
    })
