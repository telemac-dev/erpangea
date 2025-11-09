from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import LoginForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import LoginHistory


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login_view(request):
    """
    View de login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Configurar sessão
                if not remember_me:
                    request.session.set_expiry(0)
                
                # Registrar histórico de login
                LoginHistory.objects.create(
                    user=user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'Bem-vindo de volta, {user.get_full_name() or user.username}!')
                
                # Redirecionar para a página solicitada ou dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """
    View de logout
    """
    logout(request)
    messages.info(request, 'Você saiu do sistema com sucesso.')
    return redirect('accounts:login')


def register_view(request):
    """
    View de registro de novo usuário
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Você já pode fazer login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': 'Registrar'
    }
    return render(request, 'accounts/register.html', context)


@login_required
def profile_view(request):
    """
    View do perfil do usuário
    """
    # Últimos logins
    recent_logins = LoginHistory.objects.filter(user=request.user)[:5]
    
    context = {
        'title': 'Meu Perfil',
        'recent_logins': recent_logins
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    View para editar o perfil
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'title': 'Editar Perfil',
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def password_change_view(request):
    """
    View para alterar senha
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    
    # Adicionar classes CSS aos campos
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    
    context = {
        'title': 'Alterar Senha',
        'form': form
    }
    return render(request, 'accounts/password_change.html', context)


def is_staff_or_superuser(user):
    """Verifica se o usuário é staff ou superuser"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_superuser)
def user_list_view(request):
    """
    View para listar todos os usuários (apenas para staff)
    """
    search_query = request.GET.get('search', '')
    
    users = User.objects.select_related('profile').all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Gerenciar Usuários',
        'page_obj': page_obj,
        'search_query': search_query
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def user_detail_view(request, user_id):
    """
    View para ver detalhes de um usuário específico
    """
    user = get_object_or_404(User, id=user_id)
    recent_logins = LoginHistory.objects.filter(user=user)[:10]
    
    context = {
        'title': f'Perfil de {user.get_full_name() or user.id}',
        'profile_user': user,
        'recent_logins': recent_logins
    }
    return render(request, 'accounts/user_detail.html', context)
