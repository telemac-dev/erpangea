from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, Task, Delivery, ProjectStatusChoices, TaskStatusChoices
from .forms import ProjectForm, TaskForm, DeliveryForm

@login_required
def project_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    projects = Project.objects.select_related('client', 'technical_responsible', 'manager').all()

    if query:
        projects = projects.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(client__name__icontains=query) |
            Q(city__icontains=query)
        )

    if status_filter:
        projects = projects.filter(status=status_filter)

    statuses = ProjectStatusChoices.choices

    context = {
        'projects': projects,
        'query': query,
        'status_filter': status_filter,
        'statuses': statuses,
    }
    return render(request, 'projects/project_list.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Projeto "{project.code} - {project.name}" criado com sucesso!')
            return redirect('project_detail', pk=project.pk)
        else:
            messages.error(request, 'Erro ao criar projeto. Verifique os campos.')
    else:
        count = Project.objects.count() + 1
        initial_code = f"PRJ-2026-{count:03d}"
        form = ProjectForm(initial={'code': initial_code})

    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Novo Projeto de Engenharia'})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related(
            'client', 'contract', 'technical_responsible', 'manager'
        ).prefetch_related('tasks__assigned_to', 'deliveries__delivered_by'), 
        pk=pk
    )

    task_form = TaskForm()
    delivery_form = DeliveryForm()

    if request.method == 'POST':
        if 'action_task' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.save()
                messages.success(request, 'Nova tarefa adicionada ao projeto!')
                return redirect('project_detail', pk=project.pk)
        elif 'action_delivery' in request.POST:
            delivery_form = DeliveryForm(request.POST)
            if delivery_form.is_valid():
                delivery = delivery_form.save(commit=False)
                delivery.project = project
                delivery.delivered_by = request.user
                delivery.save()
                messages.success(request, 'Entrega registrada com sucesso!')
                return redirect('project_detail', pk=project.pk)

    context = {
        'project': project,
        'tasks': project.tasks.all(),
        'deliveries': project.deliveries.all(),
        'task_form': task_form,
        'delivery_form': delivery_form,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Projeto "{project.code}" atualizado com sucesso.')
            return redirect('project_detail', pk=project.pk)
        else:
            messages.error(request, 'Erro ao atualizar projeto.')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'title': f'Editar Projeto {project.code}'})

@login_required
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(TaskStatusChoices.choices):
            task.status = new_status
            task.save()
            messages.success(request, f'Status da tarefa "{task.name}" atualizado para {task.get_status_display()}.')
    return redirect('project_detail', pk=task.project.pk)
