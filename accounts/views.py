from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import CustomUser, UserRoleChoices
from .forms import CustomUserCreationForm, UserAdminEditForm
from .decorators import admin_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Erro ao criar conta. Verifique os dados informados.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# --- USER MANAGEMENT VIEWS (ADMIN RESTRICTED) ---

@admin_required
def user_list(request):
    role_filter = request.GET.get('role', '')
    query = request.GET.get('q', '')

    users = CustomUser.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    roles = UserRoleChoices.choices

    context = {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'roles': roles,
    }
    return render(request, 'accounts/user_list.html', context)

@admin_required
def user_edit(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserAdminEditForm(request.POST, instance=target_user)
        if form.is_valid():
            u = form.save()
            messages.success(request, f'Nível de acesso do usuário "{u.username}" atualizado com sucesso!')
            return redirect('user_list')
        else:
            messages.error(request, 'Erro ao atualizar usuário.')
    else:
        form = UserAdminEditForm(instance=target_user)

    return render(request, 'accounts/user_form.html', {'form': form, 'target_user': target_user})

@admin_required
def user_toggle_active(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_label = "ativado" if target_user.is_active else "desativado"
        messages.success(request, f'Usuário "{target_user.username}" foi {status_label}.')
    return redirect('user_list')
